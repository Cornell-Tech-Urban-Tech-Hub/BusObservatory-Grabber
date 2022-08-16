aws s3 cp config/bus_observatory_config.json s3://busobservatory/bus_observatory_config.json &&
sam build --use-container &&
sam local start-api --debug