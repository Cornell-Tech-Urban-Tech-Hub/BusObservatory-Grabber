import json
from libraries.Feed import *
from libraries.DataLake import *
from libraries.Config import *

def lambda_handler(event, context):
    
    # get config
    region="us-east-1"
    bucket="busobservatory"
    config_object_key = "_bus_observatory_config.json"
    config, system_id = get_config(event, 
                        region,
                        bucket,
                        config_object_key)
    
    # fetch + parse data
    feed = Feed(config, system_id)
    positions_df = feed.scrape_feed()

    # dump to S3 as parquet
    dump_buses(region,
                bucket,
                system_id,
                positions_df)

    # report summary
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"BusObservatoryGrabber: wrote {positions_df['vehicle.trip.route_id'].nunique()} routes and {len(positions_df)} buses from {system_id} to s://{bucket}/{system_id}/.",
        }),
    }    
