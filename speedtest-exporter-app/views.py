"""Provides a Prometheus export for the Ookla Speedtest CLI"""

import datetime
import json
import logging
import os
import subprocess
from prometheus_client import make_wsgi_app, Gauge, Info
from flask import Flask
from . import app

# Setup logging values
FORMAT_STRING = "level=%(levelname)s datetime=%(asctime)s %(message)s"
logging.basicConfig(
    encoding="utf-8",
    level=logging.INFO,  # Changed from DEBUG to INFO for performance
    format=FORMAT_STRING,
)

# Create Metrics
jitter = Gauge(
    "speedtest_jitter_latency_milliseconds",
    "Speedtest current Jitter in ms",
)
ping = Gauge(
    "speedtest_ping_latency_milliseconds",
    "Speedtest current Ping in ms",
)
download_speed = Gauge(
    "speedtest_download_bits_per_second",
    "Speedtest current Download Speed in bit/s",
)
upload_speed = Gauge(
    "speedtest_upload_bits_per_second",
    "Speedtest current Upload speed in bits/s",
)
up = Gauge(
    "speedtest_up",
    "Speedtest status whether the scrape worked",
)
test_info = Info(
    "speedtest",
    "Speedtest Info",
)

def bytes_to_bits(bytes_per_sec):
    """Converts bytes to bits"""
    return bytes_per_sec * 8


def bits_to_megabits(bits_per_sec):
    """Converts bits to megabits"""
    megabits = round(bits_per_sec * (10**-6), 2)
    return f"{megabits}Mbps"


def is_json(myjson):
    """Test for valid json"""
    if not myjson:
        return False
    try:
        json.loads(myjson)
        return True
    except (ValueError, TypeError):
        return False


def run_test():
    """Run the speedtest and return the extracted results"""

    logging.info("Running a new speedtest")

    manual_server_id = os.environ.get("SPEEDTEST_SERVER")
    timeout = int(os.environ.get("SPEEDTEST_TIMEOUT", 90))

    cmd = [
        "speedtest",
        "--format=json-pretty",
        "--progress=no",
        "--accept-license",
        "--accept-gdpr",
    ]
    if manual_server_id:
        cmd.append(f"--server-id={manual_server_id}")

    try:
        output = subprocess.check_output(cmd, timeout=timeout)
    except subprocess.CalledProcessError as e:
        logging.error("Speedtest CLI Error: %s", e)
        return (0, 0, 0, 0, 0, "", "", "", "", "", "")
    except subprocess.TimeoutExpired:
        logging.error("Speedtest CLI process timeout")
        return (0, 0, 0, 0, 0, "", "", "", "", "", "")

    if not is_json(output):
        return (0, 0, 0, 0, 0, "", "", "", "", "", "")

    try:
        data = json.loads(output)
        if "error" in data:
            logging.error("Speedtest error: %s", data["error"])
            return (0, 0, 0, 0, 0, "", "", "", "", "", "")

        if data.get("type") == "result":
            # Metric - jitter
            # Metric - latency
            # Metric - download
            # Metric - upload
            # Metric - up
            # Metric - id
            # Metric - uuid
            # Metric - name
            # Metric - location
            # Metric - country
            # Metric - isp
            return (                
                data["ping"]["jitter"],
                data["ping"]["latency"],
                bytes_to_bits(data["download"]["bandwidth"]),
                bytes_to_bits(data["upload"]["bandwidth"]),
                1,
                str(data["server"]["id"]),
                data["result"]["id"],
                data["server"]["name"],
                data["server"]["location"],
                data["server"]["country"],
                data["isp"],
            )
    except (KeyError, TypeError) as e:
        logging.error("Error parsing speedtest result: %s", e)
        return (0, 0, 0, 0, 0, "", "", "", "", "", "")

    return (0, 0, 0, 0, 0, "", "", "", "", "", "")


@app.route("/metrics")
def update_results():
    """Trigger the speedtest and return the metrics"""
    logging.info("Starting speedtest check")
    (
        r_jitter,
        r_ping,
        r_download,
        r_upload,
        r_status,
        r_server,
        r_testuuid,
        r_servername,
        r_serverlocation,
        r_servercountry,
        r_isp,
    ) = run_test()
    jitter.set(r_jitter)
    ping.set(r_ping)
    download_speed.set(r_download)
    upload_speed.set(r_upload)
    up.set(r_status)
    test_info.info({
        'id': r_server, 
        'uuid': r_testuuid,
        'name': r_servername,
        'location': r_serverlocation,
        'country': r_servercountry,
        'isp': r_isp
        })

    if r_status:  # Only log if test was successful
        logging.info(
            "UUID=%s ServerID=%s ServerName=%s ServerLocation=%s ServerCountry=%s ISP=%s Jitter=%sms Ping=%sms Download=%s Upload=%s",
            r_testuuid,
            r_server,
            r_servername,
            r_serverlocation,
            r_servercountry,
            r_isp,
            r_jitter,
            r_ping,
            bits_to_megabits(r_download),
            bits_to_megabits(r_upload),
        )

    return make_wsgi_app()


@app.route("/")
def main_page():
    """A simple default page"""
    return (
        "<h1>Welcome to Speedtest-Exporter.</h1>"
        + "Click <a href='/metrics'>here</a> to see metrics."
    )
