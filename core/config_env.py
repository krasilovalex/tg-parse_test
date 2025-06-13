import os
from dotenv import load_dotenv
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class Config:
    def get_env(self, variable:str, default=None):
        value = os.environ.get(variable, default=default)
        if value is None:
            logger.error(f"Перменная окружения {variable} - не была найдена")
        return value