from flask import Flask, render_template, request
from data import teachers
from json import dumps, loads
from random import shuffle
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, SelectField

goals = {"travel": "⛱ Для путешествий", "study": "🏫 Для школы", "work": "🏢 Для работы",
         "relocate": "🚜 Для переезда"}

with open('teachers.json', 'w') as f:
    teachers_json = dumps(teachers)
    f.write(teachers_json)

app = Flask(__name__)
app.secret_key = 'come_to_me_or_not'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///_database.db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Tutor(db.Model):
    """ Учителя """

    __tablename__ = "tutor"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    about = db.Column(db.String(), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String(), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    goals = db.Column(db.String(), nullable=False)
    free = db.Column(db.String(), nullable=False)

    bookings = db.relationship('Booking', back_populates='tutor_info')


class Booking(db.Model):
    """  Бронь занятия """

    __tablename__ = "booking"

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(), nullable=False)
    client_phone = db.Column(db.String(), nullable=False)

    tutor_id = db.Column(db.Integer, db.ForeignKey("tutor.id"))
    tutor_info = db.relationship("Tutor", back_populates="bookings")


class Pick(db.Model):
    """ Заявка на подбор учителя """

    __tablename__ = "pick"

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(), nullable=False)
    client_phone = db.Column(db.String(), nullable=False)
    time = db.Column(db.String(), nullable=False)
    goal = db.Column(db.String(), nullable=False)


tutors = db.session.query(Tutor).all()
teachers_list = []
for tutor in tutors:
    teachers_list.append(tutor)

shuffle(teachers_list)


def time_table(id):
    """ Формируем расписание для вывода """

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
    free = loads(teachers_list[id].free.replace('\'', '"').replace('False', 'false').replace('True', 'true'))
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
    """ Перенос данных из файла в БД """

    with open('teachers.json', 'r') as f:
        teachers_dict = loads(f.read())

        teachers_list = []
        for i, value in teachers_dict.items():
            teachers_list.append(value)

        for teacher in teachers_list:
            t = Tutor(
                name=teacher['name'], about=teacher['about'], rating=teacher['rating'],
                picture=teacher['picture'], price=teacher['price'], goals=str(teacher['goals']),
                free=str(teacher['free']
                         ))

            db.session.add(t)

        db.session.commit()


# data_transfer()

class ClientInfo(FlaskForm):
    name = StringField('Вас зовут', validators=[DataRequired()])
    phone = StringField('Телефон', validators=[DataRequired()])


class PickInfo(FlaskForm):
    goal = SelectField('Какая цель занятий?',
                       choices=[("travel", "Для путешествий"), ("study", "Для школы"),
                                ("work", "Для работы"), ("relocate", "Для переезда")],
                       validators=[DataRequired()])
    time = SelectField('Сколько времени есть?',
                       choices=[('1-2', '1-2 часа в неделю'), ('3-5', '3-5 часов в неделю'),
                                ('5-7', '5-7 часов в неделю'), ('7-10', '7-10 часов в неделю')],
                       validators=[DataRequired()])
    name = StringField('Вас зовут', validators=[DataRequired()])
    phone = StringField('Телефон', validators=[DataRequired()])


def selection_teachers_by_goal(goal, teachers_list):
    """ Отбираем учителей по целям """
    suitable_teachers = []
    for teacher in teachers_list:
        if goal in teacher.goals:
            suitable_teachers.append(teacher)

    return suitable_teachers


@app.route('/')
def index():
    print(teachers_list)
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
    form = ClientInfo()
    return render_template('booking.html', teacher=teachers_list[id], id=id, form=form)


@app.route('/sent/<int:id>', methods=['POST'])
def sent(id):

    form = ClientInfo()
    b = Booking(client_id=teachers_list[id].id, client_name=form.name.data, client_phone=form.phone.data)
    db.session.add(b)
    db.session.commit()

    return render_template('sent.html', teacher=teachers_list[id], name=form.name.data, phone=form.phone.data)


@app.route('/pick/')
def pick():
    form = PickInfo()
    return render_template('pick.html', form=form)


@app.route('/sent_pick/', methods=['POST'])
def sent_pick():

    form = PickInfo()
    p = Pick(goal=form.goal.data, time=form.time.data, client_name=form.name.data, client_phone=form.phone.data)
    db.session.add(p)
    db.session.commit()

    return render_template('sent_pick.html', name=form.name.data, phone=form.phone.data)


app.run('0.0.0.0', 8000)
