from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class UserThrottle(UserRateThrottle):
    scope = 'user'

class AnonThrottle(AnonRateThrottle):
    scope = 'anon'

class OrderUserThrottle(UserRateThrottle):
    scope = 'order_user'    

class OrderAnonThrottle(AnonRateThrottle):
    scope = 'order_anon'

class PaymentUserThrottle(UserRateThrottle):
    scope = 'payment_user'