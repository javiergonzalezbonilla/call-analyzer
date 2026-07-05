# Questions

## How does this scale to 10k calls/day?

### Answer

It would scale by using lambda functions for audio file processing, removing the need for a celery process. Since lambda functions can be configured to trigger when a file uploads, the lambda function can call the STT API, create the needed records in the DB, and save other results in a different bucket for further analysis. Lambda functions are scalable by default since AWS manages the underlying infrastructure for us, and cost is not a concern since they are serverless and we only pay for what we use.

## Where are the bottlenecks?

### Answer

Bottlenecks are mainly in the upload process on the user side, because it depends on the user's internet connection and the number and size of files to upload. There could also be a bottleneck in the STT API if there are too many requests, but that is something we can scale by using a load balancer and multiple STT services.

## What would you change for production?

### Answer

- Use a different config file with different params stored in AWS Parameter Store.
- Run the app on a k8s cluster.
- Use a PostgreSQL instance in RDS for the database, possibly a serverless db.
- Use different STT credentials and possibly a different transcription model.
- Use an elastic autoscaler in AWS to autoscale the app based on traffic, mainly for the transcription worker process in celery.

## How would you ensure correct PII handling and storage?

### Answer

Use encryption for conversations: audio files would be stored in S3 with encryption enabled, and the database would be encrypted at rest and in transit.
