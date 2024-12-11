from dataclasses import dataclass


# TODO: store in aws secret manager or the like
@dataclass
class DBContext:
    user: str = "exampleuser"
    password: str = "examplepassword"
    host: str = "127.0.0.1"
    port: str = "5432"
    db: str = "exampledb"


@dataclass
class Context:
    db_context: DBContext

    def __init__(self, db_context=None):
        self.db_context = db_context or DBContext()
    
    #sets up LLI Context as a singleton
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Context, cls).__new__(cls)
        return cls.instance
