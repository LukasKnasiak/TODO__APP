from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    task = db.Column(db.String(300), unique = True)
    complete = db.Column(db.Boolean, default = False)
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())

@app.route("/")
def home():
    todo_list = Todo.query.all()
    message = request.args.get('message', None)
    return render_template("index.html", todo_list=todo_list, message = message)

@app.route("/add", methods=["POST"])
def add():
    try:
        task = request.form.get("task")
        existing_todo = Todo.query.filter_by(task=task).first()
        if existing_todo:
            message = "Sorry, this task is already on the list. Try add new one!?"
        else:
            new_todo = Todo(task=task)
            db.session.add(new_todo)
            db.session.commit()
            message = "Thanks for adding a new task! Thats great!"
        return redirect(url_for("home", message=message))
    except Exception as e:
        message = "An error occurred while adding the task."
        print(e)
        return redirect(url_for("home", message=message))


@app.route("/update/<todo_id>", methods=["POST"])
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<todo_id>", methods=["POST"])
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/edit/<todo_id>", methods=["GET", "POST"])
def edit(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    if request.method == "POST":
        new_task = request.form.get("task")
        todo.task = new_task
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", todo=todo)

    
    

if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)