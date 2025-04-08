
from ttms.general_use_functions import obtain_info_from_webpage, get_current_date_time,update_database_for,\
                                        display_message_on_page, redirect_to_web_page
from ttms.models_booking import find_payment_using
from ttms.stripe_checkout import restore_stripe_session_using


def check_payment_status_update_database():
    booking_id = obtain_info_from_webpage()
    payment_record = find_payment_using(booking_id)
    online_payment = restore_stripe_session_using(payment_record)
    if online_payment.is_paid_in_full:
         current_date_time = get_current_date_time()
         payment_record.update_with(payment_status = 'paid')
         payment_record.update_with(date = current_date_time)
         update_database_for(payment_record)
         display_message_on_page("Payment successful! Your booking is confirmed.", 'success')
    else:
         display_message_on_page("Booking not paid for. Online payment didn't go through.", 'danger')
    return redirect_to_web_page('user_get')
        
        
