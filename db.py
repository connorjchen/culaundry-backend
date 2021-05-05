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
                    numWash INTEGER NOT NULL,
                    numDry INTEGER NOT NULL
                );
                """
            )
            self.conn.commit()
        except Exception as e:
            print(e)
        
    def get_all_users(self):
        cursor = self.conn.execute("SELECT * FROM user;")
        users = parse_cursor(cursor, ["id", "name", "netid"])
        return users

    def insert_user_table(self, name, netid, balance):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO user (name, netid, balance) VALUES (?, ?, ?);
            """,
            (name, netid, balance)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_user_by_id(self, id):
        cursor = self.conn.execute("SELECT * FROM user WHERE ID = ?;", (id,))

        userData = None

        for row in cursor:
            userData= parse_row(row, ["id", "name", "netid", "balance"])

            cursor2 = self.conn.execute("SELECT * FROM txn WHERE user_id = ?;", (id,))

            txnData = []
            for arow in cursor2:
                txnData.append(
                    {
                        "id": arow[0],
                        "timestamp": arow[1],
                        "user_id": arow[2],
                        "hall_anme": arow[3],
                        "machine_name": arow[4],
                        "amount": arow[5],
                    }
                )
            userData["transactions"]=txnData
        if userData is not None:
            return userData
        return None

    def delete_user_by_id(self, id):
        self.conn.execute(
            """
            DELETE FROM user WHERE id = ?;
            """,
            (id,)
        )

    def change_user_balance_by_id(self, user_id, newUserBalance):
        self.conn.execute(
            """
            UPDATE user SET balance=? WHERE id=?;
            """,
            (newUserBalance, user_id)
        )
        self.conn.commit()

#-----------------------Transaction Model---------------------------------

    def create_txn_table(self):
            try:
                self.conn.execute(
                    """
                    CREATE TABLE txn (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        user_id INTEGER SECONDARY KEY NOT NULL,
                        hall_name TEXT NOT NULL,
                        machine_name TEXT NOT NULL, 
                        amount INTEGER NOT NULL
                    );
                """
                )
            except Exception as e:
                print(e)

    def insert_txn_table(self, user_id, hall_name, machine_name, amount):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO txn (timestamp, user_id, hall_name, machine_name, amount) VALUES (?, ?, ?, ?, ?);
            """,
            (datetime.datetime.now(), user_id, hall_name, machine_name, amount)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_txn_by_id(self, id):
        cursor = self.conn.execute("SELECT * FROM txn WHERE ID = ?;", (id,))
 
        for row in cursor:
            return parse_row(row, ["id", "timestamp", "user_id", "hall_name", "machine_name", "amount"])
        return None


#------------------------------------Machine Model---------------------------------------
    def create_machine_table(self):
            try:
                self.conn.execute(
                    """
                    CREATE TABLE machine (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        hall_name TEXT NOT NULL,
                        machine_name TEXT NOT NULL,
                        isWasher BOOLEAN NOT NULL,
                        isAvailable BOOLEAN NOT NULL
                    );
                """
                )
            except Exception as e:
                print(e)

    def insert_machine_table(self, hall_name, machine_name, isWasher, isAvailable):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO machine (hall_name, machine_name, isWasher, isAvailable) VALUES (?, ?, ?, ?);
            """,
            (hall_name, machine_name, isWasher, isAvailable)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_all_machines_in_hall(self, hall_name):
        cursor = self.conn.execute("SELECT * FROM machine WHERE hall_name = ?;", (hall_name,))
        machines = parse_cursor(cursor, ["id", "hall_name", "machine_name", "isWasher", "isAvailable"])
        return machines

    def get_machine_by_id(self, id):
        cursor = self.conn.execute("SELECT * FROM machine WHERE ID = ?;", (id,))
 
        for row in cursor:
            return parse_row(row, ["id", "hall_name", "machine_name", "isWasher", "isAvailable"])
        return None

    # def get_machine_by_name(self, machine_name):
    #     cursor = self.conn.execute("SELECT * FROM machine WHERE machine_name = ?;", (machine_name,))
 
    #     for row in cursor:
    #         return parse_row(row, ["id", "hall_name", "machine_name", "isWasher", "isAvailable"])
    #     return None
    
    def update_machine_by_id(self, machine_id, isAvailable):
        self.conn.execute(
            """
            UPDATE machine
            SET isAvailable = ?
            WHERE id = ?;
        """,
            (isAvailable, machine_id),
        )
        self.conn.commit()


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