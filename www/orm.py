import traceback
import asyncio
import aiomysql
import logging


def log(sql, *args):
    print('SQL is:{}'.format(sql))


# 创建连接池
async def create_pool(**kw):
    logging.info('create connections about database...')
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port'),
        user=kw.get('user'),
        password=kw.get('password'),
        db=kw.get('db'),
        charset=kw.get('charset'),
        autocommit=kw.get('autocommit'),
        maxsize=kw.get('maxsize'),
        minsize=kw.get('minsize')
    )


async def select(sql, args, size=None):
    log(sql)
    global __pool
    async with __pool.get() as conn:
        cur = await conn.cursor(aiomysql.DictCursor)
        await cur.execute(sql.replace('?', '%'), args or ())
        if size:
            rs = await cur.fetchmany(size)
        else:
            rs = await cur.fetchall()
        await cur.close()
        logging.info('rows returned:{}'.format(len(rs)))
        return rs


async def execute(sql, args):
    log(sql)
    global __pool
    with __pool.get() as conn:
        try:
            cur = await conn.cursor()
            await cur.execute(sql.replace('?', "%"), args)
            affected = cur.rowcount
            logging.info('affected = {}'.format(affected))
            return affected
        except:
            traceback.print_exc()
            raise


class ModelMetaClass(type):
    pass


# ORM映射的基类
class Model(dict, metaclass=ModelMetaClass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mapping__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.info('using default value  for {}:{}'.format(key, value))
                setattr(self, key, value)

        return value
