import logging
from contextlib import closing
from datetime import datetime
from srv import backoff
from elc_func import ElasticLoader
import psycopg2
from config import dsl, es_conf
from psycopg2.extras import DictCursor
from pg_func import PGLoader
import time

log = logging.getLogger('MainLog')

if __name__ == '__main__':
    columns = ['id', 'title', 'description', 'imdb_rating',
               'genre', 'director', 'actors_names', 'writers_names',
               'actors', 'writers']
    batch = 100

    @backoff()
    def load_data():
        with closing(psycopg2.connect(**dsl, cursor_factory=DictCursor)) as pg_conn:
            log.info(f'{datetime.now()}\n\nПодключение с Postgres установлено. Загрузка данных')
            db = PGLoader(pg_conn)
            block_records = db.pg_loader()
        return block_records

    def elastic_saver():
        log.info(f'{datetime.now()}\n\nПодключение с ES установлено. Загрузка данных')
        elc = ElasticLoader(es_conf)
        elc.create_index('movies')
        pg_records = load_data()
        count_records = len(pg_records)
        i = 0
        block = []
        while count_records != 0:
            if count_records >=batch:
                for row in pg_records[i: i + batch]:
                    block.append(dict(zip(columns, row)))
                    i += 1
                count_records -= batch
                elc.load_data_es(block)
                block.clear()
            else:
                elc.load_data_es([dict(zip(columns, row)) for row in pg_records[i: i + count_records]])
                count_records -= count_records

    while True:
        elastic_saver()
        print('Complete')
        time.sleep(10)