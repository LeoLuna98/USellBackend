from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import exc
from datetime import datetime
import os

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.String(9), nullable=False)
    profile_image_url = db.Column(db.String(500))
    career_id = db.Column(db.Integer, db.ForeignKey('career.id'), nullable=False)
    career = db.relationship('Career', backref='student')

class Career(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    career_name = db.Column(db.String(50), unique=True, nullable=False)

class StudentSchema(ma.ModelSchema):
    class Meta:
        model = Student

class CarrerSchema(ma.ModelSchema):
    class Meta:
        model = Career


student_schema = StudentSchema()
career_schema = CarrerSchema()
careers_schema = CarrerSchema(many=True)
students_schema = StudentSchema(many=True)

@app.route('/')
def index():
    return jsonify({'message' : 'app running'})

@app.route('/student/<id>')
def get_student(id):
    student = Student.query.filter_by(id=id).first()
    if student == None:
        return jsonify({'error' : 'Usuario no encontrado.'})
    else:
        return jsonify({'message' : 'Usuario encontrado.'}, {'student' : student_schema.dump(student)})


@app.route('/all_careers')
def get_all_careers():
    all_careers = Career.query.all()
    if all_careers == None:
        return jsonify({'error' : 'No hay carreras registradas.'})
    else:
        return jsonify({'message' : 'Se encontraron carreras.'}, {'career' : careers_schema.dump(all_careers)})

@app.route('/all_students')
def get_all_students():
    all_students = Student.query.all()
    if all_students == None:
        return jsonify({'error' : 'No hay estudiantes registrados.'})
    else:
        return jsonify({'student' : students_schema.dump(all_students)})

@app.route('/register', methods=['POST'])
def register():
    career_name = request.json['career_name']
    career = Career.query.filter_by(career_name=career_name).first()

    if career == None:
        return jsonify({'error' : 'Carrera no encontrada.'}) 
    else:
        try:
            id = request.json['studend_id']
            email = request.json['email']
            name = request.json['name']
            level = request.json['level']
            phone_number = request.json['phone_number']
            career_name = request.json['career_name']
            if 'profile_image_url' not in request.get_json():
                profile_image_url = None
            else:
                profile_image_url = request.json['profile_image_url']
            career = Career.query.filter_by(career_name=career_name).first()
            student = Student(id=id,email=email,name=name,level=level,phone_number=phone_number,career=career, profile_image_url=profile_image_url)
            db.session.add(student)
            db.session.commit()
            return jsonify({'message' : 'Usuario registrado satisfactoriamente.'})
        except exc.IntegrityError as e:
            return jsonify({'error' : 'Usuario ya registrado.'}) 
        except Exception as e:
            return jsonify({'error' : f'Error al regisrar usuario. {e}'})

@app.route('create_carrers')
def create_careers():
    car1 = Career(career_name='Administración')
    car2 = Career(career_name='Contabilidad')
    car3 = Career(career_name='Economía')
    car4 = Career(career_name='Marketing')
    car5 = Career(career_name='Negocios Internacionales')
    car6 = Career(career_name='Comunicación')
    car7 = Career(career_name='Derecho')
    car8 = Career(career_name='Arquitectura')
    car9 = Career(career_name='Ingeniería Civil')
    car10 = Career(career_name='Ingeniería Industrial')
    car11 = Career(career_name='Ingeniería de Sistemas')
    car12 = Career(career_name='Psicología') 



if __name__ == '__main__':
    app.run(debug=True)