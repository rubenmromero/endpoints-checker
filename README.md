# Endpoints Checker

Tool to check periodically a set of services defined in a configuration schema

## Configuration

1. Download the project code in your favourite path:

       $ git clone https://github.com/rubenmromero/endpoints-checker.git

2. If you want to customize the configuration schema file before the first tool execution, copy the [schema.yml](schema.yml.dist) template to `schema.yml` and update it:

        # From the project root folder
        $ cp -p schema.yml.dist schema.yml
        $ vi schema.yml

## Execution Methods

### Local

    $ pip3 install -r requirements.txt
    $ python3 checker.py

### Docker Compose

    $ docker-compose up -d

### Kubernetes

    $ kubectl apply -f checker-service.yaml,checker-claim0-persistentvolumeclaim.yaml,checker-deployment.yaml
