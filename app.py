from flask import Flask, render_template, request, session, redirect, url_for, make_response, jsonify
import dash
from dash import html
from dash import dcc
from decimal import Decimal
import psycopg2
from helper import log_history, login_required, parse_numeric_value, capitalize_string
from functools import wraps
import bcrypt
import string

def create_conncur():
    conn = psycopg2.connect(
        dbname="salloc",
        user="postgres",
        password="Sarapus1",
        host="localhost"  # or the address of your PostgreSQL server
    )
    return conn, conn.cursor()

server = Flask(__name__)
server.secret_key = "sarapus1"


@server.route("/")
def landing():
    return render_template("landing.html")


# LOGIN
@server.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password").encode("utf-8")
        conn, cur = create_conncur()
        with conn:
            cur.execute(
                "SELECT * FROM users WHERE username = %s", 
                (username,)
            )
            user = cur.fetchone()
            if user and bcrypt.checkpw(password, user[2].encode("utf-8")):
                session["user_id"] = user[0]
                if user[4]:
                    resp = make_response(redirect("/index"))
                    if "consent" not in request.cookies:
                        resp.set_cookie("consent", "true")
                    return resp
                else:
                    return redirect("/index")
            else:
                return "Incorrect username or password"
        
    return render_template("landing.html")


@server.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect("/index")
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        consent = request.form.get("consentField")
        hashpass = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        hashpass = hashpass.decode("utf-8")
        conn, cur = create_conncur()
        with conn:
            cur.execute(
                "SELECT username FROM users WHERE username = %s",
                (username,)
            )
            check = cur.fetchone()
            if check:
                return "Username already registered, did you forget your password?"
            if password != confirm:
                return "Password did not match with confirmation password"
            if consent == "yes":
                consent_db = "t"
            elif consent == "no":
                consent_db = "f"
            else:
                return "Invalid or missing cookie consent value"    
            
            cur.execute(
                "INSERT INTO users (username, password, cookies) VALUES (%s, %s, %s)",
                (username, hashpass, consent_db)
            )
            resp = make_response(redirect("/account"))
            
            if consent == "yes":
                resp.set_cookie('consent', 'true', max_age=60*60*24*365*2)   
            return resp
            
    return render_template("register.html")

@server.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/")


@server.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    conn, cur = create_conncur()
    with conn:
        cur.execute(
            "DELETE FROM posts WHERE user_id = %s",
            (session["user_id"],)
        )
        cur.execute(
            "DELETE FROM history WHERE user_id = %s",
            (session["user_id"],)
        )
        cur.execute(
            "DELETE FROM users WHERE id = %s",
            (session["user_id"],)
        )
    
    session.pop("user_id", None)
    return redirect("/")


@server.route("/update_consent", methods=["POST"])
@login_required
def update_consent():
    consent = request.form.get("consentUpdate")
    resp = make_response(redirect("/account"))
    
    if consent == "yes":
        consent_db = "t"
        resp.set_cookie('consent', 'true', max_age=60*60*24*365*2)   
    elif consent == "no":
        consent_db = "f"
        cookies_to_delete = [cookie for cookie in request.cookies if cookie != "session"]
        for cookie_name in cookies_to_delete:
            resp.delete_cookie(cookie_name)
    else:
        return "No consent registered"
    
    conn, cur = create_conncur()
    with conn:
        cur.execute(
            "UPDATE users SET cookies = %s WHERE id = %s",
            (consent_db, session["user_id"],)
        )
        return resp
        


@server.route("/account")
@login_required
def account():
    conn, cur = create_conncur()
    with conn:
        cur.execute(
            "SELECT balance FROM users WHERE id = %s",
            (session["user_id"],)
        )
        balance = cur.fetchone()[0]
        cur.execute(
            "SELECT name, allocation_percentage, total_saved, goal FROM posts WHERE user_id = %s ORDER BY allocation_percentage DESC",
            (session["user_id"],)
        )
        posts = cur.fetchall()
        cur.execute(
            "SELECT TO_CHAR(date, 'DD/MM/YY'), post, type, amount, notes FROM history WHERE user_id = %s ORDER BY date DESC, time DESC",
            (session["user_id"],)
        )
        history = cur.fetchall()
        # Calulates remaining % to allocate
        total_alloc = sum(post[1] for post in posts)
        total_goal = sum(post[3] for post in posts)
        remain_alloc = max(0, 100 - total_alloc)
    return render_template(
        "account.html", 
        posts=posts, 
        history=history, 
        remain_alloc=remain_alloc, 
        balance=balance, 
        total_goal=total_goal)
        
        
