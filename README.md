TTMS is a simple table tennis management system that allows to:
  * sign up players
  * regularly update player rank based on match results (ELO ranking)
  * store match details and individual ranking in database
  * book/pay for matches using Stripe
  * cancel/refund bookings using Stripe. Refund available if booking cancelled at least 24 hrs prior.

Important:
  * ensure your database location is updated in __init__ file
  * schedule daily running of 'daily_ranking_update.py' to ensure regular player ranking update
  * replace the value of TEST stripe api key in 'stripe_checkout.py' with REAL stripe api key
  * replace greeting in index.html (currently 'Welcome to Tony's Tennis Booking Page!') with your greeting

