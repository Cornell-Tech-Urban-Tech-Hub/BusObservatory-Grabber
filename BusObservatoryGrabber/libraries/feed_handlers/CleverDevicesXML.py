################################################################## 
################################################################## 
# NEW CODE
################################################################## 
################################################################## 


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
# fetch data
##################################################################   

data, fetch_timestamp = get_xml_data('nj','all_buses')

################################################################## 
# parse data
##################################################################

positions = pd.DataFrame([vars(bus) for bus in parse_xml_getBusesForRouteAll(data)])
positions['timestamp'] = fetch_timestamp
positions = positions.drop(['name','bus'], axis=1) 
positions[["lat", "lon"]] = positions[["lat", "lon"]].apply(pd.to_numeric)


import os
import xml.etree.ElementTree
import time
from math import cos, asin, sqrt
from datetime import datetime, date
import typing
from starlette.responses import Response
import json
from dateutil.parser import isoparse


# API like: https://github.com/harperreed/transitapi/wiki/Unofficial-Bustracker-API

_sources = {
  'nj': 'http://mybusnow.njtransit.com/bustime/map/'
}

_api = {
  'all_buses': 'getBusesForRouteAll.jsp',
  'route_points': 'getRoutePoints.jsp',
  'pattern_points': 'getPatternPoints.jsp',
  'stop_predictions': 'getStopPredictions.jsp',
  'bus_predictions': 'getBusPredictions.jsp',
  'buses_for_route': 'getBusesForRoute.jsp',
  'schedules': 'schedules.jsp',
  'time_and_temp': 'getTimeAndTemp.jsp',
  'route_directions_xml':  'routeDirectionStopAsXML',
}


def _gen_command(source, func, **kwargs):
    result = _sources[source] + _api[func]
    params = ''
    for k, v in list(kwargs.items()):
        params = params + k + '=' + str(v) + '&'
    if params:
        result += '?' + params[:-1]
    return result

def _cond_get_single(tree, key, default=''):
    res = tree.find(key)
    if res is not None:
        return res.text 
    return default

class KeyValueData:
    def __init__(self, **kwargs):
        self.name = 'KeyValueData'
        for k, v in list(kwargs.items()):
            setattr(self, k, v)

    def add_kv(self, key, value):
        setattr(self, key, value)

    def __repr__(self):
        line = []
        for prop, value in vars(self).items():
            line.append((prop, value))
        line.sort(key=lambda x: x[0])
        out_string = ' '.join([k + '=' + str(v) for k, v in line])
        return self.name + '[%s]' % out_string

    def to_dict(self):
        line = []
        for prop, value in vars(self).items():
            line.append((prop, value)) # list of tuples
        line.sort(key=lambda x: x[0])
        out_dict = dict()
        for l in line:
            out_dict[l[0]]=l[1]
        return out_dict

class Bus(KeyValueData):
    def __init__(self, **kwargs):
        KeyValueData.__init__(self, **kwargs)
        self.name = 'Bus'


class Route(KeyValueData):

    class Path(KeyValueData):
        def __init__(self):
            KeyValueData.__init__(self)
            self.name = 'Path'
            self.points = []
            self.id = ''
            self.d = ''
            self.dd = ''

    class Point(KeyValueData):
        def __init__(self):
            KeyValueData.__init__(self)
            self.name = 'Point'
            self.lat = ''
            self.lon = ''
            self.d = ''
            # self.waypoint_id = '' # are we using this?
            self.distance_to_prev_waypoint = ''

    class Stop(KeyValueData):
        def __init__(self):
            KeyValueData.__init__(self)
            self.name = 'Stop'
            self.identity = ''
            self.st = ''
            self.lat = ''
            self.lon = ''
            self.d = ''

    def __init__(self):
        KeyValueData.__init__(self)
        self.name = 'route'
        self.identity = ''
        self.paths = []

