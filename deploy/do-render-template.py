import boto3
import json
from jinja2 import Environment, FileSystemLoader


# load config from s3
s3 = boto3.resource("s3")
obj = s3.Object(
    'busobservatory',
    '_bus_observatory_config.json'
    )
config = json.load(obj.get()['Body'])

# load jinja template
environment = Environment(loader=FileSystemLoader("deploy/templates/"))
template = environment.get_template("ScheduledGrabberTemplate.jinja")

# build up the yaml to insert in Events:
entries = []
n = 0
for system_id, system_config in config.items():
    n = n + 1

    content = template.render(
        n=n,
        system_id=system_id,
        system_name=system_config['system_name']
    )
    print(content)
    entries.append(content)

