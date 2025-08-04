from netmiko import ConnectHandler
from jinja2 import Environment, FileSystemLoader
import yaml
import os

def load_config(config_file):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

def generate_config(template_file, variables):
    template_dir = os.path.dirname(os.path.abspath(__file__))
    
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)
    
    config = template.render(variables)
    return config

device_ip = "172.31.21.5"
username = "admin"
password = "cisco"

device_params = {
    'device_type': 'cisco_ios',
    'ip': device_ip,
    'username': username,
    # 'password': password,
    'key_file': "/home/devasc/.ssh/id_rsa",
    'use_keys': True,
}

try:
    config_vars = load_config('router_vars.yml')
except FileNotFoundError:
    print("Error: router_vars.yml file not found!")
    exit(1)
except yaml.YAMLError as e:
    print(f"Error parsing YAML file: {e}")
    exit(1)

try:
    router_config = generate_config('router_config.j2', config_vars)
except Exception as e:
    print(f"Error generating configuration from template: {e}")
    exit(1)

print("Generated Configuration:")
print("=" * 50)
print(router_config)
print("=" * 50)

try:
    with ConnectHandler(**device_params) as ssh:
        print("Connecting to device...")
        
        result = ssh.enable()
        print("Enable mode:", result)

        result = ssh.config_mode()
        print("Config mode:", result)
        
        print("\nApplying configuration...")
        result = ssh.send_config_set(router_config.split('\n'))
        print("Configuration applied successfully!")
        
        result = ssh.save_config()
        print("Configuration saved:", result)
        
        ssh.disconnect()
        print("Connection closed.")
        
except Exception as e:
    print(f"Error connecting to device or applying configuration: {e}")
    exit(1)
    