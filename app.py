from flask import Flask, render_template, redirect, url_for, flash, request, current_app
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_migrate import Migrate
from models import db, User, Prompt
from config import Config
from email_service import EmailService
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import os
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Ensure the instance folder exists
if not os.path.exists("instance"):
    os.makedirs("instance")

# Initialize database
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# Initialize email service with secret key
email_service = EmailService(
    api_key=app.config.get("RESEND_API_KEY"), secret_key=app.config.get("SECRET_KEY")
)

# Initialize URL safe serializer for tokens
ts = URLSafeTimedSerializer(app.config.get("SECRET_KEY"))

# Create database tables
with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            flash("Username already exists", "error")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered", "error")
            return redirect(url_for("register"))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Send welcome email
        try:
            email_service.send_welcome_email(email, username)
        except Exception as e:
            app.logger.error(f"Failed to send welcome email: {str(e)}")

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = request.form.get("remember", False)

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get("next")
            if next_page and not next_page.startswith("/"):
                next_page = None
            flash("Login successful!", "success")
            return redirect(next_page or url_for("dashboard"))

        flash("Invalid username or password", "error")
    return render_template("login.html")


@app.route("/magic-link", methods=["POST"])
def magic_link():
    email = request.form.get("email")
    if not email:
        flash("Please provide an email address", "error")
        return redirect(url_for("login"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("No account found with this email address", "error")
        return redirect(url_for("login"))

    try:
        # Send magic link
        base_url = request.host_url.rstrip("/")
        email_service.send_magic_link(email, base_url)
        flash("Magic link sent! Please check your email.", "success")
    except Exception as e:
        app.logger.error(f"Failed to send magic link: {str(e)}")
        flash("Failed to send magic link. Please try again later.", "error")

    return redirect(url_for("login"))


@app.route("/login/verify/<token>")
def verify_magic_link(token):
    try:
        email = ts.loads(token, salt="email-confirm", max_age=600)  # 10 minutes expiry
        user = User.query.filter_by(email=email).first()

        if user:
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid user", "error")
            return redirect(url_for("login"))

    except SignatureExpired:
        flash("The magic link has expired", "error")
        return redirect(url_for("login"))
    except BadSignature:
        flash("Invalid magic link", "error")
        return redirect(url_for("login"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    prompts = current_user.prompts.order_by(Prompt.created_at.desc()).all()
    return render_template("dashboard.html", prompts=prompts)


@app.route("/prompt/new", methods=["GET", "POST"])
@login_required
def new_prompt():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")

        if not title or not content:
            flash("Title and content are required", "error")
            return redirect(url_for("new_prompt"))

        prompt = Prompt(title=title, content=content, user_id=current_user.id)
        db.session.add(prompt)
        db.session.commit()

        flash("Prompt created successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("new_prompt.html")


@app.route("/prompt/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_prompt(id):
    prompt = Prompt.query.get_or_404(id)

    if prompt.user_id != current_user.id:
        flash("You do not have permission to edit this prompt", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")

        if not title or not content:
            flash("Title and content are required", "error")
            return redirect(url_for("edit_prompt", id=id))

        prompt.title = title
        prompt.content = content
        prompt.updated_at = datetime.utcnow()
        db.session.commit()

        flash("Prompt updated successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("edit_prompt.html", prompt=prompt)


@app.route("/prompt/<int:id>/delete", methods=["POST"])
@login_required
def delete_prompt(id):
    prompt = Prompt.query.get_or_404(id)

    if prompt.user_id != current_user.id:
        flash("You do not have permission to delete this prompt", "error")
        return redirect(url_for("dashboard"))

    db.session.delete(prompt)
    db.session.commit()

    flash("Prompt deleted successfully!", "success")
    return redirect(url_for("dashboard"))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()

        if user:
            try:
                # Generate reset token
                token = ts.dumps(email, salt="password-reset-salt")
                reset_url = url_for("reset_password", token=token, _external=True)

                # Send password reset email
                email_service.send_password_reset_email(email, reset_url)
                flash("Password reset instructions sent to your email", "info")
            except Exception as e:
                app.logger.error(f"Failed to send password reset email: {str(e)}")
                flash(
                    "Failed to send reset instructions. Please try again later.",
                    "error",
                )
        else:
            flash("No account found with this email address", "error")

        return redirect(url_for("login"))

    return render_template("forgot_password.html")


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = ts.loads(
            token, salt="password-reset-salt", max_age=3600
        )  # 1 hour expiry
    except:
        flash("Invalid or expired reset link", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        user = User.query.filter_by(email=email).first()
        if user:
            password = request.form.get("password")
            user.set_password(password)
            db.session.commit()
            flash("Your password has been reset", "success")
            return redirect(url_for("login"))

        flash("User not found", "error")
        return redirect(url_for("login"))

    return render_template("reset_password.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("500.html"), 500


# CLI commands
@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
    print("Database initialized!")


@app.cli.command("create-admin")
def create_admin():
    """Create an admin user."""
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")

    with app.app_context():
        if User.query.filter_by(username=username).first():
            print("Username already exists!")
            return
        if User.query.filter_by(email=email).first():
            print("Email already exists!")
            return

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print("Admin user created successfully!")


if __name__ == "__main__":
    app.run(debug=True)
