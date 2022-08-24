aws s3 cp config/_bus_observatory_config.json s3://busobservatory/_bus_observatory_config.json &&
sam build --use-container &&
sam local start-api --debug