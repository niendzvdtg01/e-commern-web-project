from functools import wraps
from flask import Flask, render_template, request, url_for, redirect, session, jsonify
import searchUser
from werkzeug.security import generate_password_hash, check_password_hash
# Liên kết với file .env (pip install python-dotenv)
from dotenv import load_dotenv
load_dotenv()
# pip install google-auth-oauthlib==1.0.0 google-auth==2.17.3
# Google OAuth imports
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests
import json
import os

app = Flask(__name__)

# Google OAuth setup
with open('client_secret.json', 'r') as f:
    client_secrets = json.load(f)

GOOGLE_CLIENT_ID = client_secrets['web']['client_id']
GOOGLE_CLIENT_SECRET = client_secrets['web']['client_secret']
GOOGLE_REDIRECT_URI = client_secrets['web']['redirect_uris'][0]
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # to allow Http traffic for local dev

# Init Supabase client để dùng các hàm của supabase (pip install supabase)
# kết nối đến db bằng api supabase
import os
from supabase import create_client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

KEY_SESSION = os.environ.get("KEY_SESSION") 
app.secret_key = KEY_SESSION  # Khóa bí mật để mã hóa session

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("main.html")  # Không lấy dữ liệu ngay tại đây

#search api
@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('q', '').strip()
    return searchUser.searchUser(query)  # Gọi API để lấy dữ liệu

@app.route('/product/<int:product_id>', methods=['GET','POST'])
def product(product_id):
    # Lấy thông tin sản phẩm từ Supabase
    product = supabase.table("product").select("*").eq("product_id", product_id).execute()
    if product.data:
        if product_id == 1:
            return render_template("product1.html")
        elif product_id == 2:
            return render_template("product2.html", product=product.data[0])
        elif product_id == 3:
            return render_template("product3.html", product=product.data[0])
        elif product_id == 4:
            return render_template("product4.html", product=product.data[0])
    else:
        return "Product not found", 404

@app.route('/account',methods=['GET','POST'])
def account():
    if 'email' in session:
        if request.method == 'POST':
            # Only update fields that have actual values
            update_data = {}
            address = request.form.get('address', '').strip()
            phone = request.form.get('phone', '').strip()
            
            if address:
                update_data['address'] = address
            if phone:
                update_data['phone'] = phone
                
            if update_data:
                supabase.table("users").update(update_data).eq("email", session['email']).execute()
            return redirect(url_for('account'))
            
        # Lấy thông tin người dùng từ Supabase
        response = (
            supabase.table("users")
            .select("*")
            .eq("email", session['email']).execute()
        )
        data = response.data
        user_name = data[0].get('username')
        address = data[0].get('address')
        phone = data[0].get('phone')
        email = data[0].get('email')
        # Truyền dữ liệu vào template
        return render_template("account.html", user_name=user_name, address=address, phone=phone,email=email)
    else:
        return redirect(url_for('login'))

@app.route('/change-password', methods=['GET','POST'])
def change_password():
    if 'email' in session:
        if request.method == 'POST':
            old_password = request.form.get('old-password', '').strip()
            new_password = request.form.get('new-password', '').strip()
            confirm_password = request.form.get('confirm-password', '').strip()
            response = (
                supabase.table("users")
                .select("password_hash")
                .eq("email", session['email']).execute()
            )
            data = response.data
            if check_password_hash(data[0].get('password_hash'), old_password):
                if confirm_password != new_password:
                    return render_template("changepassword.html", error="❌ Mật khẩu xác nhận không khớp!")
                new_password = generate_password_hash(new_password)
                supabase.table("users").update({
                    "password_hash": new_password
                }).eq("email", session['email']).execute()
                return redirect(url_for('account'))
            else:
                return render_template("changepassword.html", error="❌ Mật khẩu cũ không đúng!")
        return render_template("changepassword.html")
    return redirect(url_for('login'))

@app.route('/product/<int:product_id>/cart', methods=['GET', 'POST'])
def cart(product_id):
    # Lấy thông tin sản phẩm từ Supabase
    response = supabase.table("product").select("*").eq("product_id", product_id).execute()
    
    if not response.data:  # Kiểm tra sản phẩm có tồn tại không
        return "Product not found", 404

    product = response.data[0]  # Lấy sản phẩm đầu tiên từ danh sách

    # Lấy số lượng từ form
    quantity = int(request.form.get("quantity", 1))  # Mặc định là 1 nếu không có input

    # Tạo dictionary chứa thông tin sản phẩm
    product_dict = {
        "id": product_id,
        "product_name": product["product_name"],  
        "price": product["price"],
        "quantity": quantity
    }

    # Lấy giỏ hàng từ session
    cart = session.get("cart", [])

    # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
    found = False
    for item in cart:
        if item["product_name"] == product["product_name"]:
            item["quantity"] += quantity
            found = True
            break

    if not found:
        cart.append(product_dict)

    session["cart"] = cart  # Cập nhật session
    if response.data:
        if product_id == 1:
            return render_template("product1.html")
        elif product_id == 2:
            return render_template("product2.html")
        elif product_id == 3:
            return render_template("product3.html")
        elif product_id == 4:
            return render_template("product4.html")
    else:
        return "Product not found", 404

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
            .select("email, password_hash") 
            .eq("email", email)
            .execute()
        )
        data = response.data
        # print(f"✅ Dữ liệu tìm thấy: {data}")

        if not data or len(data) == 0:
            email_err = "❌ Email không tồn tại!"
            return render_template('login.html', email_err=email_err)
        print(email)
        user = data[0]
        db_password = user.get('password_hash')
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
    return render_template("signup.html", google_client_id=GOOGLE_CLIENT_ID)

@app.route('/google-login')
def google_login():
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
        redirect_uri=GOOGLE_REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/callback', methods=['GET'])
def callback():
    if 'state' not in session or session['state'] != request.args.get('state'):
        return redirect(url_for('signup'))
    
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
        redirect_uri=GOOGLE_REDIRECT_URI
    )
    
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    id_info = id_token.verify_oauth2_token(credentials.id_token, requests.Request(), GOOGLE_CLIENT_ID)
    
    # Check if user exists in database
    response = supabase.table("users").select("*").eq("email", id_info['email']).execute()
    
    if not response.data:
        # Create new user if doesn't exist
        supabase.table("users").insert({
            "username": id_info['name'],
            "email": id_info['email'],
            "password_hash": generate_password_hash(id_info['sub'])  # Using Google ID as password
        }).execute()
    
    session['email'] = id_info['email']
    session.permanent = True
    return redirect(url_for('index'))

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

if __name__ == '__main__':
    app.run(debug=True)