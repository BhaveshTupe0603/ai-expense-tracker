from flask_login import UserMixin
from database import get_db_connection

class User(UserMixin):
    def __init__(self, id, username, email, full_name=None, age=None, occupation=None, role=None, monthly_budget=0):
        self.id = id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.age = age
        self.occupation = occupation
        self.role = role
        self.monthly_budget = monthly_budget

    @staticmethod
    def get(user_id):
        conn = get_db_connection()
        user_data = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        
        if not user_data:
            return None

        # Return User object with ALL profile fields
        return User(
            id=user_data['id'], 
            username=user_data['username'], 
            email=user_data['email'],
            full_name=user_data['full_name'],
            age=user_data['age'],
            occupation=user_data['occupation'],
            role=user_data['role'],
            monthly_budget=user_data['monthly_budget']
        )