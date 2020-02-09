import subprocess
import os
import pdb
import pathlib

class Codebase:

    @classmethod
    def template_file(self):
        current_dir = pathlib.Path(__file__).parent.absolute()
        return os.path.abspath(os.path.join(current_dir, '../cfn/distribution.yml'))

    @classmethod
    def build_dir(self):
        current_dir = pathlib.Path(__file__).parent.absolute()
        return os.path.abspath(os.path.join(current_dir, '../.aws-sam'))

    @classmethod
    def build(self):
        subprocess.call(("sam build -t " + self.template_file() + " -b " + self.build_dir()).split())
