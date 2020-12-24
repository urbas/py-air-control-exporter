# 0.3.0

- Hours remaining to replace or clean filters are now exported as `py_air_control_filter_hours` gauges.

# 0.2.0

- Default listening port and address are now displayed in the CLI help.
- The exporter now counts sampling errors and exports this as a metric rather than crash the process.

# 0.1.5

- Introduced the `py-air-control-exporter` command line tool.

# 0.1.4

- Packaging fixes:
   - Building outside a git repository now supported.
   - Build process now verifies that the CHANGELOG.md version matches the git version.

# 0.1.3

- Source distribution fixes: using SCM version, including test sources, including
   `CHANGELOG.md`.

# 0.1.2

- Removed the `py-air-control-exporter` entry point.
- Fixed `pyairctrl.http_air_client` references to `pyairctrl.http_client`.

# 0.1.1

- Ported to `prometheus_client` and added descriptions to each metric.

# 0.1.0

- Initial release.
