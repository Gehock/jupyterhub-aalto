#!/usr/bin/env python3
import os
import time

import requests
from hub_status_service import API, AUTH_DATA_FILE, TokenAuth
from prometheus_client import Gauge, start_http_server

API = os.environ.get("JUPYTERHUB_API_URL", API)

JUPYTERHUB_URL = f"{API}/users"
TOKEN = "API_TOKEN"

auth_data = open(AUTH_DATA_FILE).readlines()
token = auth_data[0].strip()
auth = TokenAuth(token)

SHOW_STOPPED_SERVERS = False

user_server_running = Gauge(
    "jupyterhub_user_server_running", "Whether a user has a running server", ["user"]
)

user_servers = Gauge(
    "jupyterhub_user_servers", "Number of running servers for the user", ["user"]
)

active_users = Gauge("jupyterhub_active_users", "Total active users")

running_servers = Gauge("jupyterhub_running_servers", "Total running servers")


def collect():
    r = requests.get(JUPYTERHUB_URL, auth=auth)
    r.raise_for_status()

    users = r.json()

    active = 0
    servers_total = 0

    for user in users:
        name = user["name"]
        servers = user.get("servers", {})
        count = len(servers)

        if count > 0:
            user_server_running.labels(name).set(1)
            active += 1
        elif SHOW_STOPPED_SERVERS:
            user_server_running.labels(name).set(0)

        user_servers.labels(name).set(count)
        servers_total += count

    active_users.set(active)
    running_servers.set(servers_total)


if __name__ == "__main__":
    start_http_server(9109)

    while True:
        collect()
        time.sleep(30)
