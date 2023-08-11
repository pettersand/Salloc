from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
    make_response,
    jsonify,
    flash,
)
from flask_mail import Mail, Message
import dash
from dash import html, dcc
from dash import dcc
from decimal import Decimal
import psycopg2
from helper import (
    log_history, 
    login_required, 
    parse_numeric_value, 
    capitalize_string, 
    is_valid_length, 
    is_valid_email, 
    sanitize_input,
)
from functools import wraps
import bcrypt
import string
import re


def create_conncur():
    conn = psycopg2.connect(
        dbname="salloc",
        user="postgres",
        password="Sarapus1",
        host="localhost",  # or the address of your PostgreSQL server
    )
    return conn, conn.cursor()


server = Flask(__name__)
server.secret_key = "sarapus1"

# Configure Flask-Mail with Gmail settings
server.config["MAIL_SERVER"] = "smtp.sendgrid.net"
server.config["MAIL_PORT"] = 587
server.config["MAIL_USERNAME"] = "apikey"
server.config[
    "MAIL_PASSWORD"
] = "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"
server.config["MAIL_USE_TLS"] = True
server.config["MAIL_USE_SSL"] = False

mail = Mail(server)




# Add check if logged in, auto redirect
@server.route("/")
def landing():
    return render_template("landing.html")


# LOGIN
@server.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = sanitize_input(request.form.get("username"))
        password = request.form.get("password").encode("utf-8")

        # Validate input
        conn, cur = create_conncur()
        with conn:
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            if user and bcrypt.checkpw(password, user[2].encode("utf-8")):
                session["user_id"] = user[0]
                next_url = request.args.get('next') or url_for('index')
                resp = make_response(redirect(next_url))
                if user[4] and "consent" not in request.cookies:
                    resp.set_cookie("consent", "true", secure=True, httponly=True)
                return resp
            else:
                error = "Incorrect username or password"

    return render_template("landing.html", error=error)


@server.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if "user_id" in session:
        return redirect("/index")

    if request.method == "POST":
        username = sanitize_input(request.form.get("username"))
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        consent = request.form.get("consentField")

        # Validate username and password
        if not is_valid_length(username, 4, 12) or not username.isalnum():
            error = "Invalid username. Must be 4-12 alphanumeric characters."
        elif not is_valid_length(password, 6, 40) or password != confirm:
            error = "Invalid password or passwords do not match."
        else:
            hashpass = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            hashpass = hashpass.decode("utf-8")
            conn, cur = create_conncur()
            with conn:
                cur.execute("SELECT username FROM users WHERE username = %s", (username,))
                check = cur.fetchone()
                if check:
                    error = "Username already taken."
                else:
                    if consent == "yes":
                        consent_db = "t"
                    elif consent == "no":
                        consent_db = "f"
                    else:
                        error = "Choose an option for the consent checkboxes."

                    if not error:
                        cur.execute(
                            "INSERT INTO users (username, password, cookies) VALUES (%s, %s, %s)",
                            (username, hashpass, consent_db),
                        )
                        resp = make_response(redirect("/index"))

                        if consent == "yes":
                            resp.set_cookie("consent", "true", max_age=60 * 60 * 24 * 365 * 2, secure=True, httponly=True)
                        return resp

    return render_template("register.html", error=error)


@server.route("/logout")
def logout():
    session.clear() # Clear the entire session
    flash("You have been logged out successfully.", "success") # Flash a success message
    return redirect("/")

from flask import flash, redirect, url_for

@server.route("/contact_me", methods=["POST"])
@login_required
def contact_me():
    name = sanitize_input(request.form["name"])
    email = sanitize_input(request.form["email"])
    topic = sanitize_input(request.form["topic"])
    message_body = sanitize_input(request.form["message"])

    if not is_valid_email(email):
        flash("Invalid email address!", "error")
        return redirect(url_for('index')) # Redirect to the contact page or appropriate page

    msg = Message(
        "New Contact Form Submission",
        sender="savingsalloc@gmail.com",
        recipients=["petter.sand@gmail.com"],
    )
    msg.body = f"Name: {name}\nEmail: {email}\nTopic: {topic}\nMessage: {message_body}"

    try:
        mail.send(msg)
        flash("Message Sent!", "success")
    except Exception as e:
        flash(f"An error occurred while sending the message: {str(e)}", "error")

    return redirect("/index")


