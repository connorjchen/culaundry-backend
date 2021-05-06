import os
import sqlite3
import datetime

def parse_row(row, columns):
    parsed_row = {}
    for i in range(len(columns)):
        parsed_row[columns[i]] = row[i]
    return parsed_row

def parse_cursor(cursor, columns):
    return [parse_row(row, columns) for row in cursor]

# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for the Task app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        self.conn = sqlite3.connect('CULaundry.db', check_same_thread=False)
        self.create_hall_table()
        self.create_machine_table()
#------------------------------------Hall Model--------------------------------------
    def create_hall_table(self):
        try:
            self.conn.execute(
                """
                CREATE TABLE hall (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    lv_id TEXT NOT NULL,
                    num_avail_wash INTEGER NOT NULL,
                    num_avail_dry INTEGER NOT NULL,
                );
                """
            )
            self.conn.commit()
        except Exception as e:
            print(e)
        
    def get_all_halls(self):
        cursor = self.conn.execute("SELECT * FROM hall;")
        halls = parse_cursor(cursor, ["name", "lv_id", "num_avail_wash", "num_avail_dry"])
        return halls

    def get_hall_by_name(self, hall_name):
        cursor = self.conn.execute("SELECT * FROM hall WHERE name = ?;", (hall_name,))
        hall = parse_cursor(cursor, ["name"])

        #might not work -- txn data thing
        cursor2 = self.conn.execute("SELECT * FROM machine WHERE hall_name = ?;", (hall_name,))
        machineData = parse_cursor(cursor2, ["machine_name", "isWasher", "isAvailable", "isOOS", "timeLeft"])

        hall["machines"]=machineData

        return hall

    def insert_hall_table(self, name, lv_id):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO hall (name, lv_id, num_avail_wash, num_avail_dry) VALUES (?, ?, ?, ?);
            """,
            (name, lv_id, num_avail_wash, num_avail_dry)
        )
        self.conn.commit()
        return cur.lastrowid

    def update_hall_by_name(self, name, num_avail_wash, num_avail_dry):
        self.conn.execute(
            """
            UPDATE hall
            SET num_avail_wash = ?
            SET num_avail_dry = ?
            WHERE name = ?;
        """,
            (num_avail_wash, num_avail_dry, name),
        )
        self.conn.commit()

    def delete_hall_by_name(self, name):
        self.conn.execute(
            """
            DELETE FROM hall WHERE name = ?;
            """,
            (name,)
        )

#------------------------------------Machine Model---------------------------------------
    def create_machine_table(self):
            try:
                self.conn.execute(
                    """
                    CREATE TABLE machine (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        hall_name TEXT SECONDARY KEY NOT NULL,
                        machine_name TEXT NOT NULL,
                        machine_lv_id INTEGER NOT NULL,
                        isWasher BOOLEAN NOT NULL,
                        isAvailable BOOLEAN NOT NULL,
                        isOOS BOOLEAN NOT NULL, 
                        timeLeft INTEGER NOT NULL,
                    );
                """
                )
            except Exception as e:
                print(e)

    def insert_machine_table(self, hall_name, machine_name, machine_lv_id, isWasher, isAvailable, isOOS, timeLeft):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO machine (hall_name, machine_name, machine_lv_id, isWasher, isAvailable, isOOS, timeLeft) VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (hall_name, machine_name, machine_lv_id, isWasher, isAvailable, isOOS, timeLeft)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_all_machines_in_hall(self, hall_name):
        cursor = self.conn.execute("SELECT * FROM machine WHERE hall_name = ?;", (hall_name,))
        machines = parse_cursor(cursor, ["machine_name", "isWasher", "isAvailable", "isOOS", "timeLeft"])
        return machines
    
    def update_machine_by_machine_lv_id(self, machine_lv_id, isAvailable, isOOS, timeLeft):
        self.conn.execute(
            """
            UPDATE machine
            SET isAvailable = ?
            SET isOOS = ?
            SET timeLeft = ?
            WHERE machine_lv_id = ?;
        """,
            (isAvailable, isOOS, timeLeft, machine_lv_id),
        )
        self.conn.commit()

    def delete_machine_by_machine_lv_id(self, machine_lv_id):
        self.conn.execute(
            """
            DELETE FROM machine WHERE machine_lv_id = ?;
            """,
            (machine_lv_id,)
        )

#----------------------------------------------------------------------------
    def delete_user_table(self):
        self.conn.execute(
            """
            DROP TABLE IF EXISTS user;
            """
        )
        self.conn.commit()

    def delete_txn_table(self):
        self.conn.execute(
            """
            DROP TABLE IF EXISTS txn;
            """
        )
        self.conn.commit()    

    def delete_machine_table(self):
        self.conn.execute(
            """
            DROP TABLE IF EXISTS machine;
            """
        )
        self.conn.commit()    

DatabaseDriver = singleton(DatabaseDriver)