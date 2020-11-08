# Philips Air Purifier Exporter

Exports air quality metrics to Prometheus.

This exporter uses [py-air-control] to obtain data.

## Installation

```bash
pip install py-air-control-exporter
```

## Running

```bash
PY_AIR_CONTROL_HOST=<ip of your air purifier> PY_AIR_CONTROL_PROTOCOL=<http|coap|plain_coap> FLASK_ENV=development FLASK_APP=py_air_control_exporter.app flask run --host 0.0.0.0
```

This will serve metrics at `http://localhost:5000/metrics`.

You can make Prometheus scrape these with this scrape config:

```yaml
scrape_configs:
  - job_name: "py_air_control"
    static_configs:
      - targets: ["<the IP of your exporter host>:5000"]
        labels:
          location: "bedroom"
```

[py-air-control]: https://github.com/rgerganov/py-air-control
