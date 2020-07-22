from abc import abstractmethod
import json
import pandas as pd
from decimal import Decimal
from datetime import datetime

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.exc import ProgrammingError, OperationalError
from sshtunnel import SSHTunnelForwarder, HandlerSSHTunnelForwarderError

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch.exceptions import NotFoundError

import redis


class SSHTunnelMixin(object):

    def open_tunnel(self, host, port, ssh_host, ssh_user, ssh_key):
        if not hasattr(self, 'tunnel'):
            for tport in range(int(port) + 1, int(port) + 100):
                try:
                    self.tunnel = SSHTunnelForwarder(
                        ssh_host=(ssh_host, 22),
                        ssh_username=ssh_user,
                        ssh_pkey=ssh_key,
                        remote_bind_address=(host, int(port)),
                        local_bind_address=('0.0.0.0', tport)
                    )
                    self.tunnel.daemon_forward_servers = True
                    self.tunnel.daemon_transport = True
                    self.tunnel.start()
                except HandlerSSHTunnelForwarderError:
                    print("port {} is already used.".format(tport))
                    pass
                except Exception as e:
                    print(e)
                    pass
                else:
                    print("open tunnel in port {}.".format(tport))
                    self.tport = tport
                    break;
        else:
            if not self.tunnel.is_alive:
                self.tunnel.start()
                print("open tunnel in port {}.".format(self.tport))
            else:
                print("tunnel is already alive.")

    def close_tunnel(self):
        if hasattr(self, 'tunnel'):
            print("tunnel closed.")
            self.tunnel.stop()
        else:
            print("tunnel is not exists.")


class GenericNoSQLContraoller(SSHTunnelMixin, object):
    def __init__(self, db_conn, host, port, *args, **kwargs):

        if not isinstance(db_conn, GenericDBConnector):
            raise Exception('your db_conn object must be GenericDBConnector Class')

        self.db_conn = db_conn

        is_tunneling = "ssh_host" in kwargs and "ssh_user" in kwargs and "ssh_key" in kwargs

        if is_tunneling:
            self.open_tunnel(
                host=host, port=int(port),
                ssh_host=kwargs.get('ssh_host'),
                ssh_user=kwargs.get('ssh_user'),
                ssh_key=kwargs.get('ssh_key'))

        self.account = {
            "host": host if not is_tunneling else '127.0.0.1',
            "port": int(port) if not is_tunneling else self.tport,
        }

        if 'db' in kwargs:
            self.account['db'] = kwargs.get('db', 15)

        self.connect()

    def setup(self, ts_col, table=None, sql=None, index=None, id_cols=[]):
        self.table = table
        self.sql = sql
        self.id_cols = id_cols
        self.ts_col = ts_col
        self.records = []

        if not table and not sql:
            raise Exception("either table or query is required.")
        if index:
            self.index = index
        elif (not index and table):
            self.index = table

        else:
            raise Exception("query method need index name.")
        if sql and not id_cols:
            raise Exception('query method need id_cols(type list) parameter.')
        if not ts_col:
            raise Exception("timestamp column needed.")

    def run(self):
        if not hasattr(self, 'table'):
            raise Exception('setup migration infomation first.')

        self.get_ts()
        self.get()
        self.put()

    def get(self):
        if self.sql:
            sql = self.sql.format(datetime.strptime(self.ts, '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S'))
        else:
            sql = """
                   select * from {table} where {ts_col} > '{ts}'
               """.format(
                table=self.table,
                ts_col=self.ts_col,
                ts=datetime.strptime(self.ts, '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S'))

        self.db_conn.execute(sql)
        self.records = self.db_conn.get(type='dict')
        if self.table:
            print("{table} table's primary key ({pks})".format(
                table=self.table,
                pks="-".join(self.db_conn.get_pks(self.table))))

    def close(self):
        self.db_conn.close()

    @abstractmethod
    def put(self):
        pass

    @abstractmethod
    def get_ts(self):
        pass

    @abstractmethod
    def connect(self):
        pass


class RedisController(GenericNoSQLContraoller):
    def __init__(self, db_conn, host, port=6379, db=15, *args, **kwargs):
        super().__init__(db_conn=db_conn, host=host, port=port, db=db, *args, **kwargs)

    def connect(self):
        self.conn = redis.StrictRedis(**self.account)

    def get_ts(self):
        self.ts = self.conn.get('{index}:maxts'.format(index=self.index)).decode()
        if not self.ts:
            self.ts = '1970-01-01 00:00:00.000000'
        print("timestamp : ", self.ts)

    def put(self):
        pks = self.db_conn.get_pks(self.table) if not self.sql else self.id_cols
        maxts = self.ts
        for idx, record in enumerate(self.records):
            id = "-".join([record[pk] for pk in pks])

            self.conn.set(
                name='{index}:{id}'.format(index=self.index, id=id),
                value=json.dumps(record, default=self.json_parser, ensure_ascii=False).encode('utf-8')
            )
            if datetime.strptime(maxts, '%Y-%m-%d %H:%M:%S.%f') < record[self.ts_col]:
                maxts = record[self.ts_col].strftime('%Y-%m-%d %H:%M:%S.%f')
        self.conn.set('{index}:maxts'.format(index=self.index), maxts)
        print("upsert record count : ", len(self.records))

    def drop(self, index):
        res = self.conn.delete('{}:*'.format(index))
        print(res)
        print("{} index dropped.".format(index))

    def json_parser(self, value):
        if isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S.%f')
        raise TypeError('{} not JSON serializable'.format(type(value)))


