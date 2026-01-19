#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource

from config import app, db, api
from models import User, UserSchema

user_schema = UserSchema()


with app.app_context():
    db.create_all()


class ClearSession(Resource):

    def get(self):
        session.pop('page_views', None)
        session.pop('user_id', None)
        return '', 204

    def delete(self):
        session.pop('page_views', None)
        session.pop('user_id', None)
        return '', 204


class Signup(Resource):

    def post(self):
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')

        user = User(username=username)
        user.password_hash = password

        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        return user_schema.dump(user), 201


class CheckSession(Resource):

    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return '', 204

        user = User.query.filter(User.id == user_id).first()
        if not user:
            return '', 204

        return user_schema.dump(user), 200


class Login(Resource):

    def post(self):
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter(User.username == username).first()
        if not user or not user.authenticate(password):
            return {}, 401

        session['user_id'] = user.id
        return user_schema.dump(user), 200


class Logout(Resource):

    def delete(self):
        session.pop('user_id', None)
        return '', 204


api.add_resource(ClearSession, '/clear', endpoint='clear')
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
