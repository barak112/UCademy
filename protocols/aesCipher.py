import base64
import hashlib
from Cryptodome import Random
from Cryptodome.Cipher import AES


class AESCipher:
    """Provides AES encryption and decryption using CBC mode.

    Uses a SHA-256 hashed key for encryption and decryption, with padding to ensure
    compatibility with AES block size requirements.

    :ivar bs: AES block size (typically 16 bytes).
    :ivar key: SHA-256 hashed key derived from the input key.
    """

    def __init__(self, key):
        """Initialize the AESCipher with a key.

        :param key: The key to use for encryption and decryption.
        """
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        """Encrypt a message using AES-CBC.

        Pads the input, generates a random IV, and returns the IV concatenated with
        the encrypted message, encoded in base64.

        :param raw: The plaintext message to encrypt.
        :return: Base64-encoded encrypted message (IV + ciphertext).
        """
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        """Decrypt a base64-encoded message using AES-CBC.

        Extracts the IV, decrypts the ciphertext, and removes padding.

        :param enc: Base64-encoded encrypted message (IV + ciphertext).
        :return: Decrypted plaintext message.
        """
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        """Pad a string to match the AES block size.

        Adds padding characters based on the required padding length.

        :param s: The string to pad.
        :return: Padded string.
        """
        padding_length = self.bs - len(s) % self.bs
        return s + (padding_length * chr(padding_length))

    @staticmethod
    def _unpad(s):
        """Remove padding from a decrypted string.

        Removes the padding characters based on the last byte's value.

        :param s: The padded string.
        :return: Unpadded string.
        """
        return s[:-ord(s[len(s) - 1:])]

    def encrypt_file(self):
        print("helo")
    
    def decrypt_file(self):
        pass
    
if __name__ == '__main__':
    cry = AESCipher("Barak")
    msg = cry.encrypt("My name is Barak")
    print(msg)
    print(cry.decrypt(msg))
