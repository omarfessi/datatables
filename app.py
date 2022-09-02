from crypt import methods
from operator import methodcaller
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql import expression
from datetime import datetime
from sqlalchemy import select, desc, text #is not necessary as I am using flask_sqlalchemy 
import pandas as pd

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/adages' #conString = "postgres://YourUserName:YourPassword@YourHostname:5432/YourDatabaseName";
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "super secret key"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    age = db.Column(db.Integer)
    address = db.Column(db.String(256))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(60), index=True)
    country = db.Column(db.String(65))
    date_of_birth = db.Column(db.DateTime, nullable=True)
    team_member = db.Column(db.String(30), nullable = False)
    is_monitored = db.Column(db.Boolean, default=False, nullable=False)
    adages_lifecycle = db.Column(db.Integer, server_default=text("0"))
    shows=db.relationship('UserHistory', backref='employee', lazy=True)


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
            'is_monitored':self.is_monitored,
            'adages_lifecycle':self.adages_lifecycle
        }

class UserHistory(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    name = db.Column(db.String(64), index=True)
    age = db.Column(db.Integer)
    address = db.Column(db.String(256))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(60), index=True)
    country = db.Column(db.String(65))
    date_of_birth = db.Column(db.DateTime, nullable=True)
    team_member = db.Column(db.String(30), nullable = False)
    is_monitored = db.Column(db.Boolean, default=False, nullable=False)
    adages_lifecycle = db.Column(db.Integer, server_default=text("0"))
    refresh_datetime = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"UserHist('{self.uid}', '{self.name}', '{self.age}', '{self.address}', '{self.phone}', '{self.email}', '{self.country}', '{self.date_of_birth}', '{self.team_member}', '{self.is_monitored}') "

@app.route('/')
def index():
    # users = User.query
    return render_template('adages.html', title = 'DataTable')

@app.route('/api/data')
def data():
    query = User.query
    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            User.name.like(f'%{search}%'),
            User.email.like(f'%{search}%')
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

@app.route('/api/updateemployee', methods=['GET', 'POST'])
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
    return render_template('adages.html', title = 'DataTable')

@app.route('/api/audittrail', methods=['GET'])
def showAuditTrail():
    id = request.args.get("employeeuid")
    
    user = UserHistory.query.filter_by(uid=id).order_by(desc(UserHistory.id))

    result_dict = [u.__dict__ for u in user.all()]
    adages_df = pd.DataFrame(result_dict)
    adages_df.drop(columns=[adages_df.columns[0], 'id'], axis = 1, inplace=True)

    adages_prev = adages_df.loc[1:]
    adages_prev.reset_index(drop=True, inplace=True)
    adages_next = adages_df.loc[:adages_df.shape[0]-2]
    adages_diff = adages_prev.fillna('') != adages_next.fillna('')
    adages_diff.drop(['refresh_datetime'], axis=1, inplace=True)
    audit_trail = []
    for index in adages_diff.index:
        modification = {}
        modification['MODIFIED_ON'] = adages_next.loc[index, 'refresh_datetime']
        modified_columns ={}
        for column in adages_diff.columns:
            if (adages_diff.loc[index, column]):
                modified_columns[column] = [str(adages_prev[column].tolist()[index]), str(adages_next[column].tolist()[index])]
        if modified_columns : 
            modification['MODIFIED_COLUMNS']=modified_columns
            audit_trail.append(modification)

    return jsonify({'htmlresponse': render_template('response.html', audit_trail=audit_trail)})
        

if __name__ == '__main__':
    app.run(debug=True)