@server.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    conn, cur = create_conncur()
    try:
        with conn:
            conn.autocommit = False # Turn off autocommit to start a transaction
            cur.execute("DELETE FROM posts WHERE user_id = %s", (session["user_id"],))
            cur.execute("DELETE FROM history WHERE user_id = %s", (session["user_id"],))
            cur.execute("DELETE FROM users WHERE id = %s", (session["user_id"],))
            conn.commit() # Commit the transaction
        flash("Your account has been deleted successfully.", "success")
    except Exception as e:
        conn.rollback() # Roll back the transaction in case of an error
        flash(f"An error occurred while deleting your account: {str(e)}", "error")
    finally:
        conn.autocommit = True # Turn autocommit back on

    session.pop("user_id", None)
    return redirect("/")


@server.route("/update_consent", methods=["POST"])
@login_required
def update_consent():
    consent = request.form.get("consentUpdate")
    if consent not in ["yes", "no"]:
        flash("Invalid consent value provided.", "error")
        return redirect("/index")

    resp = make_response(redirect("/index"))

    if consent == "yes":
        consent_db = "t"
        resp.set_cookie("consent", "true", max_age=60 * 60 * 24 * 365 * 2, secure=True, httponly=True)
    elif consent == "no":
        consent_db = "f"
        cookies_to_delete = [cookie for cookie in request.cookies if cookie != "session"]
        for cookie_name in cookies_to_delete:
            resp.delete_cookie(cookie_name)

    conn, cur = create_conncur()
    with conn:
        cur.execute(
            "UPDATE users SET cookies = %s WHERE id = %s",
            (
                consent_db,
                session["user_id"],
            ),
        )
    flash("Consent preferences updated successfully.", "success")
    return resp


# Gets new savings amount from user input, updates db
@server.route("/set_savings", methods=["POST"])
@login_required
def set_savings():
    savings = request.form.get("savings")

    # Validate the savings input
    try:
        savings = float(savings)
        if savings <= 0:
            flash("Savings amount cannot be negative.", "error")
            return redirect("/index")
    except ValueError:
        flash("Invalid savings amount provided.", "error")
        return redirect("/index")

    conn, cur = create_conncur()
    with conn:
        # Check total allocated savings
        cur.execute(
            "SELECT SUM(total_saved) FROM posts WHERE user_id = %s", 
            (session["user_id"],)
        )
        total_allocated_savings = cur.fetchone()[0] or 0

        if savings < total_allocated_savings:
            flash("Total savings must be greater than or equal to the total allocated savings.", "error")
            return redirect("/index")

        cur.execute(
            "UPDATE users SET balance = %s WHERE id = %s", 
            (savings, session["user_id"],)
        )
        
        flash("Savings amount updated successfully.", "success")
        return redirect("/index")


@server.route("/reset", methods=["POST"])
@login_required
def reset():
    user_id = session["user_id"]
    conn, cur = create_conncur()
    with conn:
        try:
            cur.execute("BEGIN") # Start a transaction
            cur.execute("UPDATE users SET balance = %s WHERE id = %s", ("0", user_id))
            cur.execute("DELETE FROM history WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM posts WHERE user_id = %s", (user_id,))
            cur.execute("COMMIT") # Commit the transaction
            flash("Account reset successfully.", "success")
        except:
            cur.execute("ROLLBACK") # Roll back the transaction in case of an error
            flash("An error occurred while resetting the account. Please try again.", "error")
    return redirect("/index")


