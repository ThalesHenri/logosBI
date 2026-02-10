import logging
from queue import Queue

class UILogHandler(logging.Handler):
    def __init__(self, log_queue: Queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record) -> None:
        log_entry = self.format(record)
        self.log_queue.put(log_entry)
