################################################################## 
################################################################## 
# NEW CODE
################################################################## 
################################################################## 

import trio
import datetime as dt
import requests
import pandas as pd


#TODO: argument is a Feed object
def get_buses(feed):
    
    positions_df = pd.DataFrame()
    
    return positions_df

################################################################## 
################################################################## 
# OLD CODE
################################################################## 
################################################################## 


################################################################## 
# configuration
################################################################## 

# aws
aws_bucket_name="busobservatory"
aws_region_name="us-east-1"

# system to track
# store api key in secret api_key_{system_id}
# e.g. api_key_nyct_mta_bus_siri
system_id="nyct_mta_bus_siri"
mta_bustime_api_key = get_secret(f'api_key_{system_id}', aws_region_name)['agency_api_key']

# endpoints
url_OBA_routelist = "http://bustime.mta.info/api/where/routes-for-agency/MTA%20NYCT.json?key={}"
url_SIRI_root="http://bustime.mta.info"
url_SIRI_suffix="/api/siri/vehicle-monitoring.json?key={}&VehicleMonitoringDetailLevel=calls&LineRef={}"


################################################################## 
# get current routes
##################################################################   

# fetch from OBA API

def get_OBA_routelist():
    url = url_OBA_routelist.format(mta_bustime_api_key)
    try:
        response = requests.get(url, timeout=5)
    except Exception as e:
        pass
    finally:
        routes = response.json()
    return routes

# generate list of SIRI endpoints to fetch
def get_SIRI_urls():
    SIRI_urls_list = []
    routes=get_OBA_routelist()   
    for route in routes['data']['list']:
        route_id = route['id']

        # entries as tuples vs dicts
        SIRI_urls_list.append(
            (
                route_id,
                url_SIRI_suffix.format(mta_bustime_api_key,route_id)
            )
        )
        
    return SIRI_urls_list

################################################################## 
# fetch all routes, asynchronously
##################################################################   

async def grabber(s,a_path,route_id):
    try:
        r = await s.get(path=a_path, retries=2, timeout=10)
        feeds.append({route_id:r})
    except Exception as e:
        print (f'\t{dt.datetime.now()}\tTimeout or too many retries for {route_id}.')

async def main(url_paths):
    from asks.sessions import Session
    s = Session(url_SIRI_root, connections=25)
    async with trio.open_nursery() as n:
        for (route_id, path) in url_paths:
            n.start_soon(grabber, s, path, route_id )

feeds = []
trio.run(main, get_SIRI_urls())

################################################################## 
# parse
##################################################################   

buses=[]   
for route_report in feeds:
    for route_id,route_data in route_report.items():
        route = route_id.split('_')[1]
        #FIXME: trap this more elegantly
        try:
            route_data=route_data.json()            
            if 'VehicleActivity' in route_data['Siri']['ServiceDelivery']['VehicleMonitoringDelivery'][0]:
                for monitored_vehicle_journey in route_data['Siri']['ServiceDelivery']['VehicleMonitoringDelivery'][0]['VehicleActivity']:
                    bus = BusObservation(route, monitored_vehicle_journey)
                    buses.append(bus)
            else:
                pass
        except:
            pass
positions_df = pd.DataFrame([vars(x) for x in buses])
positions_df['timestamp'] = positions_df['timestamp'].dt.tz_localize(None)





################################################################## 
# BusObservation
##################################################################  

from dateutil import parser

class BusObservation():

    def __init__(self,route,monitored_vehicle_journey):
        self.route = route
        self.parse_buses(monitored_vehicle_journey)

    def __repr__(self):
        output = ''
        # output = None
        for var, val in vars(self).items():
            if var == '_sa_instance_state':
                continue
            else:
                output = output + ('{} {} '.format(var,val))
        return output

    def parse_buses(self, monitored_vehicle_journey):
        lookup = {'route_long':['LineRef'],
                  'direction':['DirectionRef'],
                  'service_date': ['FramedVehicleJourneyRef', 'DataFrameRef'],
                  'trip_id': ['FramedVehicleJourneyRef', 'DatedVehicleJourneyRef'],
                  'gtfs_shape_id': ['JourneyPatternRef'],
                  'route_short': ['PublishedLineName'],
                  'agency': ['OperatorRef'],
                  'origin_id':['OriginRef'],
                  'destination_id':['DestinationRef'],
                  'destination_name':['DestinationName'],
                  'next_stop_id': ['MonitoredCall','StopPointRef'], #<-- GTFS of next stop
                  'next_stop_eta': ['MonitoredCall','ExpectedArrivalTime'], # <-- eta to next stop
                  'next_stop_d_along_route': ['MonitoredCall','Extensions','Distances','CallDistanceAlongRoute'], # <-- The distance of the stop from the beginning of the trip/route
                  'next_stop_d': ['MonitoredCall','Extensions','Distances','DistanceFromCall'], # <-- The distance of the stop from the beginning of the trip/route
                  'alert': ['SituationRef', 'SituationSimpleRef'],
                  'lat':['VehicleLocation','Latitude'],
                  'lon':['VehicleLocation','Longitude'],
                  'bearing': ['Bearing'],
                  'progress_rate': ['ProgressRate'],
                  'progress_status': ['ProgressStatus'],
                  'occupancy': ['Occupancy'],
                  'vehicle_id':['VehicleRef'], #use this to lookup if articulated or not https://en.wikipedia.org/wiki/MTA_Regional_Bus_Operations_bus_fleet
                  'gtfs_block_id':['BlockRef'],
                  'passenger_count': ['MonitoredCall', 'Extensions','Capacities','EstimatedPassengerCount']
                  }
        buses = []
        try:
            setattr(self,'timestamp',parser.isoparse(monitored_vehicle_journey['RecordedAtTime']))
            for k,v in lookup.items():
                try:
                    if len(v) == 2:
                        val = monitored_vehicle_journey['MonitoredVehicleJourney'][v[0]][v[1]]
                        setattr(self, k, val)
                    elif len(v) == 4:
                        val = monitored_vehicle_journey['MonitoredVehicleJourney'][v[0]][v[1]][v[2]][v[3]]
                        setattr(self, k, val)
                    else:
                        val = monitored_vehicle_journey['MonitoredVehicleJourney'][v[0]]
                        setattr(self, k, val)
                except LookupError:
                    # if there's no passenger count, we will set it to null
                    if k == 'passenger_count':
                        setattr(self, k, None)
                except Exception as e:
                    pass
            buses.append(self)
        except KeyError: #no VehicleActivity?
            pass
        return buses

    def to_serial(self):
        def serialize(obj):
            # Recursively walk object's hierarchy.
            if isinstance(obj, (bool, int, float)):
                return obj
            elif isinstance(obj, dict):
                obj = obj.copy()
                for key in obj:
                    obj[key] = serialize(obj[key])
                return obj
            elif isinstance(obj, list):
                return [serialize(item) for item in obj]
            elif isinstance(obj, tuple):
                return tuple(serialize([item for item in obj]))
            elif hasattr(obj, '__dict__'):
                return serialize(obj.__dict__)
            else:
                # return repr(obj) # Don't know how to handle, convert to string
                return str(obj) # avoids single quotes around strings
        # return json.dumps(serialize(self))
        return serialize(self)



################################################################## 
# get_secrets
##################################################################  

import boto3
import base64
from botocore.exceptions import ClientError
import json

def get_secret(secret_name,aws_region_name):

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=aws_region_name)

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e
    else:
        if 'SecretString' in get_secret_value_response:
            return json.loads(get_secret_value_response['SecretString'])
        else:
            return json.loads(base64.b64decode(get_secret_value_response['SecretBinary']))