@server.route("/reset_posts", methods=["POST"])
@login_required
def reset_posts():
    conn, cur = create_conncur()
    with conn:
        try:
            cur.execute(
                "DELETE FROM posts WHERE user_id = %s", 
                (session["user_id"],)
            )
            flash("Posts reset successfully.", "success")
        except:
            flash("An error occurred while resetting the posts. Please try again.", "error")
    return redirect("/index")


@server.route("/reset_savings", methods=["POST"])
@login_required
def reset_savings():
    conn, cur = create_conncur()
    with conn:
        try:
            cur.execute(
                "UPDATE posts SET total_saved = %s WHERE user_id = %s",
                ("0", session["user_id"],)
            )
            flash("Savings reset successfully.", "success")
        except:
            flash("An error occurred while resetting the savings. Please try again.", "error")
    return redirect("/index")


@server.route("/remove_post", methods=["POST"])
@login_required
def remove_post():
    post = request.form.get("post")

    # Validate the post parameter
    if not post:
        flash("Invalid post name provided.", "error")
        return redirect("/index")

    conn, cur = create_conncur()
    with conn:
        try:
            cur.execute(
                "DELETE FROM posts WHERE user_id = %s AND name = %s",
                (session["user_id"], post),
            )
            if cur.rowcount == 0:
                flash("Post not found.", "error")
            else:
                flash("Post removed successfully.", "success")
            conn.commit()
        except:
            flash("An error occurred while removing the post. Please try again.", "error")
    return redirect("/index")


@server.route("/update_table", methods=["POST"])
@login_required
def update_table():
    data = request.get_json()
    print(data)

    if not data:
        flash("No data provided for update.", "error")
        return redirect("/index")

    conn, cur = create_conncur()
    with conn:
        try:
            for row_data in data:
                old_name = row_data.get("oldName")
                new_name = row_data.get("postName")
                new_goal = row_data.get("goal")
                new_alloc = row_data.get("salloc")

                # Validate the data
                if not old_name:
                    continue  # Skip this row if old_name is missing

                if new_goal is not None:
                    new_goal = parse_numeric_value(new_goal)
                    cur.execute(
                        "UPDATE posts SET goal = %s WHERE user_id = %s AND name = %s",
                        (new_goal, session["user_id"], old_name),
                    )
                if new_alloc is not None:
                    new_alloc = parse_numeric_value(new_alloc)
                    cur.execute(
                        "UPDATE posts SET allocation_percentage = %s WHERE user_id = %s AND name = %s",
                        (new_alloc, session["user_id"], old_name),
                    )
                if new_name:
                    new_name = capitalize_string(new_name)
                    cur.execute(
                        "UPDATE posts SET name = %s WHERE user_id = %s AND name = %s",
                        (new_name, session["user_id"], old_name),
                    )                

            conn.commit()
            flash("Table updated successfully.", "success")
            return jsonify({"redirect": url_for('index')})

        except Exception as e:
            conn.rollback()
            flash(f"An error occurred while updating the table: {str(e)}", "error")
            
    return redirect("/index")


@server.route("/commit_savings", methods=["POST"])
@login_required
def commit_savings():
    conn, cur = create_conncur()
    with conn:
        cur.execute("SELECT balance FROM users WHERE id = %s", (session["user_id"],))
        balance = cur.fetchone()[0]
        cur.execute(
            "SELECT id, allocation_percentage FROM posts WHERE user_id = %s",
            (session["user_id"],),
        )
        posts = cur.fetchall()
        for post in posts:
            total_saved = balance * post[1] / 100
            cur.execute(
                "UPDATE posts SET total_saved = %s WHERE id = %s",
                (total_saved, post[0]),
            )
        conn.commit()
    return redirect("/index")


@server.route("/generate_template", methods=["POST"])
@login_required
def generate_template():
    conn, cur = create_conncur()
    with conn:
        cur.execute("SELECT balance FROM users WHERE id = %s", (session["user_id"],))
        balance = cur.fetchone()[0]
        if balance <= 0:
            return "Please set total savings before generating posts"
        cur.execute("SELECT * FROM posts WHERE user_id = %s", (session["user_id"],))
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
            "Investment": 10,
        }
        for post_name, allocation_percentage in template_posts.items():
            current_savings = (Decimal(allocation_percentage) / 100) * balance
            goal = 2 * current_savings
            cur.execute(
                "INSERT INTO posts (user_id, name, allocation_percentage, goal) VALUES (%s, %s, %s, %s)",
                (session["user_id"], post_name, allocation_percentage, goal),
            )
        return redirect("/index")


