from sympy import randprime, isprime
from random import randint


class ZpGroup:

    """
    Klasa reprezentująca grupę Z_p, gdzie p jest liczbą pierwszą postaci p = 2q + 1 (q jest pierwsza).
    """
    def __init__(self, nq):
        self.nq = nq

        self.p = None
        self.q = None

        self.zp_group = None
        self.group_generator = None

    """
    Funkcja do obliczania rzędu elementu grupy Z_p
    """
    def compute_element_order(self, element):
        order = 1

        while int(pow(element, order, self.p)) != 1:
            order += 1

        return order

    """
    Funkcja do generowania grupy Z_p i wybierania generatora
    """
    def generate_zp_group(self):
        q = randprime(2 ** self.nq, 2 ** (self.nq + 1))
        p = 2 * q + 1

        while not isprime(p):
            q = randprime(2 ** self.nq, 2 ** (self.nq + 1))
            p = 2 * q + 1

        self.p = p

        self.group_generator = randint(int(p / 2), p - 1)
        self.zp_group = {i for i in range(1, p)}

    """
    Funkcja do generowania grupy Z_q z dodawaniem jako działanie (q jest pierwsze)
    """
    def generate_zq_group(self):
        return {i for i in range(1, self.q)}

    """
    Funkcja pomocnicza - zwraca używane liczby pierwsze p i q
    """
    def get_primes(self):
        return self.p, self.q

    """
    Funkcja do generowania podgrup dla danego elementu grupy
    """
    def generate_subgroup(self, element):
        element_order = self.compute_element_order(element)

        return {int(pow(element, i, self.p)) for i in range(1, element_order + 1)}

    """
    Funkcja zwracająca generator grupy
    """
    def get_zp_group_generator(self):
        return self.group_generator

    """
    Funkcja zwracająca grupę Z_p
    """
    def get_zp_group(self):
        return self.zp_group


# testy
if __name__ == "__main__":
    zp_class = ZpGroup(15)

    zp_class.generate_zp_group()

    generator = zp_class.get_zp_group_generator()
    group = zp_class.get_zp_group()

    generator_order = zp_class.compute_element_order(generator)

    subgroup = zp_class.generate_subgroup(generator)

    print(f'Generator: {generator}')
    print(f'p : {zp_class.p}')
    print(f'Generator order: {generator_order}')
    print(f'Subgroup cardinality: {len(subgroup)}')
    print(f'Subgroup: {subgroup}')
