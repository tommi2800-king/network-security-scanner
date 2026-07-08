
# network-security-scanner

Python tool for basic network scanning and security testing built as a personal project during a cyber security course

## Features

- Host availability check using ping, compatible with both Windows and Linux
- Three port scanning modes: quick scan of common ports, full scan of all 65535 ports, and custom port range
- Live progress display during scanning
- Service identification for common open ports such as SSH, HTTP, and HTTPS
- SSH connection module supporting manual credentials or testing against a list of common default credentials to identify weak passwords
- Ability to run basic remote commands over an established SSH session

## Note

This project was built for educational purposes as part of a cyber security course, and is intended to be run only against systems you own or are authorized to test, such as personal lab environments and virtual machines

## Technologies

Python, socket, paramiko, subprocess