# Gets new savings amount from user input, updates db
@server.route("/set_savings", methods=["POST"])
@login_required
def set_savings():
    savings = request.form.get("savings")
    conn, cur = create_conncur()
    with conn:
        cur.execute("UPDATE users SET balance = %s WHERE id = %s", (savings, session["user_id"]))
        conn.commit()
        return redirect("/account")
    
@server.route("/reset", methods=["POST"])
@login_required
def reset():
    user_id = session["user_id"]
    conn, cur = create_conncur()
    with conn:
        cur.execute(
            "UPDATE users SET balance = %s WHERE id = %s",
            ("0", user_id)
        )
        cur.execute(
            "DELETE FROM history WHERE user_id = %s",
            (user_id,)
        )
        cur.execute(
            "DELETE FROM posts WHERE user_id = %s",
            (user_id,)
        )
    return redirect("/account")

@server.route("/reset_posts", methods=["POST"])
@login_required
def reset_posts():
    conn, cur = create_conncur()
    with conn:
        cur.execute(
            "DELETE FROM posts WHERE user_id = %s",
            (session["user_id"],)
        )
    return redirect("/account")

# Add new post for user, updates db
@server.route("/add_post", methods=["POST"])
@login_required
def add_post():
    post = request.form.get("post")
    allocation = int(request.form.get("allocation"))
    goal = request.form.get("goal")
    conn, cur = create_conncur()
    with conn:
        # Checks if first post
        cur.execute(
            "SELECT * FROM posts WHERE user_id = %s", 
            (session["user_id"],)
        )
        posts = cur.fetchall()
        total_alloc = sum(post[3] for post in posts)
        if total_alloc + allocation > 100:
            return "Total allocation cannot exceed 100%"
        for check in posts:
            if check[2] == post:
                return "Post already exists, please use Edit Post to change"
        cur.execute(     
            "INSERT INTO posts (user_id, name, allocation_percentage, goal) VALUES (%s, %s, %s, %s)", 
            (session["user_id"], post, allocation, goal)
        )
        return redirect("/account")
        
@server.route("/remove_post", methods=["POST"])
@login_required
def remove_post():
    post = request.form.get("post")
    conn, cur = create_conncur()
    with conn:
        cur.execute(
            "DELETE FROM posts WHERE user_id = %s AND name = %s",
            (session["user_id"], post)
        )
        conn.commit()
        return redirect("/account")
    
    
@server.route("/edit_post", methods=["POST"])
@login_required
def edit_post():
    post = request.form.get("post")
    allocation = int(request.form.get("allocation"))
    goal = request.form.get("goal")
    conn, cur = create_conncur()
    with conn:
        cur.execute(
            "UPDATE posts SET allocation_percentage = %s, goal = %s WHERE user_id = %s AND name = %s",
            (allocation, goal, session["user_id"], post)
        ) 
        conn.commit()
        return redirect("/account")

@server.route("/update_table", methods=["POST"])
@login_required
def update_table():
    data = request.get_json()
    print("data collected")
    print(data)
    for row_data in data:
        old_name = row_data["oldName"]
        new_name = row_data.get("postName")
        new_goal = row_data.get("goal")
        new_alloc = row_data.get("salloc")
        if new_goal:
            new_goal = parse_numeric_value(new_goal)
        if new_alloc:
            new_alloc = parse_numeric_value(new_alloc)
        if new_name:
            new_name = capitalize_string(new_name)
        
        print(old_name)
        print(new_name)
        print(new_goal)
        print(new_alloc)
        print("Ready for SQL")
        conn, cur = create_conncur()
        with conn:
            if new_goal:
                cur.execute(
                    "UPDATE posts SET goal = %s WHERE user_id = %s AND name = %s",
                    (new_goal, session["user_id"], old_name)
                )
            if new_alloc:
                cur.execute(
                    "UPDATE posts SET allocation_percentage = %s WHERE user_id = %s AND name = %s",
                    (new_alloc, session["user_id"], old_name)
                )
            if new_name:
                cur.execute(
                    "UPDATE posts SET name = %s WHERE user_id = %s AND name = %s",
                    (new_name, session["user_id"], old_name)
                )
            print("Finished Adding - looping")
                
    return redirect("/index")

