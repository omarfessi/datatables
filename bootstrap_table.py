from operator import index
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), index=True)
    age = db.Column(db.Integer, index=True)
    address = db.Column(db.String(256))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120), index=True)

    def __repr__(self):
        return f"User('{self.name}', '{self.age}', '{self.address}', '{self.phone}', '{self.email}'"

db.create_all()

@app.route('/')
def index():
    users = User.query
    return render_template('bootstrap_tables.html', title = 'Bootstrap table', users = users)

if __name__ == '__main__':
    app.run(debug=True)