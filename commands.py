import enum

class Commands(enum.Enum):
    HI = 0      # args: user_name
    ECHO = 1    # args: text_to_return
    QUIT = 2    # args: no

