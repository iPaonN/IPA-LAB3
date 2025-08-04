#!/usr/bin/env python3

import os
from netmiko import ConnectHandler
from pathlib import Path

current_dir = Path(__file__).parent
templates_path = current_dir / "lib" / "python3.8" / "site-packages" / "ntc_templates" / "templates"
if templates_path.exists():
    os.environ['NET_TEXTFSM'] = str(templates_path)

devices = {
    "R1": "172.31.21.4",
    "R2": "172.31.21.5",
    "S1": "172.31.21.3"
}

DEVICE_PARAMS = {
    'device_type': 'cisco_ios',
    'username': 'admin',
    'use_keys': True,
    'key_file': str(Path.home() / ".ssh" / "id_rsa"),
    'timeout': 20
}

def connect_device(name):
    """Connect to device"""
    device_params = DEVICE_PARAMS.copy()
    device_params.update({'host': devices[name]})
    return ConnectHandler(**device_params)

def set_description(conn, intf, description):
    """Set interface description"""
    commands = [
        f'int {intf}',
        f'description {description}',
        'end'
    ]
    return conn.send_config_set(commands)

def get_description(conn, intf):
    """Get interface description"""
    results = conn.send_command("show interfaces description", use_textfsm=True)
    for result in results:
        if result.get("port", "").lower() == intf.lower():
            return result.get("description", "")
    return ""

def get_cdp(conn):
    """Get CDP neighbors"""
    return conn.send_command("show cdp neighbors detail", use_textfsm=True)

def autoset_description(conn):
    """Auto set descriptions"""
    
    neighbors = get_cdp(conn)
    
    # Static PC and WAN connections
    if conn.host == "172.31.21.4":  # R1
        print("Setting on GigabitEthernet0/1: Connect to PC")
        set_description(conn, "Gi0/1", "Connect to PC")
    elif conn.host == "172.31.21.5":  # R2
        print("Setting on GigabitEthernet0/3: Connect to WAN")
        set_description(conn, "Gi0/3", "Connect to WAN")
    elif conn.host == "172.31.21.3":  # S1
        print("Setting on GigabitEthernet0/3: Connect to PC")
        set_description(conn, "Gi0/3", "Connect to PC")
    
    for entry in neighbors:
        local = entry.get("local_interface")
        nbr = entry.get("neighbor_name")
        nbr_intf = entry.get("neighbor_interface")
        
        if not all([local, nbr, nbr_intf]):
            continue
        
        short_intf = nbr_intf.replace('GigabitEthernet', 'G').replace('FastEthernet', 'F')
        desc = f"Connect to {short_intf} of {nbr}"
        print(f"Setting on {local}: {desc}")
        set_description(conn, local, desc)

if __name__ == '__main__':
    print("Configuring all devices...")
    
    for device_name in devices.keys():
        print(f"\n--- Configuring {device_name} ---")
        try:
            conn = connect_device(device_name)
            autoset_description(conn)
            conn.disconnect()
            print(f"✅ {device_name} configured")
        except Exception as e:
            print(f"❌ {device_name} failed: {e}")
    
    print("\nDone!")
