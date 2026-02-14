import os

import select
import socket
import threading
import aesCipher
import diffieHellman
import serverComm
import serverProtocol
import settings

class ServerCommVideos (serverComm.ServerComm):
    """Manages server-sipe communication with multiple clients using encryption.

    Handles client connections, message sending/receiving, and Diffie-Hellman key exchange
    for encrypted communication. Uses a separate thread for the main loop to monitor
    incoming connections and messages.

    :ivar server_socket: Socket for accepting client connections.
    :ivar port: Port number for the server.
    :ivar recvQ: Queue to store received messages.
    :ivar open_clients: Dictionary mapping client sockets to [ip, cipher] pairs.
    """

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
                        data_len = current_socket.recv(2).decode()
                        data = current_socket.recv(int(data_len)).decode()
                    except Exception as e:
                        print("error in comm mainloop -", e)
                        data = ""

                    if not data:
                        self._close_client(current_socket)
                    else:
                        ip, key = self.open_clients[current_socket]
                        decrypted_message = key.decrypt(data)

                        file_size, file_name = serverProtocol.unpack(decrypted_message)
                        self._recv_file(current_socket,file_size, file_name)

    def send_msg(self, client_ip, msg):
        """Send an encrypted message to a specific client.

        :param client_ip: ip of the client to send the message to.
        :param msg: Message to send.
        """
        client_soc = self._find_socket_by_ip(client_ip)
        if client_soc:
            encrypted_message = self.open_clients[client_soc][1].encrypt(msg)
            msg = str(len(encrypted_message)).zfill(2).encode() + encrypted_message
            try:
                client_soc.send(msg)
            except Exception as e:
                print(f"Error sending message: {e}")
                self._close_client(client_soc)


    def send_file(self, client_ip, file_path):
        """
            sends a file to the server
        :param file_path: file path to the file to be sent
        :return: file sent to server
        """
        # currently, the logic has to send send_msg with the file size and name.
        # if merry allows it, i will make it so this func uses clientProtocol to create the msg and send it herself

        with open(file_path, 'rb') as f:
            data = f.read()

        client_socket = self._find_socket_by_ip(client_ip)

        data = self.open_clients[client_socket][1].encrypt_file(data)
        msg = serverProtocol.build_command(0, [os.path.basename(file_path), len(data)])
        encrypted_message = self.open_clients[client_socket][1].encrypt(msg)
        #  0100.png@#1000000000
        # max size: max(usename, video_id) + video_size : 15+10 = 25 bytes
        try:
            client_socket.send(str(len(msg)).zfill(2).encode() + encrypted_message)
            client_socket.send(data)
        except Exception as e:
            print(f"Error sending message: {e}")


    def _recv_file(self, client_socket, file_size, file_name):
        """
            recvs file send from the server and saves it at assets//``file_name``
        :param file_size: size of the file that needs to be received
        :param file_name: the name and extension of file to be received
        :return: returns whether the recv was successful
        """
        saved_file = True
        file_content = bytearray()
        while len(file_content) < file_size:
            slice = min(1024, (file_size - len(file_content)))
            try:
                data = client_socket.recv(slice)
            except Exception as e:
                print("Error at receiving file -", e)
                data = ''

            if not data:
                saved_file = False
                break

            file_content.extend(data)

        if len(file_content) == file_size:
            with open(f"assets\\{file_name}", 'wb') as f:
                f.write(self.open_clients[client_socket][1].decrypt_file(file_content))
        else:
            self._close_client(client_socket)

        return saved_file
