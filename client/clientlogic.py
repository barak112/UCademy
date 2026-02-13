import graphics
import clientProtocol
import clientComm
import queue
import settings
import threading


class ClientLogic:
    """Manages client-side logic for the UCademy project.
    Processes server messages
    """

    def __init__(self):
        """Initialize the Client object.

        Sets up players, network communication, and graphics. Establishes a connection
        to the server.
        """
        self.players = {}  # [name] = Player object
        self.color = 0
        self.status = []
        self.recvQ = queue.Queue()
        self.comm = clientComm.ClientComm(self, settings.SERVER_IP, settings.PORT, self.recvQ)
        self.comm.connect()
        self.graph = graphics.Graphics(self)

        self.commands = {
        }

    def run(self):
        """Start the client.

        Initiates the message handler thread and opens the game lobby.
        """
        threading.Thread(target=self.handle_msgs, daemon=True).start()

    def quit(self):
        """Quit the game.

        Closes the game window, network connection, and exits the application.
        """
        self.comm.close_client()

    def handle_msgs(self):
        """Process incoming messages from the server.

        Continuously retrieves messages from the receive queue and handles them based on opcode.
        """
        while True:
            msg = self.recvQ.get()
            opcode, data = clientProtocol.unpack(msg)
            if opcode in self.commands:
                self.commands[opcode](data)

if __name__ == "__main__":
    """Main entry point to run the client."""
    client = ClientLogic()
    client.run()

