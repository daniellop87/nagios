#!/usr/bin/env python3
# va perfecto!
import os
import sys
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from pysnmp.hlapi import *

# Obtener datos de versiones de RouterOS desde el sitio web
def get_latest_versions():
    url = "https://mikrotik.com/download/changelogs/long-term-release-tree"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    version_elements = soup.find_all("a", {"data-load-ajax": True})

    versions = []

    for element in version_elements:
        version = element["data-load-ajax"]
        date = element.find_next("span", class_="pull-right pl").text
        href = element["href"]
        tab_tree_id = href[href.index("show-tab-tree_") + len("show-tab-tree_"):href.index("-id")]

        tab_tree_name = ""
        if tab_tree_id == "1":
            tab_tree_name = "Testing"
        elif tab_tree_id == "2":
            tab_tree_name = "Long-term"
        elif tab_tree_id == "3":
            tab_tree_name = "Stable"
        elif tab_tree_id == "4":
            tab_tree_name = "Development"
        elif tab_tree_id == "5":
            tab_tree_name = "Legacy"
        else:
            tab_tree_name = "Unknown"

        versions.append((version, date, tab_tree_name))

    return versions

def get_latest_version_by_release(latest_versions, release):
    for version, _, tab_tree_name in latest_versions:
        if tab_tree_name.lower() == release.lower():
            return version, _

    return "N/A", None

def compare_versions(v1, v2):
    def normalize(version):
        parts = version.split(".")
        return [int(part) if part.isnumeric() else part for part in parts]

    v1_parts = normalize(v1)
    v2_parts = normalize(v2)

    for i in range(max(len(v1_parts), len(v2_parts))):
        if i >= len(v1_parts):
            return -1
        if i >= len(v2_parts):
            return 1

        if v1_parts[i] > v2_parts[i]:
            return 1
        elif v1_parts[i] < v2_parts[i]:
            return -1

    return 0

def check_routeros_upgrade():
    if len(sys.argv) < 5:
        print("Usage: python check_upgrade.py <device_address> <port> <community> <release> [-v]")
        sys.exit(1)

    device_address = sys.argv[1]
    param_port = sys.argv[2]
    param_community = sys.argv[3]
    param_release = sys.argv[4]

    enable_logging = "-v" in sys.argv

    try:
        if enable_logging:
            print("Connecting to device...")
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(param_community),
                   UdpTransportTarget((device_address, param_port)),
                   ContextData(),
                   ObjectType(ObjectIdentity('.1.3.6.1.4.1.14988.1.1.4.4.0')))
        )
        if errorIndication:
            raise Exception(f"SNMP error: {errorIndication}")
        elif errorStatus:
            raise Exception(f"SNMP error: {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1] or '?'}")
        else:
            routeros_installed = varBinds[0][1].prettyPrint().replace('"', '')
            print(f"RouterOS version on {device_address}: {routeros_installed}")
    except Exception as e:
        error = f"Could not establish an SNMP connection to the device: {str(e)}"
        print(error)
        sys.exit(2)  # Critical

    # Obtener la fecha de la versión del release
    latest_versions = get_latest_versions()
    latest_version, latest_version_date = get_latest_version_by_release(latest_versions, param_release)

    if latest_version:
        param_release_lower = param_release.lower()
        if param_release_lower in ["testing", "development"]:
            latest_version = latest_version.replace("-initial", "")
            latest_version = latest_version.replace("rc", "rc.")
            latest_version = latest_version.replace("fix", "fix.")
            latest_version = latest_version.replace("bugfix", "bugfix.")
            latest_version = latest_version.replace("LTS", "")

        comparison_result = compare_versions(routeros_installed, latest_version)

        if comparison_result == 0:
            print(f"RouterOS version {routeros_installed} is up to date for {param_release} release.")
            sys.exit(0)  # OK
        elif comparison_result < 0:
            print(f"RouterOS version {routeros_installed} is available for {param_release} release. Consider upgrading to {latest_version}.")
        else:
            print(f"RouterOS version {routeros_installed} is newer than the latest available {param_release} release ({latest_version}).")

        if enable_logging:
            print(f"Latest version ({latest_version}) for {param_release} release was released on {latest_version_date}.")  # Agregar esta línea

        # Comparar fechas
        today = datetime.now()
        latest_version_date = datetime.strptime(latest_version_date, "%Y-%m-%d")
        time_difference = today - latest_version_date
        if time_difference.days > 30:
            print("CRITICAL: The RouterOS version is outdated by more than a month.")
            sys.exit(2)  # Critical
        else:
            print("WARNING: The RouterOS version is outdated by less than a month.")
            sys.exit(1)  # Warning
    else:
        print(f"No information available for {param_release} release.")
        sys.exit(3)  # Unknown

def main():
    check_routeros_upgrade()

if __name__ == "__main__":
    main()

