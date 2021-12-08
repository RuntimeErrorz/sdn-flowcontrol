import requests
import json
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth("karaf", "karaf")


def get_criteria(ip_protocol, in_port, mac_src, mac_dst="optional", ethtype="0x0800"):
    return [
        {
            "type": "ETH_TYPE",
                    "ethType": ethtype
        },
        {
            "type": "IP_PROTO",
                    "protocol": ip_protocol
        },
        {
            "type": "ETH_SRC",
                    "mac": mac_src
        },
        {
            "type": "IN_PORT",
                    "port": in_port
        },
        {
            "type": "ETH_DST",
                    "mac": mac_dst
        },
    ]


def add_flow(controller_ip, deviceId, appId, instructions, criteria):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    params = {
        "appId": appId
    }
    data = {
        "priority": 40000,
        "timeout": 0,
        "isPermanent": True,
        "deviceId": deviceId,
        "treatment": {
            "instructions": instructions
        },
        "selector": {
            "criteria": criteria
        }
    }
    get_device_url = 'http://{}:8181/onos/v1/flows/{}'.format(
        controller_ip, deviceId)
    resp = requests.post(url=get_device_url, params=params,
                         headers=headers, auth=auth, data=json.dumps(data))
    return resp.status_code


def add_group_table(controller_ip, deviceId, groupId, appCookie, instructions):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    data = {
        "type": "ALL",
        "appCookie": appCookie,
        "groupId": groupId,
        "buckets": [
            {
                "treatment": {
                    "instructions": instructions
                }
            }
        ]
    }
    get_device_url = 'http://{}:8181/onos/v1/groups/{}'.format(
        controller_ip, deviceId)
    resp = requests.post(url=get_device_url, headers=headers,
                         auth=auth, data=json.dumps(data))
    return resp.text

