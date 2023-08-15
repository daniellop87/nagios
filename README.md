RouterOS Upgrade Checker
=======================

This Python script is used to verify the installed version of RouterOS on a MikroTik device and compare it with the latest available version in a specific release branch.

Requirements
------------

- Python 3.x
- Python libraries: `requests`, `beautifulsoup4`, `pysnmp`

You can install the required libraries using the following command:

```bash
pip install requests beautifulsoup4 pysnmp
```

Usage
-----

```bash
python check_mikrotik_firmware.py <device_address> <port> <community> <release> [-v]
```

- `device_address`: IP address of the MikroTik device.
- `port`: SNMP port of the device.
- `community`: SNMP community string.
- `release`: RouterOS release branch to check (Stable, Long-Term, Legacy)
- `-v`: Optional flag to enable verbose logging.

## Description

The script performs the following steps:

1. Establishes an SNMP connection with the device to fetch the current installed version of RouterOS.
2. Scrapes the latest RouterOS versions available from the official MikroTik website.
3. Compares the installed version with the latest available version in the selected release branch.
4. Provides information about whether the installed version is up-to-date or an update should be considered.

## Examples

```bash
python check_upgrade.py 192.168.1.1 161 public stable
```
This command will check the installed version of RouterOS on the device with IP address 192.168.1.1, SNMP port 161, community public, and release branch stable.
