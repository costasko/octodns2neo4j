import json
import os
import yaml
import ipaddress
import csv
import requests


ZONE_PATH = os.environ.get('ZONE_PATH', 'k8s.io/dns/zone-configs/')


def get_aws_range() -> list:
    iprange = requests.get(
        'https://ip-ranges.amazonaws.com/ip-ranges.json').json()
    return [prefix['ip_prefix'] for prefix in iprange['prefixes']]


def get_gcp_range() -> list:
    iprange = requests.get(
        'https://www.gstatic.com/ipranges/cloud.json').json()
    return [prefix['ipv4Prefix'] for prefix in iprange['prefixes'] if 'ipv4Prefix' in prefix]


ip_ranges = {"AWS": get_aws_range(),
             "GCP": get_gcp_range()}

provider_names = {'GOOGLE': ['googlehosted.com.', 'google.com.', 'googledomains.com'],
                  'AWS': ['amazonses.com.', 'cloudfront.net.', '.amazonaws.com.', '.awsdns'],
                  'NETLIFY': ['netlify.app.', 'netlifyglobalcdn.com.']}


def maprange(ip):
    ipaddr = ipaddress.ip_address(ip)
    for name, networks in ip_ranges.items():
        for network in networks:
            if ipaddr in ipaddress.ip_network(network, False):
                return {name: ipaddr}
    return {'UNKNOWNIP': ipaddr}


def mapdomain(domain):
    for provider, patterns in provider_names.items():
        if any(pattern in domain for pattern in patterns):
            return {provider: domain}
    return {'UNKNOWNPROVIDER': domain}


def tofile(fqdn, record, dnstype, result):
    with open('domains.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([fqdn.split('.yaml')[0], record, dnstype, result])


def parseDNS(fqdn, record, dnstype) -> dict:
    if 'values' in record:
        for r in record['values']:
            v = picker(r, dnstype)
            if v:
                tofile(fqdn, r, dnstype, list(v.keys())[0])
    elif 'value' in record:
        v = picker(record['value'], dnstype)
        if v:
            tofile(fqdn, record['value'], dnstype, list(v.keys())[0])


def picker(record, dnstype):
    if dnstype == 'A':
        return maprange(record)
    elif dnstype == 'CNAME':
        return mapdomain(record)
    else:
        return None


for zone in os.listdir(ZONE_PATH):
    print(zone)
    with open(f'{ZONE_PATH}{zone}') as f:
        domains = yaml.load(f, Loader=yaml.BaseLoader)
    results = []
    for k, v in domains.items():
        fqdn = f'{k}.{zone}'
        if isinstance(v, list):
            for value in v:
                parseDNS(fqdn, value, value['type'])
        else:
            parseDNS(fqdn, v, v['type'])
