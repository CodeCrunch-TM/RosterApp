from App.models import ScheduleGroup, Schedule
from App.interfaces.ScheduleStrategy import ScheduleStrategy

class EvenDistributionStrategy(ScheduleStrategy):
    
    def generateSchedule(self, shifts, staff):
        if not shifts or not staff:
            raise ValueError("Missing shifts or staff")

        group = ScheduleGroup(name="Even Distribution")

        staff_index = 0

        for shift in shifts:
            assigned_staff = staff[staff_index]
            shift.staff_id = assigned_staff.id

            new_schedule = Schedule(
                name=f"Shift-{shift.id}",
                created_by=1
            )
            new_schedule.shifts.append(shift)
            group.add_schedule(new_schedule)

            staff_index = (staff_index + 1) % len(staff)

        return group