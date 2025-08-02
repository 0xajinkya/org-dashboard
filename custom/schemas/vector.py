from sqlalchemy.types import UserDefinedType


class Vector(UserDefinedType):
    def get_col_spec(self, **kw):
        return "vector"

    def bind_processor(self, dialect):
        def process(value):
            return value  # optionally serialize if needed

        return process

    def result_processor(self, dialect, coltype):
        def process(value):

            return value  # optionally deserialize

        return process
