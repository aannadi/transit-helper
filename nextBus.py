import json
import requests
from stations import stations
import sys
import xml.etree.ElementTree as ET

def next_bus(event):
    dialog_flow_stop = event["queryResult"]["parameters"]["stop"]
    dialog_flow_route = event["queryResult"]["parameters"]["route"]
    dialog_flow_direction = event["queryResult"]["parameters"]["direction"]

    stop_code = get_stop(dialog_flow_route, dialog_flow_stop)
    time = get_next_time(stop_code, dialog_flow_route, dialog_flow_direction)
    if time:
        spoken_response = get_spoken_response(dialog_flow_route, dialog_flow_stop, time)
        written_response = get_written_response(dialog_flow_route, dialog_flow_stop, time)
    else:
        spoken_response = "there are no bus service from that stop right now"
        written_response = "There are no bus service from that stop right now."
    return  {
        'statusCode': '200',
        'body': return_object(spoken_response, written_response)
        }

def get_stop(route, stop):
    url = "http://webservices.nextbus.com/service/publicXMLFeed"
    params = {"command": "routeConfig", "a": "actransit", "r": route}
    r = requests.get(url, params = params)
    root = ET.fromstring(r.text)
    stops = root.findall("./route/stop")
    codes = []
    for s in stops:
        if s.attrib['title'] == stop:
            codes += [s.attrib['tag']]
    return codes

def get_next_time(stop_codes, route, direction):
    for code in stop_codes:
        url = "http://webservices.nextbus.com/service/publicXMLFeed"
        params = {"command": "predictions", "a": "actransit", "r": route, "s": code, "useShortTitles": "true"}
        r = requests.get(url, params = params)
        root = ET.fromstring(r.text)
        direct = root.findall("./predictions/direction")
        if direct[0].attrib['title'] != direction:
            continue
        predictions = root.findall("./predictions/direction/prediction")
        times = []
        for p in predictions:
            times += [int(p.attrib['minutes'])]
        if times:
            return str(min(times)) + " " + str(code)
    return None

def get_spoken_response(route, stop, time ):
    return  "The next {route} train leaves from {stop} in {time} minutes. \
            ".format(route=route, stop=stop,time = time)

def get_written_response(route, stop, time):
    return "The next {route} train leaves {stop} in {time} minutes. \
            ".format(route=route, stop=stop,time = time)

def return_object(spoken, written):
    return json.dumps({
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


if __name__ == '__main__':
    next_bus([])
