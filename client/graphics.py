import math
import string
import sys
import threading
import time

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GUN_COLOR = (100, 100, 100)
BACKGROUND_COLOR = (248, 243, 217)
OUTLINE_COLOR = (185, 178, 138)

class Graphics:

    def __init__(self, client):
        self.client = client
