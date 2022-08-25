# BusObservatory-Grabber-GTFSRT

This project contains code and deployment information for a universal feed grabber AWS Lambda function to obtain needed configuration and scrape a bus data feed and write it to an S3 data lake.

Takes a system_id in the query URL and reads config from S3 bucket.
 
## setup
Takes a config `config/_bus_observatory_config.json`file like

```
{
    "tfnsw_buses_test":{
        "feed_type":"gtfsrt",
        "url":"https://api.transport.nsw.gov.au/v1/gtfs/vehiclepos/buses",
        "api_key":"sfhas9fas9fa9sf9asf89asf89asf",
        "header": "True",
        "header_format": {
            "key_name": "Authorization",
            "template": "apikey {key_value}"
            },
        "route_key":"vehicle.route",
        "tz": "Australia/Sydney"
    },
    "nyct_mta_bus_siri_test":{
        "feed_type":"siri",
        "url":"http://gtfsrt.prod.obanyc.com/vehiclePositions?key={}",
        "api_key":"sfhas9fas9fa9sf9asf89asf89asf",
        "header": "False",
        "route_key":"route",
        "tz": "America/New_York"
    }
```

## Testing

### local

```
    aws sso login
    sam build --use-container && sam local start-api --debug
```

Then head over to

`http://127.0.0.1:3000/BusObservatoryGrabber?system_id=tfnsw_buses`

or

`n`
`http://127.0.0.1:3000/BusObservatoryGrabber?system_id=TEST_njtransit_bus`
`http://127.0.0.1:3000/BusObservatoryGrabber?system_id=TEST_nyct_mta_bus_siri`
`http://127.0.0.1:3000/BusObservatoryGrabber?system_id=TEST_nyct_mta_bus_gtfsrt`

### cloud

Takes about 2-3 minutes on M1 MacBook Air laptop.

```
    sam build --use-container &&
    sam deploy \
        --stack-name Busobservatory-Grabber \
        --s3-bucket busobservatory-grabber \
        --capabilities CAPABILITY_IAM
```

Then head over to

`http://aws-lambda-execute.com/BusObservatoryGrabber?system_id=tfnsw_buses`




## Development Information

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

- hello_world - Code for the application's Lambda function.
- events - Invocation events that you can use to invoke the function.
- tests - Unit tests for the application code. 
- template.yaml - A template that defines the application's AWS resources.

The application uses several AWS resources, including Lambda functions and an API Gateway API. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.


### Deploy the application

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3 installed](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build --use-container
sam deploy --guided
```

The first command will build the source of your application. The second command will package and deploy your application to AWS, with a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modifies IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

You can find your API Gateway Endpoint URL in the output values displayed after deployment.

### Use the SAM CLI to build and test locally

#TODO: Define a stack name for each configured instance
AWS_SAM_STACK_NAME=<stack-name> 

#TODO: Pass the config in? how

Build your application with the `sam build --use-container` command.

```bash
$ sam build --use-container
```

The SAM CLI installs dependencies defined in `hello_world/requirements.txt`, creates a deployment package, and saves it in the `.aws-sam/build` folder.

Test a single function by invoking it directly with a test event. An event is a JSON document that represents the input that the function receives from the event source. Test events are included in the `events` folder in this project.

Run functions locally and invoke them with the `sam local invoke` command.

```bash
$ sam local invoke HelloWorldFunction --event events/event.json
```

The SAM CLI can also emulate your application's API. Use the `sam local start-api` to run the API locally on port 3000.

```bash
$ sam local start-api
$ curl http://localhost:3000/
```

The SAM CLI reads the application template to determine the API's routes and the functions that they invoke. The `Events` property on each function's definition includes the route and method for each path.

```yaml
      Events:
        HelloWorld:
          Type: Api
          Properties:
            Path: /hello
            Method: get
```

### Add a resource to your application
The application template uses AWS Serverless Application Model (AWS SAM) to define application resources. AWS SAM is an extension of AWS CloudFormation with a simpler syntax for configuring common serverless application resources such as functions, triggers, and APIs. For resources not included in [the SAM specification](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md), you can use standard [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html) resource types.

## #Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
$ sam logs -n HelloWorldFunction --stack-name $AWS_SAM_STACK_NAME --tail
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

### Tests

Tests are defined in the `tests` folder in this project. Use PIP to install the test dependencies and run tests.

```bash
$ pip install -r tests/requirements.txt --user
# unit test
$ python -m pytest tests/unit -v
# integration test, requiring deploying the stack first.
# Create the env variable AWS_SAM_STACK_NAME with the name of the stack we are testing
$ AWS_SAM_STACK_NAME=<stack-name> python -m pytest tests/integration -v
```

### Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name $AWS_SAM_STACK_NAME
```

### Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)
