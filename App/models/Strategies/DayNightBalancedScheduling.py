from App.interfaces.ScheduleStrategy import ScheduleStrategy
from App.models import Schedule, ScheduleGroup
from collections import defaultdict


class DayNightBalancedScheduling(ScheduleStrategy):

    def generateSchedule(self, shifts, staff):
        if not shifts or not staff:
            raise ValueError("Missing shifts or staff")

        schedule_group = ScheduleGroup(name="Day/Night Balanced Schedule")

        # Track number of day and night shifts per staff
        day_count = defaultdict(int)
        night_count = defaultdict(int)

        # Sort shifts chronologically for deterministic assignment
        shifts = sorted(shifts, key=lambda s: s.start_time)

        for shift in shifts:

            # Determine shift type
            hour = shift.start_time.hour
            is_day_shift = 6 <= hour < 18   # 6am–6pm is DAY

            # Choose staff who is most balanced so far
            preferred_staff = min(
                staff,
                key=lambda s: abs(day_count[s.id] - night_count[s.id])
            )

            # Update counters
            if is_day_shift:
                day_count[preferred_staff.id] += 1
            else:
                night_count[preferred_staff.id] += 1

            # Build and assign schedule item
            shift.staff_id = preferred_staff.id

            schedule = Schedule(
                name=f"Shift {shift.start_time}",
                created_by=1
            )
            schedule.shifts.append(shift)

            schedule_group.add_schedule(schedule)

        return schedule_group
