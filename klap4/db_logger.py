import logging


class DBHandler(logging.Handler):
    def __init__(self):
        print("Handler created!")

    def emit(self, record):
        print("Emitting!")
