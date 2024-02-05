# from abc import ABC, abstractmethod

# from sqlalchemy import create_engine
# from sqlalchemy.engine import URL


# # Potential classes
# class BaseDatabase(ABC):
#     def __init__(self, creds):
#         self.creds = creds

#     @abstractmethod
#     def get_connection_url(self):
#         pass

#     def get_engine(self):
#         return create_engine(self.get_connection_url(), future=True)


# class PostgresDatabase(BaseDatabase):
#     def get_connection_url(self):
#         return URL.create(**self.creds.dict())


# class MySQLDatabase(BaseDatabase):
#     def get_connection_url(self):
#         return URL.create(**self.creds.dict())


# class SQLiteDatabase(BaseDatabase):
#     def get_connection_url(self):
#         return f"sqlite:///{self.creds.host}"


# class SnowflakeDatabase(BaseDatabase):
#     def get_connection_url(self):
#         creds_dict = self.creds.dict()

#         query = {}
#         for key in ["warehouse", "role", "dbschema"]:
#             if key in creds_dict:
#                 # If the key is 'dbschema', change it to 'schema' when adding to the query dictionary
#                 if key == "dbschema":
#                     query["schema"] = creds_dict.pop(key)
#                 else:
#                     query[key] = creds_dict.pop(key)

#         return URL.create(query=query, **creds_dict)
