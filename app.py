import json
from flask import Flask, request
import datetime
import db
import os

DB = db.DatabaseDriver()

app = Flask(__name__)

def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code

def failure_response(error, code=404):
    return json.dumps({"success": False, "error": error}), code

@app.route("/")
def hello_world():
    return "Hello world!"

# your routes here

@app.route("/api/machines/<string:hall_name>/")
def get_all_machines_in_hall(hall_name):
    return success_response(DB.get_all_machines_in_hall(hall_name))

@app.route("/api/machines/availability/", methods=["POST"])
def update_machine_availability():
    body = json.loads(request.data)
    machine_id = body.get("machine_id")
    isAvailable = body.get("isAvailable")

    machine = DB.get_machine_by_id(machine_id)

    if machine is None: 
        return failure_response("Machine not found!")
    if machine_id and isAvailable is not None:
        DB.update_machine_by_id(machine_id, isAvailable)
        return success_response(DB.get_machine_by_id(machine_id))
    
    return failure_response("Not enough information! Need machine_id and isAvailable to be supplied!", 400)

@app.route("/api/machines/", methods=["POST"])
def create_machine():
    body = json.loads(request.data)
    hall_name = body.get("hall_name")
    machine_name = body.get("machine_name")
    isWasher = body.get("isWasher")
    isAvailable = body.get("isAvailable", True)

    if hall_name and machine_name and isWasher is not None:
        machine_id = DB.insert_machine_table(hall_name, machine_name, isWasher, isAvailable)
        return success_response(DB.get_machine_by_id(machine_id))
    return failure_response("Not enough information! Need hall_name, machine_name, isWasher, and isAvailable supplied!", 400)

#------------------------Delete Tables------------------

@app.route("/api/users/table/", methods=["DELETE"])
def delete_user_table():
    DB.delete_user_table()
    return success_response("deleted user table")

@app.route("/api/txn/table/", methods=["DELETE"])
def delete_txn_table():
    DB.delete_txn_table()
    return success_response("deleted txn table")

@app.route("/api/machine/table/", methods=["DELETE"])
def delete_machine_table():
    DB.delete_machine_table()
    return success_response("deleted machine table")

#-------------------------Manual Insert Tables----------------

@app.route("/api/users/table/", methods=["POST"])
def create_user_table():
    DB.create_user_table()
    return success_response("created user table")

@app.route("/api/txn/table/", methods=["POST"])
def create_txn_table():
    DB.create_txn_table()
    return success_response("created txn table")

@app.route("/api/machine/table/", methods=["POST"])
def create_machine_table():
    DB.create_machine_table()
    return success_response("created machine table")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

