#!/usr/bin/env python3
"""
TextFSM Interface Description Configuration Program
TDD Implementation for Network Device Interface Management
"""

import os
import sys
from pathlib import Path
from netmiko import ConnectHandler

class NetworkDevice:
    """Network Device class for TextFSM-based interface configuration"""
    
    def __init__(self, name, host):
        """Initialize network device connection"""
        self.name = name
        self.host = host
        self.connection = None
        
        # Setup TextFSM templates path
        current_dir = Path(__file__).parent
        templates_path = current_dir / "lib" / "python3.8" / "site-packages" / "ntc_templates" / "templates"
        if templates_path.exists():
            os.environ['NET_TEXTFSM'] = str(templates_path)
        
        # Device connection parameters
        self.device_params = {
            'device_type': 'cisco_ios',
            'host': host,
            'username': 'admin',
            'use_keys': True,
            'key_file': str(Path.home() / ".ssh" / "id_rsa"),
            'timeout': 20
        }
        
        # Connect to device
        self._connect()
    
    def _connect(self):
        """Establish connection to network device"""
        try:
            self.connection = ConnectHandler(**self.device_params)
            print(f"✅ Connected to {self.name} ({self.host})")
        except Exception as e:
            print(f"❌ Failed to connect to {self.name}: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from network device"""
        if self.connection:
            self.connection.disconnect()
            print(f"🔌 Disconnected from {self.name}")
    
    def get_cdp_neighbors(self):
        """Get CDP neighbors using TextFSM parsing"""
        try:
            output = self.connection.send_command("show cdp neighbors detail", use_textfsm=True)
            print(f"📡 Found {len(output)} CDP neighbors on {self.name}")
            return output
        except Exception as e:
            print(f"❌ Error getting CDP neighbors from {self.name}: {e}")
            return []
    
    def set_interface_description(self, interface, description):
        """Set description on specific interface"""
        try:
            commands = [
                f'interface {interface}',
                f'description {description}',
                'end'
            ]
            result = self.connection.send_config_set(commands)
            print(f"🔧 {self.name} {interface}: {description}")
            return True
        except Exception as e:
            print(f"❌ Error setting description on {self.name} {interface}: {e}")
            return False
    
    def get_interface_description(self, interface):
        """Get description of specific interface using TextFSM"""
        try:
            output = self.connection.send_command("show interfaces description", use_textfsm=True)
            for intf_data in output:
                port = intf_data.get('port', '').lower()
                if port == interface.lower():
                    return intf_data.get('description', '')
            return ""
        except Exception as e:
            print(f"❌ Error getting interface description from {self.name}: {e}")
            return ""
    
    def get_all_interface_descriptions(self):
        """Get all interface descriptions"""
        try:
            output = self.connection.send_command("show interfaces description", use_textfsm=True)
            descriptions = {}
            for intf_data in output:
                port = intf_data.get('port', '')
                desc = intf_data.get('description', '')
                if port:
                    descriptions[port] = desc
            return descriptions
        except Exception as e:
            print(f"❌ Error getting all interface descriptions from {self.name}: {e}")
            return {}
    
    def configure_interface_descriptions(self):
        """Configure interface descriptions based on topology and CDP"""
        print(f"\n🚀 Configuring interface descriptions on {self.name}...")
        
        # Step 1: Configure static connections
        self._configure_static_connections()
        
        # Step 2: Configure CDP descriptions  
        neighbors = self.get_cdp_neighbors()
        self._configure_cdp_descriptions(neighbors)
        
        print(f"✅ Completed configuration on {self.name}")
    
    def _configure_static_connections(self):
        """Configure static PC and WAN connections per topology"""
        print(f"📍 Configuring static connections on {self.name}...")
        
        static_rules = {
            "R1": {"Gi0/1": "Connect to PC"},
            "R2": {"Gi0/3": "Connect to WAN"},
            "S1": {"Gi0/3": "Connect to PC"}
        }
        
        if self.name in static_rules:
            for interface, description in static_rules[self.name].items():
                self.set_interface_description(interface, description)
    
    def _configure_cdp_descriptions(self, neighbors):
        """Configure descriptions based on CDP neighbor information"""
        print(f"🔍 Configuring CDP-based descriptions on {self.name}...")
        
        for neighbor in neighbors:
            local_intf = neighbor.get('local_interface')
            remote_device = neighbor.get('neighbor_name')
            remote_intf = neighbor.get('neighbor_interface')
            
            if not all([local_intf, remote_device, remote_intf]):
                continue
            
            # Format: "Connect to <Interface-name> of <Remote device name>"
            short_remote_intf = self._shorten_interface_name(remote_intf)
            device_name = remote_device.split('.')[0]
            description = f"Connect to {short_remote_intf} of {device_name}"
            self.set_interface_description(local_intf, description)
    
    def _shorten_interface_name(self, interface_name):
        """Shorten interface names for descriptions"""
        replacements = {
            'GigabitEthernet': 'G',
            'FastEthernet': 'F',
            'Ethernet': 'E'
        }
        
        shortened = interface_name
        for full, short in replacements.items():
            shortened = shortened.replace(full, short)
        return shortened

if __name__ == '__main__':
    """Main program entry point"""
    devices = [
        ("R1", "172.31.21.4"),
        ("R2", "172.31.21.5"), 
        ("S1", "172.31.21.3")
    ]
    
    print("🌐 Starting TextFSM Interface Description Configuration")
    
    for name, ip in devices:
        try:
            print(f"\n{'='*20} {name} {'='*20}")
            device = NetworkDevice(name, ip)
            device.configure_interface_descriptions()
            device.disconnect()
        except Exception as e:
            print(f"❌ Failed to configure {name}: {e}")
    
    print(f"\n✅ TextFSM Interface Configuration Complete!")
