import logging


class Logger:
    def __init__(self, name: str):
        self.config = {'application_name': name.upper()}

        self.log = logging.getLogger(name)

        formatter = logging.Formatter('%(asctime)s [%(application_name)s]: %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        self.log.addHandler(handler)
        self.log.setLevel(logging.DEBUG)

    def info(self, message):
        self.log.info(message, extra=self.config)

    def warning(self, message):
        self.log.warning(message, extra=self.config)

    def error(self, message):
        self.log.error(message, extra=self.config)

    def critical(self, message):
        self.log.critical(message, extra=self.config)
