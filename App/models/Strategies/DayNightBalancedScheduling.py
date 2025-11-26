from interfaces import ScheduleStrategy
from models import Schedule, ScheduleGroup
from collections import defaultdict

class DayNightBalancedScheduling(ScheduleStrategy):
    def generate_schedule(self, shifts, staff):
        schedule = ScheduleGroup()
        #setting up counters
        day_counter = defaultdict(set)
        night_counter = defaultdict(set)
        
        for shift in shifts:
            #assigning shift start times
            is_day_shift  = shift.start_time.hour < 21 # anything before 9pm
            preferred_staff = min(staff, key=lambda s: abs(day_counter[s] - night_counter[s])) # this should take the list of staff and basically check their personal day:night ratio
            if is_day_shift:
                day_counter[preferred_staff]+=1     #this is my replacement to java arraylists - to anyone reading this who's confused, dw the dict is basically a blank dictionary and we're assigning staff to it based on their index
            else:                                   #so assuming that no staff has shifts, we start from 0 on each and we assign each counter based on which shift the staff is given, so the first one will have 1 day and  night, so the next night  
                night_counter[preferred_staff]+=1   #shift goes to them, and tries to balance it such that each person has a 1:1 ratio of day:night, it won't be perfect but it'll be as close as possible, test later to refine though
            schedule.add_schedule(Schedule(shift, preferred_staff))
        return schedule