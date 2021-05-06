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
@app.route("/api/halls/")
def get_halls():
    return success_response(DB.get_all_halls)

@app.route("/api/<string:hall_name>/")
def get_all_machines_in_hall(hall_name):
    return success_response(DB.get_hall_by_name)

#hard code this in - write own thing in postman
@app.route("/api/halls/", methods=["POST"])
def create_hall():
    body = json.loads(request.data)
    name = body.get("name")
    lv_id = body.get("lv_id")
    num_avail_wash = body.get("num_avail_wash", 0)
    num_avail_dry = body.get("num_avail_dry", 0)

    if name and lv_id and num_avail_wash and num_avail_dry is not None:
        hall_id = DB.insert_hall_table(name, lv_id, num_avail_wash, num_avail_dry)
        return success_response(DB.get_hall_by_name(name))
    return failure_response("Not enough information! Need name and lv_id supplied!", 400)

@app.route("/api/halls/numAvail", methods=["POST"])
def update_halls():
    hall_list = DB.get_all_halls()

    if hall_list is None:
        return failure_response("No halls found")

    for x in hall_list:
        hall_name = x["name"]
        machine_list = get_all_machines_in_hall(hall_name)
        num_avail_wash = 0
        num_avail_dry = 0
        for y in machine_list:
            if (y["isWasher"] == True and y["isAvailable"] == True):
                num_avail_wash += 1
            elif (y["isWasher"] == False and y["isAvailable"] == True):
                num_avail_dry += 1
        DB.update_hall_by_name(hall_name, num_avail_wash, num_avail_dry)

    return success_response("Halls availability updated")

#have it update all machines 
@app.route("/api/machines/<string:hall_name>/", methods=["POST"])
def update_machines(hall_name):
    uri = "https://www.laundryview.com/api/currentRoomData?school_desc_key=52&location=" + DB.get_hall_by_name(hall_name)["lv_id"]
    try:
        uResponse = requests.get(uri)
    except requests.ConnectionError:
        return failure_response("Connection Error")
    jResponse = uResponse.text
    body = json.loads(jResponse)
    list = body["objects"]

    for x in list:
        if (x["appliance_desc_key"] is not None):
            isOOS = False
            machine_lv_id = x["appliance_desc_key"]

            if (x["time_left_lite"] == "Available"):  
                isAvailable = True
            elif (x["time_left_lite"] == "Ext. Cycle"):
                isAvailable = False
            elif (x["time_left_lite"] == "Out of service"):
                isAvailable = False
                isOOS = True
            else:
                isAvailable = False
            
            timeLeft = x["time_remaining"]

            if machine_lv_id and isAvailable and isOOS and timeLeft is not None:
                DB.update_machine_by_machine_lv_id(machine_lv_id, isAvailable, isOOS, timeLeft)
            else:
                return failure_response("Not enough information! Need machine_lv_id, isAvailable, isOOS, and timeLeft to be supplied!", 400)
        
    return success_response("Machines updated!")

@app.route("/api/create/machines/<string:hall_name>/", methods=["POST"])
def create_machine(hall_name):
    uri = "https://www.laundryview.com/api/currentRoomData?school_desc_key=52&location=" + DB.get_hall_by_name(hall_name)["lv_id"]
    try:
        uResponse = requests.get(uri)
    except requests.ConnectionError:
        return failure_response("Connection Error")
    jResponse = uResponse.text
    body = json.loads(jResponse)
    list = body["objects"]

    for x in list:
        if (x["appliance_desc_key"] is not None):
            isOOS = False
            machine_name = x["appliance_desc"]
            machine_lv_id = x["appliance_desc_key"]

            if (x["appliance_type"] == "W"):  
                isWasher = True
            elif (x["appliance_type"] == "D"):
                isWasher = False

            if (x["time_left_lite"] == "Available"):  
                isAvailable = True
            elif (x["time_left_lite"] == "Ext. Cycle"):
                isAvailable = False
            elif (x["time_left_lite"] == "Out of service"):
                isAvailable = False
                isOOS = True
            else:
                isAvailable = False
            
            timeLeft = x["time_remaining"]

            if machine_name and isWasher machine_lv_id and isAvailable and isOOS and timeLeft is not None:
                DB.insert_machine_table(hall_name, machine_name, machine_lv_id, isWasher, isAvailable, isOOS, timeLeft)
            else:
                return failure_response("Not enough information! Need machine_name, machine_lv_id, isAvailable, isOOS, and timeLeft to be supplied!", 400)
        
    return success_response("Machines created for hall!")

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

#--------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

