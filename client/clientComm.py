import threading
import socket
import queue
import settings
import aesCipher
import diffieHellman


class ClientComm:
    """Manages client-server communication with encryption.

    Handles connection to the server, sending and receiving encrypted messages,
    and key exchange using Diffie-Hellman. Uses a separate thread for listening
    to incoming messages.

    :ivar client: Client object associated with this communication.
    :ivar my_socket: Socket for server communication.
    :ivar server_ip: IP address of the server.
    :ivar port: Port number for the server connection.
    :ivar recvQ: Queue to store received messages.
    :ivar cipher: AESCipher object for message encryption/decryption.
    """

    def __init__(self, client, server_ip, port, recvQ):
        """Initialize the ClientComm object.

        :param client: Client object associated with this communication.
        :param server_ip: IP address of the server.
        :param port: Port number to connect to.
        :param recvQ: Queue to store received messages.
        """
        self.client = client
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = server_ip
        self.port = port
        self.recvQ = recvQ
        self.cipher = None
        self.closed = False

    def connect(self):
        """Establish a connection to the server and start listening for messages.

        Connects to the server, performs key exchange, and starts a separate thread
        to listen for incoming messages.
        """
        try:
            self.my_socket.connect((self.server_ip, self.port))
            print(f"Connected to server at {self.server_ip}:{self.port}")
        except Exception as e: 
            print(f"Connection error: {e}")
            self._close_client_at_connection()

        self._change_key()

        # Start listening for incoming messages in a separate thread
        threading.Thread(target=self._mainLoop, daemon=True).start()

    def _mainLoop(self):
        """Continuously listen for incoming messages from the server.

        Receives encrypted messages, decrypts them, and places them in the receive queue.
        Closes the client on connection errors or empty messages.
        """
        while not self.closed:
            data = ""
            try:
                data_len = int(self.my_socket.recv(3).decode())
                data = self.my_socket.recv(data_len).decode()
            except Exception as e:
                print(f"Error in mainLoop: {e}")
                self._close_client()

            if not data:
                self._close_client()
            else:
                msg = self.cipher.decrypt(data)
                self.recvQ.put(msg)  # Push received data into the queue

    def _close_client(self):
        """Close the client connection.

        Triggers the client's quit method to handle cleanup.
        """
        if not self.closed:
            self.client.quit()

    def _close_client_at_connection(self):
        """Closes client when failing to connect to server
            closes client and exits
        """
        self.my_socket.close()
        exit()

    def close_client(self):
        """Close the socket connection to the server."""
        self.my_socket.close()
        self.closed = True
        print("Connection closed.")

    def _change_key(self):
        """Perform Diffie-Hellman key exchange to establish encryption.

        Generates a public key, sends it to the server, receives the server's public key,
        and creates a shared key for AES encryption.
        """
        diffie_hellman = diffieHellman.DiffieHellman()
        public_key = diffie_hellman.get_public_key()

        try:
            self.my_socket.send(str(public_key).zfill(settings.P_SIZE).encode())
            server_public_key = int(self.my_socket.recv(settings.P_SIZE).decode())
        except Exception as e:
            print(f"Error in key recv: {e}")
            server_public_key = ""

        if not server_public_key:
            self._close_client_at_connection()

        shared_key = diffie_hellman.generate_shared_key(server_public_key)
        self.cipher = aesCipher.AESCipher(str(shared_key))

    def send_msg(self, msg):
        """Send an encrypted message to the server.

        :param msg: Message to send.
        """
        msg = self.cipher.encrypt(msg)
        try:
            self.my_socket.send(str(len(msg)).zfill(3).encode() + msg)
        except Exception as e:
            print(f"Error sending message: {e}")


    def send_file(self, file_path):
        #currently, the logic has to send send_msg with the file info.
        #if merry allows it, i will make it so this func uses clientProtocol to create the msg and send it herself

        with open(file_path, 'rb') as f:
            data = f.read()

        data = self.cipher.encrypt_file(data)

        try:
            self.my_socket.send(str(len(msg)).zfill(10).encode() + data)
        except Exception as e:
            print(f"Error sending message: {e}")

    def recv_file(self):
        pass

if __name__ == "__main__":
    recvQ = queue.Queue()
    client = ClientComm("127.0.0.1", 1000, recvQ)
    time.sleep(1)
    client.send("hello world")
