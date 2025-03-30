from flask import Flask, render_template, request, url_for, redirect, session, jsonify
import searchUser, Login, loadtodb
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

app = Flask(__name__)
# thay vì dùng sql đơn thuần thì dùng sqlalchemy(dùng ORM) để biến các thao tác với database thành các class và object
# Kết nối đến cơ sở dữ liệu PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:maimoremood123@db.fxmeevciubcbiyqppdln.supabase.co:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
# Tạo bảng trong cơ sở dữ liệu nếu chưa tồn tại
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

# Chạy tạo bảng trong application context
with app.app_context():
    db.create_all()

app.secret_key = "maimoremood@123"

@app.route('/', methods=['GET', 'POST'])
def index():
    data = []
    usersearch = ""
    if request.method == 'POST':
        usersearch = request.form['userInput']
        data = searchUser.searchUser(usersearch)
    return render_template("main.html", table=data, usertxt=usersearch)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_err = "incorrect username!"
        password_err = "incorrect password!"
        user = request.form['userInput']
        password = request.form['password']  
        if Login.checkuser(user, password):
            session['username'] = user
            return redirect(url_for('index'))
        else:
            return render_template("login.html", username_err=username_err, password_err=password_err)
    return render_template("login.html", username_err="", password_err="")

@app.route('/signup', methods=['GET','POST'])
def signup():
    return render_template("signup.html")
# def signup():
#     if not request.is_json:
#         return jsonify({"error": "Content-Type must be application/json"}), 415
    
#     data = request.get_json()
#     username = data.get("username")
#     email = data.get("email")
#     password = data.get("password")

#     if not username or not email or not password:
#         return jsonify({"error": "Missing username, email, or password"}), 400

#     # Kiểm tra xem user đã tồn tại chưa
#     existing_user = User.query.filter_by(username=username).first()
#     if existing_user:
#         return jsonify({"error": "Username already exists"}), 409

#     # Hash mật khẩu và lưu vào DB
#     hashed_password = generate_password_hash(password)
#     new_user = User(username=username, email=email, password_hash=hashed_password)
#     db.session.add(new_user)
#     db.session.commit()

#     return jsonify({"message": f"User {username} registered successfully!"}), 201
if __name__ == '__main__':
    app.run(debug=True)
