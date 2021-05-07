import json
from flask import Flask, request, jsonify
import datetime
import requests
import db
import os

DB = db.DatabaseDriver()

app = Flask(__name__)

input = {"halls": 
        [{"name": "Akwe:kon", "lv_id": "1638342"}, 
        {"name": "Balch Hall North", "lv_id": "1638314"}, 
        {"name": "Balch Hall South", "lv_id": "1638330"}, 
        {"name": "Bauer Hall", "lv_id": "1638358"},
        {"name": "Latino Living Center", "lv_id": "163833"},
        {"name": "Clara Dickson Hall", "lv_id": "1638321"},
        {"name": "Mary Donlon Hall", "lv_id": "1638322"},
        {"name": "George Jameson Hall", "lv_id": "1638324"},
        {"name": "High Rise 5", "lv_id": "1638325"},
        {"name": "Ecology House", "lv_id": "1638317"},
        {"name": "Kay Hall", "lv_id": "1638359"},
        {"name": "Ujamaa", "lv_id": "163837"},
        {"name": "Low Rise 6", "lv_id": "1638326"},
        {"name": "Low Rise 7", "lv_id": "1638312"},
        {"name": "HILC", "lv_id": "1638327"},
        {"name": "Just About Music", "lv_id": "1638310"},
        {"name": "Mews Hall A", "lv_id": "1638356"},
        {"name": "Mews Hall B", "lv_id": "1638357"},
        {"name": "Risley Hall", "lv_id": "1638328"},
        {"name": "Townhouse CC", "lv_id": "1638320"},
        {"name": "Townhouse E", "lv_id": "1638331"},
        {"name": "Townhouse G", "lv_id": "1638332"}]}   

def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code

def failure_response(error, code=404):
    return json.dumps({"success": False, "error": error}), code

# your routes here
@app.route("/api/halls/")
def get_halls():
    return success_response(DB.get_all_halls())

@app.route("/api/hall/<int:lv_id>/")
def get_all_machines_in_hall(lv_id):
    hall = DB.get_hall_by_lv_id(lv_id)
    hall_name = hall[0]["name"]
    if hall is None:
        return failure_response("Hall not found!")
    return success_response(DB.get_hall_by_name(hall_name))


@app.route("/api/create/halls/", methods=["POST"])
def create_halls():
    body = input
    list = body["halls"]

    for x in list:
        name = x["name"]
        lv_id = x["lv_id"]
        num_avail_wash = body.get("num_avail_wash", 0)
        num_avail_dry = body.get("num_avail_dry", 0)

        if name and lv_id is not None:
            DB.insert_hall_table(name, lv_id, num_avail_wash, num_avail_dry)
        else:
            return failure_response("Not enough information! Need name and lv_id to be supplied!", 400)
        
    return success_response("Halls created!")

@app.route("/api/update/halls/", methods=["POST"])
def update_halls():
    body = input
    list1 = body["halls"]

    for y in list1:
        lv_id = y["lv_id"]
        hall = DB.get_hall_by_lv_id(lv_id)
        hall_name = hall[0]["name"]
        if hall is None:
            return failure_response("Hall not found!")

        machine_list = DB.get_hall_by_name(hall_name)["machines"]
        num_avail_wash = 0
        num_avail_dry = 0
        for x in machine_list:
            if (x["isWasher"] == True and x["isAvailable"] == True):
                num_avail_wash += 1
            elif (x["isWasher"] == False and x["isAvailable"] == True):
                num_avail_dry += 1
        DB.update_hall_by_name(hall_name, num_avail_wash, num_avail_dry)

    return success_response("Halls availability updated")

