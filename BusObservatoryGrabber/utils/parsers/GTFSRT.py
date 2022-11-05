from google.transit import gtfs_realtime_pb2
from protobuf_to_dict import protobuf_to_dict
import pandas as pd
import requests

def get_buses(feed):

    # get data
    try:
        response = requests.get(feed.url.format(feed.api_key), headers=feed.header)
    except:
        response = requests.get(feed.url, headers=feed.header)

    # flatten data
    data = gtfs_realtime_pb2.FeedMessage()
    data.ParseFromString(response.content)
    
    # convert protobuf to dict
    buses_dict = protobuf_to_dict(data) 

    # convert dict to dataframe
    positions_df=pd.json_normalize(buses_dict['entity'])
    
    # make sure direction doesnt output as an int for nyct_mta_bus_siri
    try:
        positions_df = positions_df.astype({"vehicle.trip.direction_id": float})
    except KeyError:
        pass
    
    # convert timestamp is 4 steps to get local time recorded properly in parquet
    
    # 1 convert POSIX timestamp to datetime
    positions_df['vehicle.timestamp'] = pd.to_datetime(positions_df['vehicle.timestamp'], unit="s")
    
    # 2 tell pandas its UTC
    positions_df['vehicle.timestamp'] = positions_df['vehicle.timestamp'].dt.tz_localize('UTC')
    
    # 3 convert the offset to local time
    positions_df['vehicle.timestamp'] = positions_df['vehicle.timestamp'].dt.tz_convert(feed.tz)
    # positions_df['vehicle.timestamp'] = positions_df['vehicle.timestamp'].dt.tz_convert(feed.config['tz'])
    
    # 4 make naive again (not sure why this is needed)
    positions_df['vehicle.timestamp'] = positions_df['vehicle.timestamp'].dt.tz_localize(None)
    
    
    return positions_df
