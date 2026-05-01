import os
import queue

import select
import threading

from typing_extensions import override

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

    def __init__(self, port, recvQ, client_ip):
        """
        Initializes the instance with the given port and a queue for receiving data.

        :param port: The communication port to be used by the instance.
        :param recvQ: The queue object used for sending data to the server logic.
        """
        super().__init__(port, recvQ)
        self.idsQ = queue.Queue()
        self.client_socket = None
        self.client_ip = client_ip
        self.client_cipher = None

    # def _mainLoop(self):
    #     """Continuously monitor for incoming connections and messages.
    #
    #     Binds the server socket, listens for new client connections, and processes
    #     incoming messages from connected clients. Places received messages in the queue.
    #     """
    #     self.server_socket.bind(("0.0.0.0", self.port))
    #     self.server_socket.listen(3)
    #     #todo make for only one client
    #     while True:
    #         rlist = select.select([self.server_socket] + list(self.open_clients.keys()), [], [], 0.01)[0]
    #         for current_socket in rlist:
    #             if current_socket is self.server_socket:
    #                 client, addr = self.server_socket.accept()
    #
    #
    #                 if any(ip == addr[0] for ip, _ in self.open_clients.values()):
    #                     client.close()
    #                     print("attempted to enter through the same ip")
    #                 else:
    #                     print(f"{addr[0]} - connected")
    #                     # Start a new thread to exchange keys with the new client
    #                     threading.Thread(target=self._change_key, args=(client, addr[0])).start()
    #
    #             else:
    #                 try:
    #                     data_len = current_socket.recv(settings.MESSAGE_LENGTH_LENGTH).decode()
    #                     data = current_socket.recv(int(data_len)).decode()
    #                 except Exception as e:
    #                     print("error in comm mainloop -", e)
    #                     data = ""
    #
    #                 if not data:
    #                     self._close_client(current_socket)
    #                 else:
    #                     ip, key = self.open_clients[current_socket]
    #                     print(f"key: {key}, data: {data} in serverCommVideo")
    #                     decrypted_message = key.decrypt(data)
    #                     print("msg recved in serverCommVideo:", decrypted_message)
    #
    #                     if serverProtocol.is_file(decrypted_message):
    #                         self._recv_file(current_socket, decrypted_message)
    #                     else: # if not a file, put in recvQ, its video details
    #                         self.recvQ.put((ip, decrypted_message))

    # for a single client, still is a thread
    def _mainLoop(self):
        self.server_socket.bind(("0.0.0.0", self.port))
        self.server_socket.listen(1)

        while True:
            client_socket, addr = self.server_socket.accept()
            if addr[0] == self.client_ip:
                break
            client_socket.close()

        self.client_socket = client_socket

        # only one client, so no need for thread
        self._change_key(self.client_socket, self.client_ip)

        self.client_cipher = self.open_clients[self.client_socket][1]

        # send the user its pfp, notify logic that the client has connected to its servercommvideos
        self.recvQ.put((self.client_ip, "19"))

        while True:
            try:
                data_len = self.client_socket.recv(settings.MESSAGE_LENGTH_LENGTH).decode()
                data = self.client_socket.recv(int(data_len)).decode()
            except Exception as e:
                print("error in video comm mainloop -", e)
                data = ""

            if not data:
                self._close_client(self.client_socket)
                break
            else:
                decrypted_message = self.client_cipher.decrypt(data)
                if serverProtocol.is_file(decrypted_message):
                    self._recv_file(decrypted_message)
                else:
                    self.recvQ.put((self.client_ip, decrypted_message))

    def send_file(self, file_path):
        """
        Send a file to a client after encrypting the file.
        """

        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()

            data = self.client_cipher.encrypt_file(data)
            file_name = os.path.basename(file_path)
            file_size = len(data)
            msg = serverProtocol.build_file_details(file_name, file_size)
            encrypted_message = self.client_cipher.encrypt(msg)
            try:
                self.client_socket.send(str(len(encrypted_message)).zfill(settings.MESSAGE_LENGTH_LENGTH).encode() + encrypted_message)
                self.client_socket.send(data)
            except Exception as e:
                print(f"Error sending message: {e}")
                self._close_client(self.client_socket)

        else:
            print("file does not exist")


    def _recv_file(self, decrypted_message):
        """
        Receive and process a file sent by a client socket.

        This method handles the reception of a file from a client, decrypting its contents,
         and saving it to the proper location based on the type of file received (video, thumbnail, pfp). It ensures that the file
        size matches the expected size and takes necessary actions if the size does not
        match, such as closing the client connection.

        :param decrypted_message: The decrypted message containing metadata about the
            file being transferred.
        :return: creates file at media\\videos if video or thumbnail and media\\pfps if pfp
        """

        opcode, data = serverProtocol.unpack(decrypted_message)

        #todo get details, add to db, add to queue the id twice (once for video and once for thumbnail)
        # and then when video and thumbnail arrives, assign id to video and thumbnail
        # check if video is valid, if is, store it, if not, delete from db using the id.

        file_name, file_size, *video_details = data
        file_size = int(file_size)
        print("file_size:", file_size, "file_name:", file_name, "video_details:", video_details)
        file_content = self._recv_file_content(file_size)

        file_name, extension = file_name.split(".") # the filename received from the server is filename.extension

        if len(file_content) == file_size:
            file_content = bytearray(self.client_cipher.decrypt_file(file_content)) #  decrypts file content


            # this code assumes that pfp names are strings (the user's name) and video and thumbnail file names are a rnd int
            file_path = "media\\pfps"
            if file_name.isnumeric():
                file_path = "media\\videos"
                if video_details: # if video details is not empty, it means that it is a video
                    self.recvQ.put((self.client_ip, (file_content, extension, video_details))) # sending file content with details to logic

                else: # if file_name is a number but video_details is empty, it is a thumbnail
                    file_name = self.idsQ.get()

            if file_name and not video_details: # id 0 indicates that the video already exists, so to not save the thumbnail
                with open(f"{file_path}\\{file_name}.{extension}", 'wb') as f:
                    f.write(file_content)

            if isinstance(file_name, str): # if filename is a str, it means the file is a pfp, so send user its pfp
                self.recvQ.put((self.client_ip, "19"))

        else:
            self._close_client(self.client_socket)

    def _recv_file_content(self, file_size):
        file_content = bytearray()
        while len(file_content) < file_size:
            slice = min(1024, (file_size - len(file_content)))
            try:
                data = self.client_socket.recv(slice)
            except Exception as e:
                print("Error at receiving file -", e)
                data = b''

            if not data:
                break

            file_content.extend(data)
        return file_content
