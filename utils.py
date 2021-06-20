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

def create_db_connection():
    """
    Opens a database connection.
    """
    Path("data").mkdir(parents=True, exist_ok=True)
    dir = Path("data")
    filename = "results.db"
    filepath = dir / filename
    return sqlite3.connect(filepath)

def yes_or_no(question):
    """ Simple yes no choice function. """
    reply = str(input(f"{question} (y/n): ")).lower().strip()
    if reply[0] == "y":
        return True
    if reply[0] == "n":
        return False
    else:
        return yes_or_no("Please enter y/n")

def clear_database():
    try:
        remove_db = Path('data/results.db')
        remove_db.unlink()
    except:
        pass

def df_to_db(agg_dict):
    """ Saves results dataframes to the sqlite3 database"""
    engine = create_db_connection()

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

