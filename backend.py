from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import exc
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.String(9), nullable=False)
    career_id = db.Column(db.Integer, db.ForeignKey('career.id'), nullable=False)
    career = db.relationship('Career', backref='student')

class Career(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    career_name = db.Column(db.String(20), unique=True, nullable=False)

class StudentSchema(ma.ModelSchema):
    class Meta:
        model = Student

class CarrerSchema(ma.ModelSchema):
    class Meta:
        model = Career


student_schema = StudentSchema()
career_schema = CarrerSchema()
careers_schema = CarrerSchema(many=True)

@app.route('/user/<id>')
def get_user(id):
    student = Student.query.filter_by(id=id).first()
    if student == None:
        return jsonify({'message' : 'Usuario no encontrado.'})
    else:
        return jsonify({'message' : 'Usuario encontrado.'}, {'student' : student_schema.dump(student)})


@app.route('/all_careers')
def get_all_careers():
    all_careers = Career.query.all()
    if all_careers == None:
        return jsonify({'message' : 'No hay carreras registradas.'})
    else:
        return jsonify({'message' : 'Se encontraron carreras.'}, {'career' : careers_schema.dump(all_careers)})

@app.route('/register', methods=['POST'])
def register():
    career_name = request.json['career_name']
    career = Career.query.filter_by(career_name=career_name).first()

    if career == None:
        return jsonify({'message' : 'Carrera no encontrada.'}) 
    else:
        try:
            id = request.json['stutend_id']
            email = request.json['email']
            name = request.json['name']
            level = request.json['level']
            phone_number = request.json['phone_number']
            career_name = request.json['career_name']
            career = Career.query.filter_by(career_name=career_name).first()
            student = Student(id=id,email=email,name=name,level=level,phone_number=phone_number,career=career)
            db.session.add(student)
            db.session.commit()
            return jsonify([{'message' : 'Usuario registrado satisfactoriamente.'}])
        except exc.IntegrityError as e:
            return jsonify({'message' : 'Usuario ya registrado.'}) 
        except Exception as e:
            return jsonify([{'message' : f'Error al regisrar usuario. {e}'}])



if __name__ == '__main__':
    app.run(debug=True)