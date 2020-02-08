# buy_print

A microsite for directing OpenStax traffic looking to purchase a book to the correct
place for their country.

## Requirements

* Docker and Docker Compose
* AWS credentials in `~/.aws/credentials`

## Getting Started

All development, building, testing, and deploying happens inside of a development environment docker container.

Clone the repository and `cd` into it.  Then start the development environment container.

`$> docker-compose up`

Drop into the container to the `/code` folder:

`$> ./docker/bash`

Configure your AWS credentials.  If you have a `~/.aws/credentials` file it will be mounted in `/root/.aws/credentials`.  One way to set the credentials is to say

`/code $> source ./scripts/set_aws_env_vars openstax-sandbox`

where `openstax-sandbox` is the name of a profile in the `credentials` file.

This microsite uses the `sam` CLI. Instead of calling it directly with a bunch of options, this repository provides wrapper scripts in the `scripts` directory.

## Run unit tests

`cd` into the `app` directory, then run:

`/code/app $> python -m pytest tests/ -v`

## Local invocation

You can run your lambda function in an AWS-like test environment by calling `sam local invoke`.  This uses an AWS-provided docker container to simulate a real run in AWS.  Because we are running in a development environment container which launches this AWS-provided container, we have to do some gymnastics to make sure directories mount correctly.  For this, we have a wrapper script named `sam_local_invoke`:

`cd` into the `app` directory, then run:

`/code/app $> sam_local_invoke --event events/from_us.json`

selecting the event you want from the `events` directory.

## Build the code

You need to build the code before you can deploy it:

`/code $> ./scripts/build`

This wraps a call to `sam build` and puts the built code in a `.aws-sam` directory.

## Deploy the code

This involves running `sam deploy`, but again, we provide a wrapper script to hide some boilerplate and to standardize on things like stack names.  Make sure to have built the code first.

`/code %> ./scripts/deploy_env --env_name some-env-name`

This works for the first deploy or for an update.  Note that under the covers, `sam deploy` uses an AWS-managed S3 bucket for storing the built code.  If this is the first time you're running the deployment within an AWS account, you'll need to modify `scripts/deployment.py` to know about this new bucket, which will probably require running `sam deploy` interactively with the `--guided` mode.

## Delete a deployment

`/code %> ./scripts/delete_env --env_name some-env-name`

Note that deleting Lambda@Edge deployments normally fails, due to something related to how the lambda function is replicated all over the world.  So what will normally happen is that you run this script, it fails, and then you have to wait a few hours and try to delete it again.

## Articles that are useful

- [AWS CloudFormation Documentation][aws-cloudformation]
- [Managing Lambda@Edge and CloudFront deployments by using a CI/CD pipeline][aws-cf-lambda-ci]
- [Amazon S3 + Amazon CloudFront: A Match Made in the Cloud][aws-cf-s3]
- [Chalice CloudFormation Support][aws-chalice-support]
- [Chalice Pure Lambda Functions][aws-chalice-pure-lambda]
- [AWS Serverless Application Model][aws-sam]


[cnx-archive]: https://github.com/openstax/cnx-archive
[cnx-db]: https://github.com/openstax/cnx-db
[content-spike-concourse]: https://github.com/openstax/content-spike-concourse
[content-two-pager]: https://docs.google.com/document/d/1GW5VGrjKmIRw3nbFTIkBZgE0mlHD9ky2TJ_bSUIcJ_w/edit#heading=h.6u0c02buvzha
[aws-cloudformation]: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html
[aws-chalice-support]: https://chalice.readthedocs.io/en/latest/topics/cfn.html
[aws-chalice-pure-lambda]: https://chalice.readthedocs.io/en/latest/topics/purelambda.html
[aws-sam]: https://aws.amazon.com/serverless/sam/
[aws-cf-lambda-ci]: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-options.html
[aws-cf-s3]: https://aws.amazon.com/blogs/networking-and-content-delivery/amazon-s3-amazon-cloudfront-a-match-made-in-the-cloud/

## Credits

Thanks to the OpenStax Content Engineering team whose great code I started from to build this!
