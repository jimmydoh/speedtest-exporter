# Speedtest Exporter

Simple **Speedtest exporter** for **Prometheus** written in **Python** using the
official CLI from **Ookla**

[![Build dev image](https://github.com/jimmydoh/speedtest-exporter/actions/workflows/build-dev.yml/badge.svg)](https://github.com/jimmydoh/speedtest-exporter/actions/workflows/build-dev.yml)
[![Test main image](https://github.com/jimmydoh/speedtest-exporter/actions/workflows/build-main-pull.yml/badge.svg)](https://github.com/jimmydoh/speedtest-exporter/actions/workflows/build-main-pull.yml)
[![Release main image](https://github.com/jimmydoh/speedtest-exporter/actions/workflows/build-release.yml/badge.svg)](https://github.com/jimmydoh/speedtest-exporter/actions/workflows/build-release.yml)

Forked from [MiguelNdeCarvalho/speedtest-exporter](https://github.com/MiguelNdeCarvalho/speedtest-exporter)

The following changes have been completed:
* Add some of the adjustments / fixes implemented by [TheDaneH3](https://github.com/TheDaneH3/speedtest-exporter)
* Add additional data on client ISP, server details and test UUID from the speedtest results as labels in the Prometheus exports (similar functionality to the Go version from [aaronmwellborn](https://github.com/aaronmwelborn/speedtest_exporter) / [danopstech](https://github.com/danopstech/speedtest_exporter))
* Move from waitress to Gunicorn
* Only Docker deployment supported, remove checks for speedtest binary

The following changes are planned:
* Modify the sample Grafana dashboard in line with the new labels, based on the sample dashboards from both [MiguelNdeCarvalho](https://github.com/MiguelNdeCarvalho/speedtest-exporter/blob/main/Dashboard/Speedtest-Exporter.json) and [danopstech](https://github.com/danopstech/speedtest_exporter)
