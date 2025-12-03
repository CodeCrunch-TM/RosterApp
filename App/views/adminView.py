from flask import Blueprint, jsonify, request, render_template
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

from App.controllers import admin as adminController
from App.controllers.user import get_user
from App.models import Schedule, User, Staff, Shift
from App.database import db
from App.models.Strategies import EvenDistributionStrategy, MinimizeDaySchedulingStrategy, DayNightBalancedScheduling
from App.controllers.schedule_processor import autopopulate


admin_view = Blueprint('admin_view', __name__)


#Home Screen for admin
@admin_view.route('/admin', methods=['GET'])
@jwt_required()
def get_admin_page():
    return render_template("admin.html")

#Route to create a new schedule
@admin_view.route('/createNewSchedule', methods=['GET'])
@jwt_required()
def get_schedule_page():
    users = User.query.all()
    schedules = Schedule.query.all()
    return render_template("schedule.html", users=users, schedules=schedules)

#Route to create a new account
@admin_view.route('/createNewUser', methods=['GET'])
@jwt_required()
def get_newuser_page():
    return render_template("newUser.html")

#Route to view Schedule
@admin_view.route('/viewSchedule', methods=['GET'])
@jwt_required()
def view_schedule_page():
    schedules = Schedule.query.all()
    selected_schedule_id = request.args.get('schedule_id', type=int)
    return render_template("scheduleView.html", schedules=schedules, selected_schedule_id=selected_schedule_id)

@admin_view.route('/createSchedule', methods=['POST'])
@jwt_required()
def createSchedule():
    try:
        admin_id = get_jwt_identity()
        try:
            data = request.get_json()
        except:
            data = request.form
        scheduleName = data.get("scheduleName")

        schedule = adminController.create_schedule(admin_id, scheduleName)
        return jsonify(schedule.get_json()), 200

    except (PermissionError, ValueError) as e:
        return jsonify({"error": str(e)}), 403
    except SQLAlchemyError:
        return jsonify({"error": "Database error"}), 500

#Route to schedule a shift

@admin_view.route('/scheduleShift', methods=['GET'])
@jwt_required()
def scheduleShift():
    users = User.query.all()
    schedules = Schedule.query.all()
    return render_template("shift.html", users=users, schedules=schedules)

@admin_view.route('/createShift', methods=['POST'])
@jwt_required()
def createShift():
    try:
        admin_id = get_jwt_identity()
        try:
            data = request.get_json()
        except:
            data = request.form

        schedule_id = data.get("scheduleID")
        staff_id = data.get("staffID")
        startTime = data.get("start_time")
        endTime = data.get("end_time")

        if not all([schedule_id, staff_id, startTime, endTime]):
            return jsonify({"error": "Missing required fields"}), 400

        # Parse time
        #try:
        #    start_time = datetime.fromisoformat(startTime)
        #    end_time = datetime.fromisoformat(endTime)
        #except ValueError:
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
    
@admin_view.route('/autopopulate', methods=['GET', 'POST'])
@jwt_required()
def autopopulate():
    staff = Staff.query.all()
    shifts = Shift.query.order_by(Shift.start_time).all()
    schedules = None #making sure to reset every time
    
    if request.method=='POST':
        strategy_chosen=request.form.get("strategy")
        if strategy_chosen=="even":
            strategy = EvenDistributionStrategy()
        elif strategy_chosen=="minimal":
            strategy = MinimizeDaySchedulingStrategy()
        elif strategy_chosen=="day/night":
            strategy = DayNightBalancedScheduling()
        else:
            strategy = EvenDistributionStrategy() #brute force fallback if none selected or auto-select, however we wanna implement it
        
        schedules = strategy.generateSchedule(shifts, staff)
        for s in schedules.schedules:
            for shift in s.shifts:
                temp = Shift.query.get(shift.id)
                temp.staff_id = shift.staff_id #need to make sure this works, pending testing
        db.session.commit()
    return render_template("roster.html", schedules = schedules, staff = staff)
            