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

# SQLAlchemy Models

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.String(9), nullable=False)
    profile_image_url = db.Column(db.String(500))
    seller_rating = db.Column(db.Float, default=0.0)
    purchaser_rating = db.Column(db.Float, default=0.0)
    career_id = db.Column(db.Integer, db.ForeignKey('career.id'), nullable=False)
    career = db.relationship('Career', backref='student')

class Career(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    career_name = db.Column(db.String(50), unique=True, nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    publish_date = db.Column(db.DateTime, default=datetime.now())
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref='post')

class WishPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    added_date = db.Column(db.DateTime, default=datetime.now())
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship('Post', backref='wishPost')
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    student = db.relationship('Student', backref='wishPost')

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now())
    general_status = db.Column(db.String(20), nullable=False)
    seller_status = db.Column(db.String(20), nullable=False)
    purchaser_status = db.Column(db.String(20), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship('Post', backref='transaction')
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    student = db.relationship('Student', backref='transaction')

# Marshmallow Models

class StudentSchema(ma.ModelSchema):
    class Meta:
        model = Student

class CarrerSchema(ma.ModelSchema):
    class Meta:
        model = Career

class CategorySchema(ma.ModelSchema):
    class Meta:
        model = Category

class PostSchema(ma.ModelSchema):
    class Meta:
        model = Post

class WishPostSchema(ma.ModelSchema):
    class Meta:
        model = WishPost

class TransactionSchema(ma.ModelSchema):
    class Meta:
        model = Transaction

# Single Schemas Instances
student_schema = StudentSchema()
career_schema = CarrerSchema()
category_schema = CategorySchema()
post_schema = PostSchema()
wish_post_schema = WishPostSchema()
transaction_schema = TransactionSchema()


# Multiple Schemas Instances
careers_schema = CarrerSchema(many=True)
students_schema = StudentSchema(many=True)
categories_schema = CategorySchema(many=True)
posts_schema = PostSchema(many=True)
wish_posts_schema = WishPostSchema(many=True)
transactions_schema = TransactionSchema(many=True)

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

@app.route('/delete_student/<id>')
def delte_student(id):
    student = Student.query.filter_by(id=id).first()
    if student == None:
        return jsonify({'error' : 'Usuario no encontrado.'})
    else:
        db.session.delete(student)
        db.session.commit()
        return jsonify({'message' : 'Usuario eliminado con éxito.'})


@app.route('/all_careers')
def get_all_careers():
    all_careers = Career.query.all()
    if all_careers == None:
        return jsonify({'error' : 'No hay carreras registradas.'})
    else:
        return jsonify({'career' : careers_schema.dump(all_careers)})

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
            id = request.json['id']
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

@app.route('/create_carrers')
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
    db.session.add_all([car1,car2,car3,car4,car5,car6,car7,car8,car9,car10,car11,car12])
    db.session.commit()
    return jsonify({'message' : 'carreras creadas'})


if __name__ == '__main__':
    app.run(debug=True)