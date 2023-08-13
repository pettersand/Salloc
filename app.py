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
from dash import html
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
    format_currency,
)
import bcrypt
import string
import configparser



config = configparser.ConfigParser()
config.read('config.ini')

def create_conncur():
    config = configparser.ConfigParser()
    config.read('config.ini')

    dbname = config['database']['dbname']
    user = config['database']['user']
    password = config['database']['password']
    host = config['database']['host']

    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
    )
    return conn, conn.cursor()


server = Flask(__name__, static_url_path='/static')

server.config["SECRET_KEY"] = config['secret']['key']
server.config['APPLICATION_ROOT'] = '/salloc'
server.jinja_env.filters['currency'] = format_currency

# Configure Flask-Mail with Gmail settings
  # Make sure to provide the correct path

server.config["MAIL_SERVER"] = config['mail']['server']
server.config["MAIL_PORT"] = int(config['mail']['port'])
server.config["MAIL_USERNAME"] = config['mail']['username']
server.config["MAIL_PASSWORD"] = config['mail']['password']
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
    try:
        with conn:
            cur.execute("SELECT balance FROM users WHERE id = %s", (session["user_id"],))
            balance = cur.fetchone()[0]
            if balance is None or balance < 0:
                flash("Invalid balance detected. Please check your account.", "error")
                return redirect("/index")

            cur.execute(
                "SELECT id, allocation_percentage FROM posts WHERE user_id = %s",
                (session["user_id"],),
            )
            posts = cur.fetchall()
            for post in posts:
                allocation_percentage = post[1]
                if allocation_percentage is None or allocation_percentage < 0 or allocation_percentage > 100:
                    flash("Invalid allocation percentage detected. Please check your posts.", "error")
                    return redirect("/index")

                total_saved = balance * allocation_percentage / 100
                cur.execute(
                    "UPDATE posts SET total_saved = %s WHERE id = %s",
                    (total_saved, post[0]),
                )
            conn.commit()
            flash("Savings committed successfully.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred while committing savings: {str(e)}", "error")

    return redirect("/index")



@server.route("/generate_template", methods=["POST"])
@login_required
def generate_template():
    conn, cur = create_conncur()
    try:
        with conn:
            cur.execute("SELECT balance FROM users WHERE id = %s", (session["user_id"],))
            balance = cur.fetchone()[0]
            if balance is None or balance <= 0:
                flash("Please set total savings before generating posts", "error")
                return redirect("/index")

            cur.execute("SELECT * FROM posts WHERE user_id = %s", (session["user_id"],))
            check = cur.fetchone()
            if check:
                flash("Please reset your posts before adding template", "error")
                return redirect("/index")

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
            flash("Template generated successfully.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred while generating the template: {str(e)}", "error")

    return redirect("/index")


@server.route("/custom_setup", methods=["POST"])
@login_required
def custom_setup():
    post_names = request.form.getlist("postName[]")
    post_goals = request.form.getlist("postGoal[]")
    post_alloc = request.form.getlist("postAllocation[]")

    if not post_names or not post_goals or not post_alloc:
        flash("No data provided for custom setup.", "error")
        return redirect("/index")

    conn, cur = create_conncur()
    try:
        with conn:
            total_alloc = 0
            for name, goal, alloc in zip(post_names, post_goals, post_alloc):
                name = string.capwords(name.strip())
                goal = goal.strip() or "0"
                alloc = alloc.strip() or "0"

                if name == "" or not goal.isdigit() or not alloc.isdigit():
                    continue

                total_alloc += int(alloc)
                if total_alloc > 100:
                    flash("Total % exceeds 100%", "error")
                    return redirect("/index")

                cur.execute(
                    "INSERT INTO posts (user_id, name, allocation_percentage, goal) VALUES (%s, %s, %s, %s)",
                    (session["user_id"], name, alloc, goal),
                )

            flash("Custom setup completed successfully.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred while setting up custom posts: {str(e)}", "error")

    return redirect("/index")


