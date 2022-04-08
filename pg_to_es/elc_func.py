import json
import logging
from datetime import datetime

from elasticsearch import Elasticsearch

from elastic_index import INDEX
from srv import backoff
from state_func import JsonFileStorage, State

log = logging.getLogger('ESLog')


class ElasticLoader:
    def __init__(self, host: list, state_key='key'):
        self.client = Elasticsearch(host)
        self.data = []
        self.key = state_key

    @backoff()
    def create_index(self, index: str) -> None:
        if not self.client.indices.exists(index):
            self.client.indices.create(index=index, body=INDEX)
            log.warning(f'{datetime.now()}\n\nСоздание индекса')
        log.warning(f'{datetime.now()}\n\nИндекс уже существует')

    @backoff()
    def bulk_data(self) -> None:
        self.client.bulk(index='movies', body=self.data, refresh=True)

    def load_data_es(self, query: list) -> None:
        data_json = json.dumps(query)
        load_json = json.loads(data_json)
        for row in load_json:
            for i in row:
                if row[i] is None:
                    row[i] = []
            self.data.append({"create": {"_index": "movies", "_id": row['id']}})
            self.data.append(row)
            self.bulk_data()
            self.data.clear()
        State(JsonFileStorage('state.txt')).set_state(str(self.key), value=str(datetime.now().astimezone()))
