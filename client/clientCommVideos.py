import os.path

import clientComm
import clientProtocol


class ClientCommVideos (clientComm.ClientComm):

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
                print(data_len, msg)
                if clientProtocol.is_video(msg):
                    self._recv_file(msg)
                else:
                    self.recvQ.put(msg)  # Push received data into the queue

    def send_file(self, file_path, video_name=None, video_description=None, test_link=None):
        """
            sends a file to the server
        :param file_path: file path to the file to be sent
        :return: file sent to server
        """

        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()

            data = self.cipher.encrypt_file(data)
            file_name = os.path.basename(file_path)
            file_size = len(data)
            msg = clientProtocol.build_file_details(file_name, file_size, video_name, video_description, test_link)
            encrypted_message = self.cipher.encrypt(msg)

            #  0100.png@#1000000000@#name@#desc@#link
            # max size: max(usename, video_id) + video_size : 15+10 = 25 bytes
            try:
                self.my_socket.send(str(len(encrypted_message)).zfill(3).encode() + encrypted_message) # sends len and content of len and filename
                self.my_socket.send(data)
            except Exception as e:
                print(f"Error sending message: {e}")
        else:
            print("file does not exist")


    def _recv_file(self, msg):
        """
            recvs file send from the server and saves it at media//``file_name``
        :param file_size: size of the file that needs to be received
        :param file_name: the name and extension of file to be received
        :return: returns whether the recv was successful
        """
        # called by handle_save_file in logic
        opcode, data = clientProtocol.unpack(msg)
        file_name, file_size, *video_details = data
        file_size = int(file_size)
        file_content = self._recv_file_content(file_size)

        if len(file_content) == file_size:
            with open(f"media\\{file_name}", 'wb') as f:
                f.write(self.cipher.decrypt_file(file_content))

            if video_details:
                arrived_with_video = False
                file_extension = file_name.split('.')[1]
                if file_extension != 'png': # then it is a video
                    arrived_with_video = True
                video_details.append(arrived_with_video)
                print("arrived with a video:",arrived_with_video)
                self.recvQ.put(video_details)

        else:
            self._close_client()

    def _recv_file_content(self, file_size):
        file_content = bytearray()
        while len(file_content) < file_size:
            slice = min(1024, (file_size - len(file_content)))
            try:
                data = self.my_socket.recv(slice)
            except Exception as e:
                print("Error at receiving file -", e)
                data = ''

            if not data:
                break

            file_content.extend(data)
        return file_content