@server.route("/edit_", methods=["POST"])
@login_required
def edit_():
    conn, cur = create_conncur()
    try:
        for key, value in request.form.items():
            if key.startswith("new_goal_"):
                post = key[len("new_goal_"):]
                goal = value
                if goal != "":
                    cur.execute(
                        "UPDATE posts SET goal = %s WHERE user_id = %s AND name = %s",
                        (goal, session["user_id"], post)
                    )
            if key.startswith("new_alloc_"):
                post = key[len("new_alloc_"):]
                alloc = value
                if alloc != "":
                    cur.execute(
                        "UPDATE posts SET allocation_percentage = %s WHERE user_id = %s AND name = %s",
                        (alloc, session["user_id"], post)
                    )
                    
        # Checks if allocation exceeds 100%           
        cur.execute(
            "SELECT SUM(allocation_percentage) FROM posts WHERE user_id = %s",
            (session["user_id"],)
        )            
        total = cur.fetchone()[0]
        if total > 100:
            excess = total - 100
            conn.rollback()
            return f"Error: Total allocation exceeds 100% by {excess}%"
        else:
            conn.commit()
    except Exception as e:
        conn.rollback()
        return str(e)
                        
    return redirect("/account")

    
    
@server.route("/commit_savings", methods=["POST"])
@login_required
def commit_savings():
    conn, cur = create_conncur()
    with conn:
        cur.execute(
            "SELECT balance FROM users WHERE id = %s",
            (session["user_id"],)
        )
        balance = cur.fetchone()[0]
        cur.execute(
            "SELECT id, allocation_percentage FROM posts WHERE user_id = %s",
            (session["user_id"],)
        )
        posts = cur.fetchall()
        for post in posts:
            total_saved = balance * post[1] / 100
            cur.execute(
                "UPDATE posts SET total_saved = %s WHERE id = %s",
                (total_saved, post[0])
            )
        conn.commit()
    return redirect("/index")

@server.route("/generate_template", methods=["POST"])
@login_required
def generate_template():
    conn, cur = create_conncur()
    with conn:
        cur.execute(
            "SELECT balance FROM users WHERE id = %s",
            (session["user_id"],)
        )
        balance = cur.fetchone()[0]
        if balance <= 0:
            return "Please set total savings before generating posts"
        cur.execute(
            "SELECT * FROM posts WHERE user_id = %s",
            (session["user_id"],)
        )
        check = cur.fetchone()
        if check:
            return "Please reset your posts before adding template"
        template_posts = {
            "Emergency": 25,
            "Retirement": 20,
            "Debt Repayment": 10,
            "Vacation": 15,
            "Home Improvement": 15,
            "Personal": 5,
            "Investment": 10
        }
        for post_name, allocation_percentage in template_posts.items():
            current_savings = (Decimal(allocation_percentage) / 100) * balance
            goal = 2 * current_savings
            cur.execute(
                "INSERT INTO posts (user_id, name, allocation_percentage, goal) VALUES (%s, %s, %s, %s)",
                (session["user_id"], post_name, allocation_percentage, goal)
            )
        return redirect("/account")
        

@server.route("/custom_setup", methods=["POST"])
@login_required
def custom_setup():
    post_names = request.form.getlist("postName[]")
    post_goals = request.form.getlist("postGoal[]")
    post_alloc = request.form.getlist("postAllocation[]")
    conn, cur = create_conncur()
    with conn: 
        for name, goal, alloc in zip(post_names, post_goals, post_alloc):
            if name.strip () == "":
                continue
            
            name = string.capwords(name)
            goal = goal.strip() or "0"
            alloc = alloc.strip() or "0"

            cur.execute(
                "INSERT INTO posts (user_id, name, allocation_percentage, goal) VALUES (%s, %s, %s, %s)",
                (session["user_id"], name, alloc, goal)
            )
        cur.execute(
            "SELECT SUM(allocation_percentage) FROM posts WHERE user_id = %s",
            (session["user_id"],)
        )
        check = cur.fetchone()[0]
        if check > 100:
            return "Total % exceeds 100%"

                
    return redirect("/account")


