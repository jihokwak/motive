from abc import abstractmethod
import pandas as pd

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.exc import OperationalError
from . import pandabase

class GenericDBConnector(object):
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
            "{protocol}://{user}:{password}@{host}:{port}/{database}".format(
                **self.db_account))

        self.metadata = MetaData(self.engine)
        self.metadata.reflect()
        print("db connected.")
        self.connect()

    # connect
    def connect(self):
        self.conn = self.engine.connect()

    def get_pks(self, tbl, schema=None):
        meta = MetaData()
        table = Table(tbl, meta, schema=schema, autoload=True, autoload_with=self.engine)
        pks = [col.name for col in table.primary_key.columns.values()]
        return pks

    def execute(self, sql):
        self.sql = sql
        try:
            self.respxy = self.conn.execute(sql)
        except (OperationalError, AttributeError):
            del self.conn
            self.connect()
            print("db re-connected.")
            self.respxy = self.conn.execute(sql)

    @abstractmethod
    def get(self, type='tuple', size=-1):
        pass

    def create(self, df, tbl, schema=None, pks=[]):
        if isinstance(pks, list):
            pass
        elif isinstance(pks, tuple):
            pass
        else:
            raise Exception('pks parameter type must be list or tuple.')
        self.connect()
        df.to_sql(name=tbl, con=self.engine, index=False)
        self.execute("truncate {tbl};".format(tbl=tbl if not schema else schema + "." + tbl))
        if pks :
            self.execute("alter table {tbl} add primary key ({pks})".format(
                tbl=tbl if not schema else schema+"."+tbl,
                pks=",".join(pks)))

    def replace(self, df, tbl, schema=None):
        self.execute("truncate {tbl};".format(tbl=tbl if not schema else schema + "." + tbl))
        self.insert(df, tbl, schema=schema)

    def insert(self, df, tbl, schema=None):
        self.connect()
        df_copied = df.copy()
        pks = self.get_pks(tbl, schema)
        if pks :
            df_copied.set_index(pks, inplace=True)
            pandabase.to_sql(df_copied, table_name=tbl, con=self.engine, schema=schema, how='append', add_new_columns=True)
        else :
            df_copied.to_sql(tbl, self.engine, if_exists='append', index=False, schema=schema)

    def upsert(self, df, tbl, schema=None):
        df_copied = df.copy()
        pks = self.get_pks(tbl, schema)
        if not pks :
            raise Exception('target table primary key is needed.')
        self.connect()
        df_copied.set_index(pks, inplace=True)
        pandabase.to_sql(df_copied, table_name=tbl, con=self.engine, how='upsert', schema=schema, add_new_columns=True)

    def upload_s3(self, df, bucket, key, acc_key=None, sec_key=None, region_name='ap-northeast-2'):
        if key.find('parquet.gzip') == -1 :
            raise Exception("key file name must end with '.parquet'")

        df.to_parquet(
            path='s3://{bucket}/{key}'.format(bucket=bucket, key=key),
            engine='pyarrow', index=False)

        # s3 = boto3.resource('s3', aws_access_key_id=acc_key,
        #                     aws_secret_access_key=sec_key,
        #                     region_name=region_name)
        #
        # with BytesIO() as obj:
        #     df.to_parquet(obj, compression='gzip')
        #     s3.Object(Bucket=bucket, Key=key).put(Body=obj.getvalue())

    def drop(self, tbl, schema=None):
        self.connect()
        pandabase.util.drop_db_table(tbl, con=self.engine, schema=schema)

    def close(self):
        self.conn.close()
        print("db connection closed.")
        self.close_tunnel()


class Mysql(GenericDBConnector):
    def __init__(self, port=3306, *args, **kwargs):
        super().__init__(protocol="mysql+pymysql", port=port, *args, **kwargs)

    def get(self, type='tuple', size=-1):
        records = None
        cols = [c[0] for c in self.respxy.cursor.description] if self.respxy.cursor else []

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
        cols = [c[0] for c in self.respxy.cursor.description] if self.respxy.cursor else []

        if type == 'tuple':
            records = self.respxy.fetchmany(size)
        elif type == 'df':
            records = pd.DataFrame(self.respxy.fetchmany(size), columns=cols)
        elif type == 'dict':
            records = [{k: v for k, v in zip(cols, row)} for row in self.respxy.fetchmany(size)]
        return records

