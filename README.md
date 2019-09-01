# Philips Air Purifier Exporter


## Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Running
```bash
FLASK_ENV=development FLASK_APP=philips_air_purifier_exporter/app.py flask run --host 0.0.0.0
```
This will serve metrics at `http://localhost:5000/metrics`.

You can make Prometheus scrape these with this scrape config:
```yaml
scrape_configs:
  - job_name: 'philips_air_purifier'
    static_configs:
      - targets: ['<the IP of your exporter host>:5000']
        labels:
          location: 'bedroom'
```