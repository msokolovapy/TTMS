from datetime import datetime
class Booking:
    def __init__(self,player_login_name):
        self.player_login_name = player_login_name
        booking_date = input('Which date would you like to book? (dd/mm/yy format): ')
        booking_date = datetime.strptime(booking_date,"%d/%m/%y")
        booking_time = input('Which time slot would you like to book? (hh:mm format): ')
        booking_time = datetime.strptime(booking_time, "%H:%M").time()
        self.booking_datetime = datetime.combine(booking_date, booking_time)
        self.booking_status = True

    
class BookingSystem:
    def __init__(self):
        self.booking_lst = []

    def make_new_booking(self,player_login_name):
        new_booking = Booking(player_login_name)
        self.booking_lst.append(new_booking)
        return

    def cancel_booking(self,player_login_name):
        booking_to_delete = self.get_booking(player_login_name)
        _delete_confirm = input(f"Do you really want to delete {booking_to_delete.player_login_name}'s booking? (y/n): ")
        if _delete_confirm.lower() == 'y':
            self.booking_lst.remove(booking_to_delete)
            print("Booking deleted")
        else:
            pass
        return

    def edit_booking_day(self,player_login_name):
        booking_to_edit = self.get_booking(player_login_name)
        current_booking_day = booking_to_edit.booking_datetime.date().day
        new_day = int(input("Select day: "))
        if new_day != current_booking_day:
            booking_to_edit.booking_datetime = booking_to_edit.booking_datetime.replace(day = new_day)
        else:
            pass
        print(booking_to_edit.booking_datetime)
        return
    
    def edit_booking_time(self,player_login_name):
        booking_to_edit = self.get_booking(player_login_name)
        current_booking_hour = booking_to_edit.booking_datetime.time().hour
        current_booking_minute = booking_to_edit.booking_datetime.time().minute
        new_booking_time = input("Select time in hh:mm format: ")
        new_hour = datetime.strptime(new_booking_time,"%H:%M").time().hour
        new_minute = datetime.strptime(new_booking_time,"%H:%M").time().minute
        if new_hour != current_booking_hour or new_minute != current_booking_minute:
            booking_to_edit.booking_datetime = booking_to_edit.booking_datetime.replace(hour = new_hour,minute = new_minute)
        else:
            pass
        print(booking_to_edit.booking_datetime)
        return
    
    def get_booking(self,player_login_name):
        for booking in self.booking_lst:
            if booking.player_login_name == player_login_name:
                print(booking.__dict__)
                return booking
            return None 



Booking_system = BookingSystem()
Booking_system.make_new_booking('mike')
Booking_system.edit_booking_day('mike')
Booking_system.edit_booking_time('mike')
Booking_system.cancel_booking('mike')



        
    







