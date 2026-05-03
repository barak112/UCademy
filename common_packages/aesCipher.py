import base64
import hashlib
from Cryptodome import Random
from Cryptodome.Cipher import AES


class AESCipher:
    """Provides AES encryption and decryption using CBC mode.

    Uses a SHA-256 hashed key for encryption and decryption, with PKCS#7 padding
    applied at the byte level to correctly handle all Unicode characters.

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

        Encodes the input to UTF-8 bytes first, then applies PKCS#7 padding,
        generates a random IV, and returns the IV concatenated with the encrypted
        message, encoded in base64.

        :param raw: The plaintext message to encrypt (supports all Unicode).
        :return: Base64-encoded encrypted message (IV + ciphertext).
        """
        raw_bytes = raw.encode('utf-8')
        padding_length = self.bs - (len(raw_bytes) % self.bs)
        padded = raw_bytes + bytes([padding_length]) * padding_length

        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(padded))


    def decrypt(self, enc):
        """Decrypt a base64-encoded message using AES-CBC.

        Extracts the IV, decrypts the ciphertext, removes PKCS#7 padding,
        and decodes the result as UTF-8.

        :param enc: Base64-encoded encrypted message (IV + ciphertext).
        :return: Decrypted plaintext message.
        """
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        padded = cipher.decrypt(enc[AES.block_size:])
        padding_length = padded[-1]
        return padded[:-padding_length].decode('utf-8')

    def encrypt_file(self, raw_bytes):
        """Encrypt file content bytes using AES-CBC.

        Uses PKCS#7 padding so arbitrary file sizes can be encrypted.

        :param raw_bytes: File content bytes to encrypt.
        :return: Raw encrypted payload as bytes (IV + ciphertext).
        :raises TypeError: If ``raw_bytes`` is not bytes-like.
        """
        if not isinstance(raw_bytes, (bytes, bytearray)):
            raise TypeError("raw_bytes must be bytes-like")

        file_data = bytes(raw_bytes)
        padding_length = self.bs - (len(file_data) % self.bs)
        padded_data = file_data + bytes([padding_length]) * padding_length

        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(padded_data)

    def decrypt_file(self, enc_bytes):
        """Decrypt AES-CBC encrypted file content.

        Expects a payload formatted as ``IV + ciphertext`` and removes PKCS#7
        padding after decryption.

        :param enc_bytes: Encrypted bytes (IV + ciphertext).
        :return: Original decrypted file bytes.
        :raises TypeError: If ``enc_bytes`` is not bytes-like.
        :raises ValueError: If payload size or padding is invalid.
        """
        if not isinstance(enc_bytes, (bytes, bytearray)):
            raise TypeError("enc_bytes must be bytes-like")

        encrypted_data = bytes(enc_bytes)
        if len(encrypted_data) < AES.block_size * 2:
            raise ValueError("Encrypted data is too short")

        ciphertext = encrypted_data[AES.block_size:]
        if len(ciphertext) % self.bs != 0:
            raise ValueError("Ciphertext length must be a multiple of block size")

        iv = encrypted_data[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded_data = cipher.decrypt(ciphertext)

        padding_length = padded_data[-1]
        if padding_length < 1 or padding_length > self.bs:
            raise ValueError("Invalid padding length")
        if padded_data[-padding_length:] != bytes([padding_length]) * padding_length:
            raise ValueError("Invalid PKCS#7 padding")

        return padded_data[:-padding_length]


if __name__ == '__main__':
    cry = AESCipher("BARAK")

    # ASCII
    msg = cry.encrypt("My name is Barak")
    print(cry.decrypt(msg))

    # Hebrew
    msg2 = cry.encrypt("שלום עולם")
    print(cry.decrypt(msg2))

    # Emoji
    msg3 = cry.encrypt("Hello 🌍!")
    print(cry.decrypt(msg3))
