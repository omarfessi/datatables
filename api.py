from crypt import methods
from operator import methodcaller
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import expression


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "super secret key"


db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    age = db.Column(db.Integer, index=True)
    address = db.Column(db.String(256))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120), index=True)
    country = db.Column(db.String(80))
    date_of_birth = db.Column(db.DateTime, nullable=True)
    team_member = db.Column(db.String(80), nullable = False)
    is_monitored = db.Column(db.Boolean, server_default=expression.true(), nullable=False)
    # is_monitored = db.Column(db.Boolean, default=False, nullable=False)


    def __repr__(self):
        return f"User('{self.name}', '{self.age}', '{self.address}', '{self.phone}', '{self.email}', '{self.country}', '{self.date_of_birth}', '{self.team_member}', '{self.is_monitored}') "
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'country':self.country,
            'date_of_birth': self.date_of_birth,
            'team_member': self.team_member,
            'is_monitored':self.is_monitored
        }

db.create_all()



@app.route('/')
def index():
    # users = User.query
    return render_template('tuto.html', title = 'DataTable')

@app.route('/api/data')
def data():
    query = User.query
    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            User.name.like(f'%{search}%'),
            User.email.like(f'%{search}%'),
            User.id.like(search)
        ))
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['name', 'age', 'email', 'id']:
            col_name = 'name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(User, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)
    
    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)
    # response
    return {
        'data': [user.to_dict() for user in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': User.query.count(),
        'draw': request.args.get('draw', type=int),
    }

@app.route('/api//updateemployee', methods=['GET', 'POST'])
def update_employee():
    pk = request.form['pk']
    name = request.form['name']
    value = request.form['value']
    user=User.query.get_or_404(int(pk))
    if name == 'name':
        user.name = value
    elif name == 'monitored':
        if value == '1' : user.is_monitored = True
        elif value == '2' : user.is_monitored = False
    db.session.commit()
    print('print starts here', 'primary_key:', pk,'name of the data:', name,'and the actual value', value)
    return render_template('tuto.html', title = 'DataTable')

if __name__ == '__main__':
    app.run(debug=True)