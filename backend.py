from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import post_dump
from marshmallow_sqlalchemy import TableSchema
from sqlalchemy import exc, desc
from datetime import datetime
import os

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

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
    status = db.Column(db.String(50), default='active')
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
    general_status = db.Column(db.String(20), default='pending')
    seller_status = db.Column(db.String(20), default='pending')
    purchaser_status = db.Column(db.String(20), default='pending')
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship('Post', backref='transaction')
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    student = db.relationship('Student', backref='transaction')

# Marshmallow Models

class CategorySchema(ma.ModelSchema):
    class Meta:
        model = Category
    @post_dump
    def exclude_fields(self, data, **kwargs):
        data.pop('post')
        return data

class CarrerSchema(ma.ModelSchema):
    class Meta:
        model = Career

class StudentSchema(ma.ModelSchema):
    class Meta:
        model = Student
    career = ma.Nested(CarrerSchema)
    @post_dump
    def exclude_carrer(self, data, **kwargs):
        data['career'].pop('post')
        data['career'].pop('student')
        data.pop('post')
        data.pop('transaction')
        data.pop('wishPost')
        return data

class PostSchema(ma.ModelSchema):
    class Meta:
        model = Post
    careers = ma.Nested(CarrerSchema, many=True)
    category = ma.Nested(CategorySchema)
    student = ma.Nested(StudentSchema)
    @post_dump
    def exclude_fields(self, data, **kwargs):
        for career in data['careers']:
            career.pop('post')
            career.pop('student')
        # data['category'].pop('post')
        data.pop('transaction')
        data.pop('wishPost')
        return data

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
        return jsonify(student_schema.dump(student))

@app.route('/active_posts/<student_id>')
def get_active_posts(student_id):
    posts = Post.query.filter_by(student_id=student_id,status='active').all()
    return jsonify(posts_schema.dump(posts))

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
    return jsonify(categories_schema.dump(all_categories))

@app.route('/all_students')
def get_all_students():
    all_students = Student.query.all()
    if all_students == None:
        return jsonify({'error' : 'No hay estudiantes registrados.'})
    else:
        return jsonify(students_schema.dump(all_students))

# @app.route('/single_post/<id>')
# def get_post_by(id):
#     return jsonify({'id': id})
    # post = Post.query.filter_by(id=id,status='active').first()
    # if post == None:
    #     return jsonify({'error' : 'La publicación a la que quieres acceder no está disponible.'})
    # else:
    #     return jsonify(post_schema.dump(post))
@app.route('/single_post/<id>')
def get_sinlge_post(id):
    post = Post.query.filter_by(id=id,status='active').first()
    if post == None:
        return jsonify({'error' : 'La publicación a la que quieres acceder no está disponible.'})
    else:
        return jsonify(post_schema.dump(post))


@app.route('/all_posts')
def get_all_posts():
    all_posts = Post.query.all()
    if all_posts == None:
        return jsonify({'error' : 'No hay publicaciones registrados.'})
    else:
        return jsonify({'posts' : posts_schema.dump(all_posts)})

@app.route('/all_posts_by_category/<category_id>')
def get_all_posts_by_category(category_id):
    category = Category.query.filter_by(id=category_id).first()
    if category == None:
        return jsonify({'error' : 'La categoría no existe.'})
    posts = Post.query.filter_by(category=category).all()
    return jsonify({'posts' : posts_schema.dump(posts)})
    
@app.route('/recent_posts/<student_id>')
def get_recent_posts(student_id):
    recent_posts = Post.query.filter(Post.student_id!=student_id,Post.status=='active').order_by(desc(Post.id)).limit(50)
    if recent_posts == None:
        return jsonify({'error' : 'No hay publicaciones registrados.'})
    else:
        return jsonify(posts_schema.dump(recent_posts))

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

@app.route('/publish', methods=['POST'])
def publish():   
    category_name = request.json['category_name']
    category = Category.query.filter_by(name=category_name).first()
    if category == None:
        return jsonify({'error' : 'Categoría no encontrada.'}) 
    
    student_id = request.json['student_id']
    student = Student.query.filter_by(id=student_id).first()
    if student == None:
        return jsonify({'error' : 'Estudiante no encontrado'})

    career_names = request.json['career_names']
    careers = []
    for career_name in career_names:
        career = Career.query.filter_by(career_name=career_name).first()
        if career == None:
            return jsonify({'error' : 'Carrera no encontrada.'})
        else:
            careers.append(career)

    try:
        name = request.json['name']
        price = request.json['price']
        description = request.json['description']
        image_url = request.json['image_url']
        level = request.json['level']

        post = Post(name=name,price=price,description=description,image_url=image_url,level=level,category=category,student=student)
        post.careers.extend(careers)
        db.session.add(post)
        db.session.commit()
        return jsonify({'message' : 'Publicación registrada satisfactoriamente.'})
    except exc.IntegrityError as e:
        return jsonify({'error' : 'Error de integridad.'}) 
    except Exception as e:
        return jsonify({'error' : f'Error al realizar la publicación. {e}'})

@app.route('/create_transaction', methods=['POST'])
def create_transaction():
    student_id = request.json['student_id']
    student = Student.query.filter_by(id=student_id).first()
    if student == None:
        return jsonify({'error' : 'Estudiante no encontrado'})
    id = request.json['id']
    post = Post.query.filter_by(id=id,status='active').first()
    if post == None:
        return jsonify({'error' : 'La publicación a la que quieres acceder no está disponible.'})
    post.status = 'inProcess'
    transaction = Transaction(post=post,student=student)
    db.session.add(transaction)
    db.session.commit()
    return jsonify({'message' : '¡Felicitaciones!&sepEl artículo ha sido comprado con éxito. Ahora debes ponerte en contacto con el vendedor para que puedan acordar el lugar y la fecha de entrega. No olvides que puedes encontrar esta compra en tu historial para consultar los datos del vendedor y poder calificar la compra.'})

@app.route('/create_carreers')
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

@app.route('/create_categories')
def crate_categories():
    cat1 = Category(name='Libros',description='En esta categoría podrás encontrar diversos libros.',image_url='https://firebasestorage.googleapis.com/v0/b/u-sell-app.appspot.com/o/categoryImages%2FLibros.png?alt=media&token=7674f1bf-a685-45f5-b5a4-53bb021b7c45')
    cat2 = Category(name='Útiles',description='En esta categoría podrás encontrar útiles para tus estudios.',image_url='https://firebasestorage.googleapis.com/v0/b/u-sell-app.appspot.com/o/categoryImages%2FUtiles.png?alt=media&token=613eb19b-c331-4a8c-ad8f-3d9846dcecca')
    cat3 = Category(name='Ropa',description='En esta categoría podrás ropa, como batas.',image_url='https://firebasestorage.googleapis.com/v0/b/u-sell-app.appspot.com/o/categoryImages%2FRopa.png?alt=media&token=6bbe08da-961c-4583-b383-614010156c15')
    db.session.add_all([cat1,cat2,cat3])
    db.session.commit()
    return jsonify({'message' : 'categorias creadas'})


if __name__ == '__main__':
    app.run(debug=True)
