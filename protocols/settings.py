""" CONSTANTS """
P = 919

P_SIZE = len(str(P))

G = 327

SERVER_IP = "127.0.0.1"
PORT = 1000
VIDEO_PORT = 1001

PHYSICAL_FPS = 60

AMOUNT_OF_USERS_TO_SEND = 12
AMOUNT_OF_VIDEOS_TO_SEND = 2
AMOUNT_OF_COMMENTS_TO_SEND = 8
AMOUNT_OF_REPORTS_TO_SEND = 5

COMMENT_DIGIT_REPR = 0
VIDEO_DIGIT_REPR = 1

MIN_NAME_LENGTH = 3
MAX_NAME_LENGTH = 15

MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 256

# error codes
#username:
USERNAME_TOO_SHORT = 1
USERNAME_TOO_LONG = 2
USERNAME_ALREADY_EXISTS = 3
USERNAME_INVALID_CHARACTERS = 4
USERNAME_NOT_START_LETTER = 5

USERNAME_ERRORS = {
    USERNAME_TOO_SHORT: "Username is too short",
    USERNAME_TOO_LONG: "Username is too long",
    USERNAME_ALREADY_EXISTS: "Username already exists",
    USERNAME_INVALID_CHARACTERS: "Username contains invalid characters",
    USERNAME_NOT_START_LETTER: "Username must start with a letter"
}

#password:
PASSWORD_TOO_SHORT = 1
PASSWORD_TOO_LONG = 2
PASSWORD_NO_LETTERS = 3

PASSWORD_ERRORS = {
    PASSWORD_TOO_SHORT: "Password is too short",
    PASSWORD_TOO_LONG: "Password is too long",
    PASSWORD_NO_LETTERS: "Password must contain at least one letter"
}

#email:
EMAIL_NOT_VALID = 1

EMAIL_ERRORS = {
    EMAIL_NOT_VALID: "Email is not valid"
}

#currently 10 topics
TOPICS = ["Computer Science", "Math", "Physics", "Cooking", "Baking", "Music", "Wild", "Views", "Art", "History"]

VIDEO_EXTENSION = "mp4"
