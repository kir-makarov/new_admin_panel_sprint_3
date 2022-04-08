import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(filename='es.log', level='INFO')
log = logging.getLogger()
log.setLevel(level='INFO')


dsl = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'port': os.environ.get('DB_PORT'),
    'options':"-c search_path=content",
}

es_conf = [{
    'host': os.getenv('ES_HOST'),
    'port': os.getenv('ES_PORT'),
}]