@app.route("/api/update/machines/", methods=["POST"])
def update_machine():
    body = input
    list1 = body["halls"]

    for y in list1:
        lv_id = y["lv_id"]
        hall = DB.get_hall_by_lv_id(lv_id)
        hall_name = hall[0]["name"]
        if hall is None:
            return failure_response("Hall not found!")
        uri = "https://www.laundryview.com/api/currentRoomData?school_desc_key=52&location=" + str(lv_id)
        try:
            uResponse = requests.get(uri)
        except:
            return failure_response("Error with the URI")
        jResponse = uResponse.text
        body = json.loads(jResponse)
        list = body["objects"]

        for x in list:
            if ("appliance_desc_key" in x):
                isOOS = False
                isOffline = False
                machine_name = x["appliance_desc"]
                machine_lv_id = x["appliance_desc_key"]

                if (x["appliance_type"] == "W"):  
                    isWasher = True
                elif (x["appliance_type"] == "D"):
                    isWasher = False

                if (x["time_left_lite"] == "Available"):  
                    isAvailable = True
                elif (x["time_left_lite"] == "Out of service"):
                    isAvailable = False
                    isOOS = True
                elif (x["time_left_lite"] == "Out of service"):
                    isAvailable = False
                    isOffline = True
                else:
                    isAvailable = False
                
                timeLeft = x["time_remaining"]
                DB.update_machine_by_machine_lv_id(machine_lv_id, isAvailable, isOOS, isOffline, timeLeft)  

            if ("appliance_desc_key2" in x):
                isOOS = False
                isOffline = False
                machine_name = x["appliance_desc2"]
                machine_lv_id = x["appliance_desc_key2"]

                if (x["appliance_type"] == "W"):  
                    isWasher = True
                elif (x["appliance_type"] == "D"):
                    isWasher = False

                if (x["time_left_lite2"] == "Available"):  
                    isAvailable = True
                elif (x["time_left_lite2"] == "Out of service"):
                    isAvailable = False
                    isOOS = True
                elif (x["time_left_lite2"] == "Out of service"):
                    isAvailable = False
                    isOffline = True
                else:
                    isAvailable = False
                
                timeLeft = x["time_remaining2"]
                DB.update_machine_by_machine_lv_id(machine_lv_id, isAvailable, isOOS, isOffline, timeLeft)    
    return success_response("Machines updated for all halls!")

@app.route("/api/create/machines/", methods=["POST"])
def create_machines():
    body = input
    list1 = body["halls"]

    for y in list1:
        lv_id = y["lv_id"]
        hall = DB.get_hall_by_lv_id(lv_id)
        hall_name = hall[0]["name"]
        if hall is None:
            return failure_response("Hall not found!")
        uri = "https://www.laundryview.com/api/currentRoomData?school_desc_key=52&location=" + str(lv_id)
        try:
            uResponse = requests.get(uri)
        except:
            return failure_response("Error with the URI")
        jResponse = uResponse.text
        body = json.loads(jResponse)
        list = body["objects"]

        for x in list:
            if ("appliance_desc_key" in x):
                isOOS = False
                isOffline = False
                machine_name = x["appliance_desc"]
                machine_lv_id = x["appliance_desc_key"]

                if (x["appliance_type"] == "W"):  
                    isWasher = True
                elif (x["appliance_type"] == "D"):
                    isWasher = False

                if (x["time_left_lite"] == "Available"):  
                    isAvailable = True
                elif (x["time_left_lite"] == "Out of service"):
                    isAvailable = False
                    isOOS = True
                elif (x["time_left_lite"] == "Out of service"):
                    isAvailable = False
                    isOffline = True
                else:
                    isAvailable = False
                
                timeLeft = x["time_remaining"]
                DB.insert_machine_table(hall_name, machine_name, machine_lv_id, isWasher, isAvailable, isOOS, isOffline, timeLeft)
            
            if ("appliance_desc_key2" in x):
                isOOS = False
                isOffline = False
                machine_name = x["appliance_desc2"]
                machine_lv_id = x["appliance_desc_key2"]

                if (x["appliance_type"] == "W"):  
                    isWasher = True
                elif (x["appliance_type"] == "D"):
                    isWasher = False

                if (x["time_left_lite2"] == "Available"):  
                    isAvailable = True
                elif (x["time_left_lite2"] == "Out of service"):
                    isAvailable = False
                    isOOS = True
                elif (x["time_left_lite2"] == "Out of service"):
                    isAvailable = False
                    isOffline = True
                else:
                    isAvailable = False
                
                timeLeft = x["time_remaining2"]
                DB.insert_machine_table(hall_name, machine_name, machine_lv_id, isWasher, isAvailable, isOOS, isOffline, timeLeft)
    return success_response("Machines created for all halls!")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

