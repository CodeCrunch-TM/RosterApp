from collections import defaultdict
from App.models import ScheduleGroup, Schedule
from App.interfaces.ScheduleStrategy import ScheduleStrategy

class EvenDistributionStrategy(ScheduleStrategy):

    def generateSchedule(self, shifts, staff):
        if not shifts or not staff:
            raise ValueError("Missing shifts or staff")

        schedule_group = ScheduleGroup(name="Even Distribution Schedule Group") #had this in the wrong place, now it shouldn't need to pass through
        
        # Group shifts by date
        shifts_by_date = defaultdict(list)
        for shift in shifts:
            shifts_by_date[shift.start_time.date()].append(shift)

        # Assign staff evenly within each day
        for day, day_shifts in shifts_by_date.items():
            schedule = Schedule(name=f"Schedule {day}", created_by=1)
            for i, shift in enumerate(day_shifts):
                assigned_staff = staff[i % len(staff)]
                shift.staff_id = assigned_staff.id
                schedule.shifts.append(shift)
            schedule_group.add_schedule(schedule)

        return schedule_group