@server.route("/custom_setup", methods=["POST"])
@login_required
def custom_setup():
    post_names = request.form.getlist("postName[]")
    post_goals = request.form.getlist("postGoal[]")
    post_alloc = request.form.getlist("postAllocation[]")
    conn, cur = create_conncur()
    with conn:
        for name, goal, alloc in zip(post_names, post_goals, post_alloc):
            if name.strip() == "":
                continue

            name = string.capwords(name)
            goal = goal.strip() or "0"
            alloc = alloc.strip() or "0"

            cur.execute(
                "INSERT INTO posts (user_id, name, allocation_percentage, goal) VALUES (%s, %s, %s, %s)",
                (session["user_id"], name, alloc, goal),
            )
        cur.execute(
            "SELECT SUM(allocation_percentage) FROM posts WHERE user_id = %s",
            (session["user_id"],),
        )
        check = cur.fetchone()[0]
        if check > 100:
            return "Total % exceeds 100%"

    return redirect("/index")


@server.route("/index")
@login_required
def index():
    conn, cur = create_conncur()
    with conn:
        cur.execute("SELECT balance FROM users WHERE id = %s", (session["user_id"],))
        balance = cur.fetchone()[0]
        cur.execute(
            "SELECT name, allocation_percentage, total_saved, goal FROM posts WHERE user_id = %s",
            (session["user_id"],),
        )
        posts = cur.fetchall()
        alerts = []
        # Calulates remaining % to allocate
        total_alloc = sum(post[1] for post in posts)
        remain_alloc = int(max(0, 100 - total_alloc))
        total_saved = sum(post[2] for post in posts)
        total_goal = sum(post[3] for post in posts)
        remainder = balance - total_saved
        for post in posts:
            if post[2] >= post[3]:
                alerts.append(
                    f"Congratulations! You've reached your goal for Post '{post[0]}'. Don't forget to either increase the goal, or reallocate its percentage."
                )

        if remainder > 0:
            alerts.append(
                f"You have funds not yet allocated to the sum of {remainder}. Use the 'Allocate now' button"
            )
        if remain_alloc > 0:
            alerts.append(f"You have {remain_alloc}% left to allocate.")
        cur.execute(
            "SELECT TO_CHAR(date, 'DD/MM/YY'), post, type, amount, notes FROM history WHERE user_id = %s ORDER BY date DESC, time DESC LIMIT 7",
            (session["user_id"],),
        )
        history = cur.fetchall()

    return render_template(
        "index.html",
        posts=posts,
        total_alloc=total_alloc,
        total_saved=total_saved,
        total_goal=total_goal,
        remain_alloc=remain_alloc,
        balance=balance,
        remainder=remainder,
        history=history,
        alerts=alerts,
    )


