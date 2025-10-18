from werkzeug.security import generate_password_hash, check_password_hash


class User:
    def __init__(self, collection):
        self.collection = collection

    def find_by_username(self, username):
        return self.collection.find_one({'username': username})

    def create_user(self, username, password):
        if self.find_by_username(username):
            return None
        hashed = generate_password_hash(password)
        doc = {'username': username, 'password': hashed}
        self.collection.insert_one(doc)
        return doc

    def verify(self, username, password):
        user = self.find_by_username(username)
        if not user:
            return False
        return check_password_hash(user['password'], password)
