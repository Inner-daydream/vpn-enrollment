import wireguard
import re
import config
import app.dynamodb as dynamodb
import werkzeug.utils as wutils
import boto3
import subprocess

config = config.WireGuardConfig
config_files = ["wg0.conf","wg0-peers.conf"]

def add_peer(peer_name,Id):
    server = wireguard.Server(
        description=config.SERVER_DESCRIPTION,
        subnet=config.SERVER_SUBNET,
        address=config.SERVER_ADDRESS,
        private_key=config.PRIVATE_KEY
    )
    peer = server.peer(
        description=f"{peer_name}#{Id}"
    )
    server.config().write(config_path=config.TEMP_CONFIG_PATH)
    with open(f'{config.TEMP_CONFIG_PATH}/wg0.conf',"r+") as temp_config:
        content = temp_config.read()
        content = re.sub(r"%i .*wg0-peers.conf$",f"%i {config.PRODUCTION_CONFIG_PATH}/wg0-peers.conf",content)
        with open(f'{config.PRODUCTION_CONFIG_PATH}/wg0.conf',"w") as production_config:
            production_config.write(content)
    with open(f"{config.PRODUCTION_CONFIG_PATH}/wg0-peers.conf","a+") as production_config:
        content = production_config.read()
        content += server.config().peers
        production_config.write(content)
    dynamodb.add_peer(Id=Id,peer_name=peer_name,public_key=peer.public_key,AllowedIPs=str(peer.allowed_ips))
    local_config = re.sub(r"ListenPort = \d+","",peer.config().local_config)
    local_config = re.sub(r"AllowedIPs = \d+\.\d+\.\d+\.\d+\/\d{1,2}\n",f"AllowedIPs = {config.ALLOWED_IPS}\n",local_config)
    local_config = local_config.replace("[Interface]\n",f"[Interface]\nDNS = {config.DNS}\n")
    local_config += f"Endpoint = {config.ENDPOINT}\n"
    local_config += f'PersistentKeepalive = {config.KEEPALIVE}'
    filename = wutils.secure_filename(f'{peer_name}.conf')
    save_config()
    subprocess.Popen('/bin/bash -c "wg syncconf wg0 <(wg-quick strip wg0 && wg-quick strip wg0-peers)"',shell=True)
    return filename,local_config

def remove_peer(peer_name,Id):
    with open(f"{config.PRODUCTION_CONFIG_PATH}/wg0-peers.conf","r+") as production_config:
        content =  production_config.read()
        remove_regex = r"\[Peer\]\nAllowedIPs = \d+\.\d+\.\d+\.\d+\/\d{1,2}\n# "+ re.escape(f"{peer_name}#{Id}") + r"\nPublicKey = .*="
        content = re.sub(remove_regex,"",content)
        content = re.sub(r'^\n',"",content)
        production_config.truncate(0)
        production_config.seek(0)
        production_config.write(content)
    dynamodb.remove_peer(peer_name=peer_name,Id=Id)
    save_config()
    subprocess.Popen('/bin/bash -c "wg syncconf wg0 <(wg-quick strip wg0 && wg-quick strip wg0-peers)"',shell=True)

def save_config():
    s3 = boto3.client("s3")
    for file in config_files:
        s3.upload_file(
            Filename=f"{config.PRODUCTION_CONFIG_PATH}/{file}",
            Bucket="vpnenrollment",
            Key=f"config/{file}"
        )
def retrieve_config():
    s3 = boto3.client("s3")
    for file in config_files:
        s3.download_file(
            Bucket="vpnenrollment", 
            Key=f"config/{file}", 
            Filename=f"{config.PRODUCTION_CONFIG_PATH}/{file}"
        )
  