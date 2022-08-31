import os
import json
from utils.Feed import *
from utils.DataLake import *
from utils.Config import *

def lambda_handler(event, context):

    # config
    bucket=os.environ['S3_BUCKET']
    region=os.environ['AWS_REGION']
    # bucket="busobservatory"
    # bucket="busobservatory-migration"
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
            "message": f"{system_id}: wrote {positions_df[feed.route_key].nunique()} routes and {len(positions_df)} buses from {system_id} to s3://{bucket}/{system_id}/",
        }),
    }    
