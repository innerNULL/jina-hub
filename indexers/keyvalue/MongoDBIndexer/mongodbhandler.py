from typing import List, Dict, Union, Optional, Iterator

from jina.logging.logger import JinaLogger


class MongoDBException(Exception):
    """ Any errors raised by MongoDb """


class MongoDBHandler:
    """
    Mongodb Handler to connect to the database & insert documents in the collection
    MongoDB has no access control by default, hence can be used without username:password.
    If username & password are passed, we need to create it (can be changed to existing un:pw)
    """
    def __init__(self, 
                 hostname: str = '127.0.0.1', 
                 port: int = 27017, 
                 username: str = None, 
                 password: str = None,
                 database: str = 'defaultdb',
                 collection: str = 'defaultcol'):
        self.logger = JinaLogger(self.__class__.__name__)
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.database_name = database
        self.collection_name = collection
        if self.username and self.password:
            self.connection_string = \
                f'mongodb://{self.username}:{self.password}@{self.hostname}:{self.port}'
        else:
            self.connection_string = \
                f'mongodb://{self.hostname}:{self.port}'
        
    def __enter__(self):
        return self.connect()
    
    def connect(self) -> 'MongoDBHandler':
        import pymongo
        try:
            self.client = pymongo.MongoClient(self.connection_string)
            self.client.admin.command('ismaster')
            self.logger.info('Successfully connected to the database')
        except pymongo.errors.ConnectionFailure:
            raise MongoDBException('Database server is not available')
        except pymongo.errors.ConfigurationError:
            raise MongoDBException('Credentials passed are not correct!')
        except pymongo.errors.PyMongoError as exp:
            raise MongoDBException(exp)
        except Exception as exp:
            raise MongoDBException(exp)
        return self
        
    @property
    def database(self):
        return self.client[self.database_name]
    
    @property
    def collection(self):
        return self.database[self.collection_name]
    
    def find(self, query: Dict[str, Union[Dict, List]]) -> None:
        import pymongo
        try:
            return self.collection.find(query)
        except pymongo.errors.PyMongoError as exp:
            self.logger.error(f'Got an error while finding a document in the db {exp}')
        
    def insert(self, documents: Iterator[Dict]) -> Optional[str]:
        import pymongo
        try:
            result = self.collection.insert_many(documents)
            self.logger.debug(f'inserted documents in the database')
            return result.inserted_ids
        except pymongo.errors.PyMongoError as exp:
            self.logger.error(f'got an error while inserting a document in the db {exp}')

    def __exit__(self, exc_type, exc_val, exc_tb):
        import pymongo
        try:
            self.client.close()
        except pymongo.errors.PyMongoError as exp:
            raise MongoDBException(exp)
