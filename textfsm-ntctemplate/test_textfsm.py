#!/usr/bin/env python3

import sys
import os

# Add current directory to path so we can import textfsm_config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from textfsm_config import NetworkDevice

class TestTextFSMTDD:
    """TDD Test Cases for TextFSM Interface Description Configuration"""
    
    def test_r1_interface_descriptions(self):
        """Test R1 interface descriptions based on network topology"""
        device = NetworkDevice("R1", "172.31.21.4")
        
        # Configure interface descriptions
        device.configure_interface_descriptions()
        
        # Test PC connection (static)
        assert device.get_interface_description("Gi0/1") == "Connect to PC"
        
        # Test CDP neighbor connection to R2
        r2_desc = device.get_interface_description("Gi0/2")
        assert "Connect to G0/1 of R2" in r2_desc
        
        device.disconnect()
    
    def test_r2_interface_descriptions(self):
        """Test R2 interface descriptions based on network topology"""
        device = NetworkDevice("R2", "172.31.21.5")
        
        # Configure interface descriptions
        device.configure_interface_descriptions()
        
        # Test CDP neighbor connection to R1
        r1_desc = device.get_interface_description("Gi0/1")
        assert "Connect to G0/2 of R1" in r1_desc
        
        # Test CDP neighbor connection to S1
        s1_desc = device.get_interface_description("Gi0/2")
        assert "Connect to G0/1 of S1" in s1_desc
        
        # Test WAN connection (static, DHCP client)
        assert device.get_interface_description("Gi0/3") == "Connect to WAN"
        
        device.disconnect()
    
    def test_s1_interface_descriptions(self):
        """Test S1 interface descriptions based on network topology"""
        device = NetworkDevice("S1", "172.31.21.3")
        
        # Configure interface descriptions
        device.configure_interface_descriptions()
        
        # Test CDP neighbor connection to R2
        r2_desc = device.get_interface_description("Gi0/1")
        assert "Connect to G0/2 of R2" in r2_desc
        
        # Test PC connection (static)
        assert device.get_interface_description("Gi0/3") == "Connect to PC"
        
        device.disconnect()
    
    def test_cdp_neighbor_parsing(self):
        """Test CDP neighbor parsing functionality"""
        device = NetworkDevice("R1", "172.31.21.4")
        
        # Get CDP neighbors
        neighbors = device.get_cdp_neighbors()
        
        # Should have at least one neighbor (R2)
        assert len(neighbors) > 0
        
        # Check neighbor structure
        neighbor = neighbors[0]
        assert 'local_interface' in neighbor
        assert 'neighbor_name' in neighbor
        assert 'neighbor_interface' in neighbor
        
        device.disconnect()
    
    def test_interface_description_format(self):
        """Test that interface descriptions follow the correct format"""
        device = NetworkDevice("R1", "172.31.21.4")
        device.configure_interface_descriptions()
        
        # Get all interface descriptions
        descriptions = device.get_all_interface_descriptions()
        
        for intf, desc in descriptions.items():
            if desc and desc != "":
                # Should start with "Connect to"
                assert desc.startswith("Connect to"), f"Interface {intf} description '{desc}' doesn't start with 'Connect to'"
                
                # Should be either PC, WAN, or follow CDP format
                if desc == "Connect to PC" or desc == "Connect to WAN":
                    assert True  # Valid static descriptions
                else:
                    # Should contain " of " for CDP descriptions
                    assert " of " in desc, f"CDP description '{desc}' missing ' of '"
        
        device.disconnect()
    
    def test_all_devices_configuration(self):
        """Integration test - configure all devices and verify topology"""
        devices = [
            ("R1", "172.31.21.4"),
            ("R2", "172.31.21.5"),
            ("S1", "172.31.21.3")
        ]
        
        configured_devices = []
        
        try:
            # Configure all devices
            for name, ip in devices:
                device = NetworkDevice(name, ip)
                device.configure_interface_descriptions()
                configured_devices.append(device)
            
            # Verify topology connections
            r1, r2, s1 = configured_devices
            
            # R1 topology verification
            assert r1.get_interface_description("Gi0/1") == "Connect to PC"
            assert "R2" in r1.get_interface_description("Gi0/2")
            
            # R2 topology verification  
            assert "R1" in r2.get_interface_description("Gi0/1")
            assert "S1" in r2.get_interface_description("Gi0/2")
            assert r2.get_interface_description("Gi0/3") == "Connect to WAN"
            
            # S1 topology verification
            assert "R2" in s1.get_interface_description("Gi0/1")
            assert s1.get_interface_description("Gi0/3") == "Connect to PC"
            
        finally:
            # Clean up connections
            for device in configured_devices:
                device.disconnect()

if __name__ == '__main__':
    # Run tests directly without pytest for simple execution
    print("Running TDD Tests for TextFSM Interface Configuration...")
    
    test_suite = TestTextFSMTDD()
    
    tests = [
        ("R1 Interface Descriptions", test_suite.test_r1_interface_descriptions),
        ("R2 Interface Descriptions", test_suite.test_r2_interface_descriptions),
        ("S1 Interface Descriptions", test_suite.test_s1_interface_descriptions),
        ("CDP Neighbor Parsing", test_suite.test_cdp_neighbor_parsing),
        ("Interface Description Format", test_suite.test_interface_description_format),
        ("All Devices Configuration", test_suite.test_all_devices_configuration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Testing: {test_name}")
            test_func()
            print(f"✅ PASSED: {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name} - {str(e)}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"TDD Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All TDD tests passed! TextFSM implementation is correct.")
        sys.exit(0)
    else:
        print("❗ Some tests failed. Fix implementation and run again.")
        sys.exit(1)