@server.route("/deposit", methods=["POST"])
@login_required
def deposit():
    amount = int(request.form.get("deposit"))
    conn, cur = create_conncur()
    with conn:
        cur.execute("SELECT balance FROM users WHERE id = %s", (session["user_id"],))
        balance = cur.fetchone()[0]
        new_balance = balance + amount
        cur.execute(
            "UPDATE users SET balance = %s WHERE id = %s",
            (
                new_balance,
                session["user_id"],
            ),
        )
        cur.execute(
            "SELECT id, name, allocation_percentage, total_saved FROM posts WHERE user_id = %s",
            (session["user_id"],),
        )
        posts = cur.fetchall()
        for post in posts:
            deposit_amount = amount * (post[2] / 100)
            new_total = post[3] + deposit_amount
            cur.execute(
                "UPDATE posts SET total_saved = %s WHERE id = %s", (new_total, post[0])
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
        cur.execute("SELECT balance FROM users WHERE id = %s", (session["user_id"],))
        balance = cur.fetchone()[0]
        new_balance = balance + amount
        cur.execute(
            "UPDATE users SET balance = %s WHERE id = %s",
            (
                new_balance,
                session["user_id"],
            ),
        )
        cur.execute(
            "SELECT total_saved FROM posts WHERE user_id = %s AND name = %s",
            (session["user_id"], post),
        )
        savings = cur.fetchone()[0]
        new_savings = savings + amount
        cur.execute(
            "UPDATE posts SET total_saved = %s WHERE user_id = %s AND name = %s",
            (new_savings, session["user_id"], post),
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
                (session["user_id"],),
            )
            posts = cur.fetchall()
            for post in posts:
                deposit_amount = amount * (post[2] / 100)
                new_total = post[3] + deposit_amount
                cur.execute(
                    "UPDATE posts SET total_saved = %s WHERE id = %s",
                    (new_total, post[0]),
                )
            return redirect("/index")

        cur.execute(
            "SELECT total_saved FROM posts WHERE user_id = %s AND name = %s",
            (session["user_id"], destination),
        )
        savings = cur.fetchone()[0]
        new_savings = savings + amount
        cur.execute(
            "UPDATE posts SET total_saved = %s WHERE user_id = %s AND name = %s",
            (new_savings, session["user_id"], destination),
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
        cur.execute("SELECT balance FROM users WHERE id = %s", (session["user_id"],))
        balance = cur.fetchone()[0]
        new_balance = balance - amount
        cur.execute(
            "UPDATE users SET balance = %s WHERE id = %s",
            (
                new_balance,
                session["user_id"],
            ),
        )
        # Updates savings amount from the post being withdrawn from
        cur.execute(
            "SELECT total_saved FROM posts WHERE user_id = %s AND name = %s",
            (session["user_id"], post),
        )
        total = cur.fetchone()[0]
        new_total = total - amount
        cur.execute(
            "UPDATE posts SET total_saved = %s WHERE user_id = %s AND name = %s",
            (new_total, session["user_id"], post),
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
            (amount, session["user_id"], pfrom),
        )
        log_history(conn, session["user_id"], pfrom, amount, "Withdrawal", "Moved From")
        cur.execute(
            "UPDATE posts SET total_saved = total_saved + %s WHERE user_id = %s AND name = %s",
            (amount, session["user_id"], pto),
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
            (session["user_id"], pfrom),
        )
        transfer_funds = cur.fetchone()[0]
        if transfer_type == "specific":
            cur.execute(
                "SELECT total_saved FROM posts WHERE user_id = %s AND name = %s",
                (session["user_id"], pto),
            )
            posts = cur.fetchone()[0]
            new_saved = posts + transfer_funds
            cur.execute(
                "DELETE FROM posts WHERE user_id = %s AND name = %s",
                (session["user_id"], pfrom),
            )
            cur.execute(
                "UPDATE posts SET total_saved = %s WHERE user_id = %s AND name = %s",
                (new_saved, session["user_id"], pto),
            )
            return redirect("/index")

        else:
            cur.execute(
                "DELETE FROM posts WHERE user_id = %s AND name = %s",
                (session["user_id"], pfrom),
            )
            cur.execute(
                "SELECT id, total_saved, allocation_percentage FROM posts WHERE user_id = %s",
                (session["user_id"],),
            )
            posts = cur.fetchall()
            for post in posts:
                transfer = transfer_funds * (post[2] / 100)
                new_total = post[1] + transfer
                cur.execute(
                    "UPDATE posts SET total_saved = %s WHERE id = %s",
                    (new_total, post[0]),
                )

        return redirect("/index")


# Dash part
app = dash.Dash(__name__, server=server, routes_pathname_prefix="/dash/")


app.layout = html.Div("My Dash app")
app.debug = True


if __name__ == "__main__":
    server.run(debug=True)
