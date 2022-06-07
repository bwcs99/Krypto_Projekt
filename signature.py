class Signature:

    def __init__(self, message_to_sign, prime_order_group):
        self.message_to_sign = message_to_sign
        self.prime_order_group = prime_order_group

    def generate_key(self):
        pass

    def sign_message(self):
        pass

    def verify_message(self):
        pass