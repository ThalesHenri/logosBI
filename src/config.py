"""
Definção de variáveis globais
Fazendo desta forma eu consigo padronizar as variáveis em um mesmo lugar, 
garantindo assim um codigo mais limpo e uma manutenção mais clara.


"""


from pathlib import Path


#INFORMAÇÕES DO SISTEMA
APP_NAME = "LogosBI"
APP_VERSION = "1.0.0"
APP_AUTHOR = "TH Sistemas"
DEBUG = True
DEFAULT_ENCODING = "utf-8"


#PATHS DO PROJETO
ROOT_PATH = Path(__file__).resolve().parent.parent

PATH_INPUT = ROOT_PATH / "input"
PATH_PROCESSED = ROOT_PATH / "processed"
PATH_FAILED = ROOT_PATH/ "failed"

PATH_DATA = ROOT_PATH / "data"

PATH_REPORTS = ROOT_PATH / "reports"
PATH_LOGS = ROOT_PATH / "logs"


#banco de dados
DB_NAME = "database.db"
DB_PATH = PATH_DATA / DB_NAME
DB_URL = f"sqlite:///{DB_PATH}"

#tem que estar dentro da raiz do projeto para testar
DB_ABSOLUTE_PATH = "/home/thales/Programação/logosBI/data/database.db"


REQUIRED_DIRS = [
    PATH_INPUT,
    PATH_PROCESSED,
    PATH_FAILED,
    PATH_DATA,
    PATH_REPORTS,
    PATH_LOGS,
]


for directory in REQUIRED_DIRS:
    directory.mkdir(exist_ok=True, parents=True)
