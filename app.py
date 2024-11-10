from flask import Flask, render_template, redirect, url_for, flash, request
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
import os

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

email_service = EmailService()

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
            flash("Username already exists")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered")
            return redirect(url_for("register"))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Send welcome email
        email_service.send_welcome_email(email, username)

        flash("Registration successful! Please login.")
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
            return redirect(next_page or url_for("dashboard"))

        flash("Invalid username or password")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
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
            flash("Title and content are required")
            return redirect(url_for("new_prompt"))

        prompt = Prompt(title=title, content=content, user_id=current_user.id)
        db.session.add(prompt)
        db.session.commit()

        flash("Prompt created successfully!")
        return redirect(url_for("dashboard"))

    return render_template("new_prompt.html")


@app.route("/prompt/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_prompt(id):
    prompt = Prompt.query.get_or_404(id)

    if prompt.user_id != current_user.id:
        flash("You do not have permission to edit this prompt")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")

        if not title or not content:
            flash("Title and content are required")
            return redirect(url_for("edit_prompt", id=id))

        prompt.title = title
        prompt.content = content
        db.session.commit()

        flash("Prompt updated successfully!")
        return redirect(url_for("dashboard"))

    return render_template("edit_prompt.html", prompt=prompt)


@app.route("/prompt/<int:id>/delete", methods=["POST"])
@login_required
def delete_prompt(id):
    prompt = Prompt.query.get_or_404(id)

    if prompt.user_id != current_user.id:
        flash("You do not have permission to delete this prompt")
        return redirect(url_for("dashboard"))

    db.session.delete(prompt)
    db.session.commit()

    flash("Prompt deleted successfully!")
    return redirect(url_for("dashboard"))


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
    db.create_all()
    print("Database initialized!")


@app.cli.command("create-admin")
def create_admin():
    """Create an admin user."""
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print("Admin user created successfully!")


if __name__ == "__main__":
    app.run(debug=True)
