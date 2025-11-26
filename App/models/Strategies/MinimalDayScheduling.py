from models import Schedule, ScheduleGroup
from interfaces import ScheduleStrategy
from collections import defaultdict

class MinimalDayScheduling(ScheduleStrategy):
    def generate_schedule(self, shifts, staff):
        schedule = ScheduleGroup()
        active_days = defaultdict(set) #not quite sure how i wanna do this yet, my goal is to have a set of active days for each staff member, maybe separate list
        
        for shift in shifts:
            preferred_staff = min(staff, key=lambda s:len(active_days[s])) #https://www.google.com/aclk?sa=L&ai=DChsSEwjSp-bS7JCRAxWnpFoFHZORC7QYACICCAEQABoCdnU&co=1&gclid=CjwKCAiA55rJBhByEiwAFkY1QJ6dSyUTtL4n9_47q19hpiQTCdil7CylM5OjQjIcmJXUwzfHcoUJKBoCSAAQAvD_BwE&cid=CAASWuRomEKP1G3YZ-tap1WWkHlwIRBoxuERLw52oFeaTK5XyW5XPSEAkXrqvZz-yLobDiI8gXFc5cemVYyhc3Hqm22QnNQBsLOJ1HHUVF5mufYqyKNrHzjQhndfYw&cce=2&sig=AOD64_2CRcUsuQ-apzlUgbKr_cSzoXx-OA&q&adurl&ved=2ahUKEwiG_ODS7JCRAxU4SjABHXfYNuEQ0Qx6BAgUEAE
            active_days[preferred_staff].add(shift.start_time.date()) #I'm not quite sure that my logic is entirely sound here, i think it'll work but this line might be the breakpoint, nvm i think i understand now, check day/nightbalance
            schedule.add_schedule(Schedule(shift, preferred_staff)) #the above line should add the shift date to that staff member's entry in the dict of active days, to show that they have this day as active. I think this needs more refining
        return schedule                                             #but i need the other classes to be added so i can start testing.
            