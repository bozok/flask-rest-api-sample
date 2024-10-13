import os
import redis

from flask import current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt, jwt_required

from sqlalchemy import or_
from rq import Queue

from db import db
from models import UserModel, BlockList
from schemas import UserSchema, UserRegisterSchema
from tasks import send_user_registration_email


blp = Blueprint("users", __name__, description="Operations on users")
connection = redis.from_url(os.getenv("REDIS_URL"))
queue = Queue("emails", connection=connection)



@blp.route("/register", methods=["POST"])
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    def post(self, user_data):
        if UserModel.query.filter(
                or_(
                    UserModel.username == user_data["username"],
                    UserModel.email == user_data["email"]
                )
        ).first():
            abort(400, message="User already exists")

        user = UserModel(
            username=user_data["username"],
            email=user_data["email"],
            password=pbkdf2_sha256.hash(user_data["password"]),
        )

        db.session.add(user)
        db.session.commit()


        queue.enqueue(send_user_registration_email, user.email, user.username)

        return {"message": "User created"}, 201


@blp.route("/users/<int:user_id>", methods=["GET", "DELETE"])
class User(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted"}, 200


@blp.route("/login", methods=["POST"])
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.username == user_data["username"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        abort(400, message="Invalid credentials")


@blp.route('/refresh')
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_access_token}, 200




@blp.route("/logout", methods=["POST"])
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        print(jti)
        revoked_token = BlockList(token=jti)
        db.session.add(revoked_token)
        db.session.commit()
        return {"message": "Successfully logged out"}