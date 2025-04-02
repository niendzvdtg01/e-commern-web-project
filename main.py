from flask import Flask, render_template, request, url_for, redirect, session, jsonify
import searchUser
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

@app.route('/account',methods=['GET','POST'])
def account():
    if 'email' in session:
        return render_template("account.html")
    else:
        return redirect(url_for('login'))
@app.route('/change-password', methods=['POST'])
def change_password():
    if 'email' in session:
        if request.method == 'POST':
            old_password = request.form.get('old-password', '').strip()
            new_password = request.form.get('new-password', '').strip()
            confirm_password = request.form.get('confirm-password', '').strip()
            old_password=password_hash(old_password)
            new_password=password_hash(new_password)
            confirm_password=password_hash(confirm_password)
            response = (
                supabase.table("users")
                .select("password_hash")
                .eq("email", session['email'])
                .eq("password_hash", old_password).execute()
            )
            data=response.data
            if data:
                supabase.table("users").update({
                    "password_hash": generate_password_hash(new_password)
                }).eq("email", session['email']).execute()
                return jsonify({"success": True})
            else:
                return jsonify({"success": False})
    return render_template("changepassword.html")

@app.route('/cart', methods=['GET'])
def cart():
    # Lấy thông tin giỏ hàng từ Supabase
    cart_items = supabase.table("cart").select("*").execute()
    return render_template("cart.html", cart_items=cart_items.data)

#login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'email' in session:
        return redirect(url_for('account'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        response = (
            supabase.table("users")
            .select("email, password") 
            .eq("email", email)
            .execute()
        )
        data = response.data
        print(f"✅ Dữ liệu tìm thấy: {data}")

        if not data or len(data) == 0:
            email_err = "❌ Email không tồn tại!"
            return render_template('login.html', email_err=email_err)
        
        user = data[0]
        db_password = user.get('password')
        if not check_password_hash(db_password, password):
            password_err = "❌ Sai mật khẩu!"
            return render_template('login.html', password_err=password_err)

        session['email'] = email
        session.permanent = True  
        return redirect(url_for('index'))

    return render_template("login.html")
#signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'email' in session:
        return redirect(url_for('account'))
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
        response=supabase.table("users").insert({
                "username": username,
                "email": email,
                "password_hash": hashed_password
            }).execute()
        return redirect(url_for('login'))
    return render_template("signup.html")

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)