# users.py
from flask import request, session, redirect
from ttms.models_booking import create_booking_for,\
                                find_booking_using, find_available_bookings,\
                                retrieve_all_bookings_for_user, format_dates_for_display, find_payment_using
from ttms.general_use_functions import update_database_for,format_,check_,delete_from_database, \
                                       commit_changes_to_database, display_message_on_page,\
                                       redirect_to_web_page, obtain_info_from_session, obtain_info_from_webpage, \
                                       build_web_page
from ttms.stripe_checkout import obtain_refund_for, create_stripe_session_using


def not_OK_to_proceed():
    ok_to_proceed = check_(session)
    if ok_to_proceed:
       return False
    return True 

def create_booking_and_store_in_database(user_data, date):
    new_booking = create_booking_for(user_data, date)
    update_database_for(new_booking)
    new_booking_id = new_booking.booking_id
    new_booking.associat_payment.update_with(booking_id = new_booking_id)
    update_database_for(new_booking.associat_payment)
    return new_booking


# def make_payment_and_store_in_database():
#     online_payment = create_stripe_session(new_booking)
#     new_payment.update_with(online_payment.id)
#     commit_changes_to_database()
#     display_message_on_page(f"You are booked for {format_(date)}.\
#                      See you there!",'success') 
#     return redirect(online_payment.url, code=303) 

def find_booking_and_check_refund_eligibility_for(user_name, date):
    booking = find_booking_using(user_name, date)
    if booking.not_eligible_for_refund:
                 display_message_on_page("Refund not available: Cancellations must be made at least 24 hours prior to the booking date. \
                        Unfortunately, your cancellation was made too late.", 'danger')
                 return booking
    else:
        return booking


def delete_(payment, booking):
    date = booking.required_booking_date
    delete_from_database(payment)
    delete_from_database(booking)
    display_message_on_page(f"Booking on {format_(date)} cancelled successfully.",'success')
    return commit_changes_to_database()



def obtain_info_and_load_page():
    function_name = request.endpoint
    if function_name == 'users_get':
        if not_OK_to_proceed():
             return redirect_to_web_page('login')
        name, rank = obtain_info_from_session()
        available_booking_days = find_available_bookings(name)
        all_user_bookings = retrieve_all_bookings_for_user(name)
        available_booking_days = format_dates_for_display(available_booking_days)
        all_user_bookings = format_dates_for_display(all_user_bookings)         
        return build_web_page('user', 
                           all_available_bookings_period_60_days = available_booking_days,
                           available_user_booking = all_user_bookings,
                           user_name = name, 
                           player_rank = rank) 


def make_or_delete_booking():
     user_data = obtain_info_from_session() 
     date, user_intent = obtain_info_from_webpage()
     ok_to_proceed = check_(date = date) 
     if not ok_to_proceed:
         display_message_on_page('No booking made!','danger')
     else:
        if user_intent == 'new_booking':
            booking = create_booking_and_store_in_database(user_data, date)
            online_payment = create_stripe_session_using(booking)
            booking.associat_payment.update_with(online_payment_id=online_payment.id)
            commit_changes_to_database()
            display_message_on_page(f"You are booked for {format_(date)}.\
#                                     See you there!",'success')
            return redirect(online_payment.url, code=303)
        elif user_intent == 'delete_booking':
            booking = find_booking_and_check_refund_eligibility_for(user_data, date) 
            payment = find_payment_using(booking) 
            obtain_refund_for(payment)
            delete_(payment,booking)
            return redirect_to_web_page('users')


  