FROM python:3.7-slim

ENV PYTHONUNBUFFERED 1

# Supply during build with the version of the host docker install
ARG DOCKERVERSION

# always us-east-1 for lambda@edge
ENV AWS_DEFAULT_REGION=us-east-1
ENV AWS_REGION=us-east-1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    libz-dev \
    libpq-dev \
    curl \
    unzip \
    openssh-client \
    locales-all \
    && rm -rf /var/lib/apt/lists/*

# install docker CLI only (using the host's daemon)

RUN curl -fsSLO https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKERVERSION}.tgz \
    && tar xzvf docker-${DOCKERVERSION}.tgz --strip 1 -C /usr/local/bin docker/docker \
    && rm docker-${DOCKERVERSION}.tgz

# install the AWS SAM CLI; recommended path is to install via Homebrew, which does
# not like being installed as root, so make a user for that purpose, see
# https://stackoverflow.com/a/58293459/1664216

ENV PATH="/home/linuxbrew/.linuxbrew/bin:${PATH}"

RUN useradd -m -s /bin/bash linuxbrew && \
    echo 'linuxbrew ALL=(ALL) NOPASSWD:ALL' >>/etc/sudoers

USER linuxbrew
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/Linuxbrew/install/master/install.sh)"

USER root

# Install the aws-sam-cli
#
# Instead of just saying `brew install aws-sam-cli` we want to pin the version.  This is not
# as straightforward as you'd expect.  The interwebs say to pass a raw formula URL from github
# to `brew install`, but this doesn't work for this formula because it references some other code
# in the repo.  So... our solution is to clone the aws tap, checkout a commit that corresponds to
# a specific version (the one that updates the bottle to a certain version) and the use brew to
# "build-from-source".

# Sha 5869c277dbe057e7be8971bb89c9d205bf7e0b64 corresponds to aws-sam-cli 0.44.0

RUN git clone https://github.com/aws/homebrew-tap.git /tmp/aws-tap
RUN cd /tmp/aws-tap && git checkout 5869c277dbe057e7be8971bb89c9d205bf7e0b64
RUN brew install --build-from-source /tmp/aws-tap/Formula/aws-sam-cli.rb

# install the AWS CLI (probably could do using brew as well)

RUN cd /tmp && \
    curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip" && \
    unzip awscli-bundle.zip && \
    ./awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws

###

WORKDIR /code
COPY . /code/

# directory for credentials to be mounted in
RUN mkdir -p /root/.aws

# some AWS config (actually may not be used?)
RUN printf '%s\n' '[default]' 'region=us-east-1' 'output=json' > /root/.aws/config

# Install the libraries used by the scripts
RUN pip install -r /code/scripts/requirements.txt

# Install the unit test libraries
RUN pip install pytest pytest-mock --user

ENTRYPOINT ["/code/docker/entrypoint"]
