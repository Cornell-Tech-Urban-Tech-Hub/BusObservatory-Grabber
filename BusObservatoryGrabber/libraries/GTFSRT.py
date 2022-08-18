from google.transit import gtfs_realtime_pb2
from protobuf_to_dict import protobuf_to_dict
import pandas as pd

def parse_feed(response, config):

    # flatten data
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
    
    # convert protobuf to dict
    buses_dict = protobuf_to_dict(feed) 

    # convert dict to dataframe
    positions_df=pd.json_normalize(buses_dict['entity'])
    
    # convert timestamp is 4 steps to get local time recorded properly in parquet
    # 1 convert POSIX timestamp to datetime
    positions_df['vehicle.timestamp'] = pd.to_datetime(positions_df['vehicle.timestamp'], unit="s")
    # 2 tell pandas its UTC
    positions_df['vehicle.timestamp'] = positions_df['vehicle.timestamp'].dt.tz_localize('UTC')
    # 3 convert the offset to local time
    positions_df['vehicle.timestamp'] = positions_df['vehicle.timestamp'].dt.tz_convert(config['tz'])
    # 4 make naive again (not sure why this is needed)
    positions_df['vehicle.timestamp'] = positions_df['vehicle.timestamp'].dt.tz_localize(None)
    
    return positions_df