@server.route("/index")
@login_required
def index():
    conn, cur = create_conncur()
    with conn:
        cur.execute(
            "SELECT balance FROM users WHERE id = %s",
            (session["user_id"],)
        )
        balance = cur.fetchone()[0]
        cur.execute(
            "SELECT name, allocation_percentage, total_saved, goal FROM posts WHERE user_id = %s",
            (session["user_id"],)
        )
        posts = cur.fetchall()
        print(posts)
        # Calulates remaining % to allocate
        total_alloc = sum(post[1] for post in posts)
        remain_alloc = int(max(0, 100 - total_alloc))
        total_saved = sum(post[2] for post in posts)
        total_goal = sum(post[3] for post in posts)
        remainder = balance - total_saved
    return render_template(
        "index.html", 
        posts=posts, 
        total_alloc=total_alloc, 
        total_saved=total_saved, 
        total_goal=total_goal, 
        remain_alloc=remain_alloc,
        balance=balance,
        remainder=remainder
    )


@server.route("/deposit", methods=["POST"])
@login_required
def deposit():
    amount = int(request.form.get("deposit"))
    conn, cur = create_conncur()
    with conn:
        cur.execute(
            "SELECT balance FROM users WHERE id = %s",
            (session["user_id"],)
        )
        balance = cur.fetchone()[0]
        new_balance = balance + amount
        cur.execute(
            "UPDATE users SET balance = %s WHERE id = %s",
            (new_balance, session["user_id"],)
        )
        cur.execute(
            "SELECT id, name, allocation_percentage, total_saved FROM posts WHERE user_id = %s",
            (session["user_id"],)
        )
        posts = cur.fetchall()
        for post in posts:
            deposit_amount = amount * (post[2] / 100)
            new_total = post[3] + deposit_amount
            cur.execute(
                "UPDATE posts SET total_saved = %s WHERE id = %s",
                (new_total, post[0])
            )
            
    log_history(conn, session["user_id"], "All", amount, "Salloc", "General Deposit")
    return redirect("/index")


@server.route("/specific_deposit", methods=["POST"])
@login_required
def specific_deposit():
    post = request.form.get("post")
    amount = int(request.form.get("deposit"))
    conn, cur = create_conncur()
    with conn:
        cur.execute(
            "SELECT balance FROM users WHERE id = %s",
            (session["user_id"],)
        )
        balance = cur.fetchone()[0]
        new_balance = balance + amount
        cur.execute(
            "UPDATE users SET balance = %s WHERE id = %s",
            (new_balance, session["user_id"],)
        )
        cur.execute(
            "SELECT total_saved FROM posts WHERE user_id = %s AND name = %s",
            (session["user_id"], post)
        )
        savings = cur.fetchone()[0]
        new_savings = savings + amount
        cur.execute(
            "UPDATE posts SET total_saved = %s WHERE user_id = %s AND name = %s",
            (new_savings, session["user_id"], post)
        )
    log_history(conn, session["user_id"], post, amount, "Deposit", "Specific Deposit")
    return redirect("/index")
    
    
@server.route("/undefined", methods=["POST"])
@login_required
def undefined():
    destination = request.form.get("post")
    amount = Decimal(request.form.get("remainder"))
    if amount <= 0:
        return redirect("/index")
    
    conn, cur = create_conncur()
    with conn:
        if destination == "general":
            cur.execute(
                "SELECT id, name, allocation_percentage, total_saved FROM posts WHERE user_id = %s",
                (session["user_id"],)
            )
            posts = cur.fetchall()
            for post in posts:
                deposit_amount = amount * (post[2] / 100)
                new_total = post[3] + deposit_amount
                cur.execute(
                    "UPDATE posts SET total_saved = %s WHERE id = %s",
                    (new_total, post[0])
                )
            return redirect("/index")
        
        cur.execute(
            "SELECT total_saved FROM posts WHERE user_id = %s AND name = %s",
            (session["user_id"], destination)
        )
        savings = cur.fetchone()[0]
        new_savings = savings + amount
        cur.execute(
            "UPDATE posts SET total_saved = %s WHERE user_id = %s AND name = %s",
            (new_savings, session["user_id"], destination)
        )

    return redirect("/index")


