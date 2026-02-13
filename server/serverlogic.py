import queue
import threading
import serverComm
import serverProtocol
from settings import *


class ServerLogic:
    """Manages the server-side logic for the UCademy project.

    Processes incoming messages
    from clients via a queue and communicates updates using the server communication module.
    """

    def __init__(self, comm, msgsQ):
        """Initialize the server object.

        :param comm: ServerComm object for client communication.
        :param msgsQ: Queue for receiving messages from clients.
        """
        self.comm = comm
        self.msgsQ = msgsQ
        self.commands = {
        }
        threading.Thread(target=self.handle_msgs, args=(msgsQ,)).start()

    def handle_msgs(self, recvQ):
        """Process incoming messages from clients.

        :param recvQ: Queue for receiving messages.
        """
        while True:
            ip, msg = recvQ.get()
            opcode, data = serverProtocol.unpack(msg)

            if opcode in self.commands.keys():
                self.commands[opcode](ip, data)

if __name__ == "__main__":
    msgsQ = queue.Queue()
    server_comm = serverComm.ServerComm(PORT, msgsQ)
    ServerLogic(server_comm, msgsQ)
