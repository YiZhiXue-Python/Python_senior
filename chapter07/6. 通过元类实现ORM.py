
# 需求


class Filed(object):
    pass


class CharFiled(Filed):
    def __init__(self, db_column, max_length=None):
        self._value = None
        if max_length is None:
            raise ValueError('max_length 是必须的')

        elif not isinstance(max_length, int):
            raise ValueError('max_length 必须是int')

        elif max_length <= 0:
            raise ValueError('max_length 必须大于0')

        self.db_column = db_column
        self.max_length = max_length

    def __set__(self, instance, value):
        if not isinstance(value, str):
            raise ValueError('需要str类型')
        elif len(value) > self.max_length:
            raise ValueError('value 长度不能大于 max_length')
        self._value = value

    def __get__(self, instance, owner):
        return self._value

    def __delete__(self, instance):
        pass


class IntFiled(Filed):

    # 数据描述符
    def __init__(self, db_column, min_value=None, max_value=None):
        self._value = None

        if min_value is not None:
            if not isinstance(min_value, int):
                raise ValueError('min_value 需要int类型')

        if max_value is not None:
            if not isinstance(max_value, int):
                raise ValueError('max_value 需要int类型')

        if all([min_value, max_value]):
            if min_value > max_value:
                raise ValueError('min_value or max_value 设置错误')

        self.min_value = min_value
        self.max_value = max_value
        self.db_column = db_column

    def __set__(self, instance, value):
        if not isinstance(value, int):
            raise ValueError('需要int类型')
        if value < self.min_value or value > self.max_value:
            raise ValueError('value 应该在 min_value max_value 之间')

        self._value = value

    def __get__(self, instance, owner):
        return self._value

    def __delete__(self, instance):
        pass


class ModelMetaClass(type):
    def __new__(cls, name, bases, attrs, **kwargs):

        if name == 'BaseModel':
            return super().__new__(cls, name, bases, attrs, **kwargs)

        fields = dict()
        for key, value in attrs.items():
            if isinstance(value, Filed):
                fields[key] = value

        _meta = {}
        attrs_meta = attrs.get('Meta', None)
        db_table = name.lower()
        if attrs_meta is not None:
            table = getattr(attrs_meta, 'db_table', None)
            if table is not None:
                db_table = table
            del attrs['Meta']
            del attrs_meta

        _meta['db_table'] = db_table
        attrs['_meta'] = _meta
        attrs['fields'] = fields

        return super().__new__(cls, name, bases, attrs, **kwargs)


class BaseModel(metaclass=ModelMetaClass):
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        super().__init__(*args, **kwargs)

    def save(self):
        fields = []
        values = []
        for key, value in self.fields.items():
            db_column = value.db_column
            if db_column == '':
                db_column = key.lower()
                fields.append(db_column)
            db_value = getattr(self, key)
            if isinstance(db_value, str):
                db_value = ''.join(["'", db_value, "'"])
            values.append(str(db_value))

        sql = 'insert {db_table}({fields}) values({values})'.format(db_table=self._meta['db_table'],
                                                                    fields=','.join(fields),
                                                                    values=','.join(values))
        print(sql)


class User(BaseModel):

    name = CharFiled(db_column='', max_length=10)
    age = IntFiled(db_column='', min_value=0, max_value=120)

    class Meta:
        db_table = 'user'


if __name__ == '__main__':
    user = User()
    user.name = 'xiaowei'
    user.age = 23
    user.save()
