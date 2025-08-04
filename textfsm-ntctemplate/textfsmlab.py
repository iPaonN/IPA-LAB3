#!/usr/bin/env python3
"""Simple TextFSM lab - parse CDP neighbors and configure interfaces"""

import re
from netmiko import ConnectHandler


def parse_cdp_neighbors(cdp_output):
    """Parse CDP output into simple neighbor list"""
    neighbors = []
    lines = cdp_output.strip().split('\n')
    
    # Skip to data section
    data_started = False
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Find data start
        if 'Device ID' in line and 'Local Intrfce' in line:
            data_started = True
            continue
        
        # Skip non-data lines
        if not data_started or 'Total cdp entries' in line:
            continue
        if any(x in line for x in ['Capability', 'Router', 'Bridge', 'Switch']):
            continue
        
        # Parse neighbor data
        parts = line.split()
        if len(parts) >= 6:
            device_id = parts[0]
            local_int = parts[1]
            
            # Handle "Gig 0/1" format
            if len(parts) >= 7 and parts[2].startswith(('0/', '1/', '2/', '3/')):
                local_int = f"{parts[1]} {parts[2]}"
                remote_int = parts[-1]
            else:
                remote_int = parts[-1]
            
            # Normalize interfaces
            local_int = fix_interface(local_int)
            remote_int = 'PC' if 'PC' in device_id else fix_interface(remote_int)
            
            neighbors.append({
                'device_id': device_id,
                'local_interface': local_int,
                'remote_interface': remote_int
            })
    
    return neighbors


def fix_interface(interface):
    """Fix interface names to full format"""
    interface = interface.strip()
    
    # Convert short to long names
    if interface.lower().startswith(('gig', 'gi')):
        match = re.search(r'(\d+/\d+)', interface)
        if match:
            return f"GigabitEthernet{match.group(1)}"
    elif interface.lower().startswith('fa'):
        match = re.search(r'(\d+/\d+)', interface)
        if match:
            return f"FastEthernet{match.group(1)}"
    
    return interface


def generate_interface_description(neighbor):
    """Create description for interface"""
    device_id = neighbor['device_id']
    remote_int = neighbor['remote_interface']
    
    if 'PC' in device_id or remote_int == 'PC':
        return "Connect to PC"
    elif device_id == 'WAN':
        return "Connect to WAN"
    else:
        # Shorten interface name for description
        short_int = remote_int.replace('GigabitEthernet', 'G').replace('FastEthernet', 'F')
        return f"Connect to {short_int} of {device_id}"


def generate_config_commands(neighbors):
    """Generate config commands from neighbors"""
    commands = []
    for neighbor in neighbors:
        commands.append(f"interface {neighbor['local_interface']}")
        commands.append(f"description {generate_interface_description(neighbor)}")
    return commands


def handle_special_cases(device_name, neighbors):
    """Add special interfaces like R2 WAN and PC connections"""
    updated_neighbors = neighbors.copy()
    
    if device_name == 'R1':
        has_gi01 = any(n['local_interface'] == 'GigabitEthernet0/1' for n in neighbors)
        if not has_gi01:
            updated_neighbors.append({
                'device_id': 'PC',
                'local_interface': 'GigabitEthernet0/1',
                'remote_interface': 'PC'
            })
    
    elif device_name == 'R2':
        has_wan = any(n['local_interface'] == 'GigabitEthernet0/3' for n in neighbors)
        if not has_wan:
            updated_neighbors.append({
                'device_id': 'WAN',
                'local_interface': 'GigabitEthernet0/3',
                'remote_interface': 'WAN'
            })
    
    elif device_name == 'S1':
        has_gi03 = any(n['local_interface'] == 'GigabitEthernet0/3' for n in neighbors)
        if not has_gi03:
            updated_neighbors.append({
                'device_id': 'PC',
                'local_interface': 'GigabitEthernet0/3',
                'remote_interface': 'PC'
            })
    
    return updated_neighbors


def configure_device(device):
    """Configure one device"""
    device_name = device['name']
    try:
        params = {k: v for k, v in device.items() if k != 'name'}
        with ConnectHandler(**params) as conn:
            cdp_output = conn.send_command("show cdp neighbors")
            neighbors = parse_cdp_neighbors(cdp_output)
            neighbors = handle_special_cases(device_name, neighbors)
            commands = generate_config_commands(neighbors)
            
            if commands:
                conn.send_config_set(commands)
                return {'success': True, 'device': device_name, 'message': f"Configured {len(neighbors)} interfaces"}
            else:
                return {'success': True, 'device': device_name, 'message': "No interfaces to configure"}
    except Exception as e:
        return {'success': False, 'device': device_name, 'message': str(e)}

class DeviceConnection:
    def __init__(self, device):
        self.device = device
        self.connection = None
    
    def connect(self):
        try:
            params = {k: v for k, v in self.device.items() if k != 'name'}
            self.connection = ConnectHandler(**params)
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        if self.connection:
            self.connection.disconnect()
            self.connection = None


class NetworkConfigManager:
    def __init__(self, devices):
        self.devices = devices
    
    def parse_cdp_neighbors(self, cdp_output):
        return parse_cdp_neighbors(cdp_output)
    
    def generate_interface_description(self, neighbor):
        return generate_interface_description(neighbor)
    
    def generate_config_commands(self, neighbors):
        return generate_config_commands(neighbors)
    
    def handle_special_cases(self, device_name, neighbors):
        return handle_special_cases(device_name, neighbors)
    
    def configure_device(self, device):
        return configure_device(device)


if __name__ == '__main__':
    devices = [
        {'name': 'R1', 'device_type': 'cisco_ios', 'ip': '172.31.21.4', 'username': 'admin', 'key_file': '/home/devasc/.ssh/id_rsa', 'use_keys': True, 'conn_timeout': 20, 'disabled_algorithms': {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}},
        {'name': 'R2', 'device_type': 'cisco_ios', 'ip': '172.31.21.5', 'username': 'admin', 'key_file': '/home/devasc/.ssh/id_rsa', 'use_keys': True, 'conn_timeout': 20, 'disabled_algorithms': {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}},
        {'name': 'S1', 'device_type': 'cisco_ios', 'ip': '172.31.21.3', 'username': 'admin', 'key_file': '/home/devasc/.ssh/id_rsa', 'use_keys': True, 'conn_timeout': 20, 'disabled_algorithms': {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}}
    ]
    
    print("Configuring devices...")
    for device in devices:
        result = configure_device(device)
        print(f"{result['device']}: {result['message']}")
