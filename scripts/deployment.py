import subprocess
import os
import pdb

class Deployment:

    def __init__(self, env_name):
        self.name = "buy-print"
        self.env_name = env_name
        # This deployment has only one stack
        self.stack_name = "-".join([self.env_name, self.name, "main"])

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
                  "--s3-bucket aws-sam-cli-managed-default-samclisourcebucket-602i575qh4ir "
                  "--s3-prefix " + self.stack_name + " "
                  "--parameter-overrides ParameterKey=EnvName,ParameterValue=" + self.env_name + " "
                  "--stack-name " + self.stack_name)

    def __sh(self, command):
        if not(isinstance(command, list)):
            command = command.split()
        subprocess.call(command)
