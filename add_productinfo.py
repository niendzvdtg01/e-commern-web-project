from main import db, User, app, Product  # Adjust the import path to match your project structure
from werkzeug.security import generate_password_hash

with app.app_context():  # Chạy trong Flask context
    db.session.add(Product(id = 4, name = "Mận dẻo chua ngọt", price = 35000))
    db.session.commit()

print("User added successfully!")