@server.route("/index")
@login_required
def index():
    try:
        conn, cur = create_conncur()
        with conn:
            cur.execute("SELECT balance, currency FROM users WHERE id = %s", (session["user_id"],))
            balance, currency = cur.fetchone()

            # Fetch posts and calculate totals
            cur.execute(
                "SELECT name, allocation_percentage, total_saved, goal FROM posts WHERE user_id = %s",
                (session["user_id"],),
            )
            posts = cur.fetchall()
            total_alloc = sum(post[1] for post in posts)
            total_saved = sum(post[2] for post in posts)
            total_goal = sum(post[3] for post in posts)
            remain_alloc = int(max(0, 100 - total_alloc))
            remainder = balance - total_saved

            # Generate alerts
            alerts = [f"Congratulations! You've reached your goal for Post '{post[0]}'." for post in posts if post[2] >= post[3]]
            if remainder > 0:
                alerts.append(f"You have funds not yet allocated to the sum of {remainder}. Use the 'Allocate now' button")
            if remain_alloc > 0:
                alerts.append(f"You have {remain_alloc}% left to allocate.")

            # Fetch history
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
            currency=currency,
        )
    except Exception as e:
        error_message = str(e)
        flash(f"An error occurred: {error_message}", "error")
        return redirect(url_for("error_page", error_message=error_message))
    

@server.route("/error_page")
def error_page():
    error_message = request.args.get("error_message", "An unexpected error occurred.")
    return render_template("error_page.html", error_message=error_message)


@server.route("/deposit", methods=["POST"])
@login_required
def deposit():
    try:
        amount_str = request.form.get("deposit")
        if not amount_str or not amount_str.isdigit():
            flash("Invalid deposit amount. Please enter a positive integer.", "error")
            return redirect("/index")

        amount = int(amount_str)
        if amount <= 0:
            flash("Deposit amount must be greater than zero.", "error")
            return redirect("/index")

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
            flash("Deposit successful!", "success")
            return redirect("/index")
    except Exception as e:
        error_message = str(e)
        flash(f"An error occurred while processing the deposit: {error_message}", "error")
        return redirect(url_for("error_page", error_message=error_message))


@server.route("/specific_deposit", methods=["POST"])
@login_required
def specific_deposit():
    try:
        post = request.form.get("post")
        amount_str = request.form.get("deposit")

        if not post:
            flash("Please select a post for the deposit.", "error")
            return redirect("/index")

        if not amount_str or not amount_str.isdigit():
            flash("Invalid deposit amount. Please enter a positive integer.", "error")
            return redirect("/index")

        amount = int(amount_str)
        if amount <= 0:
            flash("Deposit amount must be greater than zero.", "error")
            return redirect("/index")

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
            flash(f"Deposit to '{post}' successful!", "success")
            return redirect("/index")
    except Exception as e:
        error_message = str(e)
        flash(f"An error occurred while processing the specific deposit: {error_message}", "error")
        return redirect(url_for("error_page", error_message=error_message))



@server.route("/undefined", methods=["POST"])
@login_required
def undefined():
    try:
        destination = request.form.get("post")
        amount_str = request.form.get("remainder")
        amount = Decimal(amount_str)

        if amount <= 0:
            flash("No unallocated funds to distribute.", "warning")
            return redirect("/index")

        conn, cur = create_conncur()
        with conn:
            if destination == "general":
                cur.execute(
                    "SELECT SUM(allocation_percentage) FROM posts WHERE user_id = %s",
                    (session["user_id"],),
                )
                total_alloc = cur.fetchone()[0]

                if total_alloc != 100:
                    flash("Total allocation percentage must be 100% to distribute unallocated funds.", "error")
                    return redirect("/index")

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
            else:
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

            flash("Unallocated funds distributed successfully.", "success")
            return redirect("/index")
    except Exception as e:
        error_message = str(e)
        flash(f"An error occurred while distributing unallocated funds: {error_message}", "error")
        return redirect(url_for("error_page", error_message=error_message))



@server.route("/withdrawal", methods=["POST"])
@login_required
def withdrawal():
    try:
        post = request.form.get("post")
        amount_str = request.form.get("withdrawal")
        amount = int(amount_str)
        notes = sanitize_input(request.form.get("notes"))

        if amount <= 0:
            flash("Withdrawal amount must be greater than zero.", "error")
            return redirect("/index")

        conn, cur = create_conncur()
        with conn:
            # Updates balance minus the amount withdrawn
            cur.execute("SELECT balance FROM users WHERE id = %s", (session["user_id"],))
            balance = cur.fetchone()[0]

            if amount > balance:
                flash("Withdrawal amount exceeds available balance.", "error")
                return redirect("/index")

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

            if amount > total:
                flash(f"Withdrawal amount exceeds total saved in '{post}'.", "error")
                return redirect("/index")

            new_total = total - amount
            cur.execute(
                "UPDATE posts SET total_saved = %s WHERE user_id = %s AND name = %s",
                (new_total, session["user_id"], post),
            )

            log_history(conn, session["user_id"], post, amount, "Withdrawal", notes)
            flash("Withdrawal successful.", "success")
            return redirect("/index")
    except Exception as e:
        error_message = str(e)
        flash(f"An error occurred while processing the withdrawal: {error_message}", "error")
        return redirect(url_for("error_page", error_message=error_message))



