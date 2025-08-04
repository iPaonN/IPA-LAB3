#!/usr/bin/env python3
import os
import sys
from textfsmlab import parse_cdp_neighbors, generate_config_commands, handle_special_cases
from netmiko import ConnectHandler

DEVICES = {
    'R1': {'device_type':'cisco_ios', 'ip':'172.31.21.4', 'username':'admin', 'key_file':'/home/devasc/.ssh/id_rsa', 'use_keys':True, 'conn_timeout':20, 'disabled_algorithms':{'pubkeys':['rsa-sha2-256','rsa-sha2-512']}},
    'R2': {'device_type':'cisco_ios', 'ip':'172.31.21.5', 'username':'admin', 'key_file':'/home/devasc/.ssh/id_rsa', 'use_keys':True, 'conn_timeout':20, 'disabled_algorithms':{'pubkeys':['rsa-sha2-256','rsa-sha2-512']}},
    'S1': {'device_type':'cisco_ios', 'ip':'172.31.21.3', 'username':'admin', 'key_file':'/home/devasc/.ssh/id_rsa', 'use_keys':True, 'conn_timeout':20, 'disabled_algorithms':{'pubkeys':['rsa-sha2-256','rsa-sha2-512']}}
}

def test_real_devices_complete():
    """Test everything with real devices - CDP parsing, command generation, and descriptions"""
    print("=== TESTING ALL DEVICES WITH REAL CDP DATA ===")
    
    all_passed = True
    
    for device_name, device_config in DEVICES.items():
        print(f"\n--- Testing {device_name} ---")
        
        try:
            with ConnectHandler(**device_config) as conn:
                cdp_output = conn.send_command("show cdp neighbors")
                print(f"CDP Output from {device_name}:")
                print(cdp_output)
                
                neighbors = parse_cdp_neighbors(cdp_output)
                print(f"\nParsed {len(neighbors)} neighbors:")
                for n in neighbors:
                    print(f"  {n['local_interface']} -> {n['device_id']} ({n['remote_interface']})")
                
                #Since CDP can't detect PC and WAN connections, we handle special cases
                neighbors = handle_special_cases(device_name, neighbors)
                if device_name == 'R1':
                    print(f"After special cases: {len(neighbors)} neighbors (added PC on Gi0/1 if missing)")
                elif device_name == 'R2':
                    print(f"After special cases: {len(neighbors)} neighbors (added WAN on Gi0/3 if missing)")
                elif device_name == 'S1':
                    print(f"After special cases: {len(neighbors)} neighbors (added PC on Gi0/3 if missing)")
                
                commands = generate_config_commands(neighbors) 
                print(f"\nGenerated {len(commands)} commands:")
                for cmd in commands:
                    print(f"  {cmd}")
                
                for cmd in commands:
                    assert cmd.startswith("interface") or cmd.startswith("description"), f"Bad command: {cmd}"
                    assert "shutdown" not in cmd.lower(), f"Dangerous command: {cmd}"
                    assert "reload" not in cmd.lower(), f"Dangerous command: {cmd}"
                
                descriptions = [cmd for cmd in commands if cmd.startswith("description")]
                for desc in descriptions:
                    if "PC" in desc:
                        assert desc == "description Connect to PC", f"Bad PC description: {desc}"
                    elif "WAN" in desc:
                        assert desc == "description Connect to WAN", f"Bad WAN description: {desc}"
                    else:
                        assert "Connect to" in desc, f"Missing 'Connect to': {desc}"
                        assert " of " in desc, f"Missing ' of ': {desc}"
                
                print(f"{device_name} PASSED!")
                
        except Exception as e:
            print(f"{device_name} FAILED: {e}")
            all_passed = False
    
    if all_passed:
        print("\n ALL REAL DEVICE TESTS PASSED!")
        return True
    else:
        print("\n SOME TESTS FAILED!")
        return False

def test_real_devices_complete_pytest():
    """Pytest wrapper"""
    import pytest
    pytestmark = pytest.mark.skipif(
        os.getenv('ENABLE_REAL_TESTS', '0') != '1',
        reason="Set ENABLE_REAL_TESTS=1 to enable"
    )
    assert test_real_devices_complete()

if __name__ == '__main__':
    print("Running TextFSM Lab Tests...")
    success = test_real_devices_complete()
    sys.exit(0 if success else 1)
    