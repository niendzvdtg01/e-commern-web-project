from flask import Flask, render_template, request, url_for, redirect, session
import searchUser, Login, loadtodb
app = Flask(__name__)
app.secret_key = "maimoremood@123"
@app.route('/', methods = ['GET', 'POST'])
def index():
    data = []
    usersearch = ""
    if request.method == 'POST':
        usersearch = request.form['userInput']
        data =  searchUser.searchUser(usersearch)
    return render_template("main.html", table = data, usertxt = usersearch)
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_err = "incorrect username!"; password_err = "incorrect password!"
        user = request.form['userInput']
        password = request.form['password']  
        if Login.checkuser(user, password):
            session['username'] = user
            return redirect(url_for('index'))
        else:
            return render_template("login.html", username_err = username_err, password_err = password_err)
    return render_template("login.html", username_err = "", password_err = "")
@app.route('/signup', methods = ['GET' ,'POST'])
def signup():
    name_err = ""; username_err = "";password_err = ""; success_register = ""
    if request.method == 'POST':
        name = request.form['name']
        user = request.form['userInput']
        password = request.form['password']
        if not name:
            name_err = "invalid name!"
        if not user:
            username_err = "invalid user name!"
        if not password:
            password_err = "invalid password!"
        if username_err or password_err:
            return render_template("signup.html", name_err = name_err, username_err = username_err, password_err = password_err)
        loadtodb.saveto_db(name, user, password)
        success_register = "Succesful register!"
    return render_template("signup.html", name_err = "", username_err = "", password_err = "", success_register = success_register)
if __name__ == '__main__':
    app.run(debug=True)