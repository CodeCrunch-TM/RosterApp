from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.controllers.schedule_processor import *
from App.database import db
from App.models import *
from App.models.Strategies import *

schedule_views = Blueprint('schedule_views', __name__)

def display_schedule_group(schedule):
    print("-----Schedule-----")
    for x in schedule.schedules: # if i gotta do any more in this i need to rename, i didn't think it would be bad but like 4 minutes in and i am already confusing myself
        start = x.shift.start_time.strftime("%d-%m-%Y $H:%M") #https://www.programiz.com/python-programming/datetime/strftime
        end = x.shift.end_time.strftime("%d-%m-%Y $H:%M")
        print(f"[Shift {x.shift.shift_id}]: {start} - {end} // {x.staff.name}")
        
def display_staff(schedule, staff):
    print(f"-----Schedule for {staff.name}-----")
    for x in schedule.schedules:
        if x.staff.staff_id == staff.staff_id:
            start = x.shift.start_time.strftime("%d-%m-%Y $H:%M")
            end = x.shift.end_time.strftime("%d-%m-%Y $H:%M")
            print(f"[Shift {x.shift.shift_id}]: {start} - {end}") # same code as above just added id checking lmao
            


@schedule_views.route('/api/schedule/populate/<int:schedule_id>/<string:strategy>', methods=['PUT'])
@jwt_required()
def populate_schedule(schedule_id, strategy):
    try:
        schedule = db.session.get(Schedule, schedule_id)
        
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        # Get all shifts for the given schedule
        shifts = Shift.query.filter_by(scheduleID=schedule_id).all()
        
        if not shifts:
            return jsonify({'error': 'No shifts found for this schedule'}), 404
        
        # Get all available staff
        staff = Staff.query.all()
        
        if not staff:
            return jsonify({'error': 'No staff available'}), 404
        
        
        # Determine which strategy to use
        if strategy.lower() == 'daynightbalance':
            strategy_instance = DayNightBalancedScheduling
        elif strategy.lower() == 'evendistribution':
            strategy_instance = EvenDistributionStrategy
        elif strategy.lower() == 'minimizedayscheduling':
            strategy_instance = MinimizeDaySchedulingStrategy
        else:
            return jsonify({'error': f'Invalid strategy: {strategy}'}), 400
        
        # Autopopulate using strategy
        populated_schedule = autopopulate(strategy_instance, shifts, staff)
        
        # Save the populated schedule assignments to database
        for shift in populated_schedule:
            db_shift = db.session.get(Shift, shift.shiftID)
            if db_shift:
                db_shift.staffID = shift.staffID
        
        db.session.commit()
        
        return jsonify({
            'message': f'Schedule populated successfully using {strategy} strategy'
            }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': {str(e)}}), 500

        