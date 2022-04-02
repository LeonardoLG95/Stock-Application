import logging


class Logger:
    def __init__(self, application_name: str):
        self.log_config = {'application': f'[{application_name.upper()}]'}
        logging.basicConfig(format='%(asctime)s %(application)s: %(message)s')
        self.log = logging.getLogger(application_name.upper())

    def info(self, message):
        self.log.info(message, extra=self.log_config)

    def warning(self, message):
        self.log.warning(message, extra=self.log_config)

    def error(self, message):
        self.log.error(message, extra=self.log_config)

    def critical(self, message):
        self.log.critical(message, extra=self.log_config)
