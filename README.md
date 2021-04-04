# Endpoint-Checker

Tool to check periodically a set of services defined in a configuration schema.

## Configuration

1. Clone the project in the path you want:

       $ git clone https://github.com/rubenmromero/endpoints-checker.git

2. If you want to customize the configuration schema file before the first tool execution, create a copy of [`schema.yml.dist`](schema.yml.dist) template named `schema.yml` and update it:

        # From the project root folder
        $ cp -p schema.yml.dist schema.yml
        $ vi schema.yml

## Execution Methods

### Local

    $ pip3 install -r requirements.txt
    $ export NOTIF_TOKEN=<token>
    $ python3 checker.py

### Docker Compose

    $ export NOTIF_TOKEN=<token>
    $ docker-compose up -d

### Kubernetes

    $ export NOTIF_TOKEN=<token>
    $ kubectl apply -f checker-service.yaml,checker-claim0-persistentvolumeclaim.yaml,checker-deployment.yaml
