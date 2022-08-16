aws s3 cp config/_bus_observatory_config.json s3://busobservatory/_bus_observatory_config.json &&
sam build --use-container &&
sam deploy \
    --stack-name BusObservatoryGrabber \
    --s3-bucket busobservatory \
    --s3-prefix _deployed_code/BusObservatoryGrabber \
    --capabilities CAPABILITY_IAM