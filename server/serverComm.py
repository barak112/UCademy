import select
import socket
import threading
import aesCipher
import diffieHellman
import settings


class ServerComm:
    """Manages server-sipe communication with multiple clients using encryption.

    Handles client connections, message sending/receiving, and Diffie-Hellman key exchange
    for encrypted communication. Uses a separate thread for the main loop to monitor
    incoming connections and messages.

    :ivar server_socket: Socket for accepting client connections.
    :ivar port: Port number for the server.
    :ivar recvQ: Queue to store received messages.
    :ivar open_clients: Dictionary mapping client sockets to [ip, cipher] pairs.
    """

    def __init__(self, port, recvQ):
        """Initialize the ServerComm object.

        :param port: Port number to bind the server to.
        :param recvQ: Queue to store received messages.
        """
        self.server_socket = socket.socket()
        self.port = port
        self.recvQ = recvQ
        self.open_clients = {}  # [socket] = ip, cipher

        threading.Thread(target=self._mainLoop).start()

    def _mainLoop(self):
        """Continuously monitor for incoming connections and messages.

        Binds the server socket, listens for new client connections, and processes
        incoming messages from connected clients. Places received messages in the queue.
        """
        self.server_socket.bind(("0.0.0.0", self.port))
        self.server_socket.listen(3)

        while True:
            rlist = select.select([self.server_socket] + list(self.open_clients.keys()), [], [], 0.01)[0]
            for current_socket in rlist:
                if current_socket is self.server_socket:
                    client, addr = self.server_socket.accept()

                    if any(ip == addr[0] for ip, _ in self.open_clients.values()):
                        client.close()
                        print("attempted to enter through the same ip")
                    else:
                        print(f"{addr[0]} - connected")
                        # Start a new thread to exchange keys with the new client
                        threading.Thread(target=self._change_key, args=(client, addr[0])).start()

                else:
                    try:
                        data_len = current_socket.recv(3).decode()
                        data = current_socket.recv(int(data_len))
                    except Exception as e:
                        print("error in comm mainloop -", e)
                        data = ""

                    if not data:
                        self._close_client(current_socket)
                    else:
                        ip, key = self.open_clients[current_socket]
                        decrypted_message = key.decrypt(data)
                        print("decrypted:", decrypted_message)
                        self.recvQ.put((ip, decrypted_message))  # Push received data into the queue

    def _change_key(self, client_soc, client_ip):
        """Perform Diffie-Hellman key exchange with a client.

        Generates a public key, sends it to the client, receives the client's public key,
        and establishes a shared key for AES encryption.

        :param client_soc: Client socket for communication.
        :param client_ip: Unique ip assigned to the client.
        """
        diffie_hellman = diffieHellman.DiffieHellman()
        public_key = diffie_hellman.get_public_key()

        try:
            client_soc.send(str(public_key).zfill(settings.P_SIZE).encode())
            client_public_key = int(client_soc.recv(settings.P_SIZE).decode())
        except Exception as e:
            print(f"Error in key recv: {e}")
            client_public_key = ""

        if not client_public_key:
            self._close_client(client_soc)
        else:
            shared_key = diffie_hellman.generate_shared_key(client_public_key)
            self.open_clients[client_soc] = [client_ip, aesCipher.AESCipher(str(shared_key))]

    def _close_client(self, client_soc):
        """Close a client connection and notify the logic.

        :param client_soc: Client socket to close.
        """
        if client_soc in self.open_clients.keys():
            print(f"{self.open_clients[client_soc]} - disconnected")
            self.recvQ.put((self.open_clients[client_soc][0], '3'))  # Notify logic a player has left
            del self.open_clients[client_soc]
            client_soc.close()

    def _find_socket_by_ip(self, client_ip):
        """Find a client socket by its ip.

        :param client_ip: ip of the client to find.
        :return: Client socket if found, None otherwise.
        """
        soc = None
        for sock in self.open_clients.keys():
            if self.open_clients[sock][0] == client_ip:
                soc = sock
                break
        return soc

    def send_msg(self, client_ip, msg):
        """Send an encrypted message to a specific client.

        :param client_ip: ip of the client to send the message to.
        :param msg: Message to send.
        """
        client_soc = self._find_socket_by_ip(client_ip)
        if client_soc:
            encrypted_message = self.open_clients[client_soc][1].encrypt(msg)
            msg = str(len(encrypted_message)).zfill(3).encode() + encrypted_message
            try:
                client_soc.send(msg)
            except Exception as e:
                print(f"Error sending message: {e}")
                self._close_client(client_soc)

    def send_multiple_clients(self, msg, clients_ips, except_clients=None):
        """Send an encrypted message to multiple clients.

        :param msg: Message to send.
        :param clients_ips: List of client ips to send the message to.
        :param except_clients: List of client ips to exclude from sending (default: None).
        """
        if except_clients is None:
            except_clients = []
        send_list = list(set(clients_ips) - set(except_clients))
        for ip in send_list:
            self.send(ip, msg)



