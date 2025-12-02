from App.models import Schedule, ScheduleGroup
from App.interfaces.ScheduleStrategy import ScheduleStrategy
from collections import defaultdict

class MinimizeDaySchedulingStrategy(ScheduleStrategy):

    def generateSchedule(self, shifts, staff):
        if not shifts or not staff:
            raise ValueError("Shifts and staff lists cannot be empty")

        schedule_group = ScheduleGroup(name="Minimal Day Schedule")

        # Track the set of days each staff member is already working
        active_days = defaultdict(set)

        for shift in sorted(shifts, key=lambda s: s.start_time):
            # Pick staff with the fewest active days so far
            selected_staff = min(staff, key=lambda s: len(active_days[s.id]))

            # Record the work day for this staff member
            shift_date = shift.start_time.date()
            active_days[selected_staff.id].add(shift_date)

            # Build schedule object
            schedule = Schedule(
                name=f"Shift {shift_date}",
                created_by=1
            )
            schedule.shifts.append(shift)
            shift.staff_id = selected_staff.id

            schedule_group.add_schedule(schedule)

        return schedule_group 