def display_schedule_group(schedule):
    print("-----Schedule-----")
    for x in schedule.schedules: # if i gotta do any more in this i need to rename, i didn't think it would be bad but like 4 minutes in and i am already confusing myself
        start = x.shift.start_time.strftime("%d-%m-%Y $H:%M") #https://www.programiz.com/python-programming/datetime/strftime
        end = x.shift.end_time.strftime("%d-%m-%Y $H:%M")
        print(f"[Shift {x.shift.shift_id}]: {start} - {end} // {x.staff.name}")
        
def display_staff(schedule, staff):
    print(f"-----Schedule for {staff.name}-----")
    for x in schedule.schedules:
        if x.staff.staff_id == staff.staff_id:
            start = x.shift.start_time.strftime("%d-%m-%Y $H:%M")
            end = x.shift.end_time.strftime("%d-%m-%Y $H:%M")
            print(f"[Shift {x.shift.shift_id}]: {start} - {end}") # same code as above just added id checking lmao
            
