from flask import Flask, render_template, request, url_for, redirect, session, jsonify
import searchUser, Login
from werkzeug.security import generate_password_hash
# Liên kết với file .env (pip install python-dotenv)
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Init Supabase client để dùng các hàm của supabase (pip install supabase)
# kết nối đến db bằng api supabase
import os
from supabase import create_client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

KEY_SESSION = os.environ.get("KEY_SESSION")  # Load from environment or use a default value
app.secret_key = KEY_SESSION  # Khóa bí mật để mã hóa session

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("main.html")  # Không lấy dữ liệu ngay tại đây
#search api
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    return searchUser.searchUser(query)  # Gọi API để lấy dữ liệu
@app.route('/product/<int:product_id>', methods=['GET','POST'])
def product(product_id):
    # Lấy thông tin sản phẩm từ Supabase
    product = supabase.table("product").select("*").eq("id", product_id).execute()
    if product.data:
        return render_template("product.html", product=product.data[0])
    else:
        return "Product not found", 404
@app.route('/cart', methods=['GET'])
def cart():
    # Lấy thông tin giỏ hàng từ Supabase
    cart_items = supabase.table("cart").select("*").execute()
    return render_template("cart.html", cart_items=cart_items.data)

#login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not user or not password:
            return render_template("login.html", email_err="Invalid input!", password_err="Invalid input!")

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
        username = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        username_err, email_err, password_err = "", "", ""

        if not username:
            username_err = "Invalid name!"
        if not email:
            email_err = "Invalid email!"
        if not password:
            password_err = "Invalid password!"

        if username_err or email_err or password_err:
            return render_template("signup.html", username_err=username_err, email_err=email_err, password_err=password_err)

        hashed_password = generate_password_hash(password)
        # Thêm user vào Supabase
        supabase.table("users").insert({
                "username": username,
                "email": email,
                "password_hash": hashed_password
            }).execute()
        return redirect(url_for('login'))
    return render_template("signup.html")

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)