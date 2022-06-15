from zp_group import ZpGroup
from hashlib import sha256
import sys


class SchnorrScheme:
    """
    Nieinteraktywny protokół Schnorra
    """

    def __init__(self, group: ZpGroup, hash_func=sha256):
        """
        :param group: ustalona grupa Z_p
        :param hash_func: ustalona funkcja haszująca
        """
        self.group = group
        self.hash_func = hash_func

    def get_key(self):
        """
        :return: klucz prywatny (wykładnik), klucz publiczny
        """
        p, q = self.group.get_primes()
        private_key = self.group.get_random_exponent()
        generator = self.group.get_zp_group_generator()
        public_key = (generator ** private_key) % p

        return private_key, public_key

    def sign(self, private_key, public_key):
        """
        :param private_key: klucz prywatny
        :param public_key: klucz publiczny
        :return: podpis: u, c, z
        """
        p, q = self.group.get_primes()
        r = self.group.get_random_exponent()
        g = self.group.get_zp_group_generator()
        u = g ** r

        message_to_hash = bytes(f"{g}{public_key}{u}", "utf-8")

        message_hash = self.hash_func()
        message_hash.update(message_to_hash)

        c = message_hash.hexdigest()

        c = int(c, 16)

        c_q = c % q
        z = (r + c_q * private_key)
        signature = (u, c, z)

        return signature

    def verify(self, public_key, signature):
        """
        :param public_key:
        :param signature:
        :return: 1 jeśli podpis jest poprawny, 0 w przeciwnym przypadku
        """
        p, q = self.group.get_primes()
        g = self.group.get_zp_group_generator()
        u, c, z = signature

        message_to_hash = bytes(f"{g}{public_key}{u}", "utf-8")

        message_hash = self.hash_func()
        message_hash.update(message_to_hash)
        c_v = message_hash.hexdigest()
        c_v = int(c_v, 16)

        c_v_q = c_v % q
        gz = (g ** z) % p
        gz_v = (u * (public_key ** c_v_q)) % p

        if (c_v == c) and (gz == gz_v):
            return 1
        else:
            return 0
