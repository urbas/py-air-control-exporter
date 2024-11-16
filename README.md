# py-air-control-exporter [![builder](https://github.com/urbas/py-air-control-exporter/actions/workflows/build.yml/badge.svg?branch=master)](https://github.com/urbas/py-air-control-exporter/actions/workflows/build.yml) [![pypi-badge]](https://pypi.org/project/py-air-control-exporter/)

Exports air quality metrics to Prometheus.

This exporter uses [py-air-control] to obtain data.

## Installation

```bash
pip install py-air-control-exporter
```

## Running

```bash
py-air-control-exporter --host 192.168.1.105 --protocol http
```

This will serve metrics at `http://0.0.0.0:9896/metrics`.

For more instructions run `py-air-control-exporter --help`.

You can make Prometheus scrape these with this scrape config:

```yaml
scrape_configs:
  - job_name: "py_air_control"
    static_configs:
      - targets: ["<the IP of your exporter host>:9896"]
        labels:
          location: "bedroom"
```

[py-air-control]: https://github.com/rgerganov/py-air-control
[pypi-badge]: https://badge.fury.io/py/py-air-control-exporter.svg
