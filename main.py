from flask import Flask, render_template, request, url_for, redirect, session, jsonify
import searchUser
from time import time
from datetime import datetime
import json, hmac, hashlib, urllib.request, urllib.parse, random
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
from supabase import create_client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

KEY_SESSION = os.environ.get("KEY_SESSION") 
app.secret_key = KEY_SESSION  # Khóa bí mật để mã hóa session

@app.route('/', methods=['GET', 'POST'])
def index():
    response = supabase.table("products").select("*").execute()
    products = response.data if response.data else []
    return render_template("main.html", products=products) 

#search api
@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('q', '').strip()
    return searchUser.searchUser(query)  # Gọi API để lấy dữ liệu

@app.route('/product/<int:product_id>', methods=['GET','POST'])
def product(product_id):
    # Get product from database
    product = supabase.table("products").select("*").eq("product_id", product_id).execute()
    if not product.data:
        abort(404)
    

    product_reviews = supabase.table("product_reviews").select("*").eq("product_id", product_id).execute()
    user= supabase.table("users").select("*").eq("email", product_reviews.data[0]['user_id']).execute()
    
    product_data = {
        'product_id': product_id,
        'product_name': product.data[0]['product_name'],
        'quantity': product.data[0]['quantity'],
        'image_url': product.data[0]['img_url'],
        'price': product.data[0]['price'],
        'rating': product_reviews.data[0]['rating'],
        'user_name': user.data[0]['user_name'],
        'comment': product_reviews.data[0]['comment'],
        'created_at': product_reviews.data[0]['created_at'],
        'user_id': product_reviews.data[0]['user_id'],
    }
    
    return render_template('product.html', product=product_data)

@app.route('/payment', methods=['GET'])
def payment():
    if 'email' not in session:
        return redirect(url_for('login'))
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    return render_template("payment.html", cart=cart, total=total)

@app.route('/account',methods=['GET','POST'])
def account():
    if 'email' in session:
        if request.method == 'POST':
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

@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'email' not in session:
        return redirect(url_for('login'))
        
    product = supabase.table("products").select("*").eq("product_id", product_id).execute()
    if not product.data:
        return "Product not found", 404

    quantity = int(request.form.get("quantity", 1))
    product = product.data[0]
    
    cart = session.get("cart", [])
    
    # Check if product already in cart
    for item in cart:
        if item["id"] == product_id:
            item["quantity"] += quantity
            break
    else:
        cart.append({
            "id": product_id,
            "name": product["name"],
            "price": product["price"],
            "quantity": quantity
        })
        
    session["cart"] = cart
    return redirect(url_for('cart'))

@app.route('/cart', methods=['GET'])
def view_cart():
    if 'email' not in session:
        return redirect(url_for('login'))
    cart = session.get("cart", [])
    total = sum(item["price"] * item["quantity"] for item in cart)
    return render_template("cart.html", cart=cart, total=total)

@app.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'email' not in session:
        return redirect(url_for('login'))
    
    cart = session.get("cart", [])
    cart = [item for item in cart if item["id"] != product_id]
    session["cart"] = cart
    return redirect(url_for('cart'))

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

        if not data or len(data) == 0:
            email_err = "❌ Email không tồn tại!"
            return render_template('login.html', email_err=email_err)
        
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

@app.route('/google-callback', methods=['GET'])
def google_callback():
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

# ZaloPay Configuration
config = {
    "app_id": os.environ.get("ZALOPAY_APP_ID"),
    "key1": os.environ.get("ZALOPAY_KEY1"),
    "key2": os.environ.get("ZALOPAY_KEY2"),
    "endpoint": "https://sb-openapi.zalopay.vn/v2/create",
    # "query_endpoint": "https://sb-openapi.zalopay.vn/v2/query"
}

@app.route('/create-payment', methods=['POST'])
def create_payment():
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
        
    try:
        # Get cart data from the request instead of session
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
            
        cart = data.get('items', [])
        if not cart:
            return jsonify({'success': False, 'message': 'Cart is empty'}), 400
            
        total_amount = data.get('total_amount', 0)
        if total_amount <= 0:
            return jsonify({'success': False, 'message': 'Invalid total amount'}), 400
        
        # Check if ZaloPay config is properly set up
        if not config.get("app_id") or not config.get("key1") or not config.get("key2"):
            print("ZaloPay configuration is missing. Check your environment variables.")
            return jsonify({'success': False, 'message': 'Payment service configuration error'}), 500
        
        # Generate unique transaction ID
        trans_id = random.randrange(1000000)
        
        # Create order data
        order = {
            "app_id": config["app_id"],
            "app_trans_id": "{:%y%m%d}_{}".format(datetime.today(), trans_id),
            "app_user": session['email'],
            "app_time": int(round(time() * 1000)),
            "embed_data": json.dumps({
                "email": session['email'],
                "cart": cart
            }),
            "item": json.dumps([{
                "name": item['name'],
                "quantity": item['quantity'],
                "price": item['price']
            } for item in cart]),
            "amount": total_amount,
            "description": f"Payment for order #{trans_id}",
            "bank_code": "zalopayapp"
        }

        # Generate MAC
        data = "{}|{}|{}|{}|{}|{}|{}".format(
            order["app_id"], 
            order["app_trans_id"],
            order["app_user"],
            order["amount"],
            order["app_time"],
            order["embed_data"],
            order["item"]
        )
        
        # Make sure key1 is not None before encoding
        key1 = config.get('key1')
        if not key1:
            return jsonify({'success': False, 'message': 'Payment service key is missing'}), 500
            
        order["mac"] = hmac.new(
            key1.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()

        # Send request to ZaloPay
        response = urllib.request.urlopen(
            url=config["endpoint"],
            data=urllib.parse.urlencode(order).encode()
        )
        result = json.loads(response.read())
        
        if result['return_code'] == 1:
            # Store order in database
            supabase.table("orders").insert({
                "app_trans_id": order["app_trans_id"],
                "email": session['email'],
                "amount": total_amount,
                "status": "pending",
                "cart": cart
            }).execute()
            
            return jsonify({
                'success': True,
                'payment_url': result['order_url'],
                'app_trans_id': order["app_trans_id"]
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('return_message', 'Payment creation failed')
            }), 400
            
    except Exception as e:
        print(f"Error in create-payment: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/callback', methods=['POST'])
def callback():
    try:
        data = request.json
        
        # Verify callback authenticity
        mac = hmac.new(
            config['key2'].encode(),
            data['data'].encode(),
            hashlib.sha256
        ).hexdigest()

        if mac != data['mac']:
            return jsonify({
                'return_code': -1,
                'return_message': 'Invalid MAC'
            }), 400

        # Parse callback data
        payment_data = json.loads(data['data'])
        
        # Update order status in database
        supabase.table("orders").update({
            "status": "completed" if payment_data['status'] == 1 else "failed",
            "payment_time": datetime.now().isoformat()
        }).eq("app_trans_id", payment_data['app_trans_id']).execute()

        # Clear cart if payment successful
        if payment_data['status'] == 1:
            session['cart'] = []

        return jsonify({
            'return_code': 1,
            'return_message': 'success'
        })

    except Exception as e:
        return jsonify({
            'return_code': 0,
            'return_message': str(e)
        }), 500

@app.route('/payment-status/<app_trans_id>', methods=['GET'])
def payment_status(app_trans_id):
    if 'email' not in session:
        return redirect(url_for('login'))
        
    try:
        # Query order status from database
        order = supabase.table("orders").select("*").eq("app_trans_id", app_trans_id).execute()
        
        if not order.data:
            return render_template('payment_error.html', error="Order not found")
            
        order = order.data[0]
        
        # If order is still pending, check with ZaloPay
        if order['status'] == 'pending':
            params = {
                "app_id": config["app_id"],
                "app_trans_id": app_trans_id
            }
            
            data = "{}|{}|{}".format(
                config["app_id"],
                app_trans_id,
                config["key1"]
            )
            
            params["mac"] = hmac.new(
                config['key1'].encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()

            response = urllib.request.urlopen(
                url=config["query_endpoint"],
                data=urllib.parse.urlencode(params).encode()
            )
            result = json.loads(response.read())
            
            if result['return_code'] == 1:
                # Update order status
                new_status = "completed" if result['status'] == 1 else "failed"
                supabase.table("orders").update({
                    "status": new_status,
                    "payment_time": datetime.now().isoformat()
                }).eq("app_trans_id", app_trans_id).execute()
                
                order['status'] = new_status
        
        if order['status'] == 'completed':
            return render_template('payment_success.html',
                                transaction_id=app_trans_id,
                                amount=order['amount'],
                                items=order['cart'])
        else:
            return render_template('payment_error.html',
                                error="Payment failed or was cancelled")
                                
    except Exception as e:
        return render_template('payment_error.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)