import json
from controller import *
ip = "127.0.0.1"
import heapq

arp_instruction = [{"type": "output", "port": "normal"}]
arp_criteria = [{"type": "eth_type", "eth_type": "0x0806"}]


def loadmap(devices, links, hosts):
    with open(str(devices)+".json", 'r') as j:
        ls = json.load(j)
    length = len(list(ls.values())[0])
    devices = list(ls.values())[0]
    down_devices = []
    i = 0
    temp = length
    while i < temp:
        if not devices[i]["available"]:
            down_devices.append(devices[i]["id"])
            del(devices[i])
            temp -= 1
            continue
        else:
            i += 1
    with open(str(links)+".json", 'r') as k:
        linksls = json.load(k)
    with open(str(hosts)+".json", 'r') as h:
        hostsls = json.load(h)
    hosts = list(hostsls.values())[0]
    map = [[float('inf') for i in range(length)] for i in range(length)]
    for i in range(length):
        map[i][i] = 0
    links_list = list(linksls.values())[0]
    for link in links_list:
        src_id = link['src']['device']
        dst_id = link['dst']['device']
        if src_id in down_devices or dst_id in down_devices:
            continue
        src = (int(src_id[3:], 16)) - 1
        dst = (int(dst_id[3:], 16)) - 1
        map[src][dst] = 1
    return map, links_list, devices, hosts


if __name__ == "__main__":
    map, links, devices, hosts = loadmap('devices', 'links', 'hosts')


def heapy_dijkstra(src, dsts):
    length = len(map)
    path = [-1 for i in range(length)]
    final_paths = [[]for _ in range(len(dsts))]
    distance = [float('inf') for _ in range(length)]
    distance[src - 1] = 0
    for i in range(length):
        distance[i] = map[src-i][i]
    queue = []
    heapq.heapify(queue)
    heapq.heappush(queue, distance[src-1])
    while queue:
        v = heapq.heappop(queue)
        for u in range(length):
            if distance[v] + map[v][u] < distance[u]:
                path[u] = v
                distance[u] = distance[v] + map[v][u]
                heapq.heappush(queue,distance[u])
    for (final_path, dst) in zip(final_paths, dsts):
        final_path.append(dst)
        p = dst - 1
        while path[p] != -1:
            final_path.append(path[p] + 1)
            p = path[p]
    for i in range(len(final_paths)):
        final_paths[i] = list(reversed(final_paths[i]))
    return final_paths


def find_another_way(ip_protocol, src, dst):
    for host in hosts:
        if host['id'] == src:
            mac_src = host['mac']
            port_dst = host['locations'][0]['port']
            src_id = host['locations'][0]['element_id']
            src = int(host['locations'][0]['element_id'][3:], 16)
        if host['id'] == dst:
            mac_dst = host['mac']
            last_port = host['locations'][0]['port']
            dst_id = host['locations'][0]['element_id']
            dst = int(host['locations'][0]['element_id'][3:], 16)
    add_flow(ip, src_id, 'my_app', arp_instruction, arp_criteria)
    add_flow(ip, dst_id, 'my_app', arp_instruction, arp_criteria)
    path = heapy_dijkstra(src, [dst])[0]
    print(path)
    link_allby_path(ip_protocol, path, last_port,
                  port_dst, mac_src, mac_dst=mac_dst)


