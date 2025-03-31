from flask import Flask, render_template, request, url_for, redirect, session, jsonify
import searchUser, Login, loadtodb
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import hashlib

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
    return render_template("main.html")  # Không lấy dữ liệu ngay tại đây
#search api
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    return searchUser.searchUser(query)  # Gọi API để lấy dữ liệu
#login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('userInput', '').strip()
        password = request.form.get('password', '').strip()

        if not user or not password:
            return render_template("login.html", username_err="Invalid input!", password_err="Invalid input!")

        if Login.checkuser(user, password):
            session['username'] = user
            session.permanent = True  # Session sẽ tồn tại trong thời gian nhất định
            return redirect(url_for('index'))

        return render_template("login.html", username_err="Incorrect username!", password_err="Incorrect password!")

    return render_template("login.html")
#signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        user = request.form.get('userInput', '').strip()
        password = request.form.get('password', '').strip()

        name_err, username_err, password_err, success_register = "", "", "", ""

        if not name:
            name_err = "Invalid name!"
        if not user:
            username_err = "Invalid username!"
        if not password:
            password_err = "Invalid password!"

        # Kiểm tra nếu tài khoản đã tồn tại
        if Login.checkuser(user):
            username_err = "Username already exists!"

        # Nếu có lỗi, không tiếp tục lưu
        if name_err or username_err or password_err:
            return render_template("signup.html", name_err=name_err, username_err=username_err, password_err=password_err)

        # Mã hóa mật khẩu trước khi lưu
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        loadtodb.saveto_db(name, user, hashed_password)

        success_register = "Successful registration!"
        return render_template("signup.html", success_register=success_register)

    return render_template("signup.html")
if __name__ == '__main__':
    app.run(debug=True)