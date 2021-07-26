###############################################################################
#
# Software program written by Neil Murphy in year 2021.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# By using this software, the Disclaimer and Terms distributed with the
# software are deemed accepted, without limitation, by user.
#
# You should have received a copy of the Disclaimer and Terms document
# along with this program.  If not, see... https://bit.ly/2Tlr9ii
#
###############################################################################
from datetime import datetime
import itertools
import math
from pathlib import Path
import sqlite3

def time_str_to_datetime(time):
    return datetime.strptime(time, "%H:%M").time()

def round_down(x):
    return math.trunc(x * 4) / 4

def round_up(x):
    return math.ceil(x * 4) / 4

def time_tuple(d):
    keys, values = zip(*d.items())
    return [tuple(dict(zip(keys, v)).items()) for v in itertools.product(*values)]

def yes_or_no(question):
    """ Simple yes no choice function. """
    reply = str(input(f"{question} (y/n): ")).lower().strip()
    if reply[0] == "y":
        return True
    if reply[0] == "n":
        return False
    else:
        return yes_or_no("Please enter y/n")

""" Database Utilities """

def create_db_connection(db=None):
    """
    Opens a database connection.
    """
    root = Path(__file__).parent
    Path("data").mkdir(parents=True, exist_ok=True)
    dir = Path("data")

    if db == "backtest":
        filename = "backtest.db"
    elif db == "live":
        filename = "live.db"
    else:
        raise ValueError(
            "You must indicate which database you are connecting to. "
            "You may choose either `backtest` or `live`"
        )
    filepath = root / dir / filename
    return sqlite3.connect(filepath, uri=False)

def df_to_db(agg_dict):
    """ Saves results dataframes to the sqlite3 database"""
    engine = create_db_connection(db="backtest")

    for table_name, df in agg_dict.items():
        try:
            # Remove whitespace before going to sql.
            df.columns = [name.replace(" ", "_") for name in df.columns]
            df.to_sql(
                table_name, con=engine, if_exists="append", index=False
            )
        except Exception as e:
            print(f"{e} {table_name} failed.")
    engine.close()

def clear_database(db=None):
    conn = create_db_connection(db=db)
    clear_tables(conn)

def clear_tables(conn):
    tables = all_tables(conn)
    # cursor = conn.cursor()
    for table in tables:
        sql = f'DELETE FROM {table};'
        conn.execute(sql);

    conn.commit()
    # cursor.close()
    conn.close()

def all_tables(conn):
    cursor = conn.execute(f"SELECT name FROM sqlite_master WHERE type='table';")
    tables = [
        v[0] for v in cursor.fetchall()
        if v[0] != "sqlite_sequence"
    ]
    cursor.close()
    return tables

def write_row(table, row, row_names=None):
    conn = create_db_connection(db='live')
    cur = conn.cursor()
    rowcursor = conn.execute(f'select * from {table}')
    names = list(map(lambda x: x[0], rowcursor.description))

    sql = f"INSERT INTO {table}({', '.join(names)}) VALUES ({('?, ' * len(row))[:-2]}) "

    cur.execute(sql, row)
    conn.commit()
    conn.close()
