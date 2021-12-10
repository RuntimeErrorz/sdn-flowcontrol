import requests
import os
import json
from requests.api import head
from requests.auth import HTTPBasicAuth

ip = "127.0.0.1"
auth = HTTPBasicAuth("karaf", "karaf")


def get_deviceID(src):
    src = str(hex(src))[2:]
    list = ['0' for _ in range(16 - len(src))]
    list.append(src)
    list.insert(0, 'of:')
    return ''.join(list)


def get_ports(ID1, ID2, links):
    for link in links:
        if link['src']['device'] == ID1 and link['dst']['device'] == ID2:
            return link['src']['port'], link['dst']['port']


def longestCommonPrefix(lists):
    res = []
    for tmp in zip(*lists):
        tmp_set = set(tmp)
        if len(tmp_set) == 1:
            res.append(tmp[0])
        else:
            break
    return res


def get_group_buckets(iplist, mac_dst_list, portlist):
    buckets = []
    buckets.append(
        {
            "treatment": {
                "instructions": [
                    {
                        "type": "OUTPUT",
                        "port": portlist[0]
                    }
                ]
            }
        }
    )
    for (ip, port, mac_dst) in zip(iplist[1:], portlist[1:], mac_dst_list[1:]):
        buckets.append(
            {
                "treatment": {
                    "instructions": [
                        {
                            "type": "L2MODIFICATION",
                            "subtype": "ETH_DST",
                            "mac": mac_dst
                        },
                        {
                            "type": "L3MODIFICATION",
                            "subtype": "IPV4_DST",
                            "ip": ip
                        },
                        {
                            "type": "OUTPUT",
                            "port": port
                        }
                    ]
                }
            })
    return buckets


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


def add_flow(controller_ip, deviceId, appId, instructions, criteria, priority = 40000):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    params = {
        "appId": appId
    }
    data = {
        "priority": priority,
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


def add_group_table(controller_ip, deviceId, groupId, appCookie, buckets):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    data = {
        "type": "ALL",
        "appCookie": appCookie,
        "groupId": "{}".format(groupId),
        "buckets": buckets
    }
    get_device_url = 'http://{}:8181/onos/v1/groups/{}'.format(
        controller_ip, deviceId)
    resp = requests.post(url=get_device_url, headers=headers,
                         auth=auth, data=json.dumps(data))
    return resp.text


def delete_device(controller_ip, deviceId):
    headers = {
        'Accept': 'application/json',
    }
    get_device_url = 'http://{}:8181/onos/v1/devices/{}'.format(
        controller_ip, deviceId)
    resp = requests.delete(url=get_device_url, headers=headers, auth=auth)
    return resp.status_code, resp.text


def block_fwd(controller_ip, devId):
    instruction = [{"type": "OUTPUT", "port": "drop"}]
    criteria = [{"type": "ETH_TYPE", "ethType": "0x0800"}]
    add_flow(controller_ip, devId, "block", instruction, criteria, 11000)
