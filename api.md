# API Specification
## Overview of app
This application is modeled after LaundryView, which allows users to view availability of washers and dryers in university laundry rooms across the nation. Since LaundryView has no official application, we implemented their website data and created an app to show availability of washers and dryers across North Campus of Cornell University.

***

## **Get all halls**
 **GET** /api/halls/
 ###### Response
 ```yaml
 {
    "success": true,
    "data": [
        {
            "name": "Balch Hall North",
            "lv_id": "1638314",
            "num_avail_wash": 4,
            "num_avail_dry": 7
        },
        {
            "name": "Bauer Hall",
            "lv_id": "1638358",
            "num_avail_wash": 2,
            "num_avail_dry": 4
        }
     ]
 }
```

## **Get all machines of a hall**
 **GET** /api/hall/{lv_id}/
 ###### Response
 ```yaml
{
    "success": true,
    "data": {
        "name": "Latino Living Center",
        "machines": [
            {
                "machine_name": "01",
                "isWasher": 0,
                "isAvailable": 1,
                "isOOS": 0,
                "isOffline": 0,
                "timeLeft": 60
            },
            {
                "machine_name": "02",
                "isWasher": 1,
                "isAvailable": 1,
                "isOOS": 0,
                "isOffline": 0,
                "timeLeft": 29
            }
     ]
 }
```

## **Create all halls**
 **POST** /api/create/halls/
 ###### Request
 ```yaml
 {
 }
```
###### Response
 ```yaml
{
    "success": true,
    "data": "Halls created!"
}
```

## **Update all halls**
 **POST** /api/update/halls/
 ###### Request
```yaml
{  
}
```
###### Response
 ```yaml
{
    "success": true,
    "data": "Halls availability updated"
}
```

## **Create all machines**
 **POST** /api/create/machines/
 ###### Request
```yaml
{
}
```
###### Response
 ```yaml
{
    "success": true,
    "data": "Machines created for all halls!"
}
```

## **Update all machines**
 **POST** /api/update/machines/
 ###### Request
```yaml
{
}
```
###### Response
 ```yaml
{
    "success": true,
    "data": "Machines updated for all halls!"
}
```

## **Delete hall table**
 **DELETE** /api/hall/table/
###### Response
 ```yaml
{
    "success": true,
    "data": "deleted hall table"
}
```

## **Delete machine table**
 **DELETE** /api/machine/table/
###### Response
 ```yaml
{
    "success": true,
    "data": "deleted machine table"
}
```

## **Insert hall table**
 **POST** /api/hall/table/
###### Response
 ```yaml
{
    "success": true,
    "data": "created hall table"
}
```

## **Insert machine table**
 **POST** /api/machine/table/
###### Response
 ```yaml
{
    "success": true,
    "data": "created machine table"
}
```
