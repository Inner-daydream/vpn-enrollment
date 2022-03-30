from audioop import add
from fileinput import filename
from os import sendfile
import wireguard
import re
import config
import app.dynamodb as dynamodb
import os
import io
import flask
import werkzeug.utils as wutils
config = config.WireGuardConfig
def add_peer(peer_name,Id):
    server = wireguard.Server(
        description=config.SERVER_DESCRIPTION,
        subnet=config.SERVER_SUBNET,
        address=config.SERVER_ADDRESS,
        private_key=config.PRIVATE_KEY
    )
    peer = server.peer(
        description=f"{peer_name}#{Id}",
        allowed_ips=config.ALLOWED_IPS
    )
    server.config().write(config_path=config.TEMP_CONFIG_PATH)
    os.replace(f"{config.TEMP_CONFIG_PATH}/wg0.conf",f"{config.PRODUCTION_CONFIG_PATH}/wg0.conf")
    with open(f"{config.PRODUCTION_CONFIG_PATH}/wg0-peers.conf","a+") as production_config:
        print(config.PRODUCTION_CONFIG_PATH)
        content = production_config.read()
        content += server.config().peers
        production_config.write(content)
    dynamodb.add_peer(Id=Id,peer_name=peer_name,public_key=peer.public_key,AllowedIPs=str(peer.allowed_ips))
    local_config = re.sub(r"AllowedIPs = \d+\.\d+\.\d+\.\d+\/\d{1,2}\n",f"AllowedIPs = {config.ALLOWED_IPS}\n",peer.config().local_config)
    local_config = local_config.replace("[Interface]\n",f"[Interface]\nDNS = {config.DNS}\n")
    local_config += f"Endpoint = {config.ENDPOINT}\n"
    local_config += f'PersistentKeepalive = {config.KEEPALIVE}'
    print(local_config)
    filename = wutils.secure_filename(f'{peer_name}.conf')
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