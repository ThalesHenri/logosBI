import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class LoggerMaker:
    def __init__(
        self,
        name: str = "LogosBI",
        log_dir: str = "logs",
        log_file: str = "logosbi.log",
        max_bytes: int = 5 * 1024 * 1024,
        backup_count: int = 2,
    ) -> None:
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_file = self.log_dir / log_file
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        self._ensure_log_dir()
        self.logger = logging.getLogger(self.name)
        self._configure()

    def _ensure_log_dir(self) -> None:
        self.log_dir.mkdir(exist_ok=True)

    def _configure(self) -> None:
        if self.logger.handlers:
            return  # evita duplicação

        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)

        # Arquivo
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(console)
        self.logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        return self.logger
