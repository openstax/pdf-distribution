import subprocess
import os

class Deployment:

    def __init__(self, env_name, is_sandbox=True):
        self.name = "buy-print"
        self.env_name = env_name
        # This deployment has only one stack
        self.stack_name = "-".join([self.env_name, self.name, "main"])
        self.is_sandbox = is_sandbox

        if is_sandbox:
            self.hosted_zone_name = "sandbox.openstax.org"
            self.artifact_bucket = "aws-sam-cli-managed-default-samclisourcebucket-602i575qh4ir"
        else:
            self.hosted_zone_name = "openstax.org"
            self.artifact_bucket = "unknown"

    def delete(self):
        print("Deleting " + self.stack_name)
        self.__sh("aws cloudformation delete-stack --stack-name " + self.stack_name)
        print("Waiting for deletion to complete...")
        self.__sh("aws cloudformation wait stack-delete-complete --stack-name " + self.stack_name)
        print("Deletion complete!")

    def deploy(self):
        self.__sh("sam deploy "
                  "--template-file " + os.path.join(os.path.dirname(__file__), '..') + "/.aws-sam/template.yaml "
                  "--capabilities CAPABILITY_IAM "
                  "--s3-bucket " + self.artifact_bucket + " "
                  "--s3-prefix " + self.stack_name + " "
                  "--parameter-overrides " + self.parameters_string() + " "
                  "--stack-name " + self.stack_name)

    def __sh(self, command):
        if not(isinstance(command, list)):
            command = command.split()
        subprocess.call(command)

    def domain(self):
        subdomain_parts = ["buyprint"]
        if self.env_name != "production":
            subdomain_parts.append(self.env_name)
        subdomain = "-".join(subdomain_parts)
        return subdomain + "." + self.hosted_zone_name

    def parameters_string(self):
        expanded_parameters = []
        for key, value in self.parameters_dict().items():
            expanded_parameters.append("ParameterKey=" + key + ",ParameterValue=" + value)
        return " ".join(expanded_parameters)

    def parameters_dict(self):
        return {
            'EnvName': self.env_name,
            'HostedZoneName': self.hosted_zone_name,
            'Domain': self.domain()
        }
