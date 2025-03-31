from main import db, User, app  # Adjust the import path to match your project structure
from werkzeug.security import generate_password_hash

with app.app_context():  # Chạy trong Flask context
    db.session.add(User(username="testuser", email="test@example.com", password_hash=generate_password_hash("password123")))
    db.session.commit()

print("User added successfully!")