class StopPrediction(KeyValueData):
    def __init__(self, **kwargs):
        KeyValueData.__init__(self, **kwargs)
        self.name = 'StopPrediction' 


def parse_xml_getStopPredictions(data):
    results = []
    e = xml.etree.ElementTree.fromstring(data)
    for atype in e.findall('pre'):
        fields = {}
        for field in atype.getchildren():
            if field.tag not in fields and hasattr(field, 'text'):
                if field.text is None:
                    fields[field.tag] = ''
                    continue
                fields[field.tag] = field.text

        results.append(StopPrediction(**fields))

        # go through and append the stop id and name to every result
        stop_id = e.find('id').text
        stop_nm = e.find('nm').text
        for prediction in results:
            prediction.stop_id = stop_id 
            prediction.stop_name = stop_nm 
            # and split the integer out of the prediction
            prediction.pt = prediction.pt.split(' ')[0]
    return results

def parse_xml_getBusesForRouteAll(data):
    results = []
    e = xml.etree.ElementTree.fromstring(data)
    for atype in e.findall('bus'):
        fields = {}
        for field in list(atype.iter()):
            if field.tag not in fields and hasattr(field, 'text'):
                if field.text is None:
                    fields[field.tag] = ''
                    continue
                fields[field.tag] = field.text

        results.append(Bus(**fields))

    return clean_buses(results)


# http://mybusnow.njtransit.com/bustime/map/getBusesForRoute.jsp?route=119
def parse_xml_getBusesForRoute(data):
    results = []
    e = xml.etree.ElementTree.fromstring(data)
    for atype in e.findall('bus'):
        fields = {}
        for field in atype.getchildren():
            if field.tag not in fields and hasattr(field, 'text'):
                if field.text is None:
                    fields[field.tag] = ''
                    continue
                fields[field.tag] = field.text

        results.append(Bus(**fields))
    return clean_buses(results)


def clean_buses(buses):
    buses_clean = []
    for bus in buses:
        if bus.run.isdigit() is True:  # removes any buses with non-number run id, and this should populate throughout the whole project
            if bus.rt.isdigit() is True:  # removes any buses with non-number route id, and this should populate throughout the whole project
                buses_clean.append(bus)

    return buses_clean


def validate_xmldata(xmldata):
    e = xml.etree.ElementTree.fromstring(xmldata)
    for child in e.getchildren():
        if child.tag == 'pas':
            if len(child.findall('pa')) == 0:
                print('Route not valid')
                return False
            elif len(child.findall('pa')) > 0:
                return True


def parse_xml_getRoutePoints(data):
    coordinates_bundle=dict()
    routes = list()
    route = Route()
    e = xml.etree.ElementTree.fromstring(data)
    for child in e.getchildren():
        if len(child.getchildren()) == 0:
            if child.tag == 'id':
                route.identity = child.text
            # bug we make lat, lon into float as soon as fetched? why are they string in the dict later?
            else:
                route.add_kv(child.tag, child.text)
        if child.tag == 'pas':
            n = 0
            p_prev = None
            for pa in child.findall('pa'):
                path = Route.Path()
                for path_child in pa.getchildren():
                    if len(path_child.getchildren()) == 0:
                        if path_child.tag == 'id':
                            path.id = path_child.text
                        elif path_child.tag == 'd':
                            path.d = path_child.text
                        elif path_child.tag == 'dd':
                            path.dd = path_child.text
                        else:
                            path.add_kv(path_child.tag, path_child.text)
                    elif path_child.tag == 'pt':
                        pt = path_child
                        stop = False
                        for bs in pt.findall('bs'):
                            stop = True
                            _stop_id = _cond_get_single(bs, 'id')
                            _stop_st = _cond_get_single(bs, 'st')
                            break
                        p = None
                        if not stop:
                            p = Route.Point()
                        else:
                            p = Route.Stop()
                            p.identity = _stop_id
                            p.st = _stop_st
                        p.d = path.d
                        p.lat = float(_cond_get_single(pt, 'lat'))
                        p.lon = float(_cond_get_single(pt, 'lon'))
                        p.waypoint_id = n
                        if n != 0:
                            p.distance_to_prev_waypoint = distance(p_prev.lat, p_prev.lon, p.lat, p.lon)
                        p_prev = p
                        n =+ 1
                        path.points.append(p)
                route.paths.append(path)
                routes.append(route)
            break

    return routes


