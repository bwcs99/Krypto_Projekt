from zp_group import ZpGroup
import numpy as np


class AVNet:
    """
    Klasa odpowiedzialna za protokół Anononymous Veto Network.
    """

    def __init__(self, group: ZpGroup):
        """
        :param group: ustalona dla protokołu (pojedynczej gry) grupa Z_p
        """
        self.group = group

    def compute_product(self, id, public_keys):
        """
        :param id: id gracza
        :param public_keys: tablica z kluczami publicznymi wszystkich graczy
        :return: iloraz iloczynów kluczy [ozn. g^y] oraz wykładnik y
        """
        p, q = self.group.get_primes()
        subset_1 = public_keys[:id]
        subset_2 = public_keys[(id + 1):]

        if len(subset_1) > 0:
            subproduct_1 = np.product(subset_1)
        else:
            subproduct_1 = 1

        if len(subset_2) > 0:
            subproduct_2 = np.product(subset_2)
        else:
            subproduct_2 = 1

        product = (subproduct_1 / subproduct_2) % p
        if product >= 1:
            product_exponent = self.group.compute_exponent(int(product))
        else:
            product_exponent = - self.group.compute_exponent(int(subproduct_2))
        return product, product_exponent

    def generate_public_answer(self, product_exponent, secret_answer, private_key):
        """
        :param product_exponent: wartość y dla gracza (zwracana przez compute_product)
        :param secret_answer: odpowiedź gracza na pytanie - 0 lub 1 (brak weta lub weto)
        :param private_key: klucz prywatny gracza
        :return: sekretny wykładnik, publiczna odpowiedź gracza, wykładnik odpowiedzi
        """
        p, q = self.group.get_primes()
        g = self.group.get_zp_group_generator()
        if secret_answer == 0:
            exponent = private_key

        else:
            exponent = self.group.get_random_exponent()
            while exponent == private_key:
                exponent = self.group.get_random_exponent()

        exponent_pub_key = (g ** exponent) % p
        answer_exponent = product_exponent * exponent
        return exponent, exponent_pub_key, answer_exponent

    def compute_group_answer(self, public_exponents):
        """
        :param public_answers: tablica z publicznymi wykładnikami y - odpowiedziami gracza (zwracanymi przez generate_public_answer)
        :return: decyzja grupy - 0 jeśli brak weta, 1 jeśli doszło do weta
        """
        p, q = self.group.get_primes()
        g = self.group.get_zp_group_generator()
        total_exponent = np.sum(public_exponents) % q
        product = (g ** total_exponent) % p

        if product == 1:
            return 0
        return 1