class ESController(GenericNoSQLContraoller):
    def __init__(self, db_conn, host, port=9200, *args, **kwargs):
        super().__init__(db_conn=db_conn, host=host, port=port, *args, **kwargs)

    def connect(self):
        self.conn = Elasticsearch(**self.account)

    def get_ts(self):
        res = self.conn.search(
            index=self.index,
            body={
                "aggs": {
                    "maxts": {
                        "max": {
                            "field": "upt_dt",
                            "format": "yyyy-MM-dd HH:mm:ss.SSSSSS"
                        }
                    }
                }
            },
            ignore_unavailable=True
        )
        if res['took']:  # index is exists.
            print("index is exists.")
            if res['aggregations']['maxts']['value']:  # ts_col and record are exist.
                self.ts = res['aggregations']['maxts']['value_as_string']
            else:  # ts_col or record is not exists.
                print("ts_col or record is not exists.")
                self.ts = '1970-01-01 00:00:00.000000'
        else:  # index is not exists.
            print("index is not exists.")
            self.ts = '1970-01-01 00:00:00.000000'
        print("timestamp : ", self.ts)

    def put(self):
        pks = self.db_conn.get_pks(self.table) if not self.sql else self.id_cols
        actions = [
            {
                "_index": self.index,
                "_id": "-".join([str(record[pk]) for pk in pks]),
                "_source": record
            }
            for record in self.records
        ]
        res = helpers.bulk(self.conn, actions)
        print("upsert record count : ", res[0])

    def drop(self, index):
        try:
            self.conn.indices.delete(index=index)
            print("{} index dropped.".format(index))
        except NotFoundError as e:
            print("{} index is not exists.".format(index))


class GenericDBConnector(SSHTunnelMixin, object):
    def __init__(self, user, password, host, port, database, *args, **kwargs):

        is_tunneling = "ssh_host" in kwargs and "ssh_user" in kwargs and "ssh_key" in kwargs
        if is_tunneling:
            self.open_tunnel(
                host=host, port=int(port),
                ssh_host=kwargs.get('ssh_host'),
                ssh_user=kwargs.get('ssh_user'),
                ssh_key=kwargs.get('ssh_key'))

        self.db_account = {
            "protocol": kwargs.get("protocol"),
            "host": host if not is_tunneling else '127.0.0.1',
            "port": port if not is_tunneling else self.tport,
            "user": user,
            "password": password,
            "database": database
        }

        self.engine = create_engine(
            "{protocol}://{user}:{password}@{host}:{port}/{database}?charset=utf8".format(
                **self.db_account))

        self.connect()

    # connect
    def connect(self):
        try:
            self.conn = self.engine.connect()
        except ProgrammingError:
            self.engine = create_engine(
                "{protocol}://{user}:{password}@{host}:{port}/{database}".format(
                    **self.db_account))
            self.conn = self.engine.connect()

    def get_pks(self, tbl):
        meta = MetaData()
        table = Table(tbl, meta, autoload=True, autoload_with=self.engine)
        pks = [col.name for col in table.primary_key.columns.values()]
        return pks

    def execute(self, sql):
        self.sql = sql
        try:
            self.respxy = self.conn.execute(sql)
        except OperationalError:
            self.conn.connect()
            self.respxy = self.conn.execute(sql)

    @abstractmethod
    def get(self, type='tuple', size=-1):
        pass

    def put(self, df, tbl, if_exists='append'):
        if not type(df) == 'generator':
            while True:
                try:
                    result = next(df)
                    pd.DataFrame(result).to_sql(tbl, self.engine, if_exists=if_exists)
                except Exception as e:
                    print(e)
                    break
        else:
            while True:
                try:
                    result = next(df)
                    print(result)
                    df.to_sql(df, self.engine, if_exists=if_exists)
                except Exception as e:
                    print(e)
                    break

    def close(self):
        self.conn.close()
        print("db connection closed.")
        self.close_tunnel()


class Mysql(GenericDBConnector):
    def __init__(self, port=3306, *args, **kwargs):
        super().__init__(protocol="mysql+pymysql", port=port, *args, **kwargs)

    def get(self, type='tuple', size=-1):
        records = None
        cols = [c[0] for c in self.respxy.cursor.description]
        if type == 'tuple':
            records = self.respxy.fetchmany(size)
        elif type == 'df':
            records = pd.DataFrame(self.respxy.fetchmany(size), columns=cols)
        elif type == 'dict':
            records = [{k: v for k, v in zip(cols, row)} for row in self.respxy.fetchmany(size)]
        return records


class Pgsql(GenericDBConnector):
    def __init__(self, port=5432, *args, **kwargs):
        super().__init__(protocol="postgresql", port=port, *args, **kwargs)

    def get(self, type='tuple', size=-1):
        records = None
        cols = [c.name for c in self.respxy.cursor.description]

        if type == 'tuple':
            records = self.respxy.fetchmany(size)
        elif type == 'df':
            records = pd.DataFrame(self.respxy.fetchmany(size), columns=cols)
        elif type == 'dict':
            records = [{k: v for k, v in zip(cols, row)} for row in self.respxy.fetchmany(size)]
        return records