def link_allby_path(ip_protocol, path, last_port, port_dst, mac_src, temp_port=-1, mac_dst="optional", flag=1):
    if (len(path) == 1):
        print(port_dst, temp_port)
        id1 = get_device_id(path[0])
        add_flow(ip, id1, 'my_app', arp_instruction, arp_criteria)
        instruction1 = [{"type": "output", "port": temp_port}]
        criteria1 = get_criteria(
            ip_protocol, port_dst, mac_src, mac_dst=temp_port)
        add_flow(ip, id1, "my_app", instruction1, criteria1)
        return

    for i in range(len(path) - 1):
        id1 = get_device_id(path[i])
        id2 = get_device_id(path[i+1])
        add_flow(ip, id1, 'my_app', arp_instruction, arp_criteria)
        port_src = port_dst
        port_dst, _ = get_ports(id1, id2, links)
        print(port_src, port_dst)
        instruction1 = [{"type": "output", "port": port_dst}]
        criteria1 = get_criteria(
            ip_protocol, port_src, mac_src, mac_dst=mac_dst)
        if mac_dst == "optional":
            criteria1 = criteria1[:-1]
        add_flow(ip, id1, "my_app", instruction1, criteria1)
        if flag == 1:
            instruction2 = [{"type": "output", "port": port_src}]
            criteria2 = get_criteria(
                ip_protocol, port_dst, mac_dst, mac_dst=mac_src)
            add_flow(ip, id1, "my_app", instruction2, criteria2)
        port_src, port_dst = get_ports(id1, id2, links)

    port_src = port_dst
    port_dst = last_port
    add_flow(ip, id2, "my_app", arp_instruction, arp_criteria)
    print(port_src, port_dst)
    criteria1 = get_criteria(ip_protocol, port_src, mac_src, mac_dst=mac_dst)
    instruction1 = [{"type": "output", "port": port_dst}]
    if mac_dst == "optional":
        criteria1 = criteria1[:-1]
    add_flow(ip, id2, "my_app", instruction1, criteria1)
    if flag == 1:
        instruction2 = [{"type": "output", "port": port_src}]
        criteria2 = get_criteria(
            ip_protocol, port_dst, mac_dst, mac_dst=mac_src)
        add_flow(ip, id2, "my_app", instruction2, criteria2)


def find_another_ways(ip_protocol, src, dsts):
    mac_dsts = []
    last_ports = []
    dst_ids = []
    dstss = []
    ips = []
    for host in hosts:
        if host['id'] == src:
            mac_src = host['mac']
            port_dst = host['locations'][0]['port']
            src_id = host['locations'][0]['element_id']
            src = int(host['locations'][0]['element_id'][3:], 16)
    for dst in dsts:
        for host in hosts:
            if host['id'] == dst:
                mac_dsts.append(host['mac'])
                ips.append(host['ip_addresses'][0])
                last_ports.append(host['locations'][0]['port'])
                dst_ids.append(host['locations'][0]['element_id'])
                dstss.append(int(host['locations'][0]['element_id'][3:], 16))
    add_flow(ip, src_id, 'my_app', arp_instruction, arp_criteria)
    for dst_id in dst_ids:
        add_flow(ip, dst_id, 'my_app', arp_instruction, arp_criteria)
    paths = heapy_dijkstra(src, dstss)
    print(paths)
    common_path = longest_common_prefix(paths)
    print(common_path)
    merge_point = common_path[-1]
    merge_id = get_device_id(merge_point)
    tmp_p = common_path[-2]
    temp_port, last_port = get_ports(get_device_id(tmp_p), merge_id, links)
    instructions = [{"type": "group", "group_id": 1}]
    criteria = get_criteria(ip_protocol, last_port, mac_src)[:-1]
    individual_paths = []
    for path in paths:
        individual_paths.append(path[len(common_path):])
    print(individual_paths)
    outports = [get_ports(merge_id, get_device_id(i[0]), links)[0]
                for i in individual_paths]
    add_group_table(ip, merge_id, 1, "0x1234",
                    get_group_buckets(ips, mac_dsts, outports))
    add_flow(ip, merge_id, "my_app", instructions, criteria)
    add_flow(ip, merge_id, "my_app", arp_instruction, arp_criteria)
    link_allby_path(ip_protocol, common_path[:-1],
                  last_port, port_dst, mac_src, temp_port=temp_port, flag=0)
    print("------------------")
    for (individual_path, lastport, mac_dst) in zip(individual_paths, last_ports, mac_dsts):
        print(mac_src, mac_dst)
        temp_port, port_dst = get_ports(
            merge_id, get_device_id(individual_path[0]), links)
        link_allby_path(ip_protocol, individual_path, lastport,
                      port_dst, mac_src, temp_port=temp_port, mac_dst=mac_dst, flag=0)
        print("--------------")


if __name__ == "__main__":
    pass
    # find_another_way(1, '00:00:00:00:00:01/none', '00:00:00:00:00:03/none')
    # find_another_way(1, '00:00:00:00:00:01/none', '00:00:00:00:00:02/none')
    # find_another_ways(17, '00:00:00:00:00:03/none',
    #                 ['00:00:00:00:00:01/none', '00:00:00:00:00:02/none'])
