#!/usr/bin/env python3
# =============================================================================
# KALI LINUX + WIRESHARK + FULL CYBERSECURITY TOOLS SYSTEM
# =============================================================================
# Advanced Cybersecurity Toolkit - Educational & Ethical Use Only
# Version: 4.0 - Complete Security Suite
# =============================================================================

import os
import sys
import subprocess
import shutil
import json
import time
import platform
import argparse
import hashlib
import base64
import re
import ipaddress
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import queue
import socket
import urllib.parse


# =============================================================================
# CONFIGURATION & CONSTANTS
# =============================================================================

@dataclass
class Config:
    """System Configuration"""
    TOOLS_DIR: str = "/usr/share/kali-tools"
    LOGS_DIR: str = "./logs"
    CAPTURES_DIR: str = "./captures"
    REPORTS_DIR: str = "./reports"
    WORDLISTS_DIR: str = "/usr/share/wordlists"
    OSINT_DIR: str = "./osint_data"
    MALWARE_DIR: str = "./malware_analysis"
    API_DIR: str = "./api_testing"
    MAX_THREADS: int = 10
    TIMEOUT: int = 300
    
    def __post_init__(self):
        for dir_path in [self.LOGS_DIR, self.CAPTURES_DIR, self.REPORTS_DIR, 
                        self.OSINT_DIR, self.MALWARE_DIR, self.API_DIR]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)


# =============================================================================
# COLOR & OUTPUT UTILITIES
# =============================================================================

class Colors:
    """Terminal Colors"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    @classmethod
    def banner(cls):
        return f"""
{cls.CYAN}{cls.BOLD}
╔══════════════════════════════════════════════════════════════════════╗
║     KALI LINUX + WIRESHARK + FULL CYBERSECURITY TOOLS SYSTEM         ║
║              Advanced Cybersecurity & Network Analysis Suite           ║
╠══════════════════════════════════════════════════════════════════════╣
║  Version: 4.0  |  Platform: {platform.system():<<10}  |  Python: {platform.python_version():<<8}   ║
╚══════════════════════════════════════════════════════════════════════╝
{cls.END}
{cls.YELLOW}[!] Educational & Authorized Use Only{cls.END}
{cls.YELLOW}[!] Ensure you have proper authorization before testing{cls.END}
"""


class Logger:
    """Logging System"""
    def __init__(self, config: Config):
        self.config = config
        self.log_file = Path(config.LOGS_DIR) / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        color_map = {
            "INFO": Colors.CYAN, "SUCCESS": Colors.GREEN, "ERROR": Colors.RED,
            "WARNING": Colors.YELLOW, "CRITICAL": Colors.MAGENTA
        }
        print(f"{color_map.get(level, Colors.WHITE)}[{level}]{Colors.END} {message}")
        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")
    
    def success(self, msg: str): self.log(msg, "SUCCESS")
    def error(self, msg: str): self.log(msg, "ERROR")
    def warning(self, msg: str): self.log(msg, "WARNING")
    def critical(self, msg: str): self.log(msg, "CRITICAL")
    def info(self, msg: str): self.log(msg, "INFO")


# =============================================================================
# COMMAND EXECUTOR
# =============================================================================

class CommandExecutor:
    """Execute system commands with error handling"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def run(self, command: str, shell: bool = True, timeout: int = 300) -> Tuple[bool, str]:
        self.logger.info(f"Executing: {command}")
        try:
            result = subprocess.run(
                command, shell=shell, capture_output=True, text=True, timeout=timeout
            )
            if result.returncode == 0:
                self.logger.success("Command executed successfully")
                return True, result.stdout
            else:
                self.logger.error(f"Command failed: {result.stderr}")
                return False, result.stderr
        except subprocess.TimeoutExpired:
            self.logger.error("Command timed out")
            return False, "Timeout"
        except Exception as e:
            self.logger.error(f"Exception: {str(e)}")
            return False, str(e)
    
    def run_live(self, command: str):
        self.logger.info(f"Running live: {command}")
        try:
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, text=True
            )
            for line in process.stdout:
                print(line, end='')
            process.wait()
            return process.returncode == 0
        except Exception as e:
            self.logger.error(str(e))
            return False


# =============================================================================
# TOOL MANAGER MODULE
# =============================================================================

class ToolManager:
    """Manage external tools and their installation guides"""
    def __init__(self, logger: Logger):
        self.logger = logger
        self.tool_map = {
            "nmap": "sudo apt install nmap",
            "tshark": "sudo apt install tshark",
            "airmon-ng": "sudo apt install aircrack-ng",
            "airodump-ng": "sudo apt install aircrack-ng",
            "aircrack-ng": "sudo apt install aircrack-ng",
            "wifite": "sudo apt install wifite",
            "reaver": "sudo apt install reaver",
            "masscan": "sudo apt install masscan",
            "rustscan": "https://github.com/RustScan/RustScan",
            "unicornscan": "sudo apt install unicornscan",
            "netdiscover": "sudo apt install netdiscover",
            "theHarvester": "sudo apt install theharvester",
            "dnsenum": "sudo apt install dnsenum",
            "dnsrecon": "sudo apt install dnsrecon",
            "fierce": "sudo apt install fierce",
            "dirb": "sudo apt install dirb",
            "nikto": "sudo apt install nikto",
            "sqlmap": "sudo apt install sqlmap",
            "wpscan": "sudo gem install wpscan",
            "gobuster": "sudo apt install gobuster",
            "ffuf": "sudo apt install ffuf",
            "dalfox": "go install github.com/hahwul/dalfox/v2@latest",
            "nuclei": "go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest",
            "subfinder": "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
            "amass": "go install -v github.com/OWASP/Amass/v3/...@latest",
            "assetfinder": "go install github.com/tomnomnom/assetfinder@latest",
            "gau": "go install github.com/lc/gau/v2/cmd/gau@latest",
            "waybackurls": "go install github.com/tomnomnom/waybackurls@latest",
            "httprobe": "go install github.com/tomnomnom/httprobe@latest",
            "aquatone": "https://github.com/michenriksen/aquatone",
            "sherlock": "pip3 install sherlock",
            "osintgram": "pip3 install osintgram",
            "twint": "pip3 install twint",
            "spiderfoot": "pip3 install spiderfoot",
            "maltego": "sudo apt install maltego",
            "recon-ng": "sudo apt install recon-ng",
            "setoolkit": "sudo apt install setoolkit",
            "vt": "go install github.com/VirusTotal/vt-cli/vt@latest",
            "yara": "sudo apt install yara",
            "peframe": "pip3 install peframe",
            "r2": "sudo apt install radare2",
            "ghidra": "sudo apt install ghidra",
            "volatility": "sudo apt install volatility",
            "binwalk": "sudo apt install binwalk",
            "exiftool": "sudo apt install libimage-exiftool-perl",
            "foremost": "sudo apt install foremost",
            "photorec": "sudo apt install testdisk",
            "fsstat": "sudo apt install sleuthkit",
            "autopsy": "sudo apt install autopsy",
            "searchsploit": "sudo apt install exploitdb",
            "msfconsole": "sudo apt install metasploit-framework",
            "beef-xss": "sudo apt install beef-xss",
            "armitage": "sudo apt install armitage",
            "powershell-empire": "sudo apt install powershell-empire",
            "covenant": "https://github.com/cobbr/Covenant",
            "scout": "pip3 install scoutsuite",
            "prowler": "pip3 install prowler",
            "cloudsploit": "npm install -g cloudsploit",
            "pacu": "pip3 install pacu",
            "s3scanner": "pip3 install s3scanner",
            "cloud_enum": "pip3 install cloud_enum",
            "trivy": "https://github.com/aquasecurity/trivy",
            "docker-bench-security": "https://github.com/docker/docker-bench-security",
            "kube-bench": "https://github.com/aquasecurity/kube-bench",
            "kube-hunter": "pip3 install kube-hunter",
            "grype": "https://github.com/anchore/grype",
            "newman": "npm install -g newman",
            "arjun": "pip3 install arjun",
            "crlfuzz": "go install github.com/dwisiswant0/crlfuzz/cmd/crlfuzz@latest",
            "graphqlmap": "pip3 install graphqlmap",
            "swagger-scan": "pip3 install swagger-scan",
            "hash-identifier": "sudo apt install hash-identifier",
            "hashcat": "sudo apt install hashcat",
            "john": "sudo apt install john",
            "hydra": "sudo apt install hydra",
            "medusa": "sudo apt install medusa",
            "ncrack": "sudo apt install ncrack",
            "sslscan": "sudo apt install sslscan",
            "testssl.sh": "sudo apt install testssl.sh",
            "gf": "go install github.com/tomnomnom/gf@latest",
            "cstool": "sudo apt install capstone-tool",
            "ent": "sudo apt install ent",
            "objdump": "sudo apt install binutils",
            "tcpdump": "sudo apt install tcpdump",
            "garak": "pip3 install garak",
            "vigil-llm": "pip3 install vigil-llm",
            "pyrit": "pip3 install pyrit",
            "giskard": "pip3 install giskard"
        }

    def is_installed(self, tool_name: str) -> bool:
        return shutil.which(tool_name) is not None

    def check(self, tool_name: str) -> bool:
        if self.is_installed(tool_name):
            return True

        install_cmd = self.tool_map.get(tool_name, "Installation command unknown")
        self.logger.warning(f"Tool '{tool_name}' is not installed!")
        print(f"{Colors.YELLOW}[!] To install {tool_name}, run: {Colors.BOLD}{install_cmd}{Colors.END}")
        return False


# =============================================================================
# WIRESHARK / TSHARK MODULE
# =============================================================================