def get_xml_data(source, function, **kwargs):
    import urllib.request
    tries = 1
    while True:
        try:
            data = urllib.request.urlopen(_gen_command(source, function, **kwargs)).read()
            if data:
                timestamp=datetime.now()
                break
        except Exception as e:
            print (e)
            print (str(tries) + '/12 cant connect to NJT API... waiting 5s and retry')
            if tries < 12:
                tries = tries + 1
                time.sleep(5)
            else:
                print('failed trying to connect to NJT API for 1 minute, giving up')
                # bug handle this better than TypeError: cannot unpack non-iterable NoneType object
                return
    return data, timestamp


def get_xml_data_save_raw(source, function, raw_dir, **kwargs):
    data = get_xml_data(source, function, **kwargs)
    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)
    now = datetime.now()
    handle = open(raw_dir + '/' + now.strftime('%Y%m%d.%H%M%S') + '.' + source + '.xml', 'w')
    handle.write(data)
    handle.close()
    return data




#--------------- HELPER FUNCTIONS ---------------

def unpack_query_results(query):
    return [dict(zip(tuple(query.keys()), i)) for i in query.cursor]

def query_builder(parameters):
    query_suffix = ''
    for field, value in parameters.items():
        if field == 'output':
            continue
        elif field == 'start':
            query_suffix = query_suffix + '{} >= "{}" AND ' \
                .format('timestamp', isoparse(value.replace(" ", "+", 1)))
            # replace is a hack but gets the job done because + was stripped from url replaced by space
            continue
        elif field == 'end':
            query_suffix = query_suffix + '{} < "{}" AND ' \
                .format('timestamp', isoparse(value.replace(" ", "+", 1)))
            continue
        elif field == 'rt':
            query_suffix = query_suffix + '{} = "{}" AND '.format('rt', value)
            continue
        else:
            query_suffix = query_suffix + '{} = "{}" AND '.format(field,value)
    query_suffix=query_suffix[:-4] # strip tailing ' AND'
    return query_suffix


def results_to_FeatureCollection(results):
    geojson = {'type': 'FeatureCollection', 'features': []}
    # for row in results['observations']:
    for row in results:
        feature = {'type': 'Feature',
                   'properties': {},
                   'geometry': {'type': 'Point',
                                'coordinates': []}}
        feature['geometry']['coordinates'] = [float(row['lon']), float(row['lat'])]
        for k, v in row.items():
            if isinstance(v, (datetime, date)):
                v = v.isoformat()
            feature['properties'][k] = v
        geojson['features'].append(feature)
    return geojson


#future test debug kepler output
def make_KeplerTable(query):
    results = query['observations']
    fields = [{"name":x} for x in dict.keys(results[0])]

    # make the fields list of dicts
    field_list =[]
    for f in fields:
        fmt='TBD'
        typ=type(f)
        # field_list.append("{name: '{}', format '{}', type:'{}'},".format(f,fmt,typ))
        # field_list.append("{name: '{}'},".format(f))
        field_list.append("{'TBD':'TBD',")
    # make the rows list of lists
    rows = []
    for r in results:
        (a, row)= zip(*r.items())
        rows.append(r)
    kepler_bundle = {"fields": fields, "rows": rows }
    return kepler_bundle


def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 5280 * (7918 * asin(sqrt(a))) # https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula/11178145


class PrettyJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(", ", ": "),
        ).encode("utf-8")
