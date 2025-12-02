import unittest
from datetime import datetime, timedelta
from App.models import Shift, Staff, ScheduleGroup
from App.models.strategies import (
    EvenDistributionStrategy,
    MinimizeDaySchedulingStrategy,
    DayNightBalancedScheduling
)

class StrategyUnitTests(unittest.TestCase):
    # Create test fixtures for mock staff + mock shifts
    def setUp(self):
        # Mock staff members
        self.staff = [
            self._create_mock_staff(1, "Alice"),
            self._create_mock_staff(2, "Bob"),
            self._create_mock_staff(3, "Charlie"),
        ]
        
        # Mock shifts spread across 3 days, 3 shifts per day
        base_time = datetime(2025, 1, 15, 8, 0, 0)
        self.shifts = []
        for day_offset in range(3):
            for hour in [8, 16, 22]:  # Morning, Afternoon, Night
                start = base_time + timedelta(days=day_offset, hours=hour-8)
                end = start + timedelta(hours=8)
                self.shifts.append(Shift(start_time=start, end_time=end))
        
        # For day/night testing
        self.mixed_shifts = self._create_mixed_shifts()
    
    # Helper to create mock staff without DB
    def _create_mock_staff(self, staff_id, username):
        staff = Staff(username=username, password="test")
        staff.id = staff_id
        return staff
    
    # Helper to create day and night shifts
    def _create_mixed_shifts(self):
        base = datetime(2025, 1, 15, 8, 0, 0)
        shifts = []
        
        # Day shifts (8am - 4pm)
        for i in range(3):
            shifts.append(Shift(
                start_time=base + timedelta(days=i),
                end_time=base + timedelta(days=i, hours=8)
            ))
        
        # Night shifts (8pm - 4am)
        for i in range(3):
            shifts.append(Shift(
                start_time=base.replace(hour=20) + timedelta(days=i),
                end_time=base.replace(hour=4) + timedelta(days=i+1)
            ))
        
        return shifts
    
    # Test EvenDistributionStrategy evenly distributes shifts"""
    def test_even_distribution_strategy(self):
        strategy = EvenDistributionStrategy()
        result = strategy.generateSchedule(self.shifts, self.staff)
        
        self.assertIsInstance(result, ScheduleGroup)
        self.assertEqual(result.name, "Even Distribution")
        self.assertEqual(len(result.schedules), len(set(s.start_time.date() for s in self.shifts)))
        
        staff_shift_count = {s.id: 0 for s in self.staff}
        for schedule in result.schedules:
            for shift in schedule.shifts:
                if shift.staff_id in staff_shift_count:
                    staff_shift_count[shift.staff_id] += 1
        
        self.assertEqual(staff_shift_count[1], 3)
        self.assertEqual(staff_shift_count[2], 3)
        self.assertEqual(staff_shift_count[3], 3)
    
    # Test MinimizeDaySchedulingStrategy minimizes days worked
    def test_minimize_day_scheduling_strategy(self):
        strategy = MinimizeDaySchedulingStrategy()
        result = strategy.generateSchedule(self.shifts, self.staff)
        
        self.assertIsInstance(result, ScheduleGroup)
        self.assertEqual(result.name, "Minimal Day Schedule")
        self.assertEqual(len(result.schedules), len(set(s.start_time.date() for s in self.shifts)))
        
        # Count unique days worked per staff
        staff_days = {s.id: set() for s in self.staff}
        for schedule in result.schedules:
            for shift in schedule.shifts:
                if shift.staff_id in staff_days:
                    staff_days[shift.staff_id].add(shift.start_time.date())
        
        for staff_id, days in staff_days.items():
            self.assertGreater(len(days), 0)
            self.assertLessEqual(len(days), 3)  # Adjusted max days to 3 (matches shifts input)
        
        # Check that at least one day has multiple shifts assigned to same staff
        day_assignments = {}
        for schedule in result.schedules:
            for shift in schedule.shifts:
                day = shift.start_time.date()
                if day not in day_assignments:
                    day_assignments[day] = []
                day_assignments[day].append(shift.staff_id)
        
        days_with_multiple = sum(
            1 for assignments in day_assignments.values()
            if len(set(assignments)) < len(assignments)
        )
        self.assertGreater(days_with_multiple, 0,
            "Strategy should consolidate shifts to minimize days")
    
    # Test DayNightBalancedScheduling balances day vs night
    def test_day_night_balanced_scheduling(self):
        strategy = DayNightBalancedScheduling()
        result = strategy.generateSchedule(self.mixed_shifts, self.staff)
        
        self.assertIsInstance(result, ScheduleGroup)
        self.assertEqual(result.name, "Day/Night Balanced Schedule")
        
        staff_day_count = {s.id: 0 for s in self.staff}
        staff_night_count = {s.id: 0 for s in self.staff}
        for schedule in result.schedules:
            for shift in schedule.shifts:
                hour = shift.start_time.hour
                if 6 <= hour < 18:
                    staff_day_count[shift.staff_id] += 1
                else:
                    staff_night_count[shift.staff_id] += 1
        
        for staff_id in staff_day_count.keys():
            diff = abs(staff_day_count[staff_id] - staff_night_count[staff_id])
            self.assertLessEqual(diff, 1)
    
    # Test strategies handle empty shift list
    def test_strategy_with_empty_shifts(self):
        strategy = EvenDistributionStrategy()
        with self.assertRaises(ValueError) as context:
            strategy.generateSchedule([], self.staff)
        self.assertIn("Missing shifts or staff", str(context.exception))
    
    # Test strategies handle empty staff list
    def test_strategy_with_empty_staff(self):
        strategy = EvenDistributionStrategy()
        with self.assertRaises(ValueError) as context:
            strategy.generateSchedule(self.shifts, [])
        self.assertIn("Missing shifts or staff", str(context.exception))
    
    # 21e: Assert output schedules are valid JSON
    def test_strategy_output_is_valid_json(self):
        strategy = EvenDistributionStrategy()
        result = strategy.generateSchedule(self.shifts, self.staff)
        json_output = result.get_json()
        
        self.assertIn("id", json_output)
        self.assertIn("name", json_output)
        self.assertIn("schedules", json_output)
        self.assertIsInstance(json_output["schedules"], list)
        
        for schedule_json in json_output["schedules"]:
            self.assertIn("id", schedule_json)
            self.assertIn("name", schedule_json)
            self.assertIn("shifts", schedule_json)
            for shift_json in schedule_json["shifts"]:
                self.assertIn("staff_id", shift_json)
                self.assertIn("start_time", shift_json)
                self.assertIn("end_time", shift_json)
    
    # Verify all strategies assign every shift
    def test_all_strategies_assign_all_shifts(self):
        strategies = [
            EvenDistributionStrategy(),
            MinimizeDaySchedulingStrategy(),
            DayNightBalancedScheduling()
        ]
        for strategy in strategies:
            with self.subTest(strategy=strategy.__class__.__name__):
                result = strategy.generateSchedule(self.shifts, self.staff)
                total_assigned = sum(len(schedule.shifts) for schedule in result.schedules)
                self.assertEqual(total_assigned, len(self.shifts))
