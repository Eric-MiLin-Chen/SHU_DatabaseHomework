import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import jsonify, request


class AuthManager:
    def __init__(self, secret_key):
        self.secret_key = secret_key

    def generate_token(self, username):
        expiration_date = datetime.utcnow() + timedelta(hours=1)
        token = jwt.encode(
            {"username": username, "exp": expiration_date},
            self.secret_key,
            algorithm="HS256",
        )
        return token

    def token_required(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return jsonify({"message": "Token is missing!"}), 401
            try:
                data = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                current_user = data["username"]
            except:
                return jsonify({"message": "Token is invalid!"}), 401
            return func(current_user=current_user, *args, **kwargs)

        return decorated