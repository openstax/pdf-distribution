# Returns the host directory that mounts to /code

import os
import subprocess
import json

# Command to get shell output
def sh(command):
  if not(isinstance(command, list)):
    command = command.split()
  process = subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True)
  return process.stdout.strip()

# Get information about the current container we are in
inspection = json.loads(sh("docker inspect " + sh("hostname")))

# Pull out the directory in the host that mounts to /code
binds = inspection[0]["HostConfig"]["Binds"]

for bind in binds:
  from_to = bind.split(":")
  if from_to[1] == "/code":
    print(from_to[0])
    break
