from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Prompt
from config import Config
from email_service import ResendService
from resend_service import Resend


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

resend_service = ResendService()

# Creating tables explicitly
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    prompts = Prompt.query.all()
    return render_template("home.html", prompts=prompts)


@app.route("/new", methods=["GET", "POST"])
def new_prompt():
    if request.method == "POST":
        title = request.form["title"]
        prompt_text = request.form["prompt"]
        if title and prompt_text:
            new_prompt = Prompt(title=title, prompt=prompt_text)
            db.session.add(new_prompt)
            db.session.commit()
            flash("Prompt saved successfully!", "success")
            return redirect(url_for("home"))
        else:
            flash("Title and prompt text cannot be empty.", "error")
    return render_template("new_prompt.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_prompt(id):
    prompt = Prompt.query.get_or_404(id)
    if request.method == "POST":
        prompt.title = request.form["title"]
        prompt.prompt = request.form["prompt"]
        db.session.commit()
        flash("Prompt updated successfully!", "success")
        return redirect(url_for("home"))
    return render_template("edit_prompt.html", prompt=prompt)


@app.route("/delete/<int:id>", methods=["POST"])
def delete_prompt(id):
    prompt = Prompt.query.get_or_404(id)
    db.session.delete(prompt)
    db.session.commit()
    flash("Prompt deleted successfully!", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
