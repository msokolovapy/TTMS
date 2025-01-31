from extensions import db
import datetime
from sqlalchemy import func, select
# from app import app




class Booking(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True)
    date_time_booking_made = db.Column(db.String, nullable=False)
    player_login_name = db.Column(db.String, nullable = False)
    required_booking_date = db.Column(db.String, nullable = False)

    payment = db.relationship('Payment', uselist=False, backref='booking')
    

    def __init__(self,date_time_booking_made,player_login_name,required_booking_date):
        self.date_time_booking_made = date_time_booking_made
        self.player_login_name = player_login_name
        self.required_booking_date = required_booking_date

class Payment(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True)
    fk_booking_id = db.Column(db.Integer, db.ForeignKey('booking.booking_id'), nullable=False,unique=True)
    date_time_payment_made = db.Column(db.String)
    payment_status = db.Column(db.String, nullable=False)
    stripe_session_id = db.Column(db.String)


def find_tuesdays_and_thursdays():
    today = datetime.date.today()
    two_months_later = today + datetime.timedelta(days=60)
    current_date = today
    result = []
    
    while current_date <= two_months_later:
        if current_date.weekday() in [1, 3]:  # 1 is Tuesday, 3 is Thursday
            result.append(current_date.strftime("%Y-%m-%d"))
        current_date += datetime.timedelta(days=1)
    
    return set(result)

def find_non_available_bookings():
    ranked_bookings = (
        select(
            func.date(Booking.required_booking_date).label('booking_date'),
            func.row_number().over(partition_by=func.date(Booking.required_booking_date), 
                                order_by=Booking.required_booking_date).label('row_numb')
        )
        .cte('ranked_bookings')  # Create a CTE
    )

    final_query = (
        select(ranked_bookings.c.booking_date)
        .group_by(ranked_bookings.c.booking_date)
        .having(func.max(ranked_bookings.c.row_numb) == 8)
    )

    results = db.session.execute(final_query).fetchall()
    results = {row[0] for row in results}
    return results


def find_available_bookings():
    possible_booking_dates = find_tuesdays_and_thursdays()
    non_available_bookings = find_non_available_bookings()
    available_booking_dates = possible_booking_dates - non_available_bookings
    
    return sorted(list(available_booking_dates))


def retrieve_all_bookings_for_user(user_name):
    existing_bookings_query = (
        select(Booking.required_booking_date)
        .where(Booking.player_login_name == user_name))
    existing_booking_lst = [row[0] for row in db.session.execute(existing_bookings_query).fetchall()]
    return existing_booking_lst

# with app.app_context():
#     Payment.__table__.create(db.engine)



