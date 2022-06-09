"""Provides utilities to manage the wireguard VPN"""
import re
import subprocess

import wireguard
import boto3
import werkzeug.utils as wutils

import config
from app import dynamodb

Config = config.WireGuardConfig
config_files = ["wg0.conf","wg0-peers.conf"]

def add_peer(peer_name,id):
    """add peer to config"""
    server = wireguard.Server(
        description=Config.SERVER_DESCRIPTION,
        subnet=Config.SERVER_SUBNET,
        address=Config.SERVER_ADDRESS,
        private_key=Config.PRIVATE_KEY
    )
    peer = server.peer(
        description=f"{peer_name}#{id}"
    )
    server.config().write(config_path=Config.TEMP_CONFIG_PATH)
    with open(
        f'{Config.TEMP_CONFIG_PATH}/wg0.conf',
        "r+",
         encoding="UTF-8") as temp_config:
        content = temp_config.read()
        content = re.sub(
            r"%i .*wg0-peers.conf$",
            f'%i {Config.PRODUCTION_CONFIG_PATH}/wg0-peers.conf;' \
              'iptables -A FORWARD -i %i -j ACCEPT;' \
              'iptables -A FORWARD -o %i -j ACCEPT;' \
             f"iptables -t nat -A POSTROUTING -o {Config.NET_INTERFACE} -j MASQUERADE",
            content)
        content += \
            '\nPostDown = iptables -D FORWARD -i %i -j ACCEPT;' \
            'iptables -D FORWARD -o %i -j ACCEPT;' \
            f'iptables -t nat -D POSTROUTING -o {Config.NET_INTERFACE} -j MASQUERADE'
        with open(
            f'{Config.PRODUCTION_CONFIG_PATH}/wg0.conf',
            "w",
            encoding="UTF-8") as production_config:
            production_config.write(content)

    with open(
        f"{Config.PRODUCTION_CONFIG_PATH}/wg0-peers.conf",
        "a+",
        encoding="UTF-8") as production_config:
        content = production_config.read()
        content += server.config().peers
        production_config.write(content)

    dynamodb.add_peer(
        id=id,
        peer_name=peer_name,
        public_key=peer.public_key,
        allowed_ips=str(peer.allowed_ips))
    local_config = re.sub(r"ListenPort = \d+","",peer.config().local_config)
    local_config = re.sub(
        r"AllowedIPs = \d+\.\d+\.\d+\.\d+\/\d{1,2}\n",
        f"AllowedIPs = {Config.ALLOWED_IPS}\n",
        local_config)
    local_config = local_config.replace("[Interface]\n",f"[Interface]\nDNS = {Config.DNS}\n")
    local_config += f"Endpoint = {Config.ENDPOINT}\n"
    local_config += f'PersistentKeepalive = {Config.KEEPALIVE}'
    filename = wutils.secure_filename(f'{peer_name}.conf')
    save_config()
    subprocess.Popen(
        '/bin/bash -c "wg syncconf wg0 <(wg-quick strip wg0 && wg-quick strip wg0-peers)"',
        shell=True)
    return filename,local_config

def remove_peer(peer_name,id):
    """Revoke a peer in the peers configuration file and database"""
    with open(
        f"{Config.PRODUCTION_CONFIG_PATH}/wg0-peers.conf",
        "r+",
        encoding="UTF-8") as production_config:
        content =  production_config.read()
        remove_regex = r"\[Peer\]\nAllowedIPs = \d+\.\d+\.\d+\.\d+\/\d{1,2}\n# " + \
        re.escape(f"{peer_name}#{id}") + \
        r"\nPublicKey = .*="
        content = re.sub(remove_regex,"",content)
        content = re.sub(r'^\n',"",content)
        production_config.truncate(0)
        production_config.seek(0)
        production_config.write(content)
    dynamodb.remove_peer(peer_name=peer_name,id=id)
    save_config()
    subprocess.Popen(
        '/bin/bash -c "wg syncconf wg0 <(wg-quick strip wg0 && wg-quick strip wg0-peers)"',
        shell=True)

def save_config():
    """Save the wireguard configuration files to AWS S3"""
    s3 = boto3.client("s3")
    for file in config_files:
        s3.upload_file(
            Filename=f"{Config.PRODUCTION_CONFIG_PATH}/{file}",
            Bucket="vpnenrollment",
            Key=f"config/{file}"
        )
def retrieve_config():
    """Retrieve the wireguard configuration files from AWS S3"""
    s3 = boto3.client("s3")
    for file in config_files:
        s3.download_file(
            Bucket="vpnenrollment",
            Key=f"config/{file}",
            Filename=f"{Config.PRODUCTION_CONFIG_PATH}/{file}"
        )
  