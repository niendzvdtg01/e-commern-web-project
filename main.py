from flask import Flask, render_template, request, url_for, redirect, session
import searchUser, Login, loadtodb
import hashlib
app = Flask(__name__)
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