from netmiko import ConnectHandler

# device_ip = [ "172.31.21.1", "172.31.21.2","172.31.21.3","172.31.21.4","172.31.21.5" ]
device_ip = "172.31.21.4"
username = "admin"
password = "cisco"

device_params = {
    'device_type': 'cisco_ios',
    'ip': device_ip,
    'username': username,
    # 'password': password,
    'key_file' : "/home/devasc/.ssh/id_rsa",
    'use_keys': True,
    'disabled_algorithms': {
        'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']
    }
}

with ConnectHandler(**device_params) as ssh:
    result = ssh.enable()
    print(result)

    result = ssh.config_mode()
    print(result)

    result = ssh.send_command_timing("router ospf 1 vrf control")
    print(result)

    result = ssh.send_command_timing("network 172.31.21.0 0.0.0.255 area 0")
    print(result)

    result = ssh.send_command_timing("exit")
    print(result)

    result = ssh.send_command_timing("int gi0/2")
    print(result)

    result = ssh.send_command_timing("vrf forwarding control")
    print(result)

    result = ssh.send_command_timing("ip add 172.31.21.6 255.255.255.240")
    print(result)

    result = ssh.send_command_timing("ip ospf 1 area 0")
    print(result)

    result = ssh.send_command_timing("no shut")
    print(result)

    result = ssh.send_command_timing("exit")
    print(result)

    result = ssh.send_command_timing("int loopback0")
    print(result)

    result = ssh.send_command_timing("ip add 1.1.1.1 255.255.255.0")
    print(result)

    result = ssh.send_command_timing("no shut")
    print(result)

    result = ssh.send_command_timing("vrf forwarding control")
    print(result)

    result = ssh.send_command_timing("ip ospf 1 area 0")
    print(result)


    ssh.disconnect()
    