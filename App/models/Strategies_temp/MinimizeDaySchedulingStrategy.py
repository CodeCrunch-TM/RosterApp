from App.models import Schedule, ScheduleGroup
from App.interfaces.ScheduleStrategy import ScheduleStrategy
from collections import defaultdict

class MinimizeDaySchedulingStrategy(ScheduleStrategy):

    def generateSchedule(self, shifts, staff):
        if not shifts or not staff:
            raise ValueError("Missing shifts or staff")

        schedule_group = ScheduleGroup(name="Minimal Day Schedule")

        # Group shifts by day
        shifts_by_day = defaultdict(list)
        for shift in shifts:
            shifts_by_day[shift.start_time.date()].append(shift)

        # Track the set of days each staff member is already working
        active_days = defaultdict(set)
        staff_index = 0
        staff_count = len(staff)

        # Assign all shifts on a day to a single staff to minimize unique days
        for day, day_shifts in sorted(shifts_by_day.items()):
            # Pick staff with the fewest active days so far
            selected_staff = min(staff, key=lambda s: len(active_days[s.id]))

            # Assign all shifts on this day to selected staff
            for shift in day_shifts:
                shift.staff_id = selected_staff.id
                active_days[selected_staff.id].add(day)

            # Build a schedule object for the day
            schedule = Schedule(name=f"Shifts for {day}", created_by=1)
            schedule.shifts.extend(day_shifts)
            schedule_group.add_schedule(schedule)

            staff_index += 1

        return schedule_group
