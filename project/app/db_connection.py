import psycopg2
from psycopg2 import sql
import sqlalchemy
from sqlalchemy import create_engine
import os
import time
import random
import json


class Database:

    _columns = {
        "requests": [
            "uuid", "timestamp", "destination", "source", "bssid", "ssid", "signal_strength_wroom",
            "signal_strength_rt",
        ],
        "stations": [
            "uuid", "x", "y", "name", 
        ],
    }
    
    _schemas = {
        "requests":
        "(uuid TEXT PRIMARY KEY, timestamp TEXT, destination TEXT , source TEXT,bssid TEXT, ssid TEXT, signal_strength_wroom TEXT)",
        "stations":
        "(uuid TEXT PRIMARY KEY, x INTEGER, y INTEGER, name TEXT)", 
        
    }

    @classmethod
    def get_columns(cls):
        """ 
        Getter method for columns
        """
        return cls._columns

    @classmethod
    def get_schemas(cls):
        """ 
        Getter method for schemas
        """
        return cls._schemas

class DBConnection:
    """
    This class is responsible for initiating the connection with the 
    PostgreSQL database.
    It provides a clean interface to perform operations on the database.
    
    Attributes:
        _engine: API object used to interact with database.
        _conn: handles connection (encapsulates DB session)
        _cur:  cursor object to execute PostgreSQl commands
    """

    def __init__(self,
                 db_user=os.environ['POSTGRES_USER'],
                 db_password=os.environ['POSTGRES_PASSWORD'],
                 host_addr="localhost:5432",
                 max_num_tries=20):
        """
        Initiates a connection with the PostgreSQL database as the given user 
        on the given port.

        This tries to connect to the database, if not it will retry with 
        increasing waits in between.
      

        Args:
            db_user: the name of the user connecting to the database.
            db_password: the password of said user.
            host_addr: (of the form <host>:<port>) the address where the 
            database is hosted 
            For the Postgres docker container, the default port is 5432 and 
            the host is "database".
            Docker resolves "database" to the internal subnet URL of the 
            database container.
            max_num_tries: the maximum number of tries the __init__ method 
            should try to connect to the database for.
        Returns: None (since __init__)
        Raises:
            IOError: An error occurred accessing the database.
            Raised if after the max number of tries the connection still hasn't
            been established.
        """
        db_name = os.environ['POSTGRES_DB']

        engine_params = (f'postgresql+psycopg2://{db_user}:{db_password}@'
                         f'{host_addr}/{db_name}')
        num_tries = 1

        while True:
            try:
                self._engine = create_engine(engine_params)
                self._conn = self._engine.raw_connection()
                self._cur = self._conn.cursor()
                break
            except (sqlalchemy.exc.OperationalError,
                    psycopg2.OperationalError):
                # Use binary exponential backoff
                #- i.e. sample a wait between [0..2^n]
                #when n = number of tries.
                time.sleep(random.randint(0, 2**num_tries))
                if num_tries > max_num_tries:
                    raise IOError("Database unavailable")
                num_tries += 1

    def create_tables(self):
        """
        Creates the database tables based on schema definition in Database 
        class.

        Args: None
           
        Returns: None (since commits execution result to database)
        """
        for table, schema in Database.get_schemas().items():
            self._cur.execute(
                sql.SQL("CREATE TABLE IF NOT EXISTS {} {}").format(
                    sql.Identifier(table), sql.SQL(schema)))
        self._conn.commit()
    
    def get_database_info(self):
        """
        Returns the data stored in the database, indexed by table.

        Args: None
           
        Returns: A JSON string where keys are table names and values are lists 
        of lists.
        This corresponds to the list of records in that table.
        """
        tables = {}
        self._cur.execute(
            "SELECT table_name FROM information_schema.tables \
       WHERE table_schema = 'public'"
        )  # returns an iterable collection of public tables in the database
        for table in self._cur.fetchall():
            cur2 = self._conn.cursor()
            cur2.execute(
                sql.SQL("SELECT * FROM {} ;").format(sql.Identifier(table[0]))
            )  # note sql module used for safe dynamic SQL queries
            tables[table[0]] = cur2.fetchall()
        return json.dumps(tables)
    
    def clear_data(self):
        """
        Clears the data stored in the database.

        This is useful for bootstrap and unit tests that want to start with a 
        fresh state.

        Args: None
           
        Returns: None
        """
        self._cur.execute(
            "SELECT table_name FROM information_schema.tables WHERE \
            table_schema = 'public'"
        )  # returns an iterable collection of public tables in the database
        for table in self._cur.fetchall():
            cur2 = self._conn.cursor()
            cur2.execute(
                sql.SQL("DELETE FROM {} ;").format(sql.Identifier(table[0]))
            )  # note sql module used for safe dynamic SQL queries
        self._conn.commit()