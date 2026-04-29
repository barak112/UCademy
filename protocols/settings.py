""" CONSTANTS """
P = 919

P_SIZE = len(str(P))

G = 327

SERVER_IP = "127.0.0.1"
PORT = 1000
VIDEO_PORT = 1001

MESSAGE_LENGTH_LENGTH = 5

PHYSICAL_FPS = 60

AMOUNT_OF_USERS_TO_SEND = 15
AMOUNT_OF_VIDEOS_TO_SEND = 15
AMOUNT_OF_VIDEOS_TO_REQ = 3 # amount of videos to request from server when first moving to feed
AMOUNT_OF_COMMENTS_TO_SEND = 20

COMMENT_DIGIT_REPR = 0
VIDEO_DIGIT_REPR = 1

MIN_NAME_LENGTH = 3
MAX_NAME_LENGTH = 15

MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 256

# --- reports ---
REPORT_DENIED = 0
REPORT_ACCEPTED = 1

REPORT_CONTENT_DOESNT_EXISTS = 2
REPORT_ALREADY_ISSUED = 3
REPORT_RECEIVED = 4
REPORT_CONCLUDED = 5


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
    PASSWORD_TOO_SHORT: f"Password must be at least {MIN_PASSWORD_LENGTH} characters",
    PASSWORD_TOO_LONG: f"Password must be less than {MAX_PASSWORD_LENGTH} characters",
    PASSWORD_NO_LETTERS: "Password must contain at least one letter"
}

#email:
EMAIL_NOT_VALID = 1
EMAIL_ALREADY_EXISTS = 2

EMAIL_ERRORS = {
    EMAIL_NOT_VALID: "Email is not valid",
    EMAIL_ALREADY_EXISTS: "Email already exists"
}

EMAIL_VERIFICATION_CODE_EXPIRATION = 10 * 60 #seconds->minutes
EMAIL_VERIFICATION_CODE_INVALID = 0
EMAIL_VERIFICATION_SUCCESSFUL = 1
EMAIL_VERIFICATION_CODE_EXPIRED = 2
EMAIL_VERIFICATION_CREDENTIALS_TAKEN = 3

EMAIL_VERIFICATION_ERRORS = {
    EMAIL_VERIFICATION_CODE_INVALID: "Verification code entered is invalid",
    EMAIL_VERIFICATION_CODE_EXPIRED: "Verification code entered is expired, returning to sign up",
    EMAIL_VERIFICATION_CREDENTIALS_TAKEN: "Credentials taken, returning to sign up"
}

#currently 10 topics
TOPICS = ["Technology", "Design", "Business", "Science", "Health & Fitness", "Travel", "Food & Cooking", "Music",
          "Sports", "Photography", "Fashion", "Gaming", "Books & Literature", "Movies & TV", "Art", "Nature"]
# TOPICS = ["Technology", "Math", "Physics", "Cooking", "Baking", "Music", "Wild", "Views", "Art", "History"]
#Computer Science
VIDEO_EXTENSION = "mp4"

# graphics constants
THEME_COLOR = (56, 65, 237)
OFF_WHITE = (249, 250, 251)
SUBTITLE_COLOR = (125, 120, 124)
BORDER_COLOR = (180, 180, 180)
BRIGHT_BORDER_COLOR = (220, 220, 220)
BRIGHT_PINK = (135, 140, 255)
# BRIGHT_PINK = (238, 242, 255)
UNACTIVE_BUTTON = (120, 120, 120)
BRIGHT_UNACTIVE_BUTTON = (200, 200, 200)
BRIGHT_BLUE = (238, 242, 255)


BUTTON_SIZE_Y = 55
BUTTON_TEXT_FONT_SIZE = 14
VERIFICATION_CODE_FONT_SIZE = 25
ROUND_BORDER_RADIUS = 15
SLIGHTLY_ROUND_BORDER_RADIUS = 10
#prev: 50, 11
TOPIC_WIDGET_GROWTH = 3
MIN_TOPICS = 3
TOPIC_WIDGET_WIDTH = 250

PFP_SIZE = 48
