from datetime import datetime

from models import Staff, Shift, Schedule, ScheduleGroup, GroupRosterFactory
from interfaces import ScheduleStrategy

def create_empty_group():
    return ScheduleGroup()

def autopopulate(strategy, shifts, staff):
    if not shifts or not staff:
        raise ValueError("Shifts and staff lists cannot be empty.")
    
    schedule = strategy.generate_schedule(shifts, staff)
    return schedule

def manual_assign(schedule, shift, staff):
    schedule.add_schedule(Schedule(shift, staff))
    return schedule