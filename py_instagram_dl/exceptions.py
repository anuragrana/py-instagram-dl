
class RateLimitException(Exception):
    """Rate limit reached. Set wait_between_requests to greater than 0 and try again."""


class UnknownException(Exception):
    def __init__(self, msg=None):
        if msg:
            print(msg)
        else:
            print("An Unknown Exception occurred. Please contact developer.")


class InvalidUsernameException(Exception):
    def __init__(self, msg=None):
        if msg:
            print(msg)
        else:
            print("Instagram username provided in not valid")

