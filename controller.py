import requests
import json
from requests.auth import HTTPBasicAuth

ip = "127.0.0.1"
auth = HTTPBasicAuth("karaf", "karaf")


def get_device_id(src):
    src = str(hex(src))[2:]
    list = ['0' for _ in range(16 - len(src))]
    list.append(src)
    list.insert(0, 'of:')
    return ''.join(list)


def get_ports(id1, id2, links):
    for link in links:
        if link['src']['device'] == id1 and link['dst']['device'] == id2:
            return link['src']['port'], link['dst']['port']


def longest_common_prefix(lists):
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
                        "type": "output",
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
                            "type": "l2modification",
                            "subtype": "eth_dst",
                            "mac": mac_dst
                        },
                        {
                            "type": "l3modification",
                            "subtype": "ipv4_dst",
                            "ip": ip
                        },
                        {
                            "type": "output",
                            "port": port
                        }
                    ]
                }
            })
    return buckets


def get_criteria(ip_protocol, in_port, mac_src, mac_dst="optional", ethtype="0x0800"):
    return [
        {
            "type": "eth_type",
                    "eth_type": ethtype
        },
        {
            "type": "ip_proto",
                    "protocol": ip_protocol
        },
        {
            "type": "eth_src",
                    "mac": mac_src
        },
        {
            "type": "in_port",
                    "port": in_port
        },
        {
            "type": "eth_dst",
                    "mac": mac_dst
        },
    ]


def add_flow(controller_ip, device_id, app_id, instructions, criteria, priority=40000):
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json',
    }
    params = {
        "app_id": app_id
    }
    data = {
        "priority": priority,
        "timeout": 0,
        "is_permanent": True,
        "device_id": device_id,
        "treatment": {
            "instructions": instructions
        },
        "selector": {
            "criteria": criteria
        }
    }
    get_device_url = 'http://{}:8181/onos/v1/flows/{}'.format(
        controller_ip, device_id)
    resp = requests.post(url=get_device_url, params=params,
                         headers=headers, auth=auth, data=json.dumps(data))
    return resp.status_code


def add_group_table(controller_ip, device_id, group_id, app_cookie, buckets):
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json',
    }
    data = {
        "type": "all",
        "app_cookie": app_cookie,
        "group_id": "{}".format(group_id),
        "buckets": buckets
    }
    get_device_url = 'http://{}:8181/onos/v1/groups/{}'.format(
        controller_ip, device_id)
    resp = requests.post(url=get_device_url, headers=headers,
                         auth=auth, data=json.dumps(data))
    return resp.status_code


def block_fwd(controller_ip, app_id, dev_id):
    criteria = [{"type": "eth_type", "eth_type": "0x0800"}]
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json',
    }
    params = {
        "app_id": app_id
    }
    data = {
        "priority": 6,
        "timeout": 0,
        "is_permanent": True,
        "device_id": dev_id,
        "treatment": {
        },
        "selector": {
            "criteria": criteria
        }
    }
    get_device_url = 'http://{}:8181/onos/v1/flows/{}'.format(
        controller_ip, dev_id)
    resp = requests.post(url=get_device_url, params=params,
                         headers=headers, auth=auth, data=json.dumps(data))
    return resp.status_code


def del_flows_by_app_id(controller_ip, app_id):
    headers = {
        'accept': 'application/json',
    }
    get_device_url = 'http://{}:8181/onos/v1/flows/application/{}'.format(
        controller_ip, app_id)
    resp = requests.delete(url=get_device_url, headers=headers, auth=auth)
    return resp.status_code


def del_groups_by_dev_id_app_cookie(controller_ip, dev_id, app_cookie):
    headers = {
        'accept': 'application/json',
    }
    get_device_url = 'http://{}:8181/onos/v1/groups/{}/{}'.format(
        controller_ip, dev_id, app_cookie)
    resp = requests.delete(url=get_device_url, headers=headers, auth=auth)
    return resp.status_code
