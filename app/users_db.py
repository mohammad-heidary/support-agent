from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
users = {}

def create_user(username: str, password: str):
    if username in users:
        return False
    hashed_pw = pwd_context.hash(password)
    users[username] = {"username": username, "password": hashed_pw}
    return True

def verify_user(username: str, password: str):
    user = users.get(username)
    if not user:
        return False
    return pwd_context.verify(password, user["password"])
