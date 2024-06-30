from app import bcrypt

def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')