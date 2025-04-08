from flask import url_for
import stripe
from stripe.error import StripeError as StripeAPIError
from ttms.general_use_functions import display_message_on_page

class StripeSessionWrapper():

    def __init__(self, stripe_session):
        self.stripe_session = stripe_session

    def is_paid_in_full(self):
        if self.stripe_session.payment_status == 'paid':
             return True
        return False

    def __getattr__(self, item):
             return getattr(self.stripe_session, item)


def create_stripe_session_using(booking):
    booking_id = booking.booking_id
    stripe.api_key = 'sk_test_51Qmkf8BaZDAfc4fNRXKFyD47bswWxKHpAHD1QDyy7cv3asinDAYCkFt1Tr3kLIx3A9mhjIgz8hPezzHlXTK7sh5V004fxas5eQ'
    BOOKING_PRICE = 1800 #price in cents
    
    try:
       stripe_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'aud',
                    'product_data': {
                        'name': 'Table Tennis Booking',
                    },
                    'unit_amount': BOOKING_PRICE,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('success', booking_id = booking_id, _external=True),
            cancel_url=url_for('cancel', _external=True),
        )
       return stripe_session
    except StripeAPIError as e:
        return f"Stripe error: {e.user_message} when trying to '{create_stripe_session_using.__name__}'"

    

def restore_stripe_session_using(payment):
    stripe.api_key = 'sk_test_51Qmkf8BaZDAfc4fNRXKFyD47bswWxKHpAHD1QDyy7cv3asinDAYCkFt1Tr3kLIx3A9mhjIgz8hPezzHlXTK7sh5V004fxas5eQ'
    try:
        stripe_session_id = payment.stripe_session_id
        stripe_session = stripe.checkout.Session.retrieve(stripe_session_id)
        wrapped_stripe_session = StripeSessionWrapper(stripe_session)
        return wrapped_stripe_session
    except StripeAPIError as e:
        return f"Stripe error: {e.user_message} when trying to '{restore_stripe_session_using.__name__}'"
        

def obtain_stripe_refund_for(stripe_session):
    try:
        payment_intent_id = stripe_session.payment_intent
        refund = stripe.Refund.create(payment_intent=payment_intent_id)
        display_message_on_page("Your refund is being processed. \
                                 The funds should appear in your account within 5-6 business days. \
                                 Thank you for your patience.", 'success')
        return refund
    except StripeAPIError as e:
        return f"Stripe error: {e.user_message} when trying to '{obtain_stripe_refund_for.__name__}'"

def obtain_refund_for(payment):
    stripe_session = restore_stripe_session_using(payment)
    return obtain_stripe_refund_for(stripe_session)



