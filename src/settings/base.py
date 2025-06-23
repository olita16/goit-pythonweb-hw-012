import configparser
import pathlib

path = pathlib.Path(__file__).parent.joinpath("config.ini")
print("Reading config.ini from:", path)

parser = configparser.ConfigParser()
parser.read(path)

DB_URL = parser.get("DB", "DB_URL")
SECRET_KEY = parser.get("AUTH", "SECRET_KEY")
ALGORITHM = parser.get("AUTH", "ALGORITHM")
