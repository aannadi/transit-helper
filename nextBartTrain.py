import json
import requests
from stations import stations
import sys

BART_API_KEY = "MW9S-E7SL-26DU-VV8V"

def next_bart_train(event):
    dialog_flow_station = event["queryResult"]["parameters"]["station"]
    dialog_flow_direction = event["queryResult"]["parameters"]["cardinal"]

    params, dialog_station_formatting = set_params(dialog_flow_station, dialog_flow_direction)

    r = requests.get("http://api.bart.gov/api/etd.aspx", params = params)
    train_information = r.json()

    train_departure_info= train_information['root']['station'][0]['etd']
    departure_times = []
    for arrival_stations in train_departure_info:
        departure_times += [int(arrival_stations['estimate'][0]['minutes'])]
        departure_times += [int(arrival_stations['estimate'][1]['minutes'])]
    first_departure = min(departure_times)
    departure_times.remove(first_departure)
    second_departure = min(departure_times)


    spoken_response = get_spoken_response(dialog_flow_direction, dialog_station_formatting['spoken_name'],
                        first_departure, second_departure )
    written_response = get_written_response(dialog_flow_direction, dialog_station_formatting['written_name'],
                        first_departure, second_departure )

    return_object = get_return_object(spoken_response, written_response )

    return {
        'statusCode': '200',
        'body': return_object
        }

def set_params(dialog_flow_station, dialog_flow_direction):
    params = {}
    params['key'] = BART_API_KEY
    params['cmd'] = "etd"
    params['json'] = 'y'
    dialog_station_formatting = None
    for x in stations:
        if x['dialog_flow_entity'] == dialog_flow_station:
            params['orig'] = x['abbr']
            dialog_station_formatting = x

    if dialog_flow_direction == "northbound":
        params['dir'] = 'n'
    else:
        params['dir'] = 's'
    return params, dialog_station_formatting

def get_spoken_response(direction, station, time1 , time2 ):
    return  "The next {direction} train leaves {station} in {time1} minutes. \
            Then, another {direction} train will depart {station} station in \
            {time2} minutes".format(direction=direction, station=station,
            time1 = time1, time2 = time2)

def get_written_response(direction, station, time1, time2):
    if direction == "northbound":
        formatted_direction = "North-Bound"
    else:
        formatted_direction = "South-Bound"
    return "The next {direction} train leaves {station} in {time1} minutes. Then,\
            another {direction} train will depart {station} station in \
            {time2} minutes".format(direction=formatted_direction, station=station,
            time1 = time1, time2 = time2)

def get_return_object(spoken, written):
    return json.dumps({
      "fulfillmentText": written,
      "payload": {
        "google": {
          "expectUserResponse": "true",
          "richResponse": {
            "items": [
              {
                "simpleResponse": {
                  "textToSpeech": spoken ,
                  "displayText": written
                }
              }
            ]
          }
        }
      }
    })
