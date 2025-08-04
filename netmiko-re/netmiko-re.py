#!/usr/bin/env python3

from netmiko import ConnectHandler
import re

routers = [
    {'name': 'R1', 'device_type': 'cisco_ios', 'ip': '172.31.21.4', 'username': 'admin', 'key_file': '/home/devasc/.ssh/id_rsa', 'use_keys': True},
    {'name': 'R2', 'device_type': 'cisco_ios', 'ip': '172.31.21.5', 'username': 'admin', 'key_file': '/home/devasc/.ssh/id_rsa', 'use_keys': True},
]

# Regex that matches "up", "down", or "administratively down"
brief_re = re.compile(
    r'^(\S+)\s+(\S+)\s+\S+\s+\S+\s+'
    r'((?:up|down|administratively down))\s+'
    r'(up|down)', re.I
)

for router in routers:
    info = router.copy()
    name = info.pop('name')
    print(f"\n--- {name} ---")
    try:
        conn = ConnectHandler(**info)
        brief  = conn.send_command("show ip interface brief")
        detail = conn.send_command("show interfaces")
        conn.disconnect()
    except Exception as e:
        print(f"Failed {name}: {e}")
        continue

    # parse brief
    interfaces = []
    for line in brief.splitlines():
        m = brief_re.match(line)
        if m:
            interfaces.append({
                'name':     m.group(1),
                'ip':       m.group(2),
                'status':   m.group(3).lower(),
                'protocol': m.group(4).lower()
            })

    # parse uptime
    uptime = {}
    current = None
    for L in detail.splitlines():
        hdr = re.match(r'^(\S+) is (up|down),', L)
        if hdr:
            current = hdr.group(1)
            uptime[current] = {'in': 'never', 'out': 'never'}
        elif current and "Last input" in L:
            parts = L.replace(',', '').split()
            try:
                i = parts.index('input'); o = parts.index('output')
                uptime[current]['in']  = parts[i+1]
                uptime[current]['out'] = parts[o+1]
            except ValueError:
                pass

    # print table
    print(f"{'Intf':<20}{'IP':<15}{'Stat':<22}{'Prot':<8}{'Last In':<10}{'Last Out'}")
    up, down = [], []
    for i in interfaces:
        mark = 'UP' if (i['status']=='up' and i['protocol']=='up') else 'DOWN'
        (up if mark=='UP' else down).append(i['name'])
        ui = uptime.get(i['name'], {})
        print(f"{i['name']:<20}{i['ip']:<15}{i['status']:<22}{i['protocol']:<8}"
              f"{ui.get('in','-'):<10}{ui.get('out','-')}  {mark}")

    print(f"\nSummary: {len(up)} up, {len(down)} down")
