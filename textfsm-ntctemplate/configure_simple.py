#!/usr/bin/env python3

from textfsmlab import connect_device, autoset_description

def main():
    devices = ['R1', 'R2', 'S1']
    
    for device_name in devices:
        print(f"\n=== Configuring {device_name} ===")
        
        conn = connect_device(device_name)
        autoset_description(conn)
        conn.disconnect()
        
        print(f"✅ {device_name} configured successfully")

if __name__ == '__main__':
    main()
