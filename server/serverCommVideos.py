import os
import queue

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
    :ivar open_clients: Dictionary mapping client sockets to [ip, cipher] pairs.
    """

    def __init__(self, port, recvQ):
        """
        Initializes the instance with the given port and a queue for receiving data.

        :param port: The communication port to be used by the instance.
        :param recvQ: The queue object used for sending data to the server logic.
        """
        super().__init__(port, recvQ)
        self.idsQ = queue.Queue()

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
                        data = current_socket.recv(int(data_len)).decode()
                    except Exception as e:
                        print("error in comm mainloop -", e)
                        data = ""

                    if not data:
                        self._close_client(current_socket)
                    else:
                        ip, key = self.open_clients[current_socket]
                        print(f"key: {key}, data: {data} in serverCommVideo")
                        decrypted_message = key.decrypt(data)
                        print("msg recved in serverCommVideo:", decrypted_message)
                        self._recv_file(current_socket, decrypted_message)

    def send_file(self, client_ip, file_path, video_id = None, creator = None, video_name=None, video_description=None,
                  created_at = None, likes_amount = None, comments_amount = None, liked = None):
        """
        Send a file to a client after encrypting the file and its metadata.

        This method identifies the client by their IP address, encrypts the file
        content and associated metadata, and sends them over an established
        socket connection. The metadata includes additional details about the
        file such as its video ID, creator, video name, description, creation
        timestamp, likes, comments count, and liked status. If the file does not
        exist, it prints an error message.

        :param client_ip: The IP address of the client to send the file to.
        :param file_path: The path to the file to be sent.
        :param video_id: The unique identifier of the video
        :param creator: The creator of the video
        :param video_name: The name of the video
        :param video_description: A brief description of the video
        :param created_at: A timestamp indicating when the video was created
        :param likes_amount: The number of likes the video has
        :param comments_amount: The number of comments on the video
        :param liked: Whether the video is liked by the user
        """

        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()

            client_socket = self._find_socket_by_ip(client_ip)
            data = self.open_clients[client_socket][1].encrypt_file(data)
            file_name = os.path.basename(file_path)
            file_size = len(data)
            msg = serverProtocol.build_file_details(file_name, file_size, video_id,creator, video_name, video_description,
                                                    created_at, likes_amount, comments_amount, liked)
            encrypted_message = self.open_clients[client_socket][1].encrypt(msg)
            try:
                client_socket.send(str(len(encrypted_message)).zfill(3).encode() + encrypted_message)
                client_socket.send(data)
                #need to add encryption to the file
            except Exception as e:
                print(f"Error sending message: {e}")
                self._close_client(client_socket)

        else:
            print("file does not exist")


    def _recv_file(self, client_socket, decrypted_message):
        """
        Receive and process a file sent by a client socket.

        This method handles the reception of a file from a client, processing its
        metadata, decrypting its contents, and saving it to the proper location based
        on the type of file received (video, thumbnail, etc.). It ensures that the file
        size matches the expected size and takes necessary actions if the size does not
        match, such as closing the client connection.

        :param client_socket: The client socket from which the file is being received.
        :param decrypted_message: The decrypted message containing metadata about the
            file being transferred.
        :return: creates file at assets\\ and if video, puts video_details to recvQ
        """

        client_ip = self.open_clients[client_socket][0]

        opcode, data = serverProtocol.unpack(decrypted_message)

        file_name, file_size, *video_details = data
        file_size = int(file_size)
        print("file_size:", file_size, "file_name:", file_name, "video_details:", video_details)
        file_content = self._recv_file_content(client_socket, file_size)

        file_name, extension = file_name.split(".") # the filename received from the server is filename.extension

        if len(file_content) == file_size:
            file_content = bytearray(self.open_clients[client_socket][1].decrypt_file(file_content)) #  decrypts file content

            # this code assumes that pfp names are strings (the user's name) and video and thumbnail file names are a rnd int
            if file_name.isnumeric():
                if video_details: # if video details is not empty, it means that it is a video
                    self.recvQ.put((client_ip, (file_content, extension, video_details)))

                else: # if file_name is a number but video_details is empty, it is a thumbnail
                    file_name = self.idsQ.get()

            if file_name and not video_details: # id 0 indicates that the video already exists, so to not save the thumbnail
                with open(f"assets\\{file_name}.{extension}", 'wb') as f:
                    f.write(file_content)

        else:
            self._close_client(client_socket)

    @staticmethod
    def _recv_file_content(client_socket, file_size):
        file_content = bytearray()
        while len(file_content) < file_size:
            slice = min(1024, (file_size - len(file_content)))
            try:
                data = client_socket.recv(slice)
            except Exception as e:
                print("Error at receiving file -", e)
                data = ''

            if not data:
                break

            file_content.extend(data)
        return file_content
