class CustomError(Exception):
    pass


class NoData(CustomError):
    pass


class NoServerData(NoData):
    pass


class AlreadyRegistered(CustomError):
    pass


class ServerAlreadyRegistered(AlreadyRegistered):
    pass


class UserAlreadyRegistered(AlreadyRegistered):
    pass
