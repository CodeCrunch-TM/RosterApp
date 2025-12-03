from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies
from App.database import db
from App.models import *

from.index import index_views

from App.controllers import (
    login,

)

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')




'''
Page/Action Routes
'''    

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")
    

@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    token = login(data['username'], data['password'])
    response = redirect(request.referrer)
    if not token:
        flash('Bad username or password given'), 401
    else:
        flash('Login Successful')
        set_access_cookies(response, token) 
    return response

@auth_views.route('/logout', methods=['GET'])
def logout_action():
    #response = redirect(request.referrer) 
    response = redirect(url_for('index_views.index_page'))
    flash("Logged Out!")
    unset_jwt_cookies(response)
    return response

'''
API Routes
'''

@auth_views.route('/api/login', methods=['GET'])
def get_login_page():
    return render_template("login.html")

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
    try:
        data = request.json
    except:
        data = request.form
    token = login(data['username'], data['password'])
    if not token:
        return jsonify(message='bad username or password given'), 401
    if not request.is_json:
        user = User.query.filter_by(username=data['username']).first()
        #print(user.role)
        if user.role == "staff": #Checks for admin, redirects accordingly
            response = redirect(url_for('staff_views.get_staff_page'))
        else:
            response = redirect(url_for('admin_view.get_admin_page'))
        set_access_cookies(response, token)
        return response
    
    response = jsonify(access_token=token) 
    set_access_cookies(response, token)
    return response

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    return jsonify({'message': f"username: {current_user.username}, id : {current_user.id}"})

@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response