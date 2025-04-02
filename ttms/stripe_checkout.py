from flask import url_for
import stripe

def create_stripe_session(booking):
    booking_id = booking.booking_id
    stripe.api_key = 'sk_test_51Qmkf8BaZDAfc4fNRXKFyD47bswWxKHpAHD1QDyy7cv3asinDAYCkFt1Tr3kLIx3A9mhjIgz8hPezzHlXTK7sh5V004fxas5eQ'
    BOOKING_PRICE = 1800 #price in cents
    
    try:
        session = stripe.checkout.Session.create(
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
            success_url=url_for('success', booking_id=booking_id, _external=True),
            cancel_url=url_for('cancel', _external=True),
        )
        return session
    except Exception as e:
        return str(e)
    

def restore_stripe_session(payment):
    stripe_session_id = payment.stripe_session_id
    stripe_session = stripe.checkout.Session.retrieve(stripe_session_id)
    return stripe_session

def obtain_stripe_refund(stripe_session):
    payment_intent_id = stripe_session.payment_intent
    refund = stripe.Refund.create(payment_intent=payment_intent_id)
    if refund:
        display_message_on_page("Your refund is being processed. \
                                 The funds should appear in your account within 5-6 business days. \
                                 Thank you for your patience.", 'success')
        return refund
    else:
        print('Something went wrong when trying to do Stripe refund')

def obtain_refund_for(payment):
    stripe_session = restore_stripe_session(payment)
    return obtain_stripe_refund(stripe_session)



