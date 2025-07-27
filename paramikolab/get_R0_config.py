import time
import paramiko

username = 'admin'
target_ip = "172.31.21.4"
key_path = '/home/devasc/.ssh/id_rsa'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

print(f"Connecting to {target_ip} as {username}...")

client.connect(
    hostname=target_ip,
    username=username,
    key_filename=key_path,
    look_for_keys=True,
    allow_agent=False,
    timeout=20,
    disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}
)

with client.invoke_shell() as ssh:
    print("Interactive shell established.")

    ssh.send("terminal length 0\n")
    time.sleep(1)
    output = ssh.recv(1000).decode('ascii')
    print(output)

    ssh.send("show run\n")
    time.sleep(5)
    output = ssh.recv(5000).decode('ascii')
    print(output)

    client.close()
