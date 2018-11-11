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


def create_args_string(num):
    L = []
    for n in range(num):
        L.append("?")
    return ','.join(L)

class ModelMetaClass(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        tableName = attrs.get('__table__', None) or name
        logging.info('found model: {} table: {}'.format(name, tableName))
        mappings = dict()
        fields = []
        primaryKey =  None
        for k,v in attrs.items():
            if isinstance(v,Field):
                logging.info('found mapping:{} ==> {}'.format(k, v))
                mappings[k] = v
                if v.primary_key:
                    if primaryKey:
                        raise StandardError('Duplicate primary key for field:{}'.format(k))
                    primaryKey = k
                else:
                    fields.append(k)

        if primaryKey is None:
            raise StandardError('Primary key not found.')

        for k in mappings.keys():
            attrs.pop(k)

        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        attrs['__mappings__'] = mappings
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey
        attrs['__fields__'] = fields
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ','.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `%s` (%s `%s`) values (%s)' % \
                              (tableName, ','.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' \
                              % (tableName, ','.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f),fields)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
        return type.__new__(cls, name, bases, attrs)

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

class Field(object):
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.colume_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return "<{}:{}:{}>".format(self.__class__.__name__, self.colume_type, self.name)

class StringField(Field):
    def __init__(self, name=None, primary_key=False, default=None, dd1='varchar(100)'):
        super().__init__(name, dd1, primary_key, default)