class WiresharkModule:
    """Wireshark/Tshark Packet Analysis Tools"""
    
    def __init__(self, executor: CommandExecutor, config: Config, logger: Logger, tool_manager: ToolManager):
        self.executor = executor
        self.config = config
        self.logger = logger
        self.tool_manager = tool_manager
        self.check_tshark()
    
    def check_tshark(self):
        if not self.tool_manager.check("tshark"):
            self.logger.warning("tshark is required for this module.")
    
    def list_interfaces(self) -> List[str]:
        success, output = self.executor.run("tshark -D", timeout=10)
        if success:
            return [line for line in output.strip().split('\n') if line]
        return []
    
    def capture_packets(self, interface: str, duration: int = 60, 
                       filter_expr: str = "", output_file: str = None) -> str:
        if not output_file:
            output_file = f"{self.config.CAPTURES_DIR}/capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pcap"
        cmd = f"tshark -i {interface} -a duration:{duration} -w {output_file}"
        if filter_expr:
            cmd += f" -f '{filter_expr}'"
        self.logger.info(f"Starting capture on {interface} for {duration}s...")
        self.executor.run_live(cmd)
        self.logger.success(f"Capture saved to {output_file}")
        return output_file
    
    def analyze_pcap(self, pcap_file: str) -> Dict:
        results = {}
        commands = {
            'protocol_hierarchy': f"tshark -r {pcap_file} -q -z io,phs",
            'conversations': f"tshark -r {pcap_file} -q -z conv,ip",
            'expert_info': f"tshark -r {pcap_file} -q -z expert",
            'http_requests': f"tshark -r {pcap_file} -Y http.request -T fields -e http.host -e http.request.uri -e ip.src",
            'dns_queries': f"tshark -r {pcap_file} -Y dns.qry.name -T fields -e dns.qry.name -e ip.src",
            'tls_handshake': f"tshark -r {pcap_file} -Y ssl.handshake.type==1 -T fields -e ip.src -e ssl.handshake.extensions_server_name",
            'smb_files': f"tshark -r {pcap_file} -Y smb.file -T fields -e smb.file",
            'ftp_commands': f"tshark -r {pcap_file} -Y ftp -T fields -e ftp.request.command -e ftp.request.arg"
        }
        for key, cmd in commands.items():
            success, output = self.executor.run(cmd, timeout=60)
            if success:
                results[key] = output
        return results
    
    def extract_objects(self, pcap_file: str, protocol: str = "http") -> str:
        output_dir = f"{self.config.CAPTURES_DIR}/extracted_{protocol}"
        os.makedirs(output_dir, exist_ok=True)
        cmd = f"tshark -r {pcap_file} --export-objects {protocol},{output_dir}"
        self.executor.run(cmd, timeout=120)
        return output_dir
    
    def follow_stream(self, pcap_file: str, stream_num: int, protocol: str = "tcp") -> str:
        cmd = f"tshark -r {pcap_file} -q -z follow,{protocol},ascii,{stream_num}"
        success, output = self.executor.run(cmd, timeout=30)
        return output if success else ""
    
    def generate_report(self, pcap_file: str) -> str:
        report_file = f"{self.config.REPORTS_DIR}/pcap_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        analysis = self.analyze_pcap(pcap_file)
        with open(report_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("WIRESHARK PCAP ANALYSIS REPORT\n")
            f.write(f"File: {pcap_file}\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write("=" * 80 + "\n\n")
            for section, content in analysis.items():
                f.write(f"\n{'='*40}\n{section.upper().replace('_', ' ')}\n{'='*40}\n")
                f.write(content + "\n")
        return report_file


# =============================================================================
# NETWORK SCANNING MODULE
# =============================================================================

class NetworkScanner:
    """Network Scanning & Reconnaissance"""
    
    def __init__(self, executor: CommandExecutor, logger: Logger, tool_manager: ToolManager):
        self.executor = executor
        self.logger = logger
        self.tool_manager = tool_manager
    
    def nmap_scan(self, target: str, scan_type: str = "comprehensive") -> str:
        if not self.tool_manager.check("nmap"): return "nmap not installed"
        scans = {
            "quick": "-sV -T4 --top-ports 100",
            "comprehensive": "-sS -sV -sC -O -A -T4",
            "stealth": "-sS -T2 -f --data-length 24",
            "udp": "-sU -T4 --top-ports 100",
            "vuln": "--script vuln -sV",
            "all_ports": "-p- -sV -T4",
            "script_scan": "-sC -sV -T4",
            "aggressive": "-T4 -A -v"
        }
        flags = scans.get(scan_type, scans["comprehensive"])
        output_file = f"./reports/nmap_{target.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        cmd = f"sudo nmap {flags} {target} -oN {output_file}.txt -oX {output_file}.xml"
        self.executor.run_live(cmd)
        return f"{output_file}.txt"
    
    def masscan_scan(self, target: str, ports: str = "1-65535", rate: int = 1000) -> str:
        if not self.tool_manager.check("masscan"): return "masscan not installed"
        cmd = f"sudo masscan {target} -p{ports} --rate={rate} -oG ./reports/masscan_{target}.txt"
        self.executor.run_live(cmd)
        return f"./reports/masscan_{target}.txt"
    
    def netdiscover(self, interface: str = "eth0") -> str:
        if not self.tool_manager.check("netdiscover"): return "netdiscover not installed"
        cmd = f"sudo netdiscover -i {interface} -r 192.168.1.0/24 -P"
        success, output = self.executor.run(cmd, timeout=120)
        return output
    
    def theharvester(self, domain: str, limit: int = 500) -> str:
        if not self.tool_manager.check("theHarvester"): return "theHarvester not installed"
        cmd = f"theHarvester -d {domain} -l {limit} -b all -f ./reports/harvester_{domain}"
        self.executor.run_live(cmd)
        return f"./reports/harvester_{domain}"
    
    def dns_recon(self, domain: str) -> Dict[str, str]:
        results = {}
        for tool, cmd in [
            ('dnsenum', f"dnsenum {domain}"),
            ('dnsrecon', f"dnsrecon -d {domain}"),
            ('fierce', f"fierce --domain {domain}")
        ]:
            success, output = self.executor.run(cmd, timeout=120)
            if success:
                results[tool] = output
        return results
    
    def rustscan(self, target: str, ports: str = "1-65535") -> str:
        if not self.tool_manager.check("rustscan"): return "rustscan not installed"
        cmd = f"rustscan -a {target} -p {ports} -t 1500"
        self.executor.run_live(cmd)
        return f"Rustscan completed for {target}"
    
    def unicornscan(self, target: str, ports: str = "1-65535") -> str:
        if not self.tool_manager.check("unicornscan"): return "unicornscan not installed"
        cmd = f"sudo unicornscan -mT {target}:{ports}"
        success, output = self.executor.run(cmd, timeout=120)
        return output


# =============================================================================
# WEB APPLICATION TESTING MODULE
# =============================================================================

class WebAppTester:
    """Web Application Security Testing"""
    
    def __init__(self, executor: CommandExecutor, logger: Logger, tool_manager: ToolManager):
        self.executor = executor
        self.logger = logger
        self.tool_manager = tool_manager
    
    def dirb_scan(self, url: str, wordlist: str = "/usr/share/dirb/wordlists/common.txt") -> str:
        if not self.tool_manager.check("dirb"): return "dirb not installed"
        output = f"./reports/dirb_{url.replace('://', '_').replace('/', '_')}.txt"
        cmd = f"dirb {url} {wordlist} -o {output}"
        self.executor.run_live(cmd)
        return output
    
    def nikto_scan(self, url: str) -> str:
        if not self.tool_manager.check("nikto"): return "nikto not installed"
        output = f"./reports/nikto_{url.replace('://', '_').replace('/', '_')}.txt"
        cmd = f"nikto -h {url} -output {output}"
        self.executor.run_live(cmd)
        return output
    
    def sqlmap_test(self, url: str, data: str = None, level: int = 1, risk: int = 1) -> str:
        if not self.tool_manager.check("sqlmap"): return "sqlmap not installed"
        cmd = f"sqlmap -u '{url}' --level={level} --risk={risk} --batch"
        if data:
            cmd += f" --data='{data}'"
        self.executor.run_live(cmd)
        return "SQLMap scan completed"
    
    def wpscan(self, url: str, enumerate: str = "vp,vt,tt") -> str:
        if not self.tool_manager.check("wpscan"): return "wpscan not installed"
        cmd = f"wpscan --url {url} --enumerate {enumerate}"
        self.executor.run_live(cmd)
        return "WPScan completed"
    
    def gobuster_scan(self, url: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt",
                      extensions: str = "php,txt,html") -> str:
        if not self.tool_manager.check("gobuster"): return "gobuster not installed"
        output = f"./reports/gobuster_{url.replace('/', '_')}.txt"
        cmd = f"gobuster dir -u {url} -w {wordlist} -x {extensions} -o {output}"
        self.executor.run_live(cmd)
        return output
    
    def ffuf_scan(self, url: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt") -> str:
        if not self.tool_manager.check("ffuf"): return "ffuf not installed"
        output = f"./reports/ffuf_{url.replace('/', '_')}.txt"
        cmd = f"ffuf -u {url}/FUZZ -w {wordlist} -o {output} -of json"
        self.executor.run_live(cmd)
        return output
    
    def dalfox_scan(self, url: str) -> str:
        if not self.tool_manager.check("dalfox"): return "dalfox not installed"
        cmd = f"dalfox url {url} --silence"
        self.executor.run_live(cmd)
        return "Dalfox XSS scan completed"
    
    def nuclei_scan(self, target: str, templates: str = None) -> str:
        if not self.tool_manager.check("nuclei"): return "nuclei not installed"
        cmd = f"nuclei -u {target}"
        if templates:
            cmd += f" -t {templates}"
        self.executor.run_live(cmd)
        return f"Nuclei scan completed for {target}"


# =============================================================================
# WIRELESS & EXPLOITATION MODULE
# =============================================================================

class WirelessTools:
    """Wireless Network Testing"""
    
    def __init__(self, executor: CommandExecutor, logger: Logger, tool_manager: ToolManager):
        self.executor = executor
        self.logger = logger
        self.tool_manager = tool_manager
    
    def airmon_start(self, interface: str) -> bool:
        if not self.tool_manager.check("airmon-ng"): return False
        cmd = f"sudo airmon-ng start {interface}"
        success, _ = self.executor.run(cmd, timeout=30)
        return success
    
    def airodump_scan(self, interface: str = "wlan0mon", channel: int = None, write_file: str = None) -> str:
        if not self.tool_manager.check("airodump-ng"): return "airodump-ng not installed"
        if not write_file:
            write_file = f"./captures/wifi_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        cmd = f"sudo airodump-ng {interface} -w {write_file}"
        if channel:
            cmd += f" -c {channel}"
        self.executor.run_live(cmd)
        return f"{write_file}-01.csv"
    
    def aircrack_wpa(self, capture_file: str, wordlist: str = "/usr/share/wordlists/rockyou.txt") -> str:
        if not self.tool_manager.check("aircrack-ng"): return "aircrack-ng not installed"
        cmd = f"sudo aircrack-ng {capture_file} -w {wordlist}"
        success, output = self.executor.run(cmd, timeout=3600)
        return output
    
    def wifite_scan(self) -> str:
        if not self.tool_manager.check("wifite"): return "wifite not installed"
        cmd = "sudo wifite"
        self.executor.run_live(cmd)
        return "Wifite scan completed"
    
    def reaver_wps(self, bssid: str, interface: str = "wlan0mon") -> str:
        if not self.tool_manager.check("reaver"): return "reaver not installed"
        cmd = f"sudo reaver -i {interface} -b {bssid} -vv"
        self.executor.run_live(cmd)
        return "Reaver WPS attack completed"


# =============================================================================
# OSINT MODULE (NEW)
# =============================================================================

class OSINTModule:
    """Open Source Intelligence Gathering"""
    
    def __init__(self, executor: CommandExecutor, config: Config, logger: Logger, tool_manager: ToolManager):
        self.executor = executor
        self.config = config
        self.logger = logger
        self.tool_manager = tool_manager
    
    def maltego(self, target: str):
        if not self.tool_manager.check("maltego"): return
        self.logger.info("Launching Maltego...")
        self.executor.run_live(f"maltego")
    
    def spiderfoot_scan(self, target: str) -> str:
        if not self.tool_manager.check("spiderfoot"): return "spiderfoot not installed"
        output = f"{self.config.OSINT_DIR}/spiderfoot_{target}.txt"
        cmd = f"spiderfoot -s {target} -o {output}"
        self.executor.run_live(cmd)
        return output
    
    def recon_ng(self, domain: str):
        if not self.tool_manager.check("recon-ng"): return
        self.logger.info("Launching Recon-ng...")
        self.executor.run_live("recon-ng")
    
    def sherlock_username(self, username: str) -> str:
        if not self.tool_manager.check("sherlock"): return "sherlock not installed"
        cmd = f"sherlock {username} --folderoutput {self.config.OSINT_DIR}/sherlock"
        self.executor.run_live(cmd)
        return f"{self.config.OSINT_DIR}/sherlock"
    
    def social_engineering_toolkit(self):
        if not self.tool_manager.check("setoolkit"): return
        self.logger.info("Launching SET (Social Engineering Toolkit)...")
        self.executor.run_live("setoolkit")
    
    def osintgram(self, username: str) -> str:
        if not self.tool_manager.check("osintgram"): return "osintgram not installed"
        cmd = f"osintgram {username} -f {self.config.OSINT_DIR}"
        self.executor.run_live(cmd)
        return f"OSINTgram data saved to {self.config.OSINT_DIR}"
    
    def twint_search(self, username: str) -> str:
        if not self.tool_manager.check("twint"): return "twint not installed"
        cmd = f"twint -u {username} -o {self.config.OSINT_DIR}/twint_{username}.json --json"
        self.executor.run_live(cmd)
        return f"{self.config.OSINT_DIR}/twint_{username}.json"
    
    def theharvester_deep(self, domain: str, limit: int = 1000) -> Dict:
        results = {}
        sources = ["google", "bing", "linkedin", "twitter", "github"]
        for source in sources:
            cmd = f"theHarvester -d {domain} -l {limit} -b {source} -f ./reports/harv_{source}_{domain}"
            success, output = self.executor.run(cmd, timeout=180)
            if success:
                results[source] = output
        return results


# =============================================================================
# MALWARE ANALYSIS MODULE (NEW)
# =============================================================================

class MalwareAnalysis:
    """Malware Analysis & Reverse Engineering"""
    
    def __init__(self, executor: CommandExecutor, config: Config, logger: Logger, tool_manager: ToolManager):
        self.executor = executor
        self.config = config
        self.logger = logger
        self.tool_manager = tool_manager
    
    def virustotal_scan(self, file_path: str, api_key: str = None) -> str:
        if not self.tool_manager.check("vt"): return "vt not installed"
        if not api_key:
            self.logger.warning("VirusTotal API key not provided. Install vt-cli and configure.")
            return "Configure vt-cli first"
        cmd = f"vt scan file {file_path}"
        self.executor.run_live(cmd)
        return "VirusTotal scan submitted"
    
    def yara_scan(self, rule_file: str, target_dir: str) -> str:
        if not self.tool_manager.check("yara"): return "yara not installed"
        cmd = f"yara -r {rule_file} {target_dir}"
        success, output = self.executor.run(cmd, timeout=120)
        return output
    
    def peframe_analyze(self, file_path: str) -> str:
        if not self.tool_manager.check("peframe"): return "peframe not installed"
        cmd = f"peframe {file_path}"
        success, output = self.executor.run(cmd, timeout=60)
        return output
    
    def radare2_analysis(self, file_path: str):
        if not self.tool_manager.check("r2"): return
        self.logger.info("Launching radare2...")
        self.executor.run_live(f"r2 {file_path}")
    
    def ghidra_analysis(self, file_path: str):
        if not self.tool_manager.check("ghidra"): return
        self.logger.info("Launching Ghidra...")
        self.executor.run_live(f"ghidra {file_path}")
    
    def objdump_disassemble(self, file_path: str) -> str:
        if not self.tool_manager.check("objdump"): return "objdump not installed"
        cmd = f"objdump -d {file_path}"
        success, output = self.executor.run(cmd, timeout=60)
        return output
    
    def capstone_disassemble(self, file_path: str) -> str:
        if not self.tool_manager.check("cstool"): return "cstool not installed"
        cmd = f"cstool x64 {file_path}"
        success, output = self.executor.run(cmd, timeout=60)
        return output
    
    def volatility_memory(self, memory_dump: str, profile: str = None) -> Dict:
        if not self.tool_manager.check("volatility"): return {}
        results = {}
        commands = {
            'pslist': f"volatility -f {memory_dump} --profile={profile} pslist",
            'netscan': f"volatility -f {memory_dump} --profile={profile} netscan",
            'malfind': f"volatility -f {memory_dump} --profile={profile} malfind",
            'cmdline': f"volatility -f {memory_dump} --profile={profile} cmdline"
        }
        for key, cmd in commands.items():
            success, output = self.executor.run(cmd, timeout=120)
            if success:
                results[key] = output
        return results
    
    def static_analysis(self, file_path: str) -> Dict:
        results = {}
        # File type
        if self.tool_manager.check("file"):
            success, output = self.executor.run(f"file {file_path}")
        if success:
            results['file_type'] = output
        # Hashes
        for algo in ['md5', 'sha1', 'sha256']:
            if self.tool_manager.check(f"{algo}sum"):
                success, output = self.executor.run(f"{algo}sum {file_path}")
            if success:
                results[algo] = output.strip()
        # Strings
        if self.tool_manager.check("strings"):
            success, output = self.executor.run(f"strings -n 6 {file_path}")
        if success:
            results['strings'] = output[:2000]
        # Entropy
        if self.tool_manager.check("ent"):
            success, output = self.executor.run(f"ent {file_path}")
        if success:
            results['entropy'] = output
        return results


# =============================================================================
# CLOUD SECURITY MODULE (NEW)
# =============================================================================

class CloudSecurity:
    """Cloud Security Assessment Tools"""
    
    def __init__(self, executor: CommandExecutor, logger: Logger, tool_manager: ToolManager):
        self.executor = executor
        self.logger = logger
        self.tool_manager = tool_manager
    
    def scout_aws(self, profile: str = "default") -> str:
        if not self.tool_manager.check("scout"): return "scout not installed"
        cmd = f"scout aws --profile {profile}"
        self.executor.run_live(cmd)
        return "AWS Scout scan completed"
    
    def prowler_aws(self) -> str:
        if not self.tool_manager.check("prowler"): return "prowler not installed"
        cmd = "prowler -M csv"
        self.executor.run_live(cmd)
        return "Prowler AWS scan completed"
    
    def cloudsploit_scan(self, cloud: str = "aws") -> str:
        if not self.tool_manager.check("cloudsploit"): return "cloudsploit not installed"
        cmd = f"cloudsploit scan --cloud {cloud}"
        self.executor.run_live(cmd)
        return "CloudSploit scan completed"
    
    def pacu_framework(self):
        if not self.tool_manager.check("pacu"): return
        self.logger.info("Launching Pacu (AWS exploitation framework)...")
        self.executor.run_live("pacu")
    
    def s3scanner(self, bucket_name: str) -> str:
        if not self.tool_manager.check("s3scanner"): return "s3scanner not installed"
        cmd = f"s3scanner scan --bucket {bucket_name}"
        success, output = self.executor.run(cmd, timeout=60)
        return output
    
    def cloud_enum(self, keyword: str) -> str:
        if not self.tool_manager.check("cloud_enum"): return "cloud_enum not installed"
        cmd = f"cloud_enum -k {keyword}"
        self.executor.run_live(cmd)
        return "Cloud enumeration completed"


# =============================================================================
# CONTAINER & DEVSECOPS MODULE (NEW)
# =============================================================================

class ContainerSecurity:
    """Container & Kubernetes Security"""
    
    def __init__(self, executor: CommandExecutor, logger: Logger, tool_manager: ToolManager):
        self.executor = executor
        self.logger = logger
        self.tool_manager = tool_manager
    
    def trivy_scan_image(self, image: str) -> str:
        if not self.tool_manager.check("trivy"): return "trivy not installed"
        cmd = f"trivy image {image}"
        self.executor.run_live(cmd)
        return f"Trivy scan completed for {image}"
    
    def trivy_scan_fs(self, path: str = ".") -> str:
        if not self.tool_manager.check("trivy"): return "trivy not installed"
        cmd = f"trivy fs {path}"
        self.executor.run_live(cmd)
        return f"Trivy filesystem scan completed for {path}"
    
    def docker_bench_security(self) -> str:
        if not self.tool_manager.check("docker-bench-security"): return "docker-bench-security not installed"
        cmd = "docker-bench-security"
        self.executor.run_live(cmd)
        return "Docker Bench Security scan completed"
    
    def kube_bench(self) -> str:
        if not self.tool_manager.check("kube-bench"): return "kube-bench not installed"
        cmd = "kube-bench"
        self.executor.run_live(cmd)
        return "Kube-bench scan completed"
    
    def kube_hunter(self, remote: str = None) -> str:
        if not self.tool_manager.check("kube-hunter"): return "kube-hunter not installed"
        cmd = "kube-hunter"
        if remote:
            cmd += f" --remote {remote}"
        self.executor.run_live(cmd)
        return "Kube-hunter scan completed"
    
    def grype_scan(self, target: str) -> str:
        if not self.tool_manager.check("grype"): return "grype not installed"
        cmd = f"grype {target}"
        self.executor.run_live(cmd)
        return f"Grype scan completed for {target}"


# =============================================================================
# API SECURITY MODULE (NEW)
# =============================================================================

class APISecurity:
    """API Security Testing"""
    
    def __init__(self, executor: CommandExecutor, logger: Logger, tool_manager: ToolManager):
        self.executor = executor
        self.logger = logger
        self.tool_manager = tool_manager
    
    def postman_collection_test(self, collection_file: str) -> str:
        if not self.tool_manager.check("newman"): return "newman not installed"
        cmd = f"newman run {collection_file}"
        self.executor.run_live(cmd)
        return "Postman/Newman test completed"
    
    def arjun_scan(self, url: str) -> str:
        if not self.tool_manager.check("arjun"): return "arjun not installed"
        cmd = f"arjun -u {url}"
        self.executor.run_live(cmd)
        return "Arjun parameter discovery completed"
    
    def crlfuzz_scan(self, url: str) -> str:
        if not self.tool_manager.check("crlfuzz"): return "crlfuzz not installed"
        cmd = f"crlfuzz -u {url}"
        self.executor.run_live(cmd)
        return "CRLFuzz scan completed"
    
    def graphql_scan(self, endpoint: str) -> str:
        if not self.tool_manager.check("graphqlmap"): return "graphqlmap not installed"
        cmd = f"graphqlmap -u {endpoint}"
        self.executor.run_live(cmd)
        return "GraphQL scan completed"
    
    def swagger_scan(self, swagger_url: str) -> str:
        if not self.tool_manager.check("swagger-scan"): return "swagger-scan not installed"
        cmd = f"swagger-scan -u {swagger_url}"
        self.executor.run_live(cmd)
        return "Swagger API scan completed"


# =============================================================================
# AI & LLM SECURITY MODULE (NEW)
# =============================================================================

class AISecurityTools:
    """AI & Large Language Model Security Testing"""

    def __init__(self, executor: CommandExecutor, logger: Logger, tool_manager: ToolManager):
        self.executor = executor
        self.logger = logger
        self.tool_manager = tool_manager

    def run_garak(self, target_url: str) -> str:
        if not self.tool_manager.check("garak"): return "garak not installed"
        cmd = f"garak --model_type openai --model_name gpt-3.5-turbo --url {target_url}"
        self.executor.run_live(cmd)
        return "Garak LLM scan completed"

    def run_vigil(self, input_text: str) -> str:
        if not self.tool_manager.check("vigil-llm"): return "vigil-llm not installed"
        cmd = f"vigil -i '{input_text}'"
        self.executor.run_live(cmd)
        return "Vigil LLM prompt scan completed"

    def run_pyrit(self) -> str:
        if not self.tool_manager.check("pyrit"): return "pyrit not installed"
        self.logger.info("Launching PyRIT (Python Risk Identification Tool)...")
        self.executor.run_live("pyrit")
        return "PyRIT session completed"

    def run_giskard(self, model_path: str) -> str:
        if not self.tool_manager.check("giskard"): return "giskard not installed"
        cmd = f"giskard scan --model {model_path}"
        self.executor.run_live(cmd)
        return "Giskard model scan completed"


# =============================================================================
# CRYPTOGRAPHY & HASH MODULE (NEW)
# =============================================================================

class CryptoTools:
    """Cryptography & Hash Utilities"""
    
    def __init__(self, executor: CommandExecutor, logger: Logger, tool_manager: ToolManager):
        self.executor = executor
        self.logger = logger
        self.tool_manager = tool_manager
    
    def hash_identifier(self, hash_value: str) -> str:
        if not self.tool_manager.check("hash-identifier"): return "hash-identifier not installed"
        cmd = f"hash-identifier {hash_value}"
        success, output = self.executor.run(cmd, timeout=30)
        return output
    
    def hashcat_crack(self, hash_file: str, hash_type: int = 0, 
                      wordlist: str = "/usr/share/wordlists/rockyou.txt") -> str:
        if not self.tool_manager.check("hashcat"): return "hashcat not installed"
        cmd = f"hashcat -m {hash_type} {hash_file} {wordlist}"
        self.executor.run_live(cmd)
        return "Hashcat cracking completed"
    
    def john_crack(self, hash_file: str, wordlist: str = "/usr/share/wordlists/rockyou.txt") -> str:
        if not self.tool_manager.check("john"): return "john not installed"
        cmd = f"john --wordlist={wordlist} {hash_file}"
        self.executor.run_live(cmd)
        return "John cracking completed"
    
    def hydra_brute(self, target: str, service: str, 
                    userlist: str, passlist: str) -> str:
        if not self.tool_manager.check("hydra"): return "hydra not installed"
        cmd = f"hydra -L {userlist} -P {passlist} {target} {service}"
        self.executor.run_live(cmd)
        return "Hydra scan completed"
    
    def medusa_brute(self, target: str, service: str, 
                     userlist: str, passlist: str) -> str:
        if not self.tool_manager.check("medusa"): return "medusa not installed"
        cmd = f"medusa -h {target} -U {userlist} -P {passlist} -M {service}"
        self.executor.run_live(cmd)
        return "Medusa scan completed"
    
    def ncrack_scan(self, target: str, service: str) -> str:
        if not self.tool_manager.check("ncrack"): return "ncrack not installed"
        cmd = f"ncrack -v {service}://{target}"
        self.executor.run_live(cmd)
        return "Ncrack scan completed"
    
    def openssl_check(self, host: str, port: int = 443) -> str:
        cmd = f"openssl s_client -connect {host}:{port} -showcerts"
        success, output = self.executor.run(cmd, timeout=30)
        return output
    
    def sslscan_test(self, host: str, port: int = 443) -> str:
        if not self.tool_manager.check("sslscan"): return "sslscan not installed"
        cmd = f"sslscan {host}:{port}"
        self.executor.run_live(cmd)
        return "SSLScan completed"
    
    def testssl_sh(self, host: str) -> str:
        if not self.tool_manager.check("testssl.sh"): return "testssl.sh not installed"
        cmd = f"testssl.sh {host}"
        self.executor.run_live(cmd)
        return "testssl.sh completed"


# =============================================================================
# BUG BOUNTY & AUTOMATION MODULE (NEW)
# =============================================================================

class BugBountyTools:
    """Bug Bounty & Automation Tools"""
    
    def __init__(self, executor: CommandExecutor, logger: Logger, tool_manager: ToolManager):
        self.executor = executor
        self.logger = logger
        self.tool_manager = tool_manager
    
    def subfinder_enum(self, domain: str) -> str:
        if not self.tool_manager.check("subfinder"): return "subfinder not installed"
        output = f"./reports/subfinder_{domain}.txt"
        cmd = f"subfinder -d {domain} -o {output}"
        self.executor.run_live(cmd)
        return output
    
    def amass_enum(self, domain: str) -> str:
        if not self.tool_manager.check("amass"): return "amass not installed"
        output = f"./reports/amass_{domain}.json"
        cmd = f"amass enum -d {domain} -o {output} -json"
        self.executor.run_live(cmd)
        return output
    
    def assetfinder_enum(self, domain: str) -> str:
        if not self.tool_manager.check("assetfinder"): return "assetfinder not installed"
        cmd = f"assetfinder --subs-only {domain}"
        success, output = self.executor.run(cmd, timeout=120)
        return output
    
    def gau_urls(self, domain: str) -> str:
        if not self.tool_manager.check("gau"): return "gau not installed"
        output = f"./reports/gau_{domain}.txt"
        cmd = f"gau {domain} | tee {output}"
        self.executor.run_live(cmd)
        return output
    
    def waybackurls(self, domain: str) -> str:
        if not self.tool_manager.check("waybackurls"): return "waybackurls not installed"
        output = f"./reports/wayback_{domain}.txt"
        cmd = f"waybackurls {domain} | tee {output}"
        self.executor.run_live(cmd)
        return output
    
    def httprobe_live(self, url_file: str) -> str:
        if not self.tool_manager.check("httprobe"): return "httprobe not installed"
        output = f"./reports/live_hosts.txt"
        cmd = f"cat {url_file} | httprobe | tee {output}"
        self.executor.run_live(cmd)
        return output
    
    def aquatone_screenshot(self, url_file: str) -> str:
        if not self.tool_manager.check("aquatone"): return "aquatone not installed"
        output_dir = "./reports/aquatone"
        cmd = f"cat {url_file} | aquatone -out {output_dir}"
        self.executor.run_live(cmd)
        return output_dir
    
    def dalfox_xss(self, url_file: str) -> str:
        if not self.tool_manager.check("dalfox"): return "dalfox not installed"
        cmd = f"dalfox file {url_file}"
        self.executor.run_live(cmd)
        return "Dalfox XSS scan completed"
    
    def gf_patterns(self, url_file: str, pattern: str = "xss") -> str:
        if not self.tool_manager.check("gf"): return "gf not installed"
        cmd = f"cat {url_file} | gf {pattern}"
        success, output = self.executor.run(cmd, timeout=60)
        return output
    
    def nuclei_template_scan(self, target_file: str) -> str:
        if not self.tool_manager.check("nuclei"): return "nuclei not installed"
        cmd = f"nuclei -l {target_file} -t nuclei-templates"
        self.executor.run_live(cmd)
        return "Nuclei template scan completed"


# =============================================================================
# FORENSICS & REVERSE ENGINEERING
# =============================================================================

class ForensicsTools:
    """Digital Forensics Tools"""
    
    def __init__(self, executor: CommandExecutor, logger: Logger, tool_manager: ToolManager):
        self.executor = executor
        self.logger = logger
        self.tool_manager = tool_manager
    
    def binwalk_scan(self, file_path: str) -> str:
        if not self.tool_manager.check("binwalk"): return "binwalk not installed"
        cmd = f"binwalk {file_path}"
        success, output = self.executor.run(cmd, timeout=60)
        return output
    
    def exiftool_scan(self, file_path: str) -> str:
        if not self.tool_manager.check("exiftool"): return "exiftool not installed"
        cmd = f"exiftool {file_path}"
        success, output = self.executor.run(cmd, timeout=30)
        return output
    
    def strings_extract(self, file_path: str, min_length: int = 4) -> str:
        cmd = f"strings -n {min_length} {file_path}"
        success, output = self.executor.run(cmd, timeout=60)
        return output
    
    def foremost_extract(self, file_path: str, output_dir: str = "./forensics_output") -> str:
        if not self.tool_manager.check("foremost"): return "foremost not installed"
        os.makedirs(output_dir, exist_ok=True)
        cmd = f"foremost -i {file_path} -o {output_dir}"
        self.executor.run(cmd, timeout=120)
        return output_dir
    
    def photorec_recovery(self, disk: str, output_dir: str = "./recovered") -> str:
        if not self.tool_manager.check("photorec"): return "photorec not installed"
        os.makedirs(output_dir, exist_ok=True)
        cmd = f"photorec /d {output_dir} /cmd {disk} search"
        self.executor.run_live(cmd)
        return output_dir
    
    def sleuthkit_analysis(self, disk_image: str) -> str:
        if not self.tool_manager.check("fsstat"): return "fsstat not installed"
        cmd = f"fsstat {disk_image}"
        success, output = self.executor.run(cmd, timeout=60)
        return output
    
    def autopsy_launch(self, case_dir: str = "./autopsy_cases"):
        if not self.tool_manager.check("autopsy"): return
        os.makedirs(case_dir, exist_ok=True)
        self.logger.info("Launching Autopsy...")
        self.executor.run_live(f"autopsy -d {case_dir}")


# =============================================================================
# EXPLOITATION FRAMEWORK
# =============================================================================

class ExploitationFramework:
    """Exploitation Tools Wrapper"""
    
    def __init__(self, executor: CommandExecutor, logger: Logger, tool_manager: ToolManager):
        self.executor = executor
        self.logger = logger
        self.tool_manager = tool_manager
    
    def searchsploit(self, query: str) -> str:
        if not self.tool_manager.check("searchsploit"): return "searchsploit not installed"
        cmd = f"searchsploit {query}"
        success, output = self.executor.run(cmd, timeout=30)
        return output
    
    def metasploit_console(self, resource_file: str = None):
        if not self.tool_manager.check("msfconsole"): return
        if resource_file:
            cmd = f"msfconsole -r {resource_file}"
        else:
            cmd = "msfconsole"
        self.executor.run_live(cmd)
    
    def beef_framework(self):
        if not self.tool_manager.check("beef-xss"): return
        self.logger.info("Launching BeEF (Browser Exploitation Framework)...")
        self.executor.run_live("beef-xss")
    
    def armitage_launch(self):
        if not self.tool_manager.check("armitage"): return
        self.logger.info("Launching Armitage...")
        self.executor.run_live("armitage")
    
    def empire_launch(self):
        if not self.tool_manager.check("powershell-empire"): return
        self.logger.info("Launching Empire (PowerShell Empire)...")
        self.executor.run_live("powershell-empire")
    
    def covenant_launch(self):
        if not self.tool_manager.check("covenant"): return
        self.logger.info("Launching Covenant C2...")
        self.executor.run_live("covenant")


# =============================================================================
# SYSTEM UTILITIES
# =============================================================================

class SystemUtils:
    """System and Network Utilities"""
    
    def __init__(self, executor: CommandExecutor, logger: Logger, tool_manager: ToolManager):
        self.executor = executor
        self.logger = logger
        self.tool_manager = tool_manager
    
    def netstat_info(self) -> str:
        cmd = "netstat -tulpn"
        success, output = self.executor.run(cmd, timeout=10)
        return output
    
    def iptables_rules(self) -> str:
        cmd = "sudo iptables -L -v -n"
        success, output = self.executor.run(cmd, timeout=10)
        return output
    
    def system_info(self) -> Dict:
        info = {}
        commands = {
            'kernel': "uname -a",
            'os': "cat /etc/os-release",
            'cpu': "lscpu | grep 'Model name'",
            'memory': "free -h",
            'disk': "df -h"
        }
        for key, cmd in commands.items():
            success, output = self.executor.run(cmd, timeout=5)
            if success:
                info[key] = output.strip()
        return info
    
    def running_processes(self) -> str:
        cmd = "ps aux --sort=-%mem | head -20"
        success, output = self.executor.run(cmd, timeout=10)
        return output
    
    def lsof_open_files(self) -> str:
        cmd = "sudo lsof -i -P -n"
        success, output = self.executor.run(cmd, timeout=10)
        return output
    
    def full_system_check(self):
        self.logger.info("Starting Full System Dependency Check...")
        missing = []
        installed = []

        for tool in sorted(self.tool_manager.tool_map.keys()):
            if self.tool_manager.is_installed(tool):
                installed.append(tool)
            else:
                missing.append(tool)

        print(f"\n{Colors.BOLD}{Colors.GREEN}[+] Installed Tools ({len(installed)}):{Colors.END}")
        print(", ".join(installed))

        print(f"\n{Colors.BOLD}{Colors.RED}[-] Missing Tools ({len(missing)}):{Colors.END}")
        for tool in missing:
            print(f"  - {Colors.YELLOW}{tool:<20}{Colors.END} : {self.tool_manager.tool_map[tool]}")

        return len(missing) == 0

    def tcpdump_capture(self, interface: str = "any", count: int = 100) -> str:
        if not self.tool_manager.check("tcpdump"): return "tcpdump not installed"
        output = f"./captures/tcpdump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pcap"
        cmd = f"sudo tcpdump -i {interface} -c {count} -w {output}"
        self.executor.run(cmd, timeout=120)
        return output


# =============================================================================
# MAIN MENU SYSTEM
# =============================================================================

class KaliToolsSystem:
    """Main Application Controller"""
    
    def __init__(self):
        self.config = Config()
        self.logger = Logger(self.config)
        self.executor = CommandExecutor(self.logger)
        self.tool_manager = ToolManager(self.logger)
        
        # Initialize all modules
        self.wireshark = WiresharkModule(self.executor, self.config, self.logger, self.tool_manager)
        self.scanner = NetworkScanner(self.executor, self.logger, self.tool_manager)
        self.web_tester = WebAppTester(self.executor, self.logger, self.tool_manager)
        self.wireless = WirelessTools(self.executor, self.logger, self.tool_manager)
        self.forensics = ForensicsTools(self.executor, self.logger, self.tool_manager)
        self.exploitation = ExploitationFramework(self.executor, self.logger, self.tool_manager)
        self.system = SystemUtils(self.executor, self.logger, self.tool_manager)
        
        # NEW MODULES
        self.osint = OSINTModule(self.executor, self.config, self.logger, self.tool_manager)
        self.malware = MalwareAnalysis(self.executor, self.config, self.logger, self.tool_manager)
        self.cloud = CloudSecurity(self.executor, self.logger, self.tool_manager)
        self.container = ContainerSecurity(self.executor, self.logger, self.tool_manager)
        self.api_sec = APISecurity(self.executor, self.logger, self.tool_manager)
        self.ai_sec = AISecurityTools(self.executor, self.logger, self.tool_manager)
        self.crypto = CryptoTools(self.executor, self.logger, self.tool_manager)
        self.bugbounty = BugBountyTools(self.executor, self.logger, self.tool_manager)
    
    def clear(self):
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def print_menu(self, title: str, options: List[Tuple[str, str]]):
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.WHITE}{title.center(60)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
        for idx, (key, desc) in enumerate(options, 1):
            print(f"{Colors.YELLOW}{idx}.{Colors.END} {desc}")
        print(f"{Colors.RED}0.{Colors.END} Back/Exit")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
    
    def get_choice(self, max_option: int) -> int:
        try:
            choice = input(f"\n{Colors.GREEN}[?] Enter choice: {Colors.END}")
            if choice == '0':
                return 0
            val = int(choice)
            if 1 <= val <= max_option:
                return val
            self.logger.error("Invalid choice!")
            return -1
        except ValueError:
            self.logger.error("Please enter a number!")
            return -1
    
    # -------------------------------------------------------------------------
    # WIRESHARK MENU
    # -------------------------------------------------------------------------
    def wireshark_menu(self):
        while True:
            self.clear()
            print(Colors.banner())
            self.print_menu("WIRESHARK / TSHARK TOOLS", [
                ("interfaces", "List Network Interfaces"),
                ("capture", "Capture Packets"),
                ("analyze", "Analyze PCAP File"),
                ("extract", "Extract Objects from PCAP"),
                ("stream", "Follow TCP Stream"),
                ("report", "Generate Full Report")
            ])
            choice = self.get_choice(6)
            if choice == 0: break
            elif choice == 1:
                interfaces = self.wireshark.list_interfaces()
                for iface in interfaces:
                    print(f"{Colors.CYAN}{iface}{Colors.END}")
                input("\nPress Enter to continue...")
            elif choice == 2:
                interfaces = self.wireshark.list_interfaces()
                for i, iface in enumerate(interfaces, 1):
                    print(f"{i}. {iface}")
                iface_idx = int(input("Select interface number: ")) - 1
                if 0 <= iface_idx < len(interfaces):
                    iface = interfaces[iface_idx].split('.')[1].split(' ')[0]
                    duration = int(input("Capture duration (seconds): ") or "60")
                    filter_expr = input("Capture filter (optional): ")
                    self.wireshark.capture_packets(iface, duration, filter_expr)
                input("\nPress Enter to continue...")
            elif choice == 3:
                pcap = input("Enter PCAP file path: ")
                if os.path.exists(pcap):
                    analysis = self.wireshark.analyze_pcap(pcap)
                    for section, content in analysis.items():
                        print(f"\n{Colors.BOLD}{section.upper()}{Colors.END}")
                        print(content[:500] + "..." if len(content) > 500 else content)
                else:
                    self.logger.error("File not found!")
                input("\nPress Enter to continue...")
            elif choice == 4:
                pcap = input("Enter PCAP file path: ")
                protocol = input("Protocol (http/smb/ftp): ") or "http"
                self.wireshark.extract_objects(pcap, protocol)
                input("\nPress Enter to continue...")
            elif choice == 5:
                pcap = input("Enter PCAP file path: ")
                stream = int(input("Stream number: "))
                result = self.wireshark.follow_stream(pcap, stream)
                print(result[:1000])
                input("\nPress Enter to continue...")
            elif choice == 6:
                pcap = input("Enter PCAP file path: ")
                self.wireshark.generate_report(pcap)
                input("\nPress Enter to continue...")
    
    # -------------------------------------------------------------------------
    # NETWORK SCANNING MENU
    # -------------------------------------------------------------------------
    def scanning_menu(self):
        while True:
            self.clear()
            print(Colors.banner())
            self.print_menu("NETWORK SCANNING & RECONNAISSANCE", [
                ("nmap", "Nmap Port Scan"),
                ("masscan", "Masscan Fast Scan"),
                ("rustscan", "Rustscan Ultra-Fast Scan"),
                ("unicornscan", "Unicornscan"),
                ("netdiscover", "ARP Host Discovery"),
                ("harvester", "TheHarvester (Email/Subdomain)"),
                ("dns", "DNS Reconnaissance")
            ])
            choice = self.get_choice(7)
            if choice == 0: break
            elif choice == 1:
                target = input("Target IP/Range: ")
                print("Types: quick, comprehensive, stealth, udp, vuln, all_ports, script_scan, aggressive")
                scan_type = input("Scan type: ") or "comprehensive"
                self.scanner.nmap_scan(target, scan_type)
                input("\nPress Enter to continue...")
            elif choice == 2:
                target = input("Target IP/Range: ")
                ports = input("Port range (default 1-65535): ") or "1-65535"
                self.scanner.masscan_scan(target, ports)
                input("\nPress Enter to continue...")
            elif choice == 3:
                target = input("Target IP: ")
                self.scanner.rustscan(target)
                input("\nPress Enter to continue...")
            elif choice == 4:
                target = input("Target IP: ")
                self.scanner.unicornscan(target)
                input("\nPress Enter to continue...")
            elif choice == 5:
                iface = input("Interface (default eth0): ") or "eth0"
                print(self.scanner.netdiscover(iface))
                input("\nPress Enter to continue...")
            elif choice == 6:
                domain = input("Target domain: ")
                limit = int(input("Result limit (default 500): ") or "500")
                self.scanner.theharvester(domain, limit)
                input("\nPress Enter to continue...")
            elif choice == 7:
                domain = input("Target domain: ")
                results = self.scanner.dns_recon(domain)
                for tool, output in results.items():
                    print(f"\n{Colors.BOLD}{tool}{Colors.END}")
                    print(output[:500])
                input("\nPress Enter to continue...")
    
    # -------------------------------------------------------------------------
    # WEB APP TESTING MENU
    # -------------------------------------------------------------------------
    def webapp_menu(self):
        while True:
            self.clear()
            print(Colors.banner())
            self.print_menu("WEB APPLICATION TESTING", [
                ("dirb", "DIRB Directory Brute-force"),
                ("nikto", "Nikto Vulnerability Scan"),
                ("sqlmap", "SQLMap SQL Injection Test"),
                ("wpscan", "WPScan WordPress Audit"),
                ("gobuster", "Gobuster Enumeration"),
                ("ffuf", "FFUF Fast Fuzzing"),
                ("dalfox", "Dalfox XSS Scan"),
                ("nuclei", "Nuclei Vulnerability Scan")
            ])
            choice = self.get_choice(8)
            if choice == 0: break
            elif choice == 1:
                self.web_tester.dirb_scan(input("Target URL: "))
                input("\nPress Enter to continue...")
            elif choice == 2:
                self.web_tester.nikto_scan(input("Target URL: "))
                input("\nPress Enter to continue...")
            elif choice == 3:
                url = input("Target URL: ")
                data = input("POST data (optional): ") or None
                self.web_tester.sqlmap_test(url, data)
                input("\nPress Enter to continue...")
            elif choice == 4:
                self.web_tester.wpscan(input("WordPress URL: "))
                input("\nPress Enter to continue...")
            elif choice == 5:
                self.web_tester.gobuster_scan(input("Target URL: "))
                input("\nPress Enter to continue...")
            elif choice == 6:
                self.web_tester.ffuf_scan(input("Target URL: "))
                input("\nPress Enter to continue...")
            elif choice == 7:
                self.web_tester.dalfox_scan(input("Target URL: "))
                input("\nPress Enter to continue...")
            elif choice == 8:
                self.web_tester.nuclei_scan(input("Target URL: "))
                input("\nPress Enter to continue...")
    
    # -------------------------------------------------------------------------
    # WIRELESS MENU
    # -------------------------------------------------------------------------
    def wireless_menu(self):
        while True:
            self.clear()
            print(Colors.banner())
            self.print_menu("WIRELESS NETWORK TESTING", [
                ("airmon", "Start Monitor Mode"),
                ("airodump", "Scan Wireless Networks"),
                ("aircrack", "Crack WPA Handshake"),
                ("wifite", "Wifite Automated Attack"),
                ("reaver", "Reaver WPS Attack")
            ])
            choice = self.get_choice(5)
            if choice == 0: break
            elif choice == 1:
                self.wireless.airmon_start(input("Wireless interface (e.g., wlan0): "))
                input("\nPress Enter to continue...")
            elif choice == 2:
                self.wireless.airodump_scan(input("Monitor interface (e.g., wlan0mon): ") or "wlan0mon")
                input("\nPress Enter to continue...")
            elif choice == 3:
                cap = input("Capture file (.cap): ")
                wordlist = input("Wordlist (default rockyou.txt): ") or "/usr/share/wordlists/rockyou.txt"
                self.wireless.aircrack_wpa(cap, wordlist)
                input("\nPress Enter to continue...")
            elif choice == 4:
                self.wireless.wifite_scan()
                input("\nPress Enter to continue...")
            elif choice == 5:
                bssid = input("Target BSSID: ")
                self.wireless.reaver_wps(bssid)
                input("\nPress Enter to continue...")
    
    # -------------------------------------------------------------------------
    # OSINT MENU (NEW)
    # -------------------------------------------------------------------------
    def osint_menu(self):
        while True:
            self.clear()
            print(Colors.banner())
            self.print_menu("OSINT & SOCIAL ENGINEERING", [
                ("maltego", "Maltego Transform"),
                ("spiderfoot", "SpiderFoot Scan"),
                ("recon-ng", "Recon-ng Framework"),
                ("sherlock", "Sherlock Username Search"),
                ("osintgram", "OSINTgram Instagram"),
                ("twint", "Twint Twitter Search"),
                ("harvester", "Deep TheHarvester"),
                ("set", "Social Engineering Toolkit")
            ])
            choice = self.get_choice(8)
            if choice == 0: break
            elif choice == 1:
                self.osint.maltego(input("Target domain/IP: "))
                input("\nPress Enter to continue...")
            elif choice == 2:
                self.osint.spiderfoot_scan(input("Target domain: "))
                input("\nPress Enter to continue...")
            elif choice == 3:
                self.osint.recon_ng(input("Target domain: "))
                input("\nPress Enter to continue...")
            elif choice == 4:
                self.osint.sherlock_username(input("Username: "))
                input("\nPress Enter to continue...")
            elif choice == 5:
                self.osint.osintgram(input("Instagram username: "))
                input("\nPress Enter to continue...")
            elif choice == 6:
                self.osint.twint_search(input("Twitter username: "))
                input("\nPress Enter to continue...")
            elif choice == 7:
                domain = input("Target domain: ")
                results = self.osint.theharvester_deep(domain)
                for source, output in results.items():
                    print(f"\n{Colors.BOLD}{source}{Colors.END}")
                    print(output[:300])
                input("\nPress Enter to continue...")
            elif choice == 8:
                self.osint.social_engineering_toolkit()
                input("\nPress Enter to continue...")
    
    # -------------------------------------------------------------------------
    # MALWARE ANALYSIS MENU (NEW)
    # -------------------------------------------------------------------------
    def malware_menu(self):
        while True:
            self.clear()
            print(Colors.banner())
            self.print_menu("MALWARE ANALYSIS & REVERSE ENGINEERING", [
                ("virustotal", "VirusTotal Scan"),
                ("yara", "YARA Rule Scan"),
                ("peframe", "PEframe Analysis"),
                ("radare2", "Radare2 Interactive"),
                ("ghidra", "Ghidra Analysis"),
                ("objdump", "Objdump Disassembly"),
                ("volatility", "Volatility Memory Forensics"),
                ("static", "Static Analysis (Hashes/Strings/Entropy)")
            ])
            choice = self.get_choice(8)
            if choice == 0: break
            elif choice == 1:
                self.malware.virustotal_scan(input("File path: "))
                input("\nPress Enter to continue...")
            elif choice == 2:
                rule = input("YARA rule file: ")
                target = input("Target directory: ")
                print(self.malware.yara_scan(rule, target))
                input("\nPress Enter to continue...")
            elif choice == 3:
                print(self.malware.peframe_analyze(input("PE file path: ")))
                input("\nPress Enter to continue...")
            elif choice == 4:
                self.malware.radare2_analysis(input("Binary file: "))
                input("\nPress Enter to continue...")
            elif choice == 5:
                self.malware.ghidra_analysis(input("Binary file: "))
                input("\nPress Enter to continue...")
            elif choice == 6:
                print(self.malware.objdump_disassemble(input("Binary file: ")))
                input("\nPress Enter to continue...")
            elif choice == 7:
                dump = input("Memory dump file: ")
                profile = input("Volatility profile (e.g., Win7SP1x64): ")
                results = self.malware.volatility_memory(dump, profile)
                for key, val in results.items():
                    print(f"\n{Colors.BOLD}{key}{Colors.END}")
                    print(val[:500])
                input("\nPress Enter to continue...")
            elif choice == 8:
                results = self.malware.static_analysis(input("File path: "))
                for key, val in results.items():
                    print(f"\n{Colors.BOLD}{key}{Colors.END}")
                    print(val[:500] if len(val) > 500 else val)
                input("\nPress Enter to continue...")
    
    # -------------------------------------------------------------------------
    # CLOUD SECURITY MENU (NEW)
    # -------------------------------------------------------------------------
    def cloud_menu(self):
        while True:
            self.clear()
            print(Colors.banner())
            self.print_menu("CLOUD SECURITY", [
                ("scout", "ScoutSuite AWS/Azure/GCP"),
                ("prowler", "Prowler AWS Audit"),
                ("cloudsploit", "CloudSploit Scan"),
                ("pacu", "Pacu AWS Exploitation"),
                ("s3scanner", "S3 Bucket Scanner"),
                ("cloud_enum", "Cloud Enum (All Providers)")
            ])
            choice = self.get_choice(6)
            if choice == 0: break
            elif choice == 1:
                self.cloud.scout_aws(input("AWS profile (default): ") or "default")
                input("\nPress Enter to continue...")
            elif choice == 2:
                self.cloud.prowler_aws()
                input("\nPress Enter to continue...")
            elif choice == 3:
                self.cloud.cloudsploit_scan(input("Cloud provider (aws/azure/gcp): ") or "aws")
                input("\nPress Enter to continue...")
            elif choice == 4:
                self.cloud.pacu_framework()
                input("\nPress Enter to continue...")
            elif choice == 5:
                print(self.cloud.s3scanner(input("S3 bucket name: ")))
                input("\nPress Enter to continue...")
            elif choice == 6:
                self.cloud.cloud_enum(input("Keyword to search: "))
                input("\nPress Enter to continue...")
    
    # -------------------------------------------------------------------------
    # CONTAINER SECURITY MENU (NEW)
    # -------------------------------------------------------------------------
    def container_menu(self):
        while True:
            self.clear()
            print(Colors.banner())
            self.print_menu("CONTAINER & KUBERNETES SECURITY", [
                ("trivy_image", "Trivy Docker Image Scan"),
                ("trivy_fs", "Trivy Filesystem Scan"),
                ("docker_bench", "Docker Bench Security"),
                ("kube_bench", "Kube-bench CIS Scan"),
                ("kube_hunter", "Kube-hunter Penetration Test"),
                ("grype", "Grype Vulnerability Scan")
            ])
            choice = self.get_choice(6)
            if choice == 0: break
            elif choice == 1:
                self.container.trivy_scan_image(input("Docker image name: "))
                input("\nPress Enter to continue...")
            elif choice == 2:
                self.container.trivy_scan_fs(input("Path to scan (default .): ") or ".")
                input("\nPress Enter to continue...")
            elif choice == 3:
                self.container.docker_bench_security()
                input("\nPress Enter to continue...")
            elif choice == 4:
                self.container.kube_bench()
                input("\nPress Enter to continue...")
            elif choice == 5:
                self.container.kube_hunter(input("Remote cluster IP (optional): ") or None)
                input("\nPress Enter to continue...")
            elif choice == 6:
                self.container.grype_scan(input("Target (image/dir): "))
                input("\nPress Enter to continue...")
    
    # -------------------------------------------------------------------------
    # API SECURITY MENU (NEW)
    # -------------------------------------------------------------------------
    def api_menu(self):
        while True:
            self.clear()
            print(Colors.banner())
            self.print_menu("API SECURITY TESTING", [
                ("postman", "Postman/Newman Collection Test"),
                ("arjun", "Arjun Parameter Discovery"),
                ("crlfuzz", "CRLFuzz Header Injection"),
                ("graphql", "GraphQL Security Scan"),
                ("swagger", "Swagger API Scan")
            ])
            choice = self.get_choice(5)
            if choice == 0: break
            elif choice == 1:
                self.api_sec.postman_collection_test(input("Collection JSON file: "))
                input("\nPress Enter to continue...")
            elif choice == 2:
                self.api_sec.arjun_scan(input("Target URL: "))
                input("\nPress Enter to continue...")
            elif choice == 3:
                self.api_sec.crlfuzz_scan(input("Target URL: "))
                input("\nPress Enter to continue...")
            elif choice == 4:
                self.api_sec.graphql_scan(input("GraphQL endpoint: "))
                input("\nPress Enter to continue...")
            elif choice == 5:
                self.api_sec.swagger_scan(input("Swagger URL: "))
                input("\nPress Enter to continue...")
    
    # -------------------------------------------------------------------------
    # AI SECURITY MENU (NEW)
    # -------------------------------------------------------------------------
    def ai_menu(self):
        while True:
            self.clear()
            print(Colors.banner())
            self.print_menu("AI & LLM SECURITY TESTING", [
                ("garak", "Garak LLM Red Teaming"),
                ("vigil", "Vigil Prompt Injection Scan"),
                ("pyrit", "PyRIT Risk Identification"),
                ("giskard", "Giskard Model Scan")
            ])
            choice = self.get_choice(4)
            if choice == 0: break
            elif choice == 1:
                self.ai_sec.run_garak(input("Target model URL: "))
                input("\nPress Enter to continue...")
            elif choice == 2:
                self.ai_sec.run_vigil(input("Prompt text to scan: "))
                input("\nPress Enter to continue...")
            elif choice == 3:
                self.ai_sec.run_pyrit()
                input("\nPress Enter to continue...")
            elif choice == 4:
                self.ai_sec.run_giskard(input("Model file path: "))
                input("\nPress Enter to continue...")

    # -------------------------------------------------------------------------
    # CRYPTOGRAPHY MENU (NEW)
    # -------------------------------------------------------------------------
    def crypto_menu(self):
        while True:
            self.clear()
            print(Colors.banner())
            self.print_menu("CRYPTOGRAPHY & PASSWORD CRACKING", [
                ("hashid", "Hash Identifier"),
                ("hashcat", "Hashcat GPU Cracking"),
                ("john", "John the Ripper"),
                ("hydra", "Hydra Online Brute Force"),
                ("medusa", "Medusa Brute Force"),
                ("ncrack", "Ncrack Network Cracking"),
                ("openssl", "OpenSSL Certificate Check"),
                ("sslscan", "SSLScan TLS Test"),
                ("testssl", "testssl.sh Complete Audit")
            ])
            choice = self.get_choice(9)
            if choice == 0: break
            elif choice == 1:
                print(self.crypto.hash_identifier(input("Hash value: ")))
                input("\nPress Enter to continue...")
            elif choice == 2:
                hf = input("Hash file: ")
                ht = int(input("Hash type number (0=MD5, 100=SHA1, 1400=SHA256): ") or "0")
                self.crypto.hashcat_crack(hf, ht)
                input("\nPress Enter to continue...")
            elif choice == 3:
                self.crypto.john_crack(input("Hash file: "))
                input("\nPress Enter to continue...")
            elif choice == 4:
                t = input("Target: ")
                s = input("Service (ssh/ftp/rdp/http-post-form): ")
                u = input("Username list: ")
                p = input("Password list: ")
                self.crypto.hydra_brute(t, s, u, p)
                input("\nPress Enter to continue...")
            elif choice == 5:
                t = input("Target: ")
                s = input("Service: ")
                u = input("Username list: ")
                p = input("Password list: ")
                self.crypto.medusa_brute(t, s, u, p)
                input("\nPress Enter to continue...")
            elif choice == 6:
                t = input("Target: ")
                s = input("Service: ")
                self.crypto.ncrack_scan(t, s)
                input("\nPress Enter to continue...")
            elif choice == 7:
                print(self.crypto.openssl_check(input("Host: "), int(input("Port (default 443): ") or "443")))
                input("\nPress Enter to continue...")
            elif choice == 8:
                self.crypto.sslscan_test(input("Host: "), int(input("Port (default 443): ") or "443"))
                input("\nPress Enter to continue...")
            elif choice == 9:
                self.crypto.testssl_sh(input("Host: "))
                input("\nPress Enter to continue...")
    
    # -------------------------------------------------------------------------
    # BUG BOUNTY MENU (NEW)
    # -------------------------------------------------------------------------
    def bugbounty_menu(self):
        while True:
            self.clear()
            print(Colors.banner())
            self.print_menu("BUG BOUNTY & AUTOMATION", [
                ("subfinder", "Subfinder Subdomain Enum"),
                ("amass", "Amass Deep Enumeration"),
                ("assetfinder", "Assetfinder Subdomains"),
                ("gau", "GetAllUrls (Gau)"),
                ("wayback", "WaybackURLs"),
                ("httprobe", "HTTPProbe Live Check"),
                ("aquatone", "Aquatone Screenshots"),
                ("dalfox", "Dalfox XSS Mass Scan"),
                ("gf", "GF Pattern Search"),
                ("nuclei", "Nuclei Mass Scan")
            ])
            choice = self.get_choice(10)
            if choice == 0: break
            elif choice == 1:
                print(self.bugbounty.subfinder_enum(input("Domain: ")))
                input("\nPress Enter to continue...")
            elif choice == 2:
                print(self.bugbounty.amass_enum(input("Domain: ")))
                input("\nPress Enter to continue...")
            elif choice == 3:
                print(self.bugbounty.assetfinder_enum(input("Domain: ")))
                input("\nPress Enter to continue...")
            elif choice == 4:
                print(self.bugbounty.gau_urls(input("Domain: ")))
                input("\nPress Enter to continue...")
            elif choice == 5:
                print(self.bugbounty.waybackurls(input("Domain: ")))
                input("\nPress Enter to continue...")
            elif choice == 6:
                f = input("URL file path: ")
                print(self.bugbounty.httprobe_live(f))
                input("\nPress Enter to continue...")
            elif choice == 7:
                f = input("URL file path: ")
                print(self.bugbounty.aquatone_screenshot(f))
                input("\nPress Enter to continue...")
            elif choice == 8:
                f = input("URL file path: ")
                self.bugbounty.dalfox_xss(f)
                input("\nPress Enter to continue...")
            elif choice == 9:
                f = input("URL file path: ")
                pattern = input("Pattern (xss/ssrf/sqli/etc): ") or "xss"
                print(self.bugbounty.gf_patterns(f, pattern))
                input("\nPress Enter to continue...")
            elif choice == 10:
                f = input("Target file path: ")
                self.bugbounty.nuclei_template_scan(f)
                input("\nPress Enter to continue...")
    
    # -------------------------------------------------------------------------
    # FORENSICS MENU
    # -------------------------------------------------------------------------
    def forensics_menu(self):
        while True:
            self.clear()
            print(Colors.banner())
            self.print_menu("DIGITAL FORENSICS", [
                ("binwalk", "Binwalk Firmware Analysis"),
                ("exiftool", "ExifTool Metadata Extraction"),
                ("strings", "Extract Strings from Binary"),
                ("foremost", "Foremost File Carving"),
                ("photorec", "PhotoRec File Recovery"),
                ("sleuthkit", "SleuthKit Disk Analysis"),
                ("autopsy", "Autopsy GUI Forensics")
            ])
            choice = self.get_choice(7)
            if choice == 0: break
            elif choice == 1:
                print(self.forensics.binwalk_scan(input("File path: ")))
                input("\nPress Enter to continue...")
            elif choice == 2:
                print(self.forensics.exiftool_scan(input("File path: ")))
                input("\nPress Enter to continue...")
            elif choice == 3:
                f = input("File path: ")
                min_len = int(input("Min string length (default 4): ") or "4")
                print(self.forensics.strings_extract(f, min_len))
                input("\nPress Enter to continue...")
            elif choice == 4:
                f = input("File path: ")
                out = input("Output dir (default ./forensics_output): ") or "./forensics_output"
                self.forensics.foremost_extract(f, out)
                input("\nPress Enter to continue...")
            elif choice == 5:
                disk = input("Disk/device (e.g., /dev/sdb1): ")
                self.forensics.photorec_recovery(disk)
                input("\nPress Enter to continue...")
            elif choice == 6:
                print(self.forensics.sleuthkit_analysis(input("Disk image: ")))
                input("\nPress Enter to continue...")
            elif choice == 7:
                self.forensics.autopsy_launch()
                input("\nPress Enter to continue...")
    
    # -------------------------------------------------------------------------
    # EXPLOITATION MENU
    # -------------------------------------------------------------------------
    def exploitation_menu(self):
        while True:
            self.clear()
            print(Colors.banner())
            self.print_menu("EXPLOITATION FRAMEWORK", [
                ("searchsploit", "Search Exploit Database"),
                ("metasploit", "Launch Metasploit Console"),
                ("beef", "BeEF Browser Exploitation"),
                ("armitage", "Armitage GUI"),
                ("empire", "PowerShell Empire"),
                ("covenant", "Covenant C2 Framework")
            ])
            choice = self.get_choice(6)
            if choice == 0: break
            elif choice == 1:
                print(self.exploitation.searchsploit(input("Search query: ")))
                input("\nPress Enter to continue...")
            elif choice == 2:
                print("Launching Metasploit... (type 'exit' to return)")
                self.exploitation.metasploit_console()
                input("\nPress Enter to continue...")
            elif choice == 3:
                self.exploitation.beef_framework()
                input("\nPress Enter to continue...")
            elif choice == 4:
                self.exploitation.armitage_launch()
                input("\nPress Enter to continue...")
            elif choice == 5:
                self.exploitation.empire_launch()
                input("\nPress Enter to continue...")
            elif choice == 6:
                self.exploitation.covenant_launch()
                input("\nPress Enter to continue...")
    
    # -------------------------------------------------------------------------
    # SYSTEM UTILITIES MENU
    # -------------------------------------------------------------------------
    def system_menu(self):
        while True:
            self.clear()
            print(Colors.banner())
            self.print_menu("SYSTEM UTILITIES", [
                ("netstat", "Network Connections"),
                ("iptables", "Firewall Rules"),
                ("sysinfo", "System Information"),
                ("processes", "Running Processes"),
                ("lsof", "Open Files/Connections"),
                ("tcpdump", "Tcpdump Quick Capture")
            ])
            choice = self.get_choice(6)
            if choice == 0: break
            elif choice == 1:
                print(self.system.netstat_info())
                input("\nPress Enter to continue...")
            elif choice == 2:
                print(self.system.iptables_rules())
                input("\nPress Enter to continue...")
            elif choice == 3:
                info = self.system.system_info()
                for key, value in info.items():
                    print(f"{Colors.BOLD}{key}:{Colors.END} {value}")
                input("\nPress Enter to continue...")
            elif choice == 4:
                print(self.system.running_processes())
                input("\nPress Enter to continue...")
            elif choice == 5:
                print(self.system.lsof_open_files())
                input("\nPress Enter to continue...")
            elif choice == 6:
                iface = input("Interface (default any): ") or "any"
                count = int(input("Packet count (default 100): ") or "100")
                print(self.system.tcpdump_capture(iface, count))
                input("\nPress Enter to continue...")
    
    # -------------------------------------------------------------------------
    # MAIN MENU
    # -------------------------------------------------------------------------
    def run(self):
        while True:
            self.clear()
            print(Colors.banner())
            self.print_menu("MAIN MENU", [
                ("wireshark", "Wireshark / Tshark Packet Analysis"),
                ("scanning", "Network Scanning & Reconnaissance"),
                ("webapp", "Web Application Testing"),
                ("wireless", "Wireless Network Testing"),
                ("osint", "OSINT & Social Engineering"),
                ("malware", "Malware Analysis & Reverse Engineering"),
                ("cloud", "Cloud Security Assessment"),
                ("container", "Container & Kubernetes Security"),
                ("api", "API Security Testing"),
                ("ai", "AI & LLM Security Testing"),
                ("crypto", "Cryptography & Password Cracking"),
                ("bugbounty", "Bug Bounty & Automation"),
                ("forensics", "Digital Forensics"),
                ("exploitation", "Exploitation Framework"),
                ("system", "System Utilities"),
                ("syscheck", "Full System Dependency Check")
            ])
            
            choice = self.get_choice(16)
            if choice == 0:
                self.logger.info("Exiting Kali Tools System. Stay ethical!")
                break
            elif choice == 1: self.wireshark_menu()
            elif choice == 2: self.scanning_menu()
            elif choice == 3: self.webapp_menu()
            elif choice == 4: self.wireless_menu()
            elif choice == 5: self.osint_menu()
            elif choice == 6: self.malware_menu()
            elif choice == 7: self.cloud_menu()
            elif choice == 8: self.container_menu()
            elif choice == 9: self.api_menu()
            elif choice == 10: self.ai_menu()
            elif choice == 11: self.crypto_menu()
            elif choice == 12: self.bugbounty_menu()
            elif choice == 13: self.forensics_menu()
            elif choice == 14: self.exploitation_menu()
            elif choice == 15: self.system_menu()
            elif choice == 16:
                self.system.full_system_check()
                input("\nPress Enter to continue...")


# =============================================================================
# COMMAND LINE INTERFACE
# =============================================================================

def cli_mode():
    parser = argparse.ArgumentParser(description="Kali Linux + Cybersecurity Tools System")
    parser.add_argument("--module", choices=[
        "wireshark", "scan", "web", "wireless", "osint", "malware", 
        "cloud", "container", "api", "ai", "crypto", "bugbounty",
        "forensics", "exploit", "system", "syscheck"
    ], help="Module to run")
    parser.add_argument("--action", help="Action within module")
    parser.add_argument("--target", help="Target IP/URL/Domain")
    parser.add_argument("--file", help="Input file")
    parser.add_argument("--interface", help="Network interface")
    parser.add_argument("--output", help="Output file")
    
    args = parser.parse_args()
    
    if not args.module:
        app = KaliToolsSystem()
        app.run()
        return
    
    config = Config()
    logger = Logger(config)
    executor = CommandExecutor(logger)
    tool_manager = ToolManager(logger)
    
    if args.module == "scan":
        scanner = NetworkScanner(executor, logger, tool_manager)
        if args.action == "nmap" and args.target:
            scanner.nmap_scan(args.target)
        elif args.action == "masscan" and args.target:
            scanner.masscan_scan(args.target)
    elif args.module == "wireshark":
        ws = WiresharkModule(executor, config, logger, tool_manager)
        if args.action == "interfaces":
            ws.list_interfaces()
        elif args.action == "analyze" and args.file:
            ws.analyze_pcap(args.file)
    elif args.module == "ai":
        ai = AISecurityTools(executor, logger, tool_manager)
        if args.action == "garak" and args.target:
            ai.run_garak(args.target)
    elif args.module == "system":
        sys_util = SystemUtils(executor, logger, tool_manager)
        if args.action == "info":
            print(sys_util.system_info())
    elif args.module == "syscheck":
        sys_util = SystemUtils(executor, logger, tool_manager)
        sys_util.full_system_check()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    try:
        cli_mode()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Interrupted by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}[!] Error: {e}{Colors.END}")
        sys.exit(1)
