from momopapa.db import Pgsql, Mysql, ESController, RedisController
def es_test():
    # 터널링정보
    tunnel_account = {
        'ssh_host': '13.124.155.171',
        'ssh_user': 'ec2-user',
        'ssh_key': '/Users/danda/keys/hellonext-prd-aws-key.pem'
    }
    # DB엔드포인트
    db_account = {
        'host': 'hellonextprd-livedb-cluster.cluster-cq8ssyppgddc.ap-northeast-2.rds.amazonaws.com',
        'user': 'hellonext',
        'password': 'hellonext',
        'database': 'HelloNextDB',
    }

    ods = Pgsql(**db_account, **tunnel_account)
    # ES엔드포인트
    es_account = {
        'db_conn': ods,
        'host': 'ip-10-28-12-102.ap-northeast-2.compute.internal',
        'port': 9200,  # 생략가능
    }

    esc = ESController(**es_account, **tunnel_account)
    '''
    CASE1 - input table
    '''
    esc.setup(table='co_ven', ts_col='upt_dt')

    '''
    CASE2 - custom query
    '''

    '''
    sql = """
        select * 
        from nextdb.gd_item 
        where upt_dt > '{}'
    """

    esc.setup(
        sql=sql,
        index='co_ven',
        id_cols=['ven_cd'],
        ts_col='upt_dt'
    )
    '''

    esc.run()
    esc.close()

    # Pgsql & Tunneling Example
    '''
    account_info = {
        'host' : 'hellonextprd-livedb-cluster.cluster-cq8ssyppgddc.ap-northeast-2.rds.amazonaws.com',
        'user' : 'hellonext',
        'password' : 'hellonext',
        'database' : 'HelloNextDB',

        'ssh_host' : '13.124.155.171',
        'ssh_user' : 'ec2-user',
        'ssh_key' : '/Users/danda/keys/hellonext-prd-aws-key.pem'
    }
    ods = Pgsql(**account_info)
    sql = "select item_cd, item_nm from nextdb.gd_item limit 5"
    ods.execute(sql)
    res = True
    while res:
        res = ods.get(type='dict', size=-1)
        print(res)

    ods.close()
    '''

    # Mysql Example
    '''
    account_info = {
        'host': 'hnproduct-cluster.cluster-cgwccuxp0zw8.ap-northeast-2.rds.amazonaws.com',
        'user': 'hndb2015',
        'password': 'gpffh20151',
        'database': 'hellontr3336_godo_co_kr',
    }
    ods = Mysql(**account_info)
    sql = "select goodsno, goodsnm from gd_goods limit 5"
    ods.execute(sql)
    res = True
    while res :
        res = ods.get(type='dict', size=1)
        print(res)

    ods.close()
    '''


def redis_test():
    # 터널링정보
    tunnel_account = {
        'ssh_host': '13.124.155.171',
        'ssh_user': 'ec2-user',
        'ssh_key': '/Users/danda/keys/hellonext-prd-aws-key.pem'
    }
    # DB엔드포인트
    db_account = {
        'host': 'hellonextprd-livedb-cluster.cluster-cq8ssyppgddc.ap-northeast-2.rds.amazonaws.com',
        'user': 'hellonext',
        'password': 'hellonext',
        'database': 'HelloNextDB',
    }

    ods = Pgsql(**db_account, **tunnel_account)

    # Redis엔드포인트
    redis_account = {
        'db_conn': ods,
        'host': 'next-prd-datalab-redis.jegaef.0001.apn2.cache.amazonaws.com',
        'port': 6379,
        'db': 15
    }

    rc = RedisController(**redis_account, **tunnel_account)
    '''
    CASE1 - input table
    '''
    rc.setup(table='co_ven', ts_col='upt_dt')
    rc.run()
    rc.close()


if __name__ == '__main__':
    es_test()
    # redis_test()