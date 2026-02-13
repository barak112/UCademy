import secrets
import settings


class DiffieHellman:
    """Implements Diffie-Hellman key exchange for secure shared key generation.

    Generates a private-public key pair and computes a shared key with another party's public key.

    :ivar private_key: Randomly generated private key (1 ≤ private_key ≤ p-1).
    :ivar public_key: Public key computed as g^private_key mod p.
    """

    def __init__(self):
        """Initialize the DiffieHellman object with a private-public key pair.

        Uses parameters from settings (P: prime modulus, G: generator).
        """
        self.private_key = secrets.randbelow(settings.P - 2) + 1  # 1 ≤ a ≤ p-1
        self.public_key = pow(settings.G, self.private_key, settings.P)

    def get_public_key(self):
        """Retrieve the public key.

        :return: The public key (g^private_key mod p).
        """
        return self.public_key

    def generate_shared_key(self, other_public_code):
        """Generate a shared key using another party's public key.

        Computes (other_public_code)^private_key mod p.

        :param other_public_code: The other party's public key.
        :return: The shared key.
        """
        shared_code = pow(int(other_public_code), self.private_key, settings.P)
        return shared_code


if __name__ == '__main__':
    diffi = DiffieHellman()
    person1 = diffi.get_public_key()

    diffi2 = DiffieHellman()
    person2 = diffi2.get_public_key()

    person1_calculate = diffi.generate_shared_key(person2)
    person2_calculate = diffi2.generate_shared_key(person1)

    print(person2_calculate, person2_calculate)
    print(person1_calculate == person2_calculate)
