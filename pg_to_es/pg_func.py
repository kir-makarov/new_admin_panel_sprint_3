from datetime import datetime

from load_query import load_query
from state_func import JsonFileStorage, State


class PGLoader:
    def __init__(self, pg_conn, state_key='key'):
        self.conn = pg_conn
        self.cursor = self.conn.cursor()
        self.key = state_key
        self.state_key = State(JsonFileStorage('state.txt')).get_state(state_key)
        self.batch = 100
        self.data_container = []
        self.count = 0

    def get_state_key(self):
        if self.state_key is None:
            return datetime.min
        return self.state_key

    def pg_loader(self) -> list:
        self.cursor.execute(load_query % self.get_state_key())
        while True:
            records = self.cursor.fetchmany(self.batch)
            if not records:
                break
            for row in records:
                self.data_container.append(row)
        return self.data_container


