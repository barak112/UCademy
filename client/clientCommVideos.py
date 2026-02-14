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

                data_len = int(self.my_socket.recv(2).decode())
                data = self.my_socket.recv(data_len).decode()

            except Exception as e:
                print(f"Error in mainLoop: {e}")
                self._close_client()

            if not data:
                self._close_client()
            else:
                msg = self.cipher.decrypt(data)
                if msg[0] == 0:
                    file_size, file_name = clientProtocol.unpack(data)
                    self._recv_file(file_size, file_name)
                else:
                    self.recvQ.put(msg)  # Push received data into the queue

    def send_file(self, file_path):
        """
            sends a file to the server
        :param file_path: file path to the file to be sent
        :return: file sent to serverd
        """
        # not relevant anymore:
        # currently, the logic has to send send_msg with the file size and name.
        # if merry allows it, i will make it so this func uses clientProtocol to create the msg and send it herself

        with open(file_path, 'rb') as f:
            data = f.read()

        data = self.cipher.encrypt_file(data)
        msg = clientProtocol.build_command(0, [os.path.basename(file_path), len(data)])
        encrypted_message = self.open_clients[client_socket][1].encrypt(msg)

        #  0100.png@#1000000000
        # max size: max(usename, video_id) + video_size : 15+10 = 25 bytes
        try:
            self.my_socket.send(str(len(msg)).zfill(2).encode() + encrypted_message) # sends len and content of len and filename
            self.my_socket.send(data)
        except Exception as e:
            print(f"Error sending message: {e}")

    def _recv_file(self, file_size, file_name):
        """
            recvs file send from the server and saves it at assets//``file_name``
        :param file_size: size of the file that needs to be received
        :param file_name: the name and extension of file to be received
        :return: returns whether the recv was successful
        """
        # called by handle_save_file in logic
        saved_file = True
        file_content = bytearray()
        while len(file_content) < file_size:
            slice = min(1024, (file_size - len(file_content)))
            try:
                data = self.my_socket.recv(slice)
            except Exception as e:
                print("Error at receiving file -", e)
                data = ''

            if not data:
                saved_file = False
                break

            file_content.extend(data)

        if len(file_content) == file_size:
            with open(f"assets\\{file_name}", 'wb') as f:
                f.write(self.cipher.decrypt_file(file_content))
        else:
            self._close_client()

        return saved_file
