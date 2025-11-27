# FASTAPI-PYTHON-TEMPLATE

This template project is designed to provide a solid foundation for building FastAPI applications with advanced features. It includes integration with Zitadel for authentication, Prometheus for metrics monitoring, and OpenTelemetry for tarces monitoring and logging. With this template, you can easily set up a FastAPI app that leverages Zitadel for secure authentication, collects metrics with Prometheus, and utilizes OpenTelemetry for comprehensive monitoring and logging. All the logs and metrics can be visualized in a Grafana platform, providing a powerful toolset for monitoring and managing your FastAPI application.

## ToC
1. [Prerequisites](#1)
2. [Installation](#2)
3. [Docker Compose Configuration](#3)
    - [Services](#3.1)
        - [Loki](#3.1.1)
        - [Prometheus](#3.1.2)
        - [Tempo](#3.1.3)
        - [Grafana](#3.1.4)
        - [Sample Applications](#3.1.4)
4. [Fast API Usage](#4)
5. [Postman requests](#5)
6. [Explore with Grafana](#6)
    - [Metrics to Traces](#6.1)
    - [Traces to Logs](#6.2)
    - [Logs to Traces](#6.3)

## Prerequisites <a name="1"></a>

- Python 3.7 or higher installed
- `poetry` package manager
- Docker (https://www.docker.com/products/docker-desktop/)
- Docker Compose

## Installation <a name="2"></a>

1. Clone the repository:

    ```bash
    git clone https://github.com/novelcore/fastapi-python-template
    ```

2. Navigate to the project directory:

    ```bash
    cd fastapi-python-template
    ```

3. Deploying the services:

    ```bash
    docker-compose up
    ```


## Docker Compose Configuration <a name="3"></a>

This [Docker Compose](https://github.com/novelcore/devOps-guestbook/tree/main/fastapi-zitadel-101/app.py) configuration sets up a monitoring and logging stack consisting of Grafana, Prometheus, Loki, Tempo, and two sample applications (app-a and app-b). Below is an overview of the services and their use within this configuration.

### Services <a name="3.1"></a>
***
#### **Loki** <a name="3.1.1"></a>
Loki is a horizontally scalable, highly available, multi-tenant log aggregation system inspired by Prometheus. It is designed to handle large amounts of log data by storing, indexing, and querying logs. Loki aggregates logs from various sources and makes them available for querying via Grafana.

**Image**: grafana/loki:2.8.3 \
**Port**: 3100 \
**Configuration**: Loki is configured with a local configuration file.\
***
#### **Prometheus** <a name="3.1.2"></a>
Prometheus is an open-source monitoring and alerting toolkit. It collects metrics from configured targets at given intervals, evaluates rule expressions, displays the results, and triggers alerts when specified conditions are observed.

**Image**: prom/prometheus:v2.45.0\
**Port**: 9090\
**Configuration**: Prometheus is configured with a local configuration file and enables exemplar storage feature.
***
#### **Tempo** <a name="3.1.3"></a>
Tempo is an open-source, easy-to-use, and high-volume trace storage backend. It is designed for fast, scalable, and cost-effective trace collection, storage, and querying.

**Image**: grafana/tempo:2.1.1\
**Port**: 14250\
**Configuration**: Tempo is configured with local storage and disables authentication.
***
#### **Grafana** <a name="3.1.4"></a>
Grafana is a multi-platform open-source analytics and interactive visualization web application. It provides charts, graphs, and alerts for the web when connected to supported data sources.

**Image**: grafana/grafana:10.1.0\
**Port**: 3000\
**Configuration**: Grafana is configured with data sources and dashboards provisioning.
***
#### **Sample Applications** (app-a and app-b) <a name="3.1.5"></a>
These are sample applications deployed for demonstration purposes. They are configured with environment variables pointing to a ZITADEL instance for authentication.

## Fast API Usage <a name="4"></a>
Once the containers are up and running, access the `app-a` application in your browser at http://localhost:8000 (or with 8001 for the `app-b`). Now if you access this http://localhost:8000/docs#/ you can see all the endpoints of the fastapi app and proceed to requests. Some of the endpoints need authorization and won't let you send request. For the those endpoints proceed to [Postman requests](#5).
![alt](/Images/fastapi.png)

## Postman requests <a name="5"></a>
Run the `client_credentials_token_generator.py` script to generate an access token. Open your terminal and navigate to the project directory, then run the script using python3:
`poetry run python .\app\app\core\zitadel\client-credentials-token-generator.py`

If successful, this will print an access token to your terminal. This is the token you'll use to authenticate your requests to the API.

Now you can use Postman (or any other HTTP client) to make requests to the API. Remember to replace your_access_token in the curl commands with the access token you obtained.

Use example:
<img
    src="Images/30 - Postman.png"
    width="100%"
    alt="Add action"
/>

## Explore with Grafana <a name="6"></a>

Check predefined dashboard `FastAPI Observability` on Grafana [http://localhost:3000/](http://localhost:3000/) login with `admin:admin`

   Dashboard screenshot:

   ![FastAPI Monitoring Dashboard](./Images/dashboard.png)

   The dashboard is also available on [Grafana Dashboards](https://grafana.com/grafana/dashboards/16110).


Grafana provides a great solution, which could observe specific actions in service between traces, metrics, and logs through trace ID and exemplar.

![Observability Correlations](./Images/observability-correlations.jpeg)

Image Source: [Grafana](https://grafana.com/blog/2021/03/31/intro-to-exemplars-which-enable-grafana-tempos-distributed-tracing-at-massive-scale/)

### Metrics to Traces <a name="6.1"></a>

Get Trace ID from an exemplar in metrics, then query in Tempo.

Query: `histogram_quantile(.99,sum(rate(fastapi_requests_duration_seconds_bucket{app_name="app-a", path!="/metrics"}[1m])) by(path, le))`

![Metrics to Traces](./Images/metrics-to-traces.png)

### Traces to Logs <a name="6.2"></a>

Get Trace ID and tags (here is `compose.service`) defined in Tempo data source from span, then query with Loki.

![Traces to Logs](./Images/traces-to-logs.png)

### Logs to Traces <a name="6.3"></a>

Get Trace ID from log (regex defined in Loki data source), then query in Tempo.

![Logs to Traces](./Images/logs-to-traces.png)
