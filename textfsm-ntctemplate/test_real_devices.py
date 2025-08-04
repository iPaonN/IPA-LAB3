#!/usr/bin/env python3
import os
import pytest
from textfsmlab import NetworkConfigManager, DeviceConnection

pytestmark = pytest.mark.skipif(
    os.getenv('ENABLE_REAL_TESTS', '0') != '1',
    reason="Set ENABLE_REAL_TESTS=1 to enable"
)

DEVICES = [
    {'name':'R1', 'device_type':'cisco_ios', 'ip':'172.31.21.4', 'username':'admin', 'key_file':'/home/devasc/.ssh/id_rsa', 'use_keys':True, 'conn_timeout':20, 'disabled_algorithms':{'pubkeys':['rsa-sha2-256','rsa-sha2-512']}},
    {'name':'R2', 'device_type':'cisco_ios', 'ip':'172.31.21.5', 'username':'admin', 'key_file':'/home/devasc/.ssh/id_rsa', 'use_keys':True, 'conn_timeout':20, 'disabled_algorithms':{'pubkeys':['rsa-sha2-256','rsa-sha2-512']}},
    {'name':'S1', 'device_type':'cisco_ios', 'ip':'172.31.21.3', 'username':'admin', 'key_file':'/home/devasc/.ssh/id_rsa', 'use_keys':True, 'conn_timeout':20, 'disabled_algorithms':{'pubkeys':['rsa-sha2-256','rsa-sha2-512']}}
]

def test_connect():
    """Test connection works"""
    conn = DeviceConnection(DEVICES[0])
    assert conn.connect()
    output = conn.connection.send_command("show version")
    assert "Cisco" in output
    conn.disconnect()

def test_cdp_parsing():
    """Test CDP parsing"""
    conn = DeviceConnection(DEVICES[0])
    conn.connect()
    cdp_data = conn.connection.send_command("show cdp neighbors")
    conn.disconnect()
    
    manager = NetworkConfigManager([])
    neighbors = manager.parse_cdp_neighbors(cdp_data)
    assert isinstance(neighbors, list)

def test_commands():
    """Test command generation"""
    manager = NetworkConfigManager([])
    sample = [
        {'device_id':'PC1', 'local_interface':'GigabitEthernet0/1', 'remote_interface':'PC'},
        {'device_id':'R2', 'local_interface':'GigabitEthernet0/2', 'remote_interface':'GigabitEthernet0/3'}
    ]
    commands = manager.generate_config_commands(sample)
    assert len(commands) == 4
    for cmd in commands:
        assert cmd.startswith('interface') or cmd.startswith('description')

def test_wan_case():
    """Test R2 WAN special case"""
    manager = NetworkConfigManager([])
    neighbors = [{'device_id':'Test', 'local_interface':'GigabitEthernet0/1', 'remote_interface':'Test'}]
    updated = manager.handle_special_cases('R2', neighbors)
    wan_found = any(n['device_id'] == 'WAN' for n in updated)
    assert wan_found

def test_backup():
    """Test backup"""
    conn = DeviceConnection(DEVICES[0])
    conn.connect()
    config = conn.connection.send_command("show running-config")
    conn.disconnect()
    assert len(config) > 50
