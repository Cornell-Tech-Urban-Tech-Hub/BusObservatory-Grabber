import json

import boto3
import os
import requests
from lib import GTFSRT, DataLake
# from lib import GTFSRT, SIRI, NJXML

def lambda_handler(event, context):
    
    ################################################################## 
    # configuration
    ################################################################## 

    # aws -- these can be hardcoded
    region="us-east-1"
    bucket="busobservatory"
    config_object_key = "_bus_observatory_config.json"
        
    # system to track
    try:
        system_id = event['queryStringParameters']['system_id']
    except KeyError:
        raise Exception("No system_id specified")
    
    # read config
    s3 = boto3.resource("s3")
    obj = s3.Object(bucket, config_object_key)
    
    #FIXME: catch if there's no matching system_id and return a 404
    try:
        config = json.load(obj.get()['Body'])[system_id]
    except:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": f"cannot find feed for system_id:{system_id}",
            }),
        } 
    ################################################################## 
    # fetch data
    ##################################################################   
    if config['header'] == 'True':
        key_name = config['header_format']['key_name']
        key_value = config['header_format']['template'].format(key_value=config['api_key']) 
        header = {key_name:key_value}
        url = config['url']
    else:
        url = config['url'](config['api_key'])
        header = None
    response = requests.get(url, headers=header)

    ################################################################## 
    # parse data
    ##################################################################
    if config['feed_type'] == "gtfsrt":
        positions_df = GTFSRT.parse_feed(response,config)
    # elif config['feed_type'] == "siri":
    #     positions_df = SIRI.parse_feed(response,config)
    # elif config['feed_type'] == "njxml":
    #     positions_df = XML.parse_feed(response,config)

    ################################################################## 
    # dump to S3 as parquet 
    ##################################################################   
    DataLake.dump_buses(region,
                        bucket,
                        system_id,
                        positions_df)

    ################################################################## 
    # report back to invoker
    ##################################################################  
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"BusObservatoryGrabber: wrote {positions_df['vehicle.trip.route_id'].nunique()} routes and {len(positions_df)} buses from {system_id} to s://{bucket}/{system_id}/.",
        }),
    }    
