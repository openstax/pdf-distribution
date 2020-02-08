FROM python:3.7-slim

ENV PYTHONUNBUFFERED 1

# TODO figure out a way to not hardcode this
ENV DOCKERVERSION=19.03.1

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
  && rm -rf /var/lib/apt/lists/*

# install docker CLI only (using the host's daemon)

RUN curl -fsSLO https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKERVERSION}.tgz \
    && tar xzvf docker-${DOCKERVERSION}.tgz --strip 1 -C /usr/local/bin docker/docker \
    && rm docker-${DOCKERVERSION}.tgz

# install the AWS SAM CLI; recommended path is to install via Homebrew, which does
# not like being installed as root, so make a user for that purpose, see
# https://stackoverflow.com/a/58293459/1664216

# RUN localedef -i en_US -f UTF-8 en_US.UTF-8

RUN useradd -m -s /bin/bash linuxbrew && \
    echo 'linuxbrew ALL=(ALL) NOPASSWD:ALL' >>/etc/sudoers

USER linuxbrew
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/Linuxbrew/install/master/install.sh)"

USER root
ENV PATH="/home/linuxbrew/.linuxbrew/bin:${PATH}"

RUN brew tap aws/tap && brew install aws-sam-cli

# install the AWS CLI (probably could do using brew as well)

RUN cd /tmp && \
    curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip" && \
    unzip awscli-bundle.zip && \
    ./awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws

###

WORKDIR /code

COPY . /code/

RUN mkdir -p /root/.aws

RUN printf '%s\n' '[default]' 'region=us-east-1' 'output=json' > /root/.aws/config

RUN pip install -r /code/scripts/requirements.txt

ENTRYPOINT ["/code/docker/entrypoint"]

CMD docker/start
