from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user, get_jwt_identity

from.index import index_views

from App.controllers import (
    create_user,
    get_all_users,
    get_all_users_json,
    jwt_required
)
from App.models import User

user_views = Blueprint('user_views', __name__, template_folder='../templates')

@user_views.route('/users', methods=['GET'])
@jwt_required()
def get_user_page():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    users = get_all_users()
    return render_template('users.html', user=user, users=users)

@user_views.route('/users', methods=['POST'])
def create_user_action():
    data = request.form
    flash(f"User {data['username']} created!")
    create_user(data['username'], data['password'])
    return redirect(url_for('user_views.get_user_page'))

@user_views.route('/api/users', methods=['GET'])
def get_users_action():
    users = get_all_users_json()
    return jsonify(users)

@user_views.route('/api/users', methods=['POST'])
def create_user_endpoint():
    try:
        data = request.json
    except:
        data = request.form
    if(data['confirm_password'] == data['password']) and not request.is_json:
        user = create_user(data['username'], data['password'], data['role']) 
        flash(f"User {data['username']} created!")
        return redirect(url_for('admin_view.get_newuser_page'))
    else:
        user = create_user(data['username'], data['password'], data['role']) 
        return jsonify({'message': f"user {user.username} created with id {user.id}"}), 201

@user_views.route('/static/users', methods=['GET'])
def static_user_page():
  return send_from_directory('static', 'static-user.html')