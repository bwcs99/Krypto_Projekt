from sympy import randprime, isprime
from random import randint


class ZpGroup:
    '''
    Klasa grupy Z_p, gdzie p = 2q + 1; p,q - pierwsze.
    '''

    def __init__(self, g=None, p=None, q=None):
        '''
        Rozważamy dwa przypadki:
        - odtworzenie grupy o znanych p,q,g,
        - utworzenie grupy 'od zera', wraz z generowaniem p,q i g.
        :param g: generator grupy
        :param p: liczba pierwsza
        :param q: liczba pierwsza
        '''
        if (p is not None) and (q is not None):
            self.p = p
            self.q = q
            if (g is not None):
                self.group_generator = g
            else:
                self.group_generator = randint(int(p / 2), p - 1)
        else:
            self.p = None
            self.q = None
            self.group_generator = None

    def compute_element_order(self, element):
        """
        :param element: element grupy Z_p
        :return: rząd elementu w grupie Z_p
        """
        order = 1

        while int(pow(element, order, self.p)) != 1:
            order += 1

        return order

    def divide(self, element_1, element_2):
        element_2_inverse = self.inverse_element(element_2)
        return (element_1 * element_2_inverse) % self.p

    def inverse_element(self, element):
        return pow(element, -1, self.p)

    def generate_zp_group(self, nq):
        """
        Generowanie grupy (p,q,g) w przypadku, gdy p,q,g nie były dane w konstruktorze.
        :param nq: parametr określający rząd wielkości q
        """
        q = randprime(2 ** nq, 2 ** (nq + 1))
        p = 2 * q + 1

        while not isprime(p):
            q = randprime(2 ** nq, 2 ** (nq + 1))
            p = 2 * q + 1

        self.p = p
        self.q = q

        g = 2
        while self.compute_element_order(g) != q:
            r = randint(2, 2 * q - 1)
            g = r ** 2 % p

        self.group_generator = g

    def get_primes(self):
        """
        :return: p,q grupy Z_p
        """
        return self.p, self.q

    def get_zp_group_generator(self):
        """
        :return: g - generator grupy Z_p
        """
        return self.group_generator

    def get_random_exponent(self):
        """
        :return: losowy wykładnik - element grupy Z_q
        """
        return randint(1, self.q)
