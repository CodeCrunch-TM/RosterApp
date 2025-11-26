from models import ScheduleGroup, Schedule
from interfaces import ScheduleStrategy

class EvenDistributionScheduling(ScheduleStrategy):
    def generate_schedule(self, shifts, staff):
        schedule = ScheduleGroup()
        x = 0 #just an index to iterate over the list of staff
        for shift in shifts:
            assigned_staff = staff[x % len(staff)] #this'll take the staff list and basically iterate one at a time and assign each shift to staff in order of the list
            schedule.add_schedule(Schedule(shift, assigned_staff)) #until someone creates scheduleGroup i can't really draft this properly cause idk what the add signature would be
            x+=1
        return schedule