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

# Mid relation
careers = db.Table('careers',
    db.Column('career_id', db.Integer, db.ForeignKey('career.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)

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
    
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    student = db.relationship('Student', backref='post')

    careers = db.relationship('Career', secondary=careers, backref='post')
    # career_id = db.Column(db.Integer, db.ForeignKey('career.id'), nullable=False)
    # career = db.relationship('Carrer', backref='post')

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

class CarrerSchema(ma.ModelSchema):
    class Meta:
        model = Career

class StudentSchema(ma.ModelSchema):
    class Meta:
        model = Student
    career = ma.Nested(CarrerSchema)

class CategorySchema(ma.ModelSchema):
    class Meta:
        model = Category

class PostSchema(ma.ModelSchema):
    class Meta:
        model = Post
    career = ma.Nested(CarrerSchema)

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

@app.route('/all_categories')
def get_all_categories():
    all_categories = Category.query.all()
    if all_categories == None:
        return jsonify({'error' : 'No hay categorias registradas.'})
    else:
        return jsonify({'categories' : categories_schema.dump(all_categories)})

@app.route('/all_students')
def get_all_students():
    all_students = Student.query.all()
    if all_students == None:
        return jsonify({'error' : 'No hay estudiantes registrados.'})
    else:
        return students_schema.dump(all_students)

@app.route('/all_posts')
def get_all_posts():
    all_posts = Post.query.all()
    if all_posts == None:
        return jsonify({'error' : 'No hay publicaciones registrados.'})
    else:
        return jsonify({'posts' : posts_schema.dump(all_posts)})

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

@app.route('/crate_categories')
def crate_categories():
    cat1 = Category(name='Libros',description='En esta categoría podrás encontrar diversos libros.',image_url='https://firebasestorage.googleapis.com/v0/b/u-sell-app.appspot.com/o/categoryImages%2FLibros.png?alt=media&token=7674f1bf-a685-45f5-b5a4-53bb021b7c45')
    cat2 = Category(name='Útiles',description='En esta categoría podrás encontrar útiles para tus estudios.',image_url='https://firebasestorage.googleapis.com/v0/b/u-sell-app.appspot.com/o/categoryImages%2FUtiles.png?alt=media&token=613eb19b-c331-4a8c-ad8f-3d9846dcecca')
    cat3 = Category(name='Ropa',description='En esta categoría podrás ropa, como batas.',image_url='https://firebasestorage.googleapis.com/v0/b/u-sell-app.appspot.com/o/categoryImages%2FRopa.png?alt=media&token=6bbe08da-961c-4583-b383-614010156c15')
    db.session.add_all([cat1,cat2,cat3])
    db.session.commit()
    return jsonify({'message' : 'categorias creadas'})


if __name__ == '__main__':
    app.run(debug=True)