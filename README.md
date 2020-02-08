# buy_print

A microsite for directing OpenStax traffic looking to purchase a book to the correct
place for their country.

## Requirements

* Docker and Docker Compose
* AWS credentials in `~/.aws/credentials`

## Getting Started

Clone the repository and `cd` into it.  Then start the container.

`$> docker-compose up`

Drop into the container to the `/code` folder:

`$> ./docker/bash`

Configure your AWS credentials.  If you have a `~/.aws/credentials` file it will be mounted in `/root/.aws/credentials`.  One way to set the credentials is to say

`$> ./scripts/set_aws_env_vars openstax-sandbox`

where `openstax-sandbox` is the name of a profile in the `credentials` file.

## Using Cloudformation


### Create the content-distribution stack in AWS once

To create the stack run the following using the `aws` cli:

```bash
aws cloudformation deploy --template-file cf-templates/firstrun-cloudfront-single-origin-bucket.yaml --region us-east-1 --stack-name content-distribution --tags Project=content-distribution Application=content-distribution Environment=dev Owner=ConEng --capabilities CAPABILITY_IAM
```

Note: This step only needs to be run the first time to create the stack. If you need to make updates please follow the
instructions in [Update the content-distribution after changes](#update-the-content-distribution-after-changes).

Note: This command will take about 15-25min to complete. It will create the following resources in AWS:

- Cloudfront distribution
- Artifact S3 Bucket
- Raw JSON S3 Bucket
- Baked HTML S3 Bucket
- Resources S3 Bucket
- It will not create the [Lambda Function](./sam-app/lambda_function.py) because this requires the Artifact S3 to be created first.

You can see the progress of deployment in the AWS console [here](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks). Click on the stack name `content-distribution` and open the `events` tab.

### Update the content-distribution after changes

#### Build SAM app

If you have done by now please build the SAM app:

```bash
cd sam-app
# activate a Python3 virtualenv here!
sam build -b ../.aws-sam
cd ..
```

#### Package SAM app and upload

The `aws cloudformation` command can package up the changes and upload to an s3 bucket.
It allows you to do this by using the `package` argument along with `--s3-bucket` and `--output-template-file` options.

This will package up the lambda function, upload to the s3 bucket, and generate a new template that has
the s3 bucket substituted in the proper locations of the template.

To update (or first install) the content-distribution stack after a merge run the following:

```bash
aws cloudformation package --template-file ./cf-templates/cloudfront-single-origin-bucket.yaml \
--s3-bucket ce-artifacts-content-distribution-373045849756 --output-template-file ./cf-templates/app-output-sam.yaml
```

This will output a SAM compiled version of the template that can be used to update the stack.

Run the following command after the one above to update the stack:

```bash
aws cloudformation update-stack --stack-name content-distribution \
--region us-east-1 --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM \
--template-body file://./cf-templates/app-output-sam.yaml
```

## Loading the books into s3

Follow the instructions in [./dump/README.md](./dump/README.md) file.

## Using SAM to build and test the Lambda@Edge function

Follow the instruction in [.sam-app/README.md](./sam-app/README.md) file.

### Articles that are useful

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
