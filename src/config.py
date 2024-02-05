import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')

REDIS_HOST = str(os.environ.get('REDIS_HOST'))
REDIS_PORT = str(os.environ.get('REDIS_PORT'))

DB_HOST_TEST = os.environ.get('DB_HOST_TEST')
DB_PORT_TEST = os.environ.get('DB_PORT_TEST')
DB_NAME_TEST = os.environ.get('DB_NAME_TEST')
DB_USER_TEST = os.environ.get('DB_USER_TEST')
DB_PASS_TEST = os.environ.get('DB_PASS_TEST')

REDIS_HOST_TEST = str(os.environ.get('REDIS_HOST_TEST'))
REDIS_PORT_TEST = str(os.environ.get('REDIS_PORT_TEST'))

SECRET = os.environ.get('SECRET')
