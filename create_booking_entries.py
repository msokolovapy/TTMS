from app import app, db
from models_booking import Booking
from datetime import datetime, timedelta
import random


# Use the application context
with app.app_context():
    db.create_all()

    player_login_names = ['john', 'jane', 'nick', 'mike', 'robert', 'bill', 
                        'sarah', 'fiona', 'james', 'jojo', 'meredith', 'momo', 'marynich']

    today = datetime.now().date()
    two_months_later = today + timedelta(days=60)
    tuesdays_and_thursdays = []
    current_date = today

    while current_date <= two_months_later:
        if current_date.weekday() in [1, 3]:  # 1 is Tuesday, 3 is Thursday
            tuesdays_and_thursdays.append(current_date)
        current_date += timedelta(days=1)

    # Ensure some dates are repeated exactly 8 times
    repeat_dates = random.sample(tuesdays_and_thursdays, 4)  # Pick 4 date to repeat
    for date in repeat_dates:
        tuesdays_and_thursdays += [date] * 7  # Repeat it 7 additional times (total of 8)

    random.shuffle(tuesdays_and_thursdays)

    bookings = []
    for i in range(30):
        booking_data = {
            'date_time_booking_made': datetime.now(),
            'player_login_name': random.choice(player_login_names),
            'required_booking_date': tuesdays_and_thursdays[i]
        }
        bookings.append(booking_data)

    for booking_data in bookings:
        booking = Booking(
            date_time_booking_made=booking_data['date_time_booking_made'],
            player_login_name=booking_data['player_login_name'],
            required_booking_date=booking_data['required_booking_date']
        )
        db.session.add(booking)

    db.session.commit()


    