@server.route("/move", methods=["POST"])
@login_required
def move():
    try:
        pfrom = request.form.get("from")
        pto = request.form.get("to")
        amount_str = request.form.get("amount")
        amount = int(amount_str)

        if pfrom == pto or amount <= 0:
            flash("Invalid move parameters.", "error")
            return redirect("/index")

        conn, cur = create_conncur()
        with conn:
            # Check if both posts exist for the user
            cur.execute("SELECT name FROM posts WHERE user_id = %s AND name IN (%s, %s)", (session["user_id"], pfrom, pto))
            if cur.rowcount != 2:
                flash("One or both of the posts do not exist.", "error")
                return redirect("/index")

            # Check if the amount is not more than what's in the source post
            cur.execute("SELECT total_saved FROM posts WHERE user_id = %s AND name = %s", (session["user_id"], pfrom))
            total_saved_from = cur.fetchone()[0]
            if amount > total_saved_from:
                flash("The amount being moved is more than what's in the source post.", "error")
                return redirect("/index")

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
            conn.commit()
            
        flash("Move successful.", "success")
        return redirect("/index")
    except Exception as e:
        error_message = str(e)
        flash(f"An error occurred while moving funds: {error_message}", "error")
        return redirect(url_for("error_page", error_message=error_message))




@server.route("/transfer", methods=["POST"])
@login_required
def transfer():
    try:
        pfrom = request.form.get("from")
        pto = request.form.get("to")
        transfer_type = request.form.get("type")

        if pfrom == pto or not transfer_type:
            flash("Invalid transfer parameters.", "error")
            return redirect("/index")

        conn, cur = create_conncur()
        with conn:
            # Check if the source post exists
            cur.execute("SELECT total_saved FROM posts WHERE user_id = %s AND name = %s", (session["user_id"], pfrom))
            transfer_funds = cur.fetchone()
            if transfer_funds is None:
                flash("The source post does not exist.", "error")
                return redirect("/index")
            transfer_funds = transfer_funds[0]

            if transfer_type == "specific":
                # Check if the destination post exists
                cur.execute("SELECT total_saved FROM posts WHERE user_id = %s AND name = %s", (session["user_id"], pto))
                posts = cur.fetchone()
                if posts is None:
                    flash("The destination post does not exist.", "error")
                    return redirect("/index")
                new_saved = posts[0] + transfer_funds

                cur.execute(
                    "DELETE FROM posts WHERE user_id = %s AND name = %s",
                    (session["user_id"], pfrom),
                )
                cur.execute(
                    "UPDATE posts SET total_saved = %s WHERE user_id = %s AND name = %s",
                    (new_saved, session["user_id"], pto),
                )
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

            conn.commit()
            flash("Transfer successful.", "success")
            return redirect("/index")
    except Exception as e:
        error_message = str(e)
        flash(f"An error occurred while transferring funds: {error_message}", "error")
        return redirect(url_for("error_page", error_message=error_message))


@server.route("/set_currency", methods=["POST"])
@login_required
def set_currency():
    currency_type = request.form.get("currency_type")
    if currency_type in ['NOK', 'USD', 'EUR']:
        # Update the database
        conn, cur = create_conncur()
        with conn:
            cur.execute(
                "UPDATE users SET currency = %s WHERE id = %s",
                (currency_type, session["user_id"]),
            )
        # Store the preference in the session
        session['currency_type'] = currency_type
    flash("Currency set successfully.", "success")
    return redirect("/index")


@server.errorhandler(404)
def page_not_found(error):
    error_code = 404
    error_message = "The page you requested could not be found."
    return render_template("error_page.html", error_code=error_code, error_message=error_message), 404

@server.errorhandler(500)
def internal_server_error(error):
    error_code = 500
    error_message = "An unexpected error occurred on the server."
    return render_template("error_page.html", error_code=error_code, error_message=error_message), 500

@server.errorhandler(403)
def forbidden(error):
    error_code = 403
    error_message = "You don't have permission to access this resource."
    return render_template("error_page.html", error_code=error_code, error_message=error_message), 403

@server.errorhandler(503)
def service_unavailable(error):
    error_code = 503
    error_message = "The server is currently unable to handle the request due to temporary overloading or maintenance. Please try again later."
    return render_template("error_page.html", error_code=error_code, error_message=error_message), 503


# Dash part
app = dash.Dash(__name__, server=server, routes_pathname_prefix="/dash/")


app.layout = html.Div("My Dash app")


if __name__ == "__main__":
    server.run()
