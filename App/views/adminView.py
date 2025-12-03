from flask import Blueprint, jsonify, request, render_template
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

from App.controllers import admin as adminController
from App.controllers.user import get_user
from App.models import Schedule
from App.database import db


admin_view = Blueprint('admin_view', __name__)


#Home Screen for admin
@admin_view.route('/admin', methods=['GET'])
@jwt_required()
def get_admin_page():
    return render_template("admin.html")

@admin_view.route('/createSchedule', methods=['POST'])
@jwt_required()
def createSchedule():
    try:
        admin_id = get_jwt_identity()
        data = request.get_json()
        scheduleName = data.get("scheduleName")

        schedule = adminController.create_schedule(admin_id, scheduleName)
        return jsonify(schedule.get_json()), 200

    except (PermissionError, ValueError) as e:
        return jsonify({"error": str(e)}), 403
    except SQLAlchemyError:
        return jsonify({"error": "Database error"}), 500


@admin_view.route('/createShift', methods=['POST'])
@jwt_required()
def createShift():
    try:
        admin_id = get_jwt_identity()
        data = request.get_json()

        schedule_id = data.get("scheduleID")
        staff_id = data.get("staffID")
        startTime = data.get("start_time")
        endTime = data.get("end_time")

        # Parse time
        try:
            start_time = datetime.fromisoformat(startTime)
            end_time = datetime.fromisoformat(endTime)
        except ValueError:
            start_time = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S")

        staff = get_user(staff_id)
        schedule = db.session.get(Schedule, schedule_id)

        shift = adminController.schedule_shift(admin_id, staff, schedule, start_time, end_time)

        return jsonify(shift.get_json()), 200

    except (PermissionError, ValueError) as e:
        return jsonify({"error": str(e)}), 403
    except SQLAlchemyError:
        return jsonify({"error": "Database error"}), 500


@admin_view.route('/shiftReport', methods=['GET'])
@jwt_required()
def shiftReport():
    try:
        admin_id = get_jwt_identity()
        report = adminController.get_shift_report(admin_id)
        return jsonify(report), 200

    except (PermissionError, ValueError) as e:
        return jsonify({"error": str(e)}), 403
    except SQLAlchemyError:
        return jsonify({"error": "Database error"}), 500
