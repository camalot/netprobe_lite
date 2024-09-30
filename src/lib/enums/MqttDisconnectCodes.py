from enum import Enum

class MqttDisconnectCodes(Enum):
    SUCCESS = 0
    BAD_PROTOCOL_VERSION = 1
    CLIENT_ID_REJECTED = 2
    SERVER_UNAVAILABLE = 3
    BAD_USERNAME_PASSWORD = 4
    NOT_AUTHORIZED = 5

    def __str__(self):
        if self.value == 0:
            return "Success"
        elif self.value == 1:
            return "Connection refused because of a bad protocol version"
        elif self.value == 2:
            return "Connection refused because the identifier was rejected"
        elif self.value == 3:
            return "Connection refused because the server is unavailable"
        elif self.value == 4:
            return "Connection refused because the user name or password is incorrect"
        elif self.value == 5:
            return "Connection refused because the client is not authorized"
        else:
            return f"Unknown error code: {self.value}"