@server.route("/withdrawal", methods=["POST"])
@login_required
def withdrawal():
    post = request.form.get("post")
    amount = int(request.form.get("withdrawal"))
    notes = request.form.get("notes")
    conn, cur = create_conncur()
    with conn:
        # Updates balance minus the amount withdrawn
        cur.execute(
            "SELECT balance FROM users WHERE id = %s",
            (session["user_id"],)
        )
        balance = cur.fetchone()[0]
        new_balance = balance - amount
        cur.execute(
            "UPDATE users SET balance = %s WHERE id = %s",
            (new_balance, session["user_id"],)
        )
        # Updates savings amount from the post being withdrawn from
        cur.execute(
            "SELECT total_saved FROM posts WHERE user_id = %s AND name = %s",
            (session["user_id"], post)
        )
        total = cur.fetchone()[0]
        new_total = total - amount
        cur.execute(
            "UPDATE posts SET total_saved = %s WHERE user_id = %s AND name = %s",
            (new_total, session["user_id"], post)
        )
    log_history(conn, session["user_id"], post, amount, "Withdrawal", notes)
    return redirect("/index")


@server.route("/move", methods=["POST"])
@login_required
def move():
    pfrom = request.form.get("from")
    pto = request.form.get("to")
    amount = int(request.form.get("amount"))
    conn, cur = create_conncur()
    with conn:
        cur.execute(
            "UPDATE posts SET total_saved = total_saved - %s WHERE user_id = %s AND name = %s",
            (amount, session["user_id"], pfrom)
        )
        log_history(conn, session["user_id"], pfrom, amount, "Withdrawal", "Moved From")
        cur.execute(
            "UPDATE posts SET total_saved = total_saved + %s WHERE user_id = %s AND name = %s",
            (amount, session["user_id"], pto)
        )
        log_history(conn, session["user_id"], pto, amount, "Deposit", "Moved To")
        return redirect("/index")
        
        
@server.route("/transfer", methods=["POST"])
@login_required
def transfer():
    pfrom = request.form.get("from")
    pto = request.form.get("to")
    transfer_type = request.form.get("type")
    conn, cur = create_conncur()
    with conn:
        cur.execute(
            "SELECT total_saved FROM posts WHERE user_id = %s AND name = %s",
            (session["user_id"], pfrom) 
        )
        transfer_funds = cur.fetchone()[0]
        if transfer_type == "specific":          
            cur.execute(
                "SELECT total_saved FROM posts WHERE user_id = %s AND name = %s",
                (session["user_id"], pto)
            )
            posts = cur.fetchone()[0]
            new_saved = posts + transfer_funds
            cur.execute(
                "DELETE FROM posts WHERE user_id = %s AND name = %s",
                (session["user_id"], pfrom)
            )
            cur.execute(
                "UPDATE posts SET total_saved = %s WHERE user_id = %s AND name = %s",
                (new_saved, session["user_id"], pto)
            )
            return redirect("/index")
        
        else:
            cur.execute(
                "DELETE FROM posts WHERE user_id = %s AND name = %s",
                (session["user_id"], pfrom)
            )
            cur.execute(
                "SELECT id, total_saved, allocation_percentage FROM posts WHERE user_id = %s",
                (session["user_id"],)
            )
            posts = cur.fetchall()
            for post in posts:
                transfer = transfer_funds * (post[2] / 100)
                new_total = post[1] + transfer
                cur.execute(
                    "UPDATE posts SET total_saved = %s WHERE id = %s",
                    (new_total, post[0])
                )
            
        return redirect("/index")
            
            
# Dash part
app = dash.Dash(
    __name__,
    server=server,
    routes_pathname_prefix='/dash/'
)


app.layout = html.Div("My Dash app")
app.debug = True


if __name__ == "__main__":
    server.run(debug=True)
