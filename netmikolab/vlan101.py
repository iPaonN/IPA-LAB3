from netmiko import ConnectHandler

# device_ip = [ "172.31.21.1", "172.31.21.2","172.31.21.3","172.31.21.4","172.31.21.5" ]
device_ip = "172.31.21.3"
username = "admin"
password = "cisco"

device_params = {
    'device_type': 'cisco_ios',
    'ip': device_ip,
    'username': username,
    'password': password,
}

with ConnectHandler(**device_params) as ssh:
    result = ssh.enable()
    print(result)

    result = ssh.config_mode()
    print(result)

    result = ssh.send_command_timing("vlan 101")
    print(result)

    result = ssh.send_command_timing("name control-data")
    print(result)
    
    result = ssh.send_command_timing("exit")
    print(result)
    
    result = ssh.send_command_timing("int vlan 101")
    print(result)
    
    result = ssh.send_command_timing("no shut")
    print(result)
    
    result = ssh.send_command_timing("exit")
    print(result)

    ssh.disconnect()
    
    