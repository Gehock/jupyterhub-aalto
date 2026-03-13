#!/usr/bin/env python3
import os
import time

import requests
from prometheus_client import Gauge, start_http_server

from hub_status_service import API, AUTH_DATA_FILE, TokenAuth

API = os.environ.get("JUPYTERHUB_API_URL", API)

JUPYTERHUB_URL = f"{API}/users"
TOKEN = "API_TOKEN"

auth_data = open(AUTH_DATA_FILE).readlines()
token = auth_data[0].strip()
auth = TokenAuth(token)


active_users = Gauge("jupyterhub_active_users", "Active JupyterHub users")
running_servers = Gauge("jupyterhub_running_servers", "Running JupyterHub servers")
user_server = Gauge(
    "jupyterhub_user_server_running",
    "Whether a user has a running server",
    ["user"]
)

def collect():
    r = requests.get(JUPYTERHUB_URL, auth=auth)
    r.raise_for_status()

    users = r.json()

    active = 0
    servers = 0

    for u in users:
        if u["servers"]:
            active += 1
            servers += len(u["servers"])
            user_server.labels(user=u["name"]).set(1)

    active_users.set(active)
    running_servers.set(servers)


if __name__ == "__main__":
    start_http_server(9109)

    while True:
        collect()
        time.sleep(30)
