# app/views/staff_views.py
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from App.controllers import staff
from App.controllers.notification import get_user_notifications, mark_as_read
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from App.models import Schedule, Shift, User

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

#Based on the controllers in App/controllers/staff.py, staff can do the following actions:
# 1. View combined roster
# 2. Clock in 
# 3. Clock out
# 4. View specific shift details
# 5. View notifications
# 6. Mark notification as read

#Home Screen for staff
@staff_views.route('/staff', methods=['GET'])
@jwt_required()
def get_staff_page():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return render_template("staff.html", user=user)

#Route to view Schedule
@staff_views.route('/viewSchedule', methods=['GET'])
@jwt_required()
def view_schedule_page():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    schedules = Schedule.query.all()
    selected_schedule_id = request.args.get('schedule_id', type=int)
    return render_template("scheduleView.html", user=user, schedules=schedules, selected_schedule_id=selected_schedule_id)


# Staff view roster route
@staff_views.route('/staff/roster', methods=['GET'])
@jwt_required()
def view_roster():
    try:
        staff_id = get_jwt_identity()  # get the user id stored in JWT
        # staffData = staff.get_user(staff_id).get_json()  # Fetch staff data
        roster = staff.get_combined_roster(staff_id)  # staff.get_combined_roster should return the json data of the roseter
        return jsonify(roster), 200
    except SQLAlchemyError:
        return jsonify({"error": "Database error"}), 500

@staff_views.route('/staff/shift', methods=['GET'])
@jwt_required()
def view_shift():
    try:
        data = request.get_json()
        shift_id = data.get("shiftID")  # gets the shiftID from the request
        shift = staff.get_shift(shift_id)  # Call controller
        if not shift:
            return jsonify({"error": "Shift not found"}), 404
        return jsonify(shift.get_json()), 200
    except SQLAlchemyError:
        return jsonify({"error": "Database error"}), 500

# Staff Clock in endpoint
@staff_views.route('/staff/clock_in', methods=['POST'])
@jwt_required()
def clock_in():
    try:
        print("CLock")
        staff_id = int(get_jwt_identity())# db uses int for userID so we must convert
        try:
            data = request.get_json()
        except:
            data = request.form #for use with template
        #shift_id = data.get("shiftID")  # gets the shiftID from the request
        shift = Shift.query.filter_by(staff_id=staff_id).first()
        shift_id = shift.id
        shiftOBJ = staff.clock_in(staff_id, shift_id)  # Call controller
        try:
            flash(f'Shift Clock out successful')
            return redirect(url_for('staff_views.get_staff_page'))
        except:
            return jsonify(shiftOBJ.get_json()), 200
    except (PermissionError, ValueError) as e:
        return jsonify({"error": str(e)}), 403
    except SQLAlchemyError:
        return jsonify({"error": "Database error"}), 500


# Staff Clock in endpoint
@staff_views.route('/staff/clock_out/', methods=['POST'])
@jwt_required()
def clock_out():
    try:
        staff_id = int(get_jwt_identity())# db uses int for userID so we must convert
        try:
            data = request.get_json()
        except:
            data = request.form #for use with template
        #shift_id = data.get("shiftID")  # gets the shiftID from the request
        shift = Shift.query.filter_by(staff_id=staff_id).first()
        shift_id = shift.id
        shift = staff.clock_out(staff_id, shift_id)  # Call controller
        try:
            flash(f'Shift Clock out successful')
            return redirect(url_for('staff_views.get_staff_page'))
        except:
            return jsonify(shift.get_json()), 200
    except (PermissionError, ValueError) as e:
        return jsonify({"error": str(e)}), 403
    except SQLAlchemyError:
        return jsonify({"error": "Database error"}), 500
    
# Staff view notifications route
@staff_views.route('/staff/notifications', methods=['GET'])
@jwt_required()
def staff_view_notifications():
    try:
        staff_id = int(get_jwt_identity())
        notifications = get_user_notifications(staff_id)
        return jsonify([n.get_json() for n in notifications]), 200
    except SQLAlchemyError:
        return jsonify({"error": "Database error"}), 500
    
# Staff mark notification as read route
@staff_views.route('/staff/notifications/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def staff_mark_notification_read(notification_id):
    try:
        staff_id = int(get_jwt_identity())
        notification = mark_as_read(notification_id)

        if not notification or notification.receiver_id != staff_id:
            return jsonify({"error": "Invalid notification"}), 403

        return jsonify(notification.get_json()), 200
    except SQLAlchemyError:
        return jsonify({"error": "Database error"}), 500