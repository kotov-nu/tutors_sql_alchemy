from flask import Flask, render_template, request
from data import goals, teachers
from json import dumps, loads
from random import shuffle
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

with open('teachers.json', 'w') as f:
    teachers_json = dumps(teachers)
    f.write(teachers_json)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Tutor(db.Model):

    __tablename__ = "tutor"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    about = db.Column(db.String(), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String(), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    goals = db.Column(db.String(), nullable=False)
    free = db.Column(db.String(), nullable=False)

    bookings = db.relationship('Booking', back_populates='client')
    picks = db.relationship('Pick', back_populates='client')


class Booking(db.Model):

    __tablename__ = "booking"

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(), nullable=False)
    client_phone = db.Column(db.String(), nullable=False)

    client_id = db.Column(db.Integer, db.ForeignKey("tutor.id"))
    client = db.relationship("Tutor", back_populates="bookings")


class Pick(db.Model):

    __tablename__ = "pick"

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(), nullable=False)
    client_phone = db.Column(db.String(), nullable=False)

    client_id = db.Column(db.Integer, db.ForeignKey("tutor.id"))
    client = db.relationship("Tutor", back_populates="picks")


# with open('teachers.json', 'r') as f:
#     teachers_dict = loads(f.read())
#
#     teachers_list = []
#     for i, value in teachers_dict.items():
#         teachers_list.append(value)
#
#     shuffle(teachers_list)

tutors = db.session.query(Tutor).all()
teachers_list = []
for tutor in tutors:
    teachers_list.append(tutor)

shuffle(teachers_list)

def time_table(id):

    time_table = {
        '8:00': [],
        '10:00': [],
        '12:00': [],
        '14:00': [],
        '16:00': [],
        '18:00': [],
        '20:00': [],
        '22:00': [],

    }

    free = teachers_list[id]['free']
    for value in free.values():
        time_table['8:00'].append(value['8:00'])
        time_table['10:00'].append(value['10:00'])
        time_table['12:00'].append(value['12:00'])
        time_table['14:00'].append(value['14:00'])
        time_table['16:00'].append(value['16:00'])
        time_table['18:00'].append(value['18:00'])
        time_table['20:00'].append(value['20:00'])
        time_table['22:00'].append(value['22:00'])

    return time_table


def data_transfer():

    with open('teachers.json', 'r') as f:
        teachers_dict = loads(f.read())

        teachers_list = []
        for i, value in teachers_dict.items():
            teachers_list.append(value)

        for teacher in teachers_list:
            t = Tutor(name=teacher['name'], about=teacher['about'], rating=teacher['rating'],
                      picture=teacher['picture'], price=teacher['price'], goals=str(teacher['goals']), free=str(teacher['free']))

            db.session.add(t)

        db.session.commit()


# data_transfer()


def selection_teachers_by_goal(goal, teachers_list):
    suitable_teachers = []
    for teacher in teachers_list:
        if goal in teacher['goals']:
            suitable_teachers.append(teacher)

    return suitable_teachers


def save_pick_info(id, name, phone):

    with open('booking.json', 'r') as f:

        all_info = f.read()
        if all_info:
            loads(all_info).update({id: {'name': name, 'phone': phone}})
        else:
            all_info = {}
            all_info.update({id: {'name': name, 'phone': phone}})

    with open('booking.json', 'w') as f:
        f.write(dumps(all_info))


@app.route('/')
def index():
    return render_template('index.html', teachers=teachers_list[:6], goals=goals)


@app.route('/profiles/<int:id>')
def profiles(id):
    return render_template('profile.html', teacher=teachers_list[id], time_table=time_table(id + 1), id=id)


@app.route('/goal/<goal>')
def goal(goal):
    suitable_teachers = selection_teachers_by_goal(goal, teachers_list)
    return render_template('goal.html', suitable_teachers=suitable_teachers, goal=goals[goal].split())


@app.route('/booking/<int:id>')
def booking(id):
    return render_template('booking.html', teacher=teachers_list[id], id=id)


@app.route('/sent/<int:id>', methods=['GET', 'POST'])
def sent(id):

    name = request.form.get('name')
    phone = request.form.get('phone')
    save_pick_info(id, name, phone)

    return render_template('sent.html', teacher=teachers_list[id], name=name, phone=phone)


# @app.route('/sent/<int:id>', methods=['GET', 'POST'])
# def sent(id):
#
#     name = request.form.get('name')
#     phone = request.form.get('phone')
#
#     return render_template('sent.html', teacher=teachers_list[id], name=name, phone=phone)



app.run('0.0.0.0', 8000)