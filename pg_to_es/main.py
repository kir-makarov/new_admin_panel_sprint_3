import logging
import time
from contextlib import closing
from datetime import datetime

import psycopg2
from psycopg2.extras import DictCursor

from config import dsl, es_conf
from elc_func import ElasticLoader
from pg_func import PGLoader
from srv import backoff

log = logging.getLogger('MainLog')

if __name__ == '__main__':
    columns = ['id', 'title', 'description', 'imdb_rating',
               'genre', 'director', 'actors_names', 'writers_names',
               'actors', 'writers']
    batch = 100

    @backoff()
    def load_data() -> list:
        with closing(psycopg2.connect(**dsl, cursor_factory=DictCursor)) as pg_conn:
            log.info(f'{datetime.now()}\n\nПодключение с Postgres установлено. Загрузка данных')
            db = PGLoader(pg_conn)
            block_records = db.pg_loader()
        return block_records

    def elastic_saver() -> None:
        log.info(f'{datetime.now()}\n\nПодключение с ES установлено. Загрузка данных')
        elc = ElasticLoader(es_conf)
        elc.create_index('movies')
        pg_records = load_data()
        count_records = len(pg_records)
        index = 0
        block = []
        while count_records != 0:
            if count_records >= batch:
                for row in pg_records[index: index + batch]:
                    block.append(dict(zip(columns, row)))
                    index += 1
                count_records -= batch
                elc.load_data_es(block)
                block.clear()
            else:
                elc.load_data_es([dict(zip(columns, row)) for row in pg_records[index: index + count_records]])
                count_records -= count_records

    while True:
        elastic_saver()
        time.sleep(10)
