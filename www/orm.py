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
        host=kw.get('host','localhost'),
        port=kw.get('port'),
        user=kw.get('user'),
        password=kw.get('password'),
        db=kw.get('db'),
        charset=kw.get('charset'),
        autocommit=kw.get('autocommit'),
        maxsize=kw.get('maxsize'),
        minsize=kw.get('minsize')
    )


async def select(sql,args,size=None):
    log(sql)
    global __pool
    async with __pool.get() as conn:
        cur = await conn.cursor(aiomysql.DictCursor)
        await cur.execute(sql.replace('?','%'), args or ())
        if size:
            rs = await cur.fetchmany(size)
        else:
            rs = await cur.fetchall()
        await cur.close()
        logging.info('rows returned:{}'.format(len(rs)))
        return rs
