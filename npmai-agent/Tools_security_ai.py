"""
tools_security_ai.py — Security & AI Tools for NPM Agent
NPMAI ECOSYSTEM — by Sonu Kumar

Provides: SecurityScannerTool, CryptographyTool, PenetrationTestingTool,
          AIImageGenerationTool, AITextGenerationAdvancedTool, MLModelTool,
          SpeechAITool, ComputerVisionTool, AutomationWorkflowTool,
          KnowledgeBaseTool
"""

import os
import sys
import json
import re
import time
import uuid
import base64
import hashlib
import sqlite3
import threading
import subprocess
import tempfile
import socket
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Callable, Optional

# ── Import shared primitives from agent_core ────────────────────────────────
from agent_core import ToolResult, CredStore, _ensure

# ── Auto-install dependencies ───────────────────────────────────────────────
for _pkg, _imp in [
    ("requests",               "requests"),
    ("cryptography",           "cryptography"),
    ("pyotp",                  "pyotp"),
    ("bcrypt",                 "bcrypt"),
    ("python-whois",           "whois"),
    ("dnspython",              "dns"),
    ("scikit-learn",           "sklearn"),
    ("joblib",                 "joblib"),
    ("pandas",                 "pandas"),
    ("numpy",                  "numpy"),
    ("flask",                  "flask"),
    ("schedule",               "schedule"),
    ("watchdog",               "watchdog"),
    ("beautifulsoup4",         "bs4"),
    ("Pillow",                 "PIL"),
    ("pytesseract",            "pytesseract"),
    ("opencv-python",          "cv2"),
    ("pyzbar",                 "pyzbar"),
    ("qrcode",                 "qrcode"),
    ("faiss-cpu",              "faiss"),
    ("sentence-transformers",  "sentence_transformers"),
    ("langchain-text-splitters","langchain_text_splitters"),
]:
    _ensure(_pkg, _imp)


# ═══════════════════════════════════════════════════════════════════════════
# 1. SecurityScannerTool
# ═══════════════════════════════════════════════════════════════════════════
class SecurityScannerTool:
    name = "security_scanner"
    description = (
        "Ethical security scanning: VirusTotal, Shodan, HaveIBeenPwned, "
        "nmap, port scan, WHOIS, SSL, DNS leak, URL safety, threat intel"
    )

    @staticmethod
    def check_virustotal(hash_or_url_or_ip: str, type: str = "hash",
                         cred_key: str = "virustotal") -> ToolResult:
        """type: hash | url | ip | domain"""
        try:
            import requests
            api_key = CredStore.load(cred_key).get("api_key", "")
            if not api_key:
                return ToolResult(False, "No VirusTotal API key. Save under 'virustotal' → {'api_key':'...'}")
            headers = {"x-apikey": api_key}
            endpoint_map = {
                "hash":   f"https://www.virustotal.com/api/v3/files/{hash_or_url_or_ip}",
                "ip":     f"https://www.virustotal.com/api/v3/ip_addresses/{hash_or_url_or_ip}",
                "domain": f"https://www.virustotal.com/api/v3/domains/{hash_or_url_or_ip}",
                "url":    None,
            }
            if type == "url":
                # Submit URL for scanning
                encoded = base64.urlsafe_b64encode(hash_or_url_or_ip.encode()).rstrip(b"=").decode()
                r = requests.get(f"https://www.virustotal.com/api/v3/urls/{encoded}",
                                 headers=headers, timeout=15)
            else:
                url = endpoint_map.get(type, endpoint_map["hash"])
                r = requests.get(url, headers=headers, timeout=15)
            r.raise_for_status()
            data = r.json().get("data", {})
            attrs = data.get("attributes", {})
            stats = attrs.get("last_analysis_stats", {})
            malicious = stats.get("malicious", 0)
            total = sum(stats.values()) if stats else 0
            return ToolResult(True, f"✓ VT: {malicious}/{total} malicious",
                              {"indicator": hash_or_url_or_ip, "type": type,
                               "stats": stats, "reputation": attrs.get("reputation", 0),
                               "tags": attrs.get("tags", [])})
        except Exception as e:
            return ToolResult(False, f"✗ check_virustotal failed: {e}")

    @staticmethod
    def scan_file_virustotal(file_path: str, cred_key: str = "virustotal") -> ToolResult:
        try:
            import requests
            api_key = CredStore.load(cred_key).get("api_key", "")
            if not api_key:
                return ToolResult(False, "No VirusTotal API key.")
            # Compute SHA-256 first and check existing report
            with open(file_path, "rb") as f:
                sha256 = hashlib.sha256(f.read()).hexdigest()
            # Check existing report
            existing = SecurityScannerTool.check_virustotal(sha256, "hash", cred_key)
            if existing.success:
                return existing
            # Upload file
            with open(file_path, "rb") as f:
                r = requests.post("https://www.virustotal.com/api/v3/files",
                                  headers={"x-apikey": api_key},
                                  files={"file": (Path(file_path).name, f)}, timeout=60)
            r.raise_for_status()
            analysis_id = r.json().get("data", {}).get("id", "")
            # Poll for result
            for _ in range(10):
                time.sleep(3)
                rp = requests.get(f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
                                  headers={"x-apikey": api_key}, timeout=15)
                rp.raise_for_status()
                status = rp.json().get("data", {}).get("attributes", {}).get("status", "")
                if status == "completed":
                    stats = rp.json()["data"]["attributes"]["stats"]
                    malicious = stats.get("malicious", 0)
                    total = sum(stats.values())
                    return ToolResult(True, f"✓ File scan: {malicious}/{total} malicious",
                                      {"sha256": sha256, "stats": stats})
            return ToolResult(False, "✗ File scan timed out waiting for results")
        except Exception as e:
            return ToolResult(False, f"✗ scan_file_virustotal failed: {e}")

    @staticmethod
    def shodan_search(query: str, facets: str = None, page: int = 1,
                      cred_key: str = "shodan") -> ToolResult:
        try:
            import requests
            api_key = CredStore.load(cred_key).get("api_key", "")
            if not api_key:
                return ToolResult(False, "No Shodan API key. Save under 'shodan' → {'api_key':'...'}")
            params = {"key": api_key, "query": query, "page": page}
            if facets:
                params["facets"] = facets
            r = requests.get("https://api.shodan.io/shodan/host/search",
                             params=params, timeout=20)
            r.raise_for_status()
            data = r.json()
            return ToolResult(True, f"✓ Shodan: {data.get('total', 0)} results",
                              {"total": data.get("total", 0), "matches": data.get("matches", [])[:10],
                               "facets": data.get("facets", {})})
        except Exception as e:
            return ToolResult(False, f"✗ shodan_search failed: {e}")

    @staticmethod
    def shodan_host(ip: str, cred_key: str = "shodan") -> ToolResult:
        try:
            import requests
            api_key = CredStore.load(cred_key).get("api_key", "")
            if not api_key:
                return ToolResult(False, "No Shodan API key.")
            r = requests.get(f"https://api.shodan.io/shodan/host/{ip}",
                             params={"key": api_key}, timeout=15)
            r.raise_for_status()
            data = r.json()
            return ToolResult(True, f"✓ Shodan host: {ip}", {
                "ip": ip, "org": data.get("org"), "country": data.get("country_name"),
                "ports": data.get("ports", []), "vulns": list(data.get("vulns", {}).keys()),
                "hostnames": data.get("hostnames", []), "os": data.get("os")
            })
        except Exception as e:
            return ToolResult(False, f"✗ shodan_host failed: {e}")

    @staticmethod
    def check_haveibeenpwned(email: str, cred_key: str = "hibp") -> ToolResult:
        try:
            import requests
            api_key = CredStore.load(cred_key).get("api_key", "")
            headers = {"hibp-api-key": api_key, "User-Agent": "NPM-Agent-HIBP-Check"} if api_key else \
                      {"User-Agent": "NPM-Agent-HIBP-Check"}
            r = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                             headers=headers, timeout=15)
            if r.status_code == 404:
                return ToolResult(True, f"✓ {email} — NOT found in any breach", {"breaches": []})
            r.raise_for_status()
            breaches = r.json()
            names = [b.get("Name", "") for b in breaches]
            return ToolResult(True, f"⚠ {email} found in {len(breaches)} breaches: {', '.join(names[:5])}",
                              {"breaches": breaches, "count": len(breaches)})
        except Exception as e:
            return ToolResult(False, f"✗ check_haveibeenpwned failed: {e}")

    @staticmethod
    def check_password_breach(password: str) -> ToolResult:
        """k-Anonymity model — only first 5 chars of SHA1 hash are sent to API."""
        try:
            import requests
            sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
            prefix, suffix = sha1[:5], sha1[5:]
            r = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}",
                             headers={"User-Agent": "NPM-Agent"}, timeout=10)
            r.raise_for_status()
            hashes = {line.split(":")[0]: int(line.split(":")[1]) for line in r.text.splitlines()}
            count = hashes.get(suffix, 0)
            if count > 0:
                return ToolResult(True, f"⚠ Password found {count:,} times in breach data",
                                  {"breached": True, "count": count})
            return ToolResult(True, "✓ Password NOT found in breach data",
                              {"breached": False, "count": 0})
        except Exception as e:
            return ToolResult(False, f"✗ check_password_breach failed: {e}")

    @staticmethod
    def nmap_scan(target: str, arguments: str = "-sV -O", output_format: str = "dict") -> ToolResult:
        try:
            import nmap
            nm = nmap.PortScanner()
            nm.scan(hosts=target, arguments=arguments)
            results = {}
            for host in nm.all_hosts():
                results[host] = {
                    "state": nm[host].state(),
                    "hostname": nm[host].hostname(),
                    "protocols": {}
                }
                for proto in nm[host].all_protocols():
                    results[host]["protocols"][proto] = {}
                    for port in nm[host][proto].keys():
                        results[host]["protocols"][proto][port] = nm[host][proto][port]
            if output_format == "json":
                return ToolResult(True, f"✓ nmap scan complete: {len(results)} hosts",
                                  json.dumps(results, indent=2))
            return ToolResult(True, f"✓ nmap scan complete: {len(results)} hosts", results)
        except ImportError:
            # Fall back to subprocess nmap
            try:
                r = subprocess.run(["nmap", arguments, target], capture_output=True,
                                   text=True, timeout=120)
                return ToolResult(r.returncode == 0, r.stdout or r.stderr, r.stdout)
            except FileNotFoundError:
                return ToolResult(False, "✗ nmap not installed. Run: pip install python-nmap and install nmap binary.")
        except Exception as e:
            return ToolResult(False, f"✗ nmap_scan failed: {e}")

    @staticmethod
    def port_scan_common(host: str) -> ToolResult:
        """Fast scan of common ports using socket (no nmap required)."""
        try:
            common_ports = {
                21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
                80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
                3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC",
                6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt", 27017: "MongoDB"
            }
            open_ports = []
            closed_ports = []

            def check(port):
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1.0)
                    result = s.connect_ex((host, port))
                    s.close()
                    if result == 0:
                        open_ports.append({"port": port, "service": common_ports.get(port, "Unknown")})
                    else:
                        closed_ports.append(port)
                except Exception:
                    closed_ports.append(port)

            threads = [threading.Thread(target=check, args=(p,)) for p in common_ports]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=5)

            return ToolResult(True, f"✓ {len(open_ports)} open ports on {host}",
                              {"host": host, "open": open_ports, "closed_count": len(closed_ports)})
        except Exception as e:
            return ToolResult(False, f"✗ port_scan_common failed: {e}")

    @staticmethod
    def whois_lookup(domain_or_ip: str) -> ToolResult:
        try:
            import whois
            w = whois.whois(domain_or_ip)
            data = {
                "domain": str(w.domain_name or domain_or_ip),
                "registrar": str(w.registrar or ""),
                "creation_date": str(w.creation_date or ""),
                "expiration_date": str(w.expiration_date or ""),
                "name_servers": [str(ns) for ns in (w.name_servers or [])],
                "org": str(w.org or ""),
                "country": str(w.country or ""),
                "emails": [str(e) for e in (w.emails if isinstance(w.emails, list)
                           else [w.emails] if w.emails else [])]
            }
            return ToolResult(True, f"✓ WHOIS for {domain_or_ip}", data)
        except Exception as e:
            return ToolResult(False, f"✗ whois_lookup failed: {e}")

    @staticmethod
    def check_ssl_grade(domain: str) -> ToolResult:
        """Check SSL certificate details directly."""
        try:
            import ssl
            import socket
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
                s.settimeout(10)
                s.connect((domain, 443))
                cert = s.getpeercert()
            expiry = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
            days_left = (expiry - datetime.utcnow()).days
            subject = dict(x[0] for x in cert.get("subject", []))
            issuer = dict(x[0] for x in cert.get("issuer", []))
            sans = [v for t, v in cert.get("subjectAltName", []) if t == "DNS"]
            grade = "A" if days_left > 30 else ("B" if days_left > 7 else "F")
            return ToolResult(True, f"✓ SSL grade: {grade} — expires in {days_left} days",
                              {"domain": domain, "grade": grade, "days_until_expiry": days_left,
                               "expiry": expiry.isoformat(), "subject": subject,
                               "issuer": issuer, "san": sans})
        except ssl.SSLCertVerificationError as e:
            return ToolResult(True, f"⚠ SSL verification failed: {e}",
                              {"domain": domain, "grade": "F", "error": str(e)})
        except Exception as e:
            return ToolResult(False, f"✗ check_ssl_grade failed: {e}")

    @staticmethod
    def check_dns_leak(servers: list = None) -> ToolResult:
        """Compare DNS resolution to detect potential leaks."""
        try:
            import dns.resolver
            test_domain = "whoami.akamai.net"
            resolvers = servers or ["8.8.8.8", "1.1.1.1", "9.9.9.9"]
            results = {}
            for server in resolvers:
                try:
                    res = dns.resolver.Resolver()
                    res.nameservers = [server]
                    res.timeout = 3
                    answers = res.resolve(test_domain, "A")
                    results[server] = [str(r) for r in answers]
                except Exception as ex:
                    results[server] = [f"Error: {ex}"]
            all_ips = set(ip for ips in results.values() for ip in ips if not ip.startswith("Error"))
            leak_detected = len(all_ips) > 2
            return ToolResult(True, f"{'⚠ Potential DNS leak' if leak_detected else '✓ DNS looks consistent'}",
                              {"results": results, "unique_ips": list(all_ips),
                               "leak_detected": leak_detected})
        except Exception as e:
            return ToolResult(False, f"✗ check_dns_leak failed: {e}")

    @staticmethod
    def scan_url_safe_browsing(url: str, api_key: str = None) -> ToolResult:
        """Google Safe Browsing API check."""
        try:
            import requests
            key = api_key or CredStore.load("google_safe_browsing").get("api_key", "")
            if not key:
                # Fall back to heuristic check
                suspicious_patterns = [".exe", ".zip", "login", "bank", "paypal", "verify",
                                       "account", "update", "secure", "confirm"]
                score = sum(1 for p in suspicious_patterns if p in url.lower())
                return ToolResult(True, f"✓ Heuristic check: {score} suspicious patterns",
                                  {"url": url, "suspicious_score": score, "method": "heuristic"})
            payload = {
                "client": {"clientId": "npm-agent", "clientVersion": "1.0"},
                "threatInfo": {
                    "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE",
                                    "POTENTIALLY_HARMFUL_APPLICATION"],
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [{"url": url}]
                }
            }
            r = requests.post(
                f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={key}",
                json=payload, timeout=10
            )
            r.raise_for_status()
            matches = r.json().get("matches", [])
            return ToolResult(True,
                              f"⚠ URL flagged: {len(matches)} threats" if matches else "✓ URL appears safe",
                              {"url": url, "threats": matches, "safe": len(matches) == 0})
        except Exception as e:
            return ToolResult(False, f"✗ scan_url_safe_browsing failed: {e}")

    @staticmethod
    def check_reputation(ip_or_domain: str) -> ToolResult:
        """AbuseIPDB check for IP reputation."""
        try:
            import requests
            api_key = CredStore.load("abuseipdb").get("api_key", "")
            if not api_key:
                # Fallback: basic DNS blacklist check
                try:
                    reversed_ip = ".".join(reversed(ip_or_domain.split(".")))
                    socket.gethostbyname(f"{reversed_ip}.zen.spamhaus.org")
                    return ToolResult(True, f"⚠ {ip_or_domain} found in Spamhaus blocklist",
                                      {"blacklisted": True, "source": "spamhaus"})
                except socket.gaierror:
                    return ToolResult(True, f"✓ {ip_or_domain} not in basic blocklists",
                                      {"blacklisted": False})
            r = requests.get("https://api.abuseipdb.com/api/v2/check",
                             headers={"Key": api_key, "Accept": "application/json"},
                             params={"ipAddress": ip_or_domain, "maxAgeInDays": 90}, timeout=10)
            r.raise_for_status()
            data = r.json().get("data", {})
            score = data.get("abuseConfidenceScore", 0)
            return ToolResult(True, f"{'⚠' if score > 25 else '✓'} Abuse score: {score}/100", data)
        except Exception as e:
            return ToolResult(False, f"✗ check_reputation failed: {e}")

    @staticmethod
    def get_threat_intel(indicator: str, type: str = "ip") -> ToolResult:
        """Aggregate threat intel from multiple free sources."""
        try:
            import requests
            results = {}
            # AlienVault OTX (free, no key required for basic lookups)
            endpoint_map = {
                "ip": f"https://otx.alienvault.com/api/v1/indicators/IPv4/{indicator}/general",
                "domain": f"https://otx.alienvault.com/api/v1/indicators/domain/{indicator}/general",
                "url": f"https://otx.alienvault.com/api/v1/indicators/url/{indicator}/general",
                "hash": f"https://otx.alienvault.com/api/v1/indicators/file/{indicator}/general",
            }
            url = endpoint_map.get(type, endpoint_map["ip"])
            r = requests.get(url, headers={"User-Agent": "NPM-Agent"}, timeout=15)
            if r.ok:
                data = r.json()
                results["otx"] = {
                    "pulse_count": data.get("pulse_info", {}).get("count", 0),
                    "reputation": data.get("reputation", 0),
                    "indicator": indicator,
                    "type": type,
                    "tags": data.get("tags", [])
                }
            pulse_count = results.get("otx", {}).get("pulse_count", 0)
            return ToolResult(True,
                              f"{'⚠ Found in ' + str(pulse_count) + ' threat pulses' if pulse_count else '✓ No major threats found'}",
                              results)
        except Exception as e:
            return ToolResult(False, f"✗ get_threat_intel failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# 2. CryptographyTool
# ═══════════════════════════════════════════════════════════════════════════
class CryptographyTool:
    name = "cryptography"
    description = (
        "RSA key pairs, AES encryption, password hashing, TOTP, "
        "SSL cert generation, digital signatures, PGP encrypt/decrypt"
    )

    @staticmethod
    def generate_rsa_keypair(bits: int = 2048, output_folder: str = ".") -> ToolResult:
        try:
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            key = rsa.generate_private_key(public_exponent=65537, key_size=bits)
            priv_pem = key.private_bytes(
                serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption()
            )
            pub_pem = key.public_key().public_bytes(
                serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
            )
            out = Path(output_folder)
            out.mkdir(parents=True, exist_ok=True)
            (out / "private_key.pem").write_bytes(priv_pem)
            (out / "public_key.pem").write_bytes(pub_pem)
            (out / "private_key.pem").chmod(0o600)
            return ToolResult(True, f"✓ RSA {bits}-bit keypair generated in {output_folder}",
                              {"private_key": str(out / "private_key.pem"),
                               "public_key": str(out / "public_key.pem")})
        except Exception as e:
            return ToolResult(False, f"✗ generate_rsa_keypair failed: {e}")

    @staticmethod
    def encrypt_with_public_key(data: str, public_key_path: str) -> ToolResult:
        try:
            from cryptography.hazmat.primitives import serialization, hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            pub_key = serialization.load_pem_public_key(Path(public_key_path).read_bytes())
            ciphertext = pub_key.encrypt(
                data.encode(),
                padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )
            return ToolResult(True, "✓ Data encrypted",
                              {"ciphertext": base64.b64encode(ciphertext).decode()})
        except Exception as e:
            return ToolResult(False, f"✗ encrypt_with_public_key failed: {e}")

    @staticmethod
    def decrypt_with_private_key(data: str, private_key_path: str) -> ToolResult:
        """data: base64-encoded ciphertext"""
        try:
            from cryptography.hazmat.primitives import serialization, hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            priv_key = serialization.load_pem_private_key(Path(private_key_path).read_bytes(), password=None)
            ciphertext = base64.b64decode(data)
            plaintext = priv_key.decrypt(
                ciphertext,
                padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )
            return ToolResult(True, "✓ Data decrypted", {"plaintext": plaintext.decode()})
        except Exception as e:
            return ToolResult(False, f"✗ decrypt_with_private_key failed: {e}")

    @staticmethod
    def sign_data(data: str, private_key_path: str) -> ToolResult:
        try:
            from cryptography.hazmat.primitives import serialization, hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            priv_key = serialization.load_pem_private_key(Path(private_key_path).read_bytes(), password=None)
            sig = priv_key.sign(data.encode(),
                                padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                            salt_length=padding.PSS.MAX_LENGTH),
                                hashes.SHA256())
            return ToolResult(True, "✓ Data signed",
                              {"signature": base64.b64encode(sig).decode()})
        except Exception as e:
            return ToolResult(False, f"✗ sign_data failed: {e}")

    @staticmethod
    def verify_signature(data: str, signature: str, public_key_path: str) -> ToolResult:
        """signature: base64-encoded"""
        try:
            from cryptography.hazmat.primitives import serialization, hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.exceptions import InvalidSignature
            pub_key = serialization.load_pem_public_key(Path(public_key_path).read_bytes())
            sig = base64.b64decode(signature)
            pub_key.verify(sig, data.encode(),
                           padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                       salt_length=padding.PSS.MAX_LENGTH),
                           hashes.SHA256())
            return ToolResult(True, "✓ Signature valid", {"valid": True})
        except Exception as e:
            valid = "InvalidSignature" not in type(e).__name__
            return ToolResult(not valid, f"✗ Signature invalid: {e}", {"valid": False})

    @staticmethod
    def aes_encrypt(data: str, password: str, algorithm: str = "AES-256-GCM") -> ToolResult:
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            from cryptography.hazmat.primitives import hashes
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=390000)
            key = kdf.derive(password.encode())
            nonce = os.urandom(12)
            aesgcm = AESGCM(key)
            ciphertext = aesgcm.encrypt(nonce, data.encode(), None)
            payload = base64.b64encode(salt + nonce + ciphertext).decode()
            return ToolResult(True, "✓ Data AES encrypted", {"ciphertext": payload, "algorithm": algorithm})
        except Exception as e:
            return ToolResult(False, f"✗ aes_encrypt failed: {e}")

    @staticmethod
    def aes_decrypt(data: str, password: str, algorithm: str = "AES-256-GCM") -> ToolResult:
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            from cryptography.hazmat.primitives import hashes
            raw = base64.b64decode(data)
            salt, nonce, ciphertext = raw[:16], raw[16:28], raw[28:]
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=390000)
            key = kdf.derive(password.encode())
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            return ToolResult(True, "✓ Data AES decrypted", {"plaintext": plaintext.decode()})
        except Exception as e:
            return ToolResult(False, f"✗ aes_decrypt failed: {e}")

    @staticmethod
    def generate_random_password(length: int = 20, complexity: str = "high") -> ToolResult:
        try:
            import secrets, string
            chars = string.ascii_letters + string.digits
            if complexity in ("high", "medium"):
                chars += string.punctuation
            password = "".join(secrets.choice(chars) for _ in range(length))
            strength_score = (
                sum([any(c.isupper() for c in password),
                     any(c.islower() for c in password),
                     any(c.isdigit() for c in password),
                     any(c in string.punctuation for c in password)]) * 25
            )
            return ToolResult(True, f"✓ Password generated (strength: {strength_score}%)",
                              {"password": password, "length": length, "strength": strength_score})
        except Exception as e:
            return ToolResult(False, f"✗ generate_random_password failed: {e}")

    @staticmethod
    def hash_password(password: str, algorithm: str = "bcrypt", salt: str = None) -> ToolResult:
        try:
            if algorithm == "bcrypt":
                import bcrypt
                hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
                return ToolResult(True, "✓ Password hashed (bcrypt)",
                                  {"hash": hashed.decode(), "algorithm": "bcrypt"})
            elif algorithm in ("sha256", "sha512"):
                s = (salt or os.urandom(32).hex()).encode()
                h = hashlib.new(algorithm, s + password.encode()).hexdigest()
                return ToolResult(True, f"✓ Password hashed ({algorithm})",
                                  {"hash": h, "salt": s.decode(), "algorithm": algorithm})
            else:
                return ToolResult(False, f"✗ Unknown algorithm: {algorithm}. Use bcrypt/sha256/sha512")
        except Exception as e:
            return ToolResult(False, f"✗ hash_password failed: {e}")

    @staticmethod
    def verify_password(password: str, hash: str) -> ToolResult:
        try:
            # Detect algorithm
            if hash.startswith("$2b$") or hash.startswith("$2a$"):
                import bcrypt
                valid = bcrypt.checkpw(password.encode(), hash.encode())
            else:
                # SHA-based — cannot verify without stored salt separately
                return ToolResult(False, "✗ Cannot verify non-bcrypt hash without salt. Use bcrypt.")
            return ToolResult(True, f"✓ Password {'valid' if valid else 'invalid'}",
                              {"valid": valid})
        except Exception as e:
            return ToolResult(False, f"✗ verify_password failed: {e}")

    @staticmethod
    def generate_totp_secret() -> ToolResult:
        try:
            import pyotp
            secret = pyotp.random_base32()
            totp = pyotp.TOTP(secret)
            uri = totp.provisioning_uri(name="NPM Agent", issuer_name="NPMAI")
            return ToolResult(True, "✓ TOTP secret generated",
                              {"secret": secret, "provisioning_uri": uri,
                               "current_token": totp.now()})
        except Exception as e:
            return ToolResult(False, f"✗ generate_totp_secret failed: {e}")

    @staticmethod
    def verify_totp(secret: str, token: str) -> ToolResult:
        try:
            import pyotp
            totp = pyotp.TOTP(secret)
            valid = totp.verify(token, valid_window=1)
            return ToolResult(True, f"✓ TOTP token {'valid' if valid else 'invalid'}",
                              {"valid": valid, "expected": totp.now()})
        except Exception as e:
            return ToolResult(False, f"✗ verify_totp failed: {e}")

    @staticmethod
    def create_ssl_certificate(domain: str, output_folder: str, days: int = 365) -> ToolResult:
        """Generate a self-signed cert (for dev/internal use)."""
        return CryptographyTool.create_self_signed_cert(domain, output_folder, days)

    @staticmethod
    def create_self_signed_cert(cn: str, output_folder: str, days: int = 365) -> ToolResult:
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "NPM Agent"),
                x509.NameAttribute(NameOID.COMMON_NAME, cn),
            ])
            cert = (x509.CertificateBuilder()
                    .subject_name(subject).issuer_name(issuer)
                    .public_key(key.public_key())
                    .serial_number(x509.random_serial_number())
                    .not_valid_before(datetime.utcnow())
                    .not_valid_after(datetime.utcnow() + timedelta(days=days))
                    .add_extension(x509.SubjectAlternativeName([x509.DNSName(cn)]), critical=False)
                    .sign(key, hashes.SHA256()))
            out = Path(output_folder)
            out.mkdir(parents=True, exist_ok=True)
            (out / "cert.pem").write_bytes(cert.public_bytes(serialization.Encoding.PEM))
            (out / "key.pem").write_bytes(
                key.private_bytes(serialization.Encoding.PEM,
                                  serialization.PrivateFormat.TraditionalOpenSSL,
                                  serialization.NoEncryption()))
            return ToolResult(True, f"✓ Self-signed cert for '{cn}' ({days} days)",
                              {"cert": str(out / "cert.pem"), "key": str(out / "key.pem")})
        except Exception as e:
            return ToolResult(False, f"✗ create_self_signed_cert failed: {e}")

    @staticmethod
    def pgp_encrypt(message: str, recipient_key: str) -> ToolResult:
        """recipient_key: path to armored public key file or key string."""
        try:
            import gnupg
            gpg = gnupg.GPG()
            # Import key if path
            if Path(recipient_key).exists():
                import_result = gpg.import_keys(Path(recipient_key).read_text())
                fingerprint = import_result.fingerprints[0] if import_result.fingerprints else None
            else:
                import_result = gpg.import_keys(recipient_key)
                fingerprint = import_result.fingerprints[0] if import_result.fingerprints else None
            if not fingerprint:
                return ToolResult(False, "✗ Could not import PGP key")
            encrypted = gpg.encrypt(message, fingerprint, always_trust=True)
            return ToolResult(str(encrypted).startswith("-----"), "✓ PGP encrypted",
                              {"encrypted": str(encrypted), "fingerprint": fingerprint})
        except ImportError:
            return ToolResult(False, "✗ python-gnupg not installed. Run: pip install python-gnupg")
        except Exception as e:
            return ToolResult(False, f"✗ pgp_encrypt failed: {e}")

    @staticmethod
    def pgp_decrypt(encrypted: str, private_key: str, passphrase: str = "") -> ToolResult:
        try:
            import gnupg
            gpg = gnupg.GPG()
            if Path(private_key).exists():
                gpg.import_keys(Path(private_key).read_text())
            else:
                gpg.import_keys(private_key)
            decrypted = gpg.decrypt(encrypted, passphrase=passphrase)
            if decrypted.ok:
                return ToolResult(True, "✓ PGP decrypted", {"plaintext": str(decrypted)})
            return ToolResult(False, f"✗ PGP decrypt failed: {decrypted.status}")
        except ImportError:
            return ToolResult(False, "✗ python-gnupg not installed.")
        except Exception as e:
            return ToolResult(False, f"✗ pgp_decrypt failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# 3. PenetrationTestingTool
# ═══════════════════════════════════════════════════════════════════════════
class PenetrationTestingTool:
    """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║  FOR AUTHORIZED TESTING ONLY                                        ║
    ║  Always obtain written permission from the system owner before      ║
    ║  running any of these tests. Unauthorized use is illegal and        ║
    ║  unethical. NPM Agent and NPMAI Ecosystem are not responsible for   ║
    ║  any misuse of these tools.                                         ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """
    name = "penetration_testing"
    description = (
        "AUTHORIZED TESTING ONLY: subdomain enum, dir bruteforce, "
        "vuln checks, HTTP headers, CORS, SQLi/XSS tests, SSL vulns, "
        "security reports, pentest checklists"
    )

    @staticmethod
    def subdomain_enumeration(domain: str, wordlist: str = None, threads: int = 20) -> ToolResult:
        """FOR AUTHORIZED TESTING ONLY."""
        try:
            import requests
            common_subs = (Path(wordlist).read_text().splitlines() if wordlist and Path(wordlist).exists()
                           else ["www", "mail", "ftp", "admin", "api", "dev", "staging", "test",
                                 "app", "blog", "shop", "vpn", "remote", "portal", "smtp", "imap",
                                 "ns1", "ns2", "mx", "cdn", "static", "assets", "auth", "login"])
            found = []
            lock = threading.Lock()

            def check_sub(sub):
                target = f"{sub}.{domain}"
                try:
                    ip = socket.gethostbyname(target)
                    with lock:
                        found.append({"subdomain": target, "ip": ip})
                except socket.gaierror:
                    pass

            batch = [threading.Thread(target=check_sub, args=(s,)) for s in common_subs]
            for t in batch:
                t.start()
            for t in batch:
                t.join(timeout=5)

            return ToolResult(True, f"✓ Found {len(found)} subdomains for {domain}", found)
        except Exception as e:
            return ToolResult(False, f"✗ subdomain_enumeration failed: {e}")

    @staticmethod
    def directory_bruteforce(url: str, wordlist: str = None, extensions: list = None,
                             threads: int = 10) -> ToolResult:
        """FOR AUTHORIZED TESTING ONLY."""
        try:
            import requests
            paths = (Path(wordlist).read_text().splitlines() if wordlist and Path(wordlist).exists()
                     else ["admin", "login", "dashboard", "api", "config", "backup", "test",
                           "upload", "uploads", "static", "assets", "phpinfo.php", "wp-admin",
                           ".git", ".env", "robots.txt", "sitemap.xml", "README.md"])
            exts = extensions or ["", ".php", ".html", ".asp", ".aspx", ".bak"]
            found = []
            lock = threading.Lock()
            session = requests.Session()
            session.headers = {"User-Agent": "Mozilla/5.0 (Security Test)"}

            def check_path(path_ext):
                target = url.rstrip("/") + "/" + path_ext
                try:
                    r = session.get(target, timeout=5, allow_redirects=False)
                    if r.status_code not in (404, 410):
                        with lock:
                            found.append({"url": target, "status": r.status_code,
                                          "size": len(r.content)})
                except Exception:
                    pass

            all_paths = [p + e for p in paths for e in exts if p and not p.endswith(e.lstrip("."))]
            batch_size = threads
            for i in range(0, len(all_paths), batch_size):
                batch = [threading.Thread(target=check_path, args=(p,)) for p in all_paths[i:i+batch_size]]
                for t in batch:
                    t.start()
                for t in batch:
                    t.join(timeout=10)

            return ToolResult(True, f"✓ Found {len(found)} accessible paths", found)
        except Exception as e:
            return ToolResult(False, f"✗ directory_bruteforce failed: {e}")

    @staticmethod
    def check_common_vulnerabilities(url: str) -> ToolResult:
        """FOR AUTHORIZED TESTING ONLY. Passive checks only."""
        try:
            import requests
            findings = []
            r = requests.get(url, timeout=10, verify=False)
            headers = {k.lower(): v for k, v in r.headers.items()}
            # Check missing security headers
            for h in ["x-frame-options", "x-content-type-options", "x-xss-protection",
                      "strict-transport-security", "content-security-policy"]:
                if h not in headers:
                    findings.append({"type": "missing_header", "header": h, "severity": "medium"})
            # Check server disclosure
            if "server" in headers:
                findings.append({"type": "server_disclosure", "value": headers["server"],
                                 "severity": "low"})
            # Check version disclosure in X-Powered-By
            if "x-powered-by" in headers:
                findings.append({"type": "tech_disclosure", "value": headers["x-powered-by"],
                                 "severity": "low"})
            # Check for HTTP (not HTTPS)
            if url.startswith("http://"):
                findings.append({"type": "no_https", "severity": "high"})
            # Check for directory listing indicators
            if "<title>Index of" in r.text:
                findings.append({"type": "directory_listing", "severity": "high"})
            # Check for common exposed files
            for path in ["/robots.txt", "/.git/config", "/.env", "/wp-config.php.bak"]:
                try:
                    rp = requests.get(url.rstrip("/") + path, timeout=5)
                    if rp.status_code == 200 and len(rp.text) > 10:
                        findings.append({"type": "exposed_file", "path": path, "severity": "high"})
                except Exception:
                    pass
            severity_counts = {"high": 0, "medium": 0, "low": 0}
            for f in findings:
                severity_counts[f.get("severity", "low")] += 1
            return ToolResult(True,
                              f"✓ {len(findings)} issues: {severity_counts['high']}H {severity_counts['medium']}M {severity_counts['low']}L",
                              {"findings": findings, "severity_summary": severity_counts})
        except Exception as e:
            return ToolResult(False, f"✗ check_common_vulnerabilities failed: {e}")

    @staticmethod
    def check_http_headers(url: str) -> ToolResult:
        """FOR AUTHORIZED TESTING ONLY."""
        try:
            import requests
            r = requests.get(url, timeout=10)
            security_headers = {
                "Strict-Transport-Security": r.headers.get("Strict-Transport-Security", "MISSING"),
                "Content-Security-Policy": r.headers.get("Content-Security-Policy", "MISSING"),
                "X-Frame-Options": r.headers.get("X-Frame-Options", "MISSING"),
                "X-Content-Type-Options": r.headers.get("X-Content-Type-Options", "MISSING"),
                "X-XSS-Protection": r.headers.get("X-XSS-Protection", "MISSING"),
                "Referrer-Policy": r.headers.get("Referrer-Policy", "MISSING"),
                "Permissions-Policy": r.headers.get("Permissions-Policy", "MISSING"),
            }
            score = sum(1 for v in security_headers.values() if v != "MISSING")
            grade = ["F", "D", "C", "C+", "B", "B+", "A", "A+"][min(score, 7)]
            return ToolResult(True, f"✓ Security headers grade: {grade} ({score}/7)",
                              {"url": url, "grade": grade, "score": f"{score}/7",
                               "headers": security_headers, "all_headers": dict(r.headers)})
        except Exception as e:
            return ToolResult(False, f"✗ check_http_headers failed: {e}")

    @staticmethod
    def check_cors(url: str) -> ToolResult:
        """FOR AUTHORIZED TESTING ONLY."""
        try:
            import requests
            test_origins = ["https://evil.com", "null", "https://attacker.example.com"]
            results = []
            for origin in test_origins:
                r = requests.get(url, headers={"Origin": origin}, timeout=10)
                acao = r.headers.get("Access-Control-Allow-Origin", "")
                acac = r.headers.get("Access-Control-Allow-Credentials", "")
                vulnerable = (acao == origin or acao == "*")
                critical = vulnerable and acac.lower() == "true"
                results.append({
                    "origin_tested": origin, "acao": acao, "credentials": acac,
                    "vulnerable": vulnerable, "critical": critical
                })
            any_vuln = any(r["vulnerable"] for r in results)
            any_crit = any(r["critical"] for r in results)
            return ToolResult(True,
                              f"{'🚨 Critical CORS' if any_crit else ('⚠ CORS vulnerable' if any_vuln else '✓ CORS OK')}",
                              {"results": results, "vulnerable": any_vuln, "critical": any_crit})
        except Exception as e:
            return ToolResult(False, f"✗ check_cors failed: {e}")

    @staticmethod
    def sql_injection_test(url: str, params: dict, method: str = "GET") -> ToolResult:
        """FOR AUTHORIZED TESTING ONLY. Error-based SQLi detection only."""
        try:
            import requests
            payloads = ["'", "''", "';--", "1' OR '1'='1", "1; SELECT 1--",
                        "' OR 1=1--", "admin'--", "' UNION SELECT NULL--"]
            sql_errors = ["sql syntax", "mysql_fetch", "unclosed quotation", "ORA-01756",
                          "SQLSyntaxErrorException", "syntax error", "unterminated string",
                          "pg_query", "Microsoft OLE DB", "ODBC SQL Server Driver"]
            findings = []
            for param, original_val in params.items():
                for payload in payloads:
                    test_params = dict(params)
                    test_params[param] = payload
                    try:
                        if method.upper() == "GET":
                            r = requests.get(url, params=test_params, timeout=8)
                        else:
                            r = requests.post(url, data=test_params, timeout=8)
                        resp_lower = r.text.lower()
                        for err in sql_errors:
                            if err.lower() in resp_lower:
                                findings.append({
                                    "param": param, "payload": payload,
                                    "error_indicator": err, "severity": "critical"
                                })
                                break
                    except Exception:
                        pass
            return ToolResult(True,
                              f"{'🚨 SQLi indicators found: ' + str(len(findings)) if findings else '✓ No SQLi indicators detected'}",
                              {"findings": findings, "payloads_tested": len(payloads) * len(params)})
        except Exception as e:
            return ToolResult(False, f"✗ sql_injection_test failed: {e}")

    @staticmethod
    def xss_test(url: str, params: dict, method: str = "GET") -> ToolResult:
        """FOR AUTHORIZED TESTING ONLY. Reflected XSS detection."""
        try:
            import requests
            payloads = [
                "<script>alert(1)</script>",
                '"><script>alert(1)</script>',
                "'><img src=x onerror=alert(1)>",
                "<svg onload=alert(1)>",
                "javascript:alert(1)",
            ]
            findings = []
            for param, _ in params.items():
                for payload in payloads:
                    test_params = dict(params)
                    test_params[param] = payload
                    try:
                        if method.upper() == "GET":
                            r = requests.get(url, params=test_params, timeout=8)
                        else:
                            r = requests.post(url, data=test_params, timeout=8)
                        if payload in r.text:
                            findings.append({
                                "param": param, "payload": payload,
                                "type": "reflected_xss", "severity": "high"
                            })
                    except Exception:
                        pass
            return ToolResult(True,
                              f"{'⚠ XSS indicators: ' + str(len(findings)) if findings else '✓ No reflected XSS detected'}",
                              {"findings": findings})
        except Exception as e:
            return ToolResult(False, f"✗ xss_test failed: {e}")

    @staticmethod
    def check_ssl_vulnerabilities(domain: str, port: int = 443) -> ToolResult:
        """FOR AUTHORIZED TESTING ONLY."""
        try:
            import ssl
            import socket
            findings = []
            # Check legacy protocols
            for proto_name, proto in [("SSLv2", None), ("SSLv3", None), ("TLSv1.0", ssl.TLSVersion.TLSv1),
                                       ("TLSv1.1", ssl.TLSVersion.TLSv1_1)]:
                try:
                    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    if proto:
                        ctx.maximum_version = proto
                        ctx.minimum_version = proto
                    with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
                        s.settimeout(5)
                        s.connect((domain, port))
                        findings.append({"type": "legacy_protocol", "protocol": proto_name,
                                         "severity": "high"})
                except Exception:
                    pass  # Protocol rejected = good
            # Check cert
            ssl_result = SecurityScannerTool.check_ssl_grade(domain)
            if ssl_result.success and ssl_result.data:
                days = ssl_result.data.get("days_until_expiry", 999)
                if days < 30:
                    findings.append({"type": "expiring_cert", "days_left": days, "severity": "medium"})
            return ToolResult(True,
                              f"{'⚠ ' + str(len(findings)) + ' SSL issues found' if findings else '✓ No critical SSL issues'}",
                              {"domain": domain, "findings": findings, "ssl_info": ssl_result.data})
        except Exception as e:
            return ToolResult(False, f"✗ check_ssl_vulnerabilities failed: {e}")

    @staticmethod
    def check_outdated_software(url: str) -> ToolResult:
        """FOR AUTHORIZED TESTING ONLY. Detect version info from headers and HTML."""
        try:
            import requests
            r = requests.get(url, timeout=10)
            findings = []
            # Header-based detection
            server = r.headers.get("Server", "")
            if server:
                findings.append({"type": "server_banner", "value": server})
            powered = r.headers.get("X-Powered-By", "")
            if powered:
                findings.append({"type": "powered_by", "value": powered})
            # HTML meta generator
            gen_match = re.search(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)["\']',
                                  r.text, re.IGNORECASE)
            if gen_match:
                findings.append({"type": "generator", "value": gen_match.group(1)})
            # WordPress detection
            if "/wp-content/" in r.text:
                findings.append({"type": "cms", "value": "WordPress detected"})
            return ToolResult(True, f"✓ {len(findings)} software indicators found", findings)
        except Exception as e:
            return ToolResult(False, f"✗ check_outdated_software failed: {e}")

    @staticmethod
    def generate_security_report(target: str, scan_results: list, output: str) -> ToolResult:
        """Generate a markdown security assessment report."""
        try:
            all_findings = []
            for result in scan_results:
                if isinstance(result, dict):
                    findings = result.get("findings", result.get("results", [result]))
                    if isinstance(findings, list):
                        all_findings.extend(findings)
            severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
            for f in all_findings:
                sev = f.get("severity", "info").lower()
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
            lines = [
                f"# Security Assessment Report",
                f"\n**Target:** {target}",
                f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                f"**Generated by:** NPM Agent / NPMAI Ecosystem\n",
                "---\n",
                "## Executive Summary\n",
                "| Severity | Count |",
                "|----------|-------|",
            ]
            for sev, count in severity_counts.items():
                lines.append(f"| {sev.capitalize()} | {count} |")
            lines += ["\n---\n", "## Findings\n"]
            for i, f in enumerate(all_findings, 1):
                sev = f.get("severity", "info").upper()
                lines.append(f"### Finding {i}: [{sev}] {f.get('type', 'Issue')}")
                for k, v in f.items():
                    if k != "type":
                        lines.append(f"- **{k.replace('_', ' ').title()}:** {v}")
                lines.append("")
            lines += ["\n---\n", "## Disclaimer\n",
                      "_This report was generated for authorized security testing only. "
                      "All findings should be remediated according to risk priority._"]
            Path(output).write_text("\n".join(lines), encoding="utf-8")
            return ToolResult(True, f"✓ Security report saved to {output}",
                              {"findings": len(all_findings), "output": output,
                               "severity_summary": severity_counts})
        except Exception as e:
            return ToolResult(False, f"✗ generate_security_report failed: {e}")

    @staticmethod
    def create_pentest_checklist(target_type: str = "web", output: str = "pentest_checklist.md") -> ToolResult:
        """target_type: web | api | network | mobile"""
        try:
            checklists = {
                "web": [
                    ("Reconnaissance", ["WHOIS lookup", "DNS enumeration", "Subdomain discovery",
                                        "Technology fingerprinting", "Google dorking"]),
                    ("Authentication", ["Default credentials", "Brute force protection", "MFA bypass",
                                        "Password complexity", "Account lockout"]),
                    ("Authorization", ["Horizontal privilege escalation", "Vertical privilege escalation",
                                       "IDOR testing", "Path traversal"]),
                    ("Injection", ["SQL injection", "Command injection", "LDAP injection",
                                   "XPath injection", "Template injection"]),
                    ("XSS", ["Reflected XSS", "Stored XSS", "DOM XSS", "CSP evaluation"]),
                    ("Business Logic", ["Parameter tampering", "Race conditions", "Workflow bypass"]),
                    ("Configuration", ["HTTP security headers", "CORS policy", "SSL/TLS config",
                                       "Error message disclosure", "Directory listing"]),
                ],
                "api": [
                    ("Discovery", ["API endpoint enumeration", "Swagger/OpenAPI exposure",
                                   "Version disclosure", "HTTP method fuzzing"]),
                    ("Authentication", ["API key exposure", "JWT vulnerabilities", "OAuth flaws"]),
                    ("Authorization", ["BOLA/IDOR", "Function-level auth", "Object property exposure"]),
                    ("Input Validation", ["Mass assignment", "Injection via API params",
                                          "File upload abuse"]),
                ],
                "network": [
                    ("Discovery", ["Host discovery", "Port scanning", "Service fingerprinting"]),
                    ("Vulnerabilities", ["Known CVEs", "Default credentials", "Unpatched services"]),
                    ("Encryption", ["Cleartext protocols", "Weak cipher suites", "Certificate validity"]),
                ],
            }
            items = checklists.get(target_type, checklists["web"])
            lines = [
                f"# Penetration Testing Checklist — {target_type.upper()}",
                f"\n**Target Type:** {target_type}",
                f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
                "\n> ⚠️ FOR AUTHORIZED TESTING ONLY\n",
                "---\n"
            ]
            for section, checks in items:
                lines.append(f"\n## {section}\n")
                for check in checks:
                    lines.append(f"- [ ] {check}")
            Path(output).write_text("\n".join(lines), encoding="utf-8")
            return ToolResult(True, f"✓ Pentest checklist saved to {output}")
        except Exception as e:
            return ToolResult(False, f"✗ create_pentest_checklist failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# 4. AIImageGenerationTool
# ═══════════════════════════════════════════════════════════════════════════
class AIImageGenerationTool:
    name = "ai_image_generation"
    description = (
        "AI image generation: Stability AI, DALL-E, local Stable Diffusion, "
        "inpainting, img2img, upscaling, background removal, variations"
    )

    @staticmethod
    def generate_image_stability(prompt: str, negative_prompt: str = "", width: int = 1024,
                                  height: int = 1024, steps: int = 30, cfg: float = 7.0,
                                  output: str = "output.png", cred_key: str = "stability") -> ToolResult:
        try:
            import requests
            api_key = CredStore.load(cred_key).get("api_key", "")
            if not api_key:
                return ToolResult(False, "No Stability API key. Save under 'stability' → {'api_key':'...'}")
            r = requests.post(
                "https://api.stability.ai/v2beta/stable-image/generate/core",
                headers={"authorization": f"Bearer {api_key}", "accept": "image/*"},
                files={"none": ""},
                data={"prompt": prompt, "negative_prompt": negative_prompt,
                      "width": width, "height": height, "steps": steps,
                      "cfg_scale": cfg, "output_format": "png"},
                timeout=60
            )
            r.raise_for_status()
            Path(output).write_bytes(r.content)
            return ToolResult(True, f"✓ Image generated: {output}", {"output": output, "size": len(r.content)})
        except Exception as e:
            return ToolResult(False, f"✗ generate_image_stability failed: {e}")

    @staticmethod
    def generate_image_dalle(prompt: str, n: int = 1, size: str = "1024x1024",
                              quality: str = "standard", style: str = "vivid",
                              output: str = "dalle_output.png", cred_key: str = "openai") -> ToolResult:
        try:
            import requests
            api_key = CredStore.load(cred_key).get("api_key", "")
            if not api_key:
                return ToolResult(False, "No OpenAI API key. Save under 'openai' → {'api_key':'...'}")
            r = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": "dall-e-3", "prompt": prompt, "n": min(n, 1),
                      "size": size, "quality": quality, "style": style},
                timeout=60
            )
            r.raise_for_status()
            url = r.json()["data"][0]["url"]
            img_r = requests.get(url, timeout=30)
            output_dir = Path(output).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            Path(output).write_bytes(img_r.content)
            return ToolResult(True, f"✓ DALL-E image saved: {output}",
                              {"output": output, "url": url, "revised_prompt": r.json()["data"][0].get("revised_prompt", "")})
        except Exception as e:
            return ToolResult(False, f"✗ generate_image_dalle failed: {e}")

    @staticmethod
    def generate_image_local_sd(prompt: str, negative_prompt: str = "", model: str = "runwayml/stable-diffusion-v1-5",
                                 width: int = 512, height: int = 512, steps: int = 20,
                                 output: str = "sd_output.png") -> ToolResult:
        try:
            _ensure("diffusers", "diffusers")
            _ensure("torch", "torch")
            from diffusers import StableDiffusionPipeline
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if device == "cuda" else torch.float32
            pipe = StableDiffusionPipeline.from_pretrained(model, torch_dtype=dtype)
            pipe = pipe.to(device)
            image = pipe(prompt, negative_prompt=negative_prompt, width=width,
                         height=height, num_inference_steps=steps).images[0]
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            image.save(output)
            return ToolResult(True, f"✓ SD image generated: {output}",
                              {"output": output, "device": device, "model": model})
        except Exception as e:
            return ToolResult(False, f"✗ generate_image_local_sd failed: {e}")

    @staticmethod
    def inpaint_image(image_path: str, mask_path: str, prompt: str, output: str = "inpainted.png",
                      cred_key: str = "stability") -> ToolResult:
        try:
            import requests
            api_key = CredStore.load(cred_key).get("api_key", "")
            if not api_key:
                return ToolResult(False, "No Stability API key.")
            with open(image_path, "rb") as img, open(mask_path, "rb") as mask:
                r = requests.post(
                    "https://api.stability.ai/v2beta/stable-image/edit/inpaint",
                    headers={"authorization": f"Bearer {api_key}", "accept": "image/*"},
                    files={"image": img, "mask": mask},
                    data={"prompt": prompt, "output_format": "png"},
                    timeout=60
                )
            r.raise_for_status()
            Path(output).write_bytes(r.content)
            return ToolResult(True, f"✓ Inpainted image saved: {output}")
        except Exception as e:
            return ToolResult(False, f"✗ inpaint_image failed: {e}")

    @staticmethod
    def img_to_img(image_path: str, prompt: str, strength: float = 0.75,
                   output: str = "img2img_output.png", cred_key: str = "stability") -> ToolResult:
        try:
            import requests
            api_key = CredStore.load(cred_key).get("api_key", "")
            if not api_key:
                return ToolResult(False, "No Stability API key.")
            with open(image_path, "rb") as img:
                r = requests.post(
                    "https://api.stability.ai/v2beta/stable-image/generate/sd3",
                    headers={"authorization": f"Bearer {api_key}", "accept": "image/*"},
                    files={"image": img},
                    data={"prompt": prompt, "strength": strength,
                          "mode": "image-to-image", "output_format": "png"},
                    timeout=60
                )
            r.raise_for_status()
            Path(output).write_bytes(r.content)
            return ToolResult(True, f"✓ img2img output saved: {output}")
        except Exception as e:
            return ToolResult(False, f"✗ img_to_img failed: {e}")

    @staticmethod
    def upscale_image_ai(image_path: str, scale: int = 2, output: str = None) -> ToolResult:
        try:
            from PIL import Image
            img = Image.open(image_path)
            new_w, new_h = img.width * scale, img.height * scale
            upscaled = img.resize((new_w, new_h), Image.LANCZOS)
            out = output or str(Path(image_path).with_stem(Path(image_path).stem + f"_x{scale}"))
            upscaled.save(out)
            return ToolResult(True, f"✓ Upscaled {scale}x: {out} ({new_w}×{new_h})")
        except Exception as e:
            return ToolResult(False, f"✗ upscale_image_ai failed: {e}")

    @staticmethod
    def remove_background_ai(image_path: str, output: str = None) -> ToolResult:
        try:
            _ensure("rembg", "rembg")
            from rembg import remove
            from PIL import Image
            import io
            img = Image.open(image_path)
            result = remove(img)
            out = output or str(Path(image_path).with_stem(Path(image_path).stem + "_nobg").with_suffix(".png"))
            result.save(out)
            return ToolResult(True, f"✓ Background removed: {out}")
        except ImportError:
            # Fallback: use Stability AI background removal
            try:
                import requests
                api_key = CredStore.load("stability").get("api_key", "")
                if not api_key:
                    return ToolResult(False, "rembg not installed and no Stability key. pip install rembg")
                with open(image_path, "rb") as f:
                    r = requests.post(
                        "https://api.stability.ai/v2beta/stable-image/edit/remove-background",
                        headers={"authorization": f"Bearer {api_key}", "accept": "image/*"},
                        files={"image": f}, data={"output_format": "png"}, timeout=30
                    )
                r.raise_for_status()
                out = output or str(Path(image_path).with_stem(Path(image_path).stem + "_nobg").with_suffix(".png"))
                Path(out).write_bytes(r.content)
                return ToolResult(True, f"✓ Background removed (Stability): {out}")
            except Exception as e:
                return ToolResult(False, f"✗ remove_background_ai failed: {e}")
        except Exception as e:
            return ToolResult(False, f"✗ remove_background_ai failed: {e}")

    @staticmethod
    def create_image_variations(image_path: str, n: int = 3, output: str = "variations",
                                cred_key: str = "openai") -> ToolResult:
        try:
            import requests
            api_key = CredStore.load(cred_key).get("api_key", "")
            if not api_key:
                return ToolResult(False, "No OpenAI API key.")
            with open(image_path, "rb") as f:
                r = requests.post(
                    "https://api.openai.com/v1/images/variations",
                    headers={"Authorization": f"Bearer {api_key}"},
                    files={"image": f},
                    data={"n": min(n, 10), "size": "1024x1024"},
                    timeout=60
                )
            r.raise_for_status()
            out_dir = Path(output)
            out_dir.mkdir(parents=True, exist_ok=True)
            saved = []
            for i, item in enumerate(r.json()["data"]):
                img_r = requests.get(item["url"], timeout=30)
                out_path = out_dir / f"variation_{i+1}.png"
                out_path.write_bytes(img_r.content)
                saved.append(str(out_path))
            return ToolResult(True, f"✓ {len(saved)} variations saved to {output}", saved)
        except Exception as e:
            return ToolResult(False, f"✗ create_image_variations failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# 5. AITextGenerationAdvancedTool
# ═══════════════════════════════════════════════════════════════════════════
class AITextGenerationAdvancedTool:
    name = "ai_text_advanced"
    description = (
        "Advanced LLM: chain prompts, few-shot, structured JSON, debate, "
        "brainstorm, critique, code gen/explain/test/refactor, translate, summarize"
    )

    @staticmethod
    def _llm(model: str = "llama3.2:3b", temperature: float = 0.7):
        from agent_core import Ollama
        return Ollama(model=model, temperature=temperature, change=True,
                      Models=["mistral:7b", "llama3.2:3b"])

    @staticmethod
    def chain_prompts(prompts: list, models: list = None, pass_previous: bool = True,
                      temperature: float = 0.7) -> ToolResult:
        try:
            results = []
            context = ""
            for i, prompt in enumerate(prompts):
                model = (models[i] if models and i < len(models) else "llama3.2:3b")
                llm = AITextGenerationAdvancedTool._llm(model, temperature)
                full_prompt = f"Previous context:\n{context}\n\n{prompt}" if pass_previous and context else prompt
                response = llm.invoke(full_prompt)
                results.append({"step": i + 1, "prompt": prompt[:100], "response": response, "model": model})
                if pass_previous:
                    context = response
            return ToolResult(True, f"✓ Chain of {len(prompts)} prompts completed", results)
        except Exception as e:
            return ToolResult(False, f"✗ chain_prompts failed: {e}")

    @staticmethod
    def few_shot_generate(examples: list, task: str, model: str = "llama3.2:3b",
                          temperature: float = 0.5, n_shots: int = 3) -> ToolResult:
        """examples: [{'input': '...', 'output': '...'}]"""
        try:
            llm = AITextGenerationAdvancedTool._llm(model, temperature)
            shots = examples[:n_shots]
            shot_text = "\n\n".join(f"Input: {s['input']}\nOutput: {s['output']}" for s in shots)
            prompt = f"Learn from these examples:\n{shot_text}\n\nNow complete:\nInput: {task}\nOutput:"
            response = llm.invoke(prompt)
            return ToolResult(True, "✓ Few-shot generation complete",
                              {"response": response, "shots_used": len(shots)})
        except Exception as e:
            return ToolResult(False, f"✗ few_shot_generate failed: {e}")

    @staticmethod
    def generate_structured_json(prompt: str, schema: dict, model: str = "llama3.2:3b",
                                  temperature: float = 0.3, retries: int = 3) -> ToolResult:
        try:
            llm = AITextGenerationAdvancedTool._llm(model, temperature)
            schema_str = json.dumps(schema, indent=2)
            full_prompt = (f"{prompt}\n\nRespond ONLY with valid JSON matching this schema:\n"
                           f"{schema_str}\n\nDo not include any explanation or markdown. Pure JSON only.")
            for attempt in range(retries):
                raw = llm.invoke(full_prompt)
                # Strip markdown fences
                cleaned = re.sub(r'```(?:json)?\s*|\s*```', '', raw).strip()
                try:
                    parsed = json.loads(cleaned)
                    return ToolResult(True, "✓ Structured JSON generated", parsed)
                except json.JSONDecodeError:
                    # Try to extract JSON object/array
                    match = re.search(r'[\[{].*[\]}]', cleaned, re.DOTALL)
                    if match:
                        try:
                            parsed = json.loads(match.group())
                            return ToolResult(True, "✓ Structured JSON extracted", parsed)
                        except Exception:
                            pass
                    if attempt == retries - 1:
                        return ToolResult(False, f"✗ Could not parse JSON after {retries} attempts",
                                          {"raw": raw})
            return ToolResult(False, "✗ generate_structured_json exhausted retries")
        except Exception as e:
            return ToolResult(False, f"✗ generate_structured_json failed: {e}")

    @staticmethod
    def debate_topic(topic: str, models: list = None, rounds: int = 2,
                     output_format: str = "text") -> ToolResult:
        try:
            model_list = models or ["llama3.2:3b", "mistral:7b"]
            transcript = []
            for round_n in range(rounds):
                for i, model in enumerate(model_list):
                    llm = AITextGenerationAdvancedTool._llm(model, 0.8)
                    side = "FOR" if i % 2 == 0 else "AGAINST"
                    context = "\n".join(f"[{t['model']}]: {t['argument']}" for t in transcript[-4:])
                    prompt = (f"Debate topic: '{topic}'\nYou are arguing {side}.\n"
                              f"Previous arguments:\n{context}\n\n"
                              f"Make your Round {round_n+1} argument in 2-3 sentences:")
                    argument = llm.invoke(prompt)
                    transcript.append({"round": round_n + 1, "side": side, "model": model,
                                       "argument": argument})
            if output_format == "json":
                return ToolResult(True, f"✓ Debate: {rounds} rounds, {len(transcript)} arguments", transcript)
            text = f"# Debate: {topic}\n\n"
            for t in transcript:
                text += f"**Round {t['round']} — {t['side']}** ({t['model']}):\n{t['argument']}\n\n"
            return ToolResult(True, f"✓ Debate complete", {"transcript": transcript, "text": text})
        except Exception as e:
            return ToolResult(False, f"✗ debate_topic failed: {e}")

    @staticmethod
    def brainstorm(topic: str, n_ideas: int = 10, perspective: str = "general",
                   model: str = "llama3.2:3b") -> ToolResult:
        try:
            llm = AITextGenerationAdvancedTool._llm(model, 0.9)
            prompt = (f"Brainstorm {n_ideas} creative ideas about: {topic}\n"
                      f"Perspective: {perspective}\n"
                      f"Format: numbered list, one idea per line, be creative and specific.")
            response = llm.invoke(prompt)
            ideas = [line.strip() for line in response.split("\n")
                     if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith("-"))]
            return ToolResult(True, f"✓ {len(ideas)} ideas generated",
                              {"ideas": ideas, "raw": response, "topic": topic})
        except Exception as e:
            return ToolResult(False, f"✗ brainstorm failed: {e}")

    @staticmethod
    def critique_and_improve(text: str, focus: str = "clarity", model: str = "llama3.2:3b",
                             iterations: int = 2) -> ToolResult:
        try:
            llm = AITextGenerationAdvancedTool._llm(model, 0.5)
            current = text
            history = []
            for i in range(iterations):
                critique_prompt = (f"Critique this text focusing on {focus}:\n\n{current}\n\n"
                                   f"List 3 specific issues:")
                critique = llm.invoke(critique_prompt)
                improve_prompt = (f"Improve this text based on these critiques:\nCritiques: {critique}\n"
                                  f"Original: {current}\n\nImproved version:")
                improved = llm.invoke(improve_prompt)
                history.append({"iteration": i+1, "critique": critique, "improved": improved})
                current = improved
            return ToolResult(True, f"✓ Text improved over {iterations} iterations",
                              {"original": text, "final": current, "history": history})
        except Exception as e:
            return ToolResult(False, f"✗ critique_and_improve failed: {e}")

    @staticmethod
    def generate_code(description: str, language: str = "python", model: str = "codellama:7b-instruct",
                      tests: bool = True, comments: bool = True) -> ToolResult:
        try:
            llm = AITextGenerationAdvancedTool._llm(model, 0.3)
            extras = []
            if comments:
                extras.append("include clear docstrings and inline comments")
            if tests:
                extras.append("include unit tests at the end")
            extra_str = "; ".join(extras)
            prompt = (f"Write {language} code for: {description}\n"
                      f"Requirements: {extra_str}\n"
                      f"Return ONLY the code, no explanation outside comments.")
            code = llm.invoke(prompt)
            # Strip markdown
            code = re.sub(r'```\w*\s*|\s*```', '', code).strip()
            return ToolResult(True, f"✓ {language} code generated",
                              {"code": code, "language": language, "description": description})
        except Exception as e:
            return ToolResult(False, f"✗ generate_code failed: {e}")

    @staticmethod
    def explain_code(code: str, level: str = "intermediate", model: str = "llama3.2:3b") -> ToolResult:
        """level: beginner | intermediate | expert"""
        try:
            llm = AITextGenerationAdvancedTool._llm(model, 0.4)
            level_prompts = {
                "beginner": "Explain this code for a complete beginner. Use simple analogies.",
                "intermediate": "Explain this code for an intermediate developer. Cover logic and patterns.",
                "expert": "Analyze this code technically. Cover algorithms, complexity, and design patterns."
            }
            prompt = f"{level_prompts.get(level, level_prompts['intermediate'])}\n\n```\n{code}\n```"
            explanation = llm.invoke(prompt)
            return ToolResult(True, "✓ Code explained", {"explanation": explanation, "level": level})
        except Exception as e:
            return ToolResult(False, f"✗ explain_code failed: {e}")

    @staticmethod
    def generate_test_cases(code: str, framework: str = "pytest", model: str = "codellama:7b-instruct") -> ToolResult:
        try:
            llm = AITextGenerationAdvancedTool._llm(model, 0.3)
            prompt = (f"Write comprehensive {framework} test cases for this code.\n"
                      f"Include edge cases, happy path, and error cases.\n"
                      f"Return ONLY the test code.\n\n```\n{code}\n```")
            tests = llm.invoke(prompt)
            tests = re.sub(r'```\w*\s*|\s*```', '', tests).strip()
            return ToolResult(True, f"✓ {framework} tests generated", {"tests": tests, "framework": framework})
        except Exception as e:
            return ToolResult(False, f"✗ generate_test_cases failed: {e}")

    @staticmethod
    def refactor_code(code: str, goals: list = None, model: str = "codellama:7b-instruct") -> ToolResult:
        try:
            llm = AITextGenerationAdvancedTool._llm(model, 0.2)
            goal_str = ", ".join(goals or ["readability", "performance", "DRY principles"])
            prompt = (f"Refactor this code for: {goal_str}\n"
                      f"Preserve all functionality. Return ONLY the refactored code.\n\n"
                      f"```\n{code}\n```")
            refactored = llm.invoke(prompt)
            refactored = re.sub(r'```\w*\s*|\s*```', '', refactored).strip()
            return ToolResult(True, "✓ Code refactored",
                              {"refactored": refactored, "original": code, "goals": goals})
        except Exception as e:
            return ToolResult(False, f"✗ refactor_code failed: {e}")

    @staticmethod
    def translate_text(text: str, target_language: str, style: str = "natural",
                       model: str = "llama3.2:3b") -> ToolResult:
        try:
            llm = AITextGenerationAdvancedTool._llm(model, 0.4)
            style_instructions = {
                "natural": "Use natural, fluent language",
                "formal": "Use formal, professional language",
                "casual": "Use casual, conversational language",
                "literal": "Translate as literally as possible"
            }
            style_note = style_instructions.get(style, style)
            prompt = (f"Translate the following text to {target_language}. {style_note}.\n"
                      f"Return ONLY the translation, no explanation.\n\n{text}")
            translation = llm.invoke(prompt)
            return ToolResult(True, f"✓ Translated to {target_language}",
                              {"translation": translation, "original": text,
                               "target_language": target_language})
        except Exception as e:
            return ToolResult(False, f"✗ translate_text failed: {e}")

    @staticmethod
    def summarize_long_document(path: str, model: str = "llama3.2:3b",
                                 chunk_size: int = 3000) -> ToolResult:
        try:
            from agent_core import Ollama
            if path.endswith(".pdf"):
                from pypdf import PdfReader
                text = "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
            else:
                text = Path(path).read_text(errors="replace")
            if not text.strip():
                return ToolResult(False, "✗ Document is empty")
            llm = Ollama(model=model, temperature=0.2, change=True, Models=["mistral:7b"])
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
            chunk_summaries = []
            for i, chunk in enumerate(chunks[:15]):
                summary = llm.invoke(f"Summarize this section briefly (2-3 sentences):\n{chunk}")
                chunk_summaries.append(summary)
            combined = "\n\n".join(chunk_summaries)
            final_summary = llm.invoke(
                f"Create a comprehensive final summary from these {len(chunk_summaries)} section summaries:\n{combined}"
            )
            return ToolResult(True, "✓ Document summarized",
                              {"summary": final_summary, "chunks_processed": len(chunks),
                               "total_chars": len(text)})
        except Exception as e:
            return ToolResult(False, f"✗ summarize_long_document failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# 6. MLModelTool
# ═══════════════════════════════════════════════════════════════════════════
class MLModelTool:
    name = "ml_model"
    description = (
        "ML operations: train classifier/regressor, predict, evaluate, "
        "feature importance, cross-validate, hyperparameter tune, "
        "save/load, serve API, explain predictions"
    )

    @staticmethod
    def _get_model(model_type: str, task: str = "classifier"):
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
        from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
        from sklearn.svm import SVC, SVR
        from sklearn.tree import DecisionTreeClassifier
        classifier_map = {
            "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
            "gradient_boosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
            "logistic_regression": LogisticRegression(max_iter=1000, random_state=42),
            "svm": SVC(probability=True, random_state=42),
            "decision_tree": DecisionTreeClassifier(random_state=42),
        }
        regressor_map = {
            "random_forest": RandomForestRegressor(n_estimators=100, random_state=42),
            "linear_regression": LinearRegression(),
            "ridge": Ridge(),
            "svr": SVR(),
        }
        if task == "regressor":
            return regressor_map.get(model_type, regressor_map["random_forest"])
        return classifier_map.get(model_type, classifier_map["random_forest"])

    @staticmethod
    def train_classifier(data_path: str, target_col: str, model_type: str = "random_forest",
                         test_size: float = 0.2, output_model: str = "classifier.joblib") -> ToolResult:
        try:
            import pandas as pd
            import joblib
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import classification_report, accuracy_score
            from sklearn.preprocessing import LabelEncoder
            df = pd.read_csv(data_path) if data_path.endswith(".csv") else pd.read_excel(data_path)
            X = df.drop(columns=[target_col])
            y = df[target_col]
            # Encode categorical columns
            for col in X.select_dtypes(include=["object"]).columns:
                X[col] = LabelEncoder().fit_transform(X[col].astype(str))
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
            model = MLModelTool._get_model(model_type, "classifier")
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred, output_dict=True)
            joblib.dump({"model": model, "features": list(X.columns), "target": target_col,
                         "model_type": model_type, "accuracy": acc}, output_model)
            return ToolResult(True, f"✓ Classifier trained. Accuracy: {acc:.4f}",
                              {"accuracy": acc, "report": report, "model_path": output_model,
                               "features": list(X.columns), "n_samples": len(df)})
        except Exception as e:
            return ToolResult(False, f"✗ train_classifier failed: {e}")

    @staticmethod
    def train_regressor(data_path: str, target_col: str, model_type: str = "random_forest",
                        test_size: float = 0.2, output_model: str = "regressor.joblib") -> ToolResult:
        try:
            import pandas as pd
            import joblib
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_squared_error, r2_score
            import numpy as np
            df = pd.read_csv(data_path) if data_path.endswith(".csv") else pd.read_excel(data_path)
            X = df.drop(columns=[target_col])
            y = df[target_col]
            for col in X.select_dtypes(include=["object"]).columns:
                from sklearn.preprocessing import LabelEncoder
                X[col] = LabelEncoder().fit_transform(X[col].astype(str))
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
            model = MLModelTool._get_model(model_type, "regressor")
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            joblib.dump({"model": model, "features": list(X.columns), "target": target_col,
                         "model_type": model_type, "r2": r2, "rmse": rmse}, output_model)
            return ToolResult(True, f"✓ Regressor trained. R²: {r2:.4f}, RMSE: {rmse:.4f}",
                              {"r2": r2, "rmse": rmse, "model_path": output_model})
        except Exception as e:
            return ToolResult(False, f"✗ train_regressor failed: {e}")

    @staticmethod
    def predict(model_path: str, input_data: Any) -> ToolResult:
        try:
            import joblib
            import pandas as pd
            saved = joblib.load(model_path)
            model = saved["model"]
            features = saved.get("features", [])
            if isinstance(input_data, dict):
                df = pd.DataFrame([input_data])
            elif isinstance(input_data, list):
                df = pd.DataFrame(input_data)
            else:
                df = input_data
            if features:
                df = df.reindex(columns=features, fill_value=0)
            predictions = model.predict(df).tolist()
            proba = None
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(df).tolist()
            return ToolResult(True, f"✓ Predicted {len(predictions)} sample(s)",
                              {"predictions": predictions, "probabilities": proba})
        except Exception as e:
            return ToolResult(False, f"✗ predict failed: {e}")

    @staticmethod
    def evaluate_model(model_path: str, test_data: str, target_col: str) -> ToolResult:
        try:
            import joblib, pandas as pd, numpy as np
            from sklearn.metrics import (classification_report, accuracy_score,
                                          mean_squared_error, r2_score)
            saved = joblib.load(model_path)
            model, features = saved["model"], saved.get("features", [])
            df = pd.read_csv(test_data)
            X = df.drop(columns=[target_col]).reindex(columns=features, fill_value=0)
            y = df[target_col]
            y_pred = model.predict(X)
            if hasattr(model, "predict_proba"):
                acc = accuracy_score(y, y_pred)
                report = classification_report(y, y_pred, output_dict=True)
                return ToolResult(True, f"✓ Accuracy: {acc:.4f}", {"accuracy": acc, "report": report})
            else:
                rmse = np.sqrt(mean_squared_error(y, y_pred))
                r2 = r2_score(y, y_pred)
                return ToolResult(True, f"✓ R²: {r2:.4f}, RMSE: {rmse:.4f}",
                                  {"r2": r2, "rmse": rmse})
        except Exception as e:
            return ToolResult(False, f"✗ evaluate_model failed: {e}")

    @staticmethod
    def feature_importance(model_path: str, feature_names: list = None,
                           output: str = None) -> ToolResult:
        try:
            import joblib, json
            saved = joblib.load(model_path)
            model = saved["model"]
            names = feature_names or saved.get("features", [])
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_.tolist()
                ranked = sorted(zip(names, importances), key=lambda x: x[1], reverse=True)
                result = [{"feature": f, "importance": round(v, 6)} for f, v in ranked]
                if output:
                    Path(output).write_text(json.dumps(result, indent=2))
                return ToolResult(True, f"✓ Feature importances computed", result)
            elif hasattr(model, "coef_"):
                coefs = model.coef_.flatten().tolist()
                result = [{"feature": names[i] if i < len(names) else f"f{i}",
                           "coefficient": round(c, 6)} for i, c in enumerate(coefs)]
                return ToolResult(True, "✓ Coefficients computed", result)
            return ToolResult(False, "✗ Model does not support feature importance")
        except Exception as e:
            return ToolResult(False, f"✗ feature_importance failed: {e}")

    @staticmethod
    def cross_validate(data_path: str, target: str, model_type: str = "random_forest",
                       folds: int = 5) -> ToolResult:
        try:
            import pandas as pd
            from sklearn.model_selection import cross_val_score
            from sklearn.preprocessing import LabelEncoder
            import numpy as np
            df = pd.read_csv(data_path)
            X = df.drop(columns=[target])
            y = df[target]
            for col in X.select_dtypes(include=["object"]).columns:
                X[col] = LabelEncoder().fit_transform(X[col].astype(str))
            is_classifier = y.dtype == object or y.nunique() < 20
            model = MLModelTool._get_model(model_type, "classifier" if is_classifier else "regressor")
            scoring = "accuracy" if is_classifier else "r2"
            scores = cross_val_score(model, X, y, cv=folds, scoring=scoring)
            return ToolResult(True, f"✓ CV {folds}-fold: {scores.mean():.4f} ± {scores.std():.4f}",
                              {"scores": scores.tolist(), "mean": float(scores.mean()),
                               "std": float(scores.std()), "metric": scoring})
        except Exception as e:
            return ToolResult(False, f"✗ cross_validate failed: {e}")

    @staticmethod
    def hyperparameter_tune(data_path: str, target: str, model_type: str = "random_forest",
                            param_grid: dict = None, cv: int = 3) -> ToolResult:
        try:
            import pandas as pd
            from sklearn.model_selection import GridSearchCV, train_test_split
            from sklearn.preprocessing import LabelEncoder
            default_grids = {
                "random_forest": {"n_estimators": [50, 100, 200], "max_depth": [None, 5, 10]},
                "gradient_boosting": {"n_estimators": [50, 100], "learning_rate": [0.05, 0.1, 0.2]},
                "logistic_regression": {"C": [0.1, 1.0, 10.0]},
            }
            df = pd.read_csv(data_path)
            X = df.drop(columns=[target])
            y = df[target]
            for col in X.select_dtypes(include=["object"]).columns:
                X[col] = LabelEncoder().fit_transform(X[col].astype(str))
            model = MLModelTool._get_model(model_type)
            grid = param_grid or default_grids.get(model_type, {"n_estimators": [50, 100]})
            gs = GridSearchCV(model, grid, cv=cv, scoring="accuracy", n_jobs=-1)
            gs.fit(X, y)
            return ToolResult(True, f"✓ Best score: {gs.best_score_:.4f}",
                              {"best_params": gs.best_params_, "best_score": gs.best_score_,
                               "cv_results": {k: v.tolist() if hasattr(v, 'tolist') else v
                                              for k, v in gs.cv_results_.items()
                                              if k in ("mean_test_score", "std_test_score", "params")}})
        except Exception as e:
            return ToolResult(False, f"✗ hyperparameter_tune failed: {e}")

    @staticmethod
    def save_model(model: Any, output_path: str, format: str = "joblib") -> ToolResult:
        try:
            if format == "joblib":
                import joblib
                joblib.dump(model, output_path)
            elif format == "pickle":
                import pickle
                with open(output_path, "wb") as f:
                    pickle.dump(model, f)
            return ToolResult(True, f"✓ Model saved to {output_path}")
        except Exception as e:
            return ToolResult(False, f"✗ save_model failed: {e}")

    @staticmethod
    def load_and_predict(model_path: str, data: Any) -> ToolResult:
        return MLModelTool.predict(model_path, data)

    @staticmethod
    def deploy_model_api(model_path: str, host: str = "0.0.0.0", port: int = 5000,
                         endpoint: str = "/predict") -> ToolResult:
        """Starts a Flask prediction API in a background thread."""
        try:
            import joblib
            from flask import Flask, request, jsonify
            saved = joblib.load(model_path)
            model = saved["model"]
            features = saved.get("features", [])
            app = Flask("NPMAgentModelAPI")

            @app.route(endpoint, methods=["POST"])
            def predict_endpoint():
                import pandas as pd
                data = request.get_json()
                df = pd.DataFrame([data] if isinstance(data, dict) else data)
                if features:
                    df = df.reindex(columns=features, fill_value=0)
                preds = model.predict(df).tolist()
                proba = model.predict_proba(df).tolist() if hasattr(model, "predict_proba") else None
                return jsonify({"predictions": preds, "probabilities": proba})

            @app.route("/health", methods=["GET"])
            def health():
                return jsonify({"status": "ok", "model": model_path})

            thread = threading.Thread(target=lambda: app.run(host=host, port=port, debug=False), daemon=True)
            thread.start()
            time.sleep(1)
            return ToolResult(True, f"✓ Model API running at http://{host}:{port}{endpoint}",
                              {"host": host, "port": port, "endpoint": endpoint})
        except Exception as e:
            return ToolResult(False, f"✗ deploy_model_api failed: {e}")

    @staticmethod
    def explain_prediction(model_path: str, instance: dict, method: str = "feature_importance") -> ToolResult:
        try:
            import joblib, pandas as pd
            saved = joblib.load(model_path)
            model, features = saved["model"], saved.get("features", [])
            df = pd.DataFrame([instance]).reindex(columns=features, fill_value=0)
            prediction = model.predict(df)[0]
            if method == "shap":
                _ensure("shap", "shap")
                import shap
                explainer = shap.TreeExplainer(model)
                shap_values = explainer.shap_values(df)
                vals = shap_values[0] if isinstance(shap_values, list) else shap_values[0]
                explanation = [{"feature": features[i], "shap_value": float(vals[i])}
                               for i in range(len(features))]
                explanation.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
                return ToolResult(True, f"✓ SHAP explanation for prediction: {prediction}",
                                  {"prediction": str(prediction), "shap_values": explanation})
            # Feature-importance-based explanation
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_
                feat_contributions = [
                    {"feature": features[i], "importance": float(importances[i]),
                     "value": float(df.iloc[0, i])}
                    for i in range(len(features))
                ]
                feat_contributions.sort(key=lambda x: x["importance"], reverse=True)
                return ToolResult(True, f"✓ Prediction: {prediction}",
                                  {"prediction": str(prediction), "top_features": feat_contributions[:10]})
            return ToolResult(True, f"✓ Prediction: {prediction}", {"prediction": str(prediction)})
        except Exception as e:
            return ToolResult(False, f"✗ explain_prediction failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# 7. SpeechAITool
# ═══════════════════════════════════════════════════════════════════════════
class SpeechAITool:
    name = "speech_ai"
    description = (
        "Speech AI: real-time transcription, file transcription, "
        "speaker diarization, VAD, voice cloning (ElevenLabs), "
        "real-time translation, command recognition, keyword detection"
    )

    @staticmethod
    def transcribe_realtime(duration: int = 10, language: str = "en",
                            model_size: str = "base", output: str = None) -> ToolResult:
        try:
            _ensure("openai-whisper", "whisper")
            _ensure("sounddevice", "sounddevice")
            _ensure("numpy", "numpy")
            import sounddevice as sd
            import numpy as np
            import whisper
            sr = 16000
            audio = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype="float32")
            sd.wait()
            model = whisper.load_model(model_size)
            audio_flat = audio.flatten()
            result = model.transcribe(audio_flat, language=language)
            text = result["text"].strip()
            if output:
                Path(output).write_text(text, encoding="utf-8")
            return ToolResult(True, f"✓ Transcribed {duration}s of audio", {"text": text, "language": language})
        except Exception as e:
            return ToolResult(False, f"✗ transcribe_realtime failed: {e}")

    @staticmethod
    def transcribe_file(audio_path: str, language: str = "en", model_size: str = "base",
                        word_timestamps: bool = False, output: str = None) -> ToolResult:
        try:
            _ensure("openai-whisper", "whisper")
            import whisper
            model = whisper.load_model(model_size)
            result = model.transcribe(audio_path, language=language, word_timestamps=word_timestamps)
            text = result["text"].strip()
            segments = result.get("segments", [])
            if output:
                if output.endswith(".srt"):
                    srt_lines = []
                    for i, seg in enumerate(segments, 1):
                        start = timedelta(seconds=seg["start"])
                        end = timedelta(seconds=seg["end"])
                        srt_lines.extend([str(i), f"{_fmt_srt(start)} --> {_fmt_srt(end)}",
                                          seg["text"].strip(), ""])
                    Path(output).write_text("\n".join(srt_lines), encoding="utf-8")
                else:
                    Path(output).write_text(text, encoding="utf-8")
            return ToolResult(True, f"✓ Transcribed: {len(text)} chars",
                              {"text": text, "segments": segments, "language": language})
        except Exception as e:
            return ToolResult(False, f"✗ transcribe_file failed: {e}")

    @staticmethod
    def speaker_diarization(audio_path: str, n_speakers: int = 2, output: str = None) -> ToolResult:
        try:
            _ensure("pyannote.audio", "pyannote")
            from pyannote.audio import Pipeline
            hf_token = CredStore.load("huggingface").get("token", "")
            pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization",
                                                use_auth_token=hf_token if hf_token else True)
            diarization = pipeline(audio_path, num_speakers=n_speakers)
            turns = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                turns.append({"speaker": speaker, "start": round(turn.start, 2), "end": round(turn.end, 2)})
            if output:
                Path(output).write_text(json.dumps(turns, indent=2), encoding="utf-8")
            return ToolResult(True, f"✓ {len(turns)} speech segments identified", turns)
        except ImportError:
            return ToolResult(False, "✗ pyannote.audio not installed. pip install pyannote.audio")
        except Exception as e:
            return ToolResult(False, f"✗ speaker_diarization failed: {e}")

    @staticmethod
    def voice_activity_detection(audio_path: str, threshold: float = 0.5,
                                  output: str = None) -> ToolResult:
        try:
            _ensure("openai-whisper", "whisper")
            import whisper
            model = whisper.load_model("tiny")
            result = model.transcribe(audio_path)
            segments = result.get("segments", [])
            vad = [{"start": round(s["start"], 2), "end": round(s["end"], 2),
                    "speech": True, "confidence": 1.0} for s in segments]
            if output:
                Path(output).write_text(json.dumps(vad, indent=2), encoding="utf-8")
            return ToolResult(True, f"✓ VAD: {len(vad)} speech segments detected", vad)
        except Exception as e:
            return ToolResult(False, f"✗ voice_activity_detection failed: {e}")

    @staticmethod
    def clone_and_speak(voice_sample: str, text: str, output: str = "cloned_voice.mp3",
                        cred_key: str = "elevenlabs") -> ToolResult:
        try:
            import requests
            api_key = CredStore.load(cred_key).get("api_key", "")
            if not api_key:
                return ToolResult(False, "No ElevenLabs API key. Save under 'elevenlabs' → {'api_key':'...'}")
            # Add voice via instant voice cloning
            with open(voice_sample, "rb") as f:
                add_r = requests.post(
                    "https://api.elevenlabs.io/v1/voices/add",
                    headers={"xi-api-key": api_key},
                    files={"files": (Path(voice_sample).name, f, "audio/mpeg")},
                    data={"name": f"clone_{int(time.time())}", "description": "NPM Agent voice clone"},
                    timeout=60
                )
            add_r.raise_for_status()
            voice_id = add_r.json()["voice_id"]
            # Generate speech
            tts_r = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={"xi-api-key": api_key, "Content-Type": "application/json"},
                json={"text": text, "model_id": "eleven_multilingual_v2",
                      "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}},
                timeout=30
            )
            tts_r.raise_for_status()
            Path(output).write_bytes(tts_r.content)
            return ToolResult(True, f"✓ Cloned voice speech saved: {output}",
                              {"voice_id": voice_id, "output": output})
        except Exception as e:
            return ToolResult(False, f"✗ clone_and_speak failed: {e}")

    @staticmethod
    def real_time_translation(source_language: str = "en", target_language: str = "es",
                              duration: int = 10, output: str = None) -> ToolResult:
        try:
            transcription_result = SpeechAITool.transcribe_realtime(
                duration=duration, language=source_language
            )
            if not transcription_result.success:
                return transcription_result
            text = transcription_result.data.get("text", "")
            translation_result = AITextGenerationAdvancedTool.translate_text(
                text, target_language, "natural"
            )
            if output and translation_result.success:
                Path(output).write_text(
                    f"[{source_language}]: {text}\n[{target_language}]: {translation_result.data['translation']}",
                    encoding="utf-8"
                )
            return ToolResult(True, "✓ Real-time translation complete",
                              {"original": text, "translation": translation_result.data.get("translation", ""),
                               "source": source_language, "target": target_language})
        except Exception as e:
            return ToolResult(False, f"✗ real_time_translation failed: {e}")

    @staticmethod
    def command_recognition(commands: list, action_map: dict, duration: int = 5) -> ToolResult:
        """commands: ['open browser', 'quit'], action_map: {'open browser': callable}"""
        try:
            result = SpeechAITool.transcribe_realtime(duration=duration)
            if not result.success:
                return result
            spoken = result.data.get("text", "").lower().strip()
            matched_command = None
            for cmd in commands:
                if cmd.lower() in spoken:
                    matched_command = cmd
                    action = action_map.get(cmd)
                    if callable(action):
                        action()
                    break
            return ToolResult(True, f"✓ Heard: '{spoken}'",
                              {"heard": spoken, "matched_command": matched_command,
                               "action_executed": matched_command is not None})
        except Exception as e:
            return ToolResult(False, f"✗ command_recognition failed: {e}")

    @staticmethod
    def keyword_detection(keywords: list, duration: int = 30, callback: Callable = None) -> ToolResult:
        """Listen for keywords and trigger callback when detected."""
        try:
            detected = []

            def _listen_loop():
                end_time = time.time() + duration
                while time.time() < end_time:
                    result = SpeechAITool.transcribe_realtime(duration=3)
                    if result.success:
                        spoken = result.data.get("text", "").lower()
                        for kw in keywords:
                            if kw.lower() in spoken:
                                detected.append({"keyword": kw, "time": datetime.now().isoformat(),
                                                 "context": spoken})
                                if callback:
                                    callback(kw, spoken)

            t = threading.Thread(target=_listen_loop, daemon=True)
            t.start()
            t.join(timeout=duration + 5)
            return ToolResult(True, f"✓ Keyword detection complete. {len(detected)} detections",
                              {"detections": detected, "keywords": keywords, "duration": duration})
        except Exception as e:
            return ToolResult(False, f"✗ keyword_detection failed: {e}")


def _fmt_srt(td: timedelta) -> str:
    """Format timedelta for SRT subtitle format."""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    ms = int(td.microseconds / 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"


# ═══════════════════════════════════════════════════════════════════════════
# 8. ComputerVisionTool
# ═══════════════════════════════════════════════════════════════════════════
class ComputerVisionTool:
    name = "computer_vision"
    description = (
        "CV: object detection/tracking (YOLO), face recognition, emotions, "
        "OCR, table extraction, QR/barcode scan, styled QR, image classify, "
        "face compare, object count, segmentation, measurements, PDF OCR"
    )

    @staticmethod
    def detect_objects(image_path: str, model: str = "yolov8n.pt",
                       confidence: float = 0.5, output: str = None) -> ToolResult:
        try:
            _ensure("ultralytics", "ultralytics")
            from ultralytics import YOLO
            yolo = YOLO(model)
            results = yolo(image_path, conf=confidence)
            detections = []
            for r in results:
                for box in r.boxes:
                    detections.append({
                        "class": r.names[int(box.cls)],
                        "confidence": round(float(box.conf), 3),
                        "bbox": [round(x, 1) for x in box.xyxy[0].tolist()]
                    })
                if output:
                    r.save(filename=output)
            return ToolResult(True, f"✓ Detected {len(detections)} objects", detections)
        except Exception as e:
            return ToolResult(False, f"✗ detect_objects failed: {e}")

    @staticmethod
    def track_objects(video_path: str, model: str = "yolov8n.pt", output: str = None) -> ToolResult:
        try:
            _ensure("ultralytics", "ultralytics")
            from ultralytics import YOLO
            yolo = YOLO(model)
            results = yolo.track(source=video_path, save=bool(output), project=str(Path(output).parent) if output else ".",
                                  name=Path(output).stem if output else "track")
            all_tracks = []
            for r in results:
                if r.boxes.id is not None:
                    for tid, cls, conf in zip(r.boxes.id.tolist(), r.boxes.cls.tolist(), r.boxes.conf.tolist()):
                        all_tracks.append({"track_id": int(tid), "class": r.names[int(cls)],
                                           "confidence": round(float(conf), 3)})
            unique_ids = len(set(t["track_id"] for t in all_tracks))
            return ToolResult(True, f"✓ Tracked {unique_ids} unique objects",
                              {"unique_objects": unique_ids, "total_detections": len(all_tracks)})
        except Exception as e:
            return ToolResult(False, f"✗ track_objects failed: {e}")

    @staticmethod
    def recognize_faces(image_path: str, known_faces_folder: str = None,
                        output: str = None) -> ToolResult:
        try:
            _ensure("face-recognition", "face_recognition")
            import face_recognition, cv2
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            results = []
            known_encodings, known_names = [], []
            if known_faces_folder and Path(known_faces_folder).exists():
                for img_file in Path(known_faces_folder).glob("*.*"):
                    try:
                        known_img = face_recognition.load_image_file(str(img_file))
                        encs = face_recognition.face_encodings(known_img)
                        if encs:
                            known_encodings.append(encs[0])
                            known_names.append(img_file.stem)
                    except Exception:
                        pass
            for loc, enc in zip(face_locations, face_encodings):
                name = "Unknown"
                if known_encodings:
                    matches = face_recognition.compare_faces(known_encodings, enc, tolerance=0.6)
                    distances = face_recognition.face_distance(known_encodings, enc)
                    if any(matches):
                        best = int(distances.argmin())
                        if matches[best]:
                            name = known_names[best]
                results.append({"name": name, "location": {"top": loc[0], "right": loc[1],
                                                              "bottom": loc[2], "left": loc[3]}})
            if output:
                img_cv = cv2.imread(image_path)
                for r in results:
                    loc = r["location"]
                    cv2.rectangle(img_cv, (loc["left"], loc["top"]), (loc["right"], loc["bottom"]), (0, 255, 0), 2)
                    cv2.putText(img_cv, r["name"], (loc["left"], loc["top"] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                cv2.imwrite(output, img_cv)
            return ToolResult(True, f"✓ Found {len(results)} face(s)", results)
        except ImportError:
            return ToolResult(False, "✗ face-recognition not installed. pip install face-recognition")
        except Exception as e:
            return ToolResult(False, f"✗ recognize_faces failed: {e}")

    @staticmethod
    def detect_emotions(image_path: str, output: str = None) -> ToolResult:
        try:
            _ensure("deepface", "deepface")
            from deepface import DeepFace
            analysis = DeepFace.analyze(img_path=image_path, actions=["emotion"],
                                         enforce_detection=False)
            results = []
            for face in (analysis if isinstance(analysis, list) else [analysis]):
                results.append({
                    "dominant_emotion": face.get("dominant_emotion", ""),
                    "emotions": face.get("emotion", {}),
                    "region": face.get("region", {})
                })
            return ToolResult(True, f"✓ Emotion detected: {results[0]['dominant_emotion'] if results else 'none'}",
                              results)
        except ImportError:
            return ToolResult(False, "✗ deepface not installed. pip install deepface")
        except Exception as e:
            return ToolResult(False, f"✗ detect_emotions failed: {e}")

    @staticmethod
    def read_text_ocr(image_path: str, language: str = "eng", output: str = None) -> ToolResult:
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang=language)
            if output:
                Path(output).write_text(text, encoding="utf-8")
            return ToolResult(True, f"✓ OCR: {len(text)} chars", {"text": text})
        except Exception as e:
            return ToolResult(False, f"✗ read_text_ocr failed: {e}")

    @staticmethod
    def read_table_from_image(image_path: str, output_csv: str = None) -> ToolResult:
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(image_path)
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            # Group text by lines using block/line numbers
            lines: dict = {}
            for i, text in enumerate(data["text"]):
                if not text.strip():
                    continue
                key = (data["block_num"][i], data["line_num"][i])
                lines.setdefault(key, []).append(text)
            rows = [" | ".join(words) for words in lines.values()]
            if output_csv:
                with open(output_csv, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    for row in rows:
                        writer.writerow(row.split(" | "))
            return ToolResult(True, f"✓ Extracted {len(rows)} table rows",
                              {"rows": rows, "raw_count": len(rows)})
        except Exception as e:
            return ToolResult(False, f"✗ read_table_from_image failed: {e}")

    @staticmethod
    def scan_qr_barcode(image_path: str) -> ToolResult:
        try:
            from pyzbar.pyzbar import decode
            from PIL import Image
            img = Image.open(image_path)
            codes = decode(img)
            results = [{"type": c.type, "data": c.data.decode("utf-8", errors="replace"),
                        "rect": {"left": c.rect.left, "top": c.rect.top,
                                 "width": c.rect.width, "height": c.rect.height}}
                       for c in codes]
            return ToolResult(True if results else False,
                              f"✓ Found {len(results)} code(s)" if results else "✗ No codes found",
                              results)
        except Exception as e:
            return ToolResult(False, f"✗ scan_qr_barcode failed: {e}")

    @staticmethod
    def generate_qr_with_style(data: str, output: str = "styled_qr.png",
                               style: str = "rounded", color: str = "#000000",
                               logo: str = None) -> ToolResult:
        try:
            import qrcode
            from qrcode.image.styledpil import StyledPilImage
            from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, SquareModuleDrawer
            from qrcode.image.styles.colormasks import SolidFillColorMask
            from PIL import Image
            drawer = RoundedModuleDrawer() if style == "rounded" else SquareModuleDrawer()
            # Parse hex color
            color_rgb = tuple(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
            qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(image_factory=StyledPilImage, module_drawer=drawer,
                                color_mask=SolidFillColorMask(front_color=color_rgb))
            if logo and Path(logo).exists():
                logo_img = Image.open(logo).convert("RGBA")
                base = img.convert("RGBA")
                qr_size = base.size[0]
                logo_size = qr_size // 4
                logo_img = logo_img.resize((logo_size, logo_size), Image.LANCZOS)
                pos = ((qr_size - logo_size) // 2, (qr_size - logo_size) // 2)
                base.paste(logo_img, pos, logo_img)
                base.save(output)
            else:
                img.save(output)
            return ToolResult(True, f"✓ Styled QR code saved: {output}")
        except Exception as e:
            return ToolResult(False, f"✗ generate_qr_with_style failed: {e}")

    @staticmethod
    def classify_image(image_path: str, model: str = "yolov8n-cls.pt", top_k: int = 5) -> ToolResult:
        try:
            _ensure("ultralytics", "ultralytics")
            from ultralytics import YOLO
            clf = YOLO(model)
            results = clf(image_path)
            classifications = []
            for r in results:
                probs = r.probs
                top_indices = probs.top5 if top_k >= 5 else list(range(min(top_k, len(probs.data))))
                for idx in top_indices[:top_k]:
                    classifications.append({
                        "class": r.names[idx],
                        "confidence": round(float(probs.data[idx]), 4)
                    })
            return ToolResult(True, f"✓ Top-{top_k} classes: {classifications[0]['class'] if classifications else 'none'}",
                              classifications)
        except Exception as e:
            return ToolResult(False, f"✗ classify_image failed: {e}")

    @staticmethod
    def compare_faces(image1: str, image2: str) -> ToolResult:
        try:
            _ensure("face-recognition", "face_recognition")
            import face_recognition
            img1 = face_recognition.load_image_file(image1)
            img2 = face_recognition.load_image_file(image2)
            enc1 = face_recognition.face_encodings(img1)
            enc2 = face_recognition.face_encodings(img2)
            if not enc1 or not enc2:
                return ToolResult(False, "✗ Face not detected in one or both images")
            distance = float(face_recognition.face_distance([enc1[0]], enc2[0])[0])
            match = distance < 0.6
            similarity = round((1 - distance) * 100, 1)
            return ToolResult(True, f"✓ Faces {'match' if match else 'do not match'} ({similarity}% similar)",
                              {"match": match, "similarity_percent": similarity, "distance": distance})
        except ImportError:
            return ToolResult(False, "✗ face-recognition not installed.")
        except Exception as e:
            return ToolResult(False, f"✗ compare_faces failed: {e}")

    @staticmethod
    def count_objects(image_path: str, object_class: str, model: str = "yolov8n.pt") -> ToolResult:
        try:
            result = ComputerVisionTool.detect_objects(image_path, model=model)
            if not result.success:
                return result
            count = sum(1 for d in (result.data or []) if d.get("class", "").lower() == object_class.lower())
            return ToolResult(True, f"✓ Counted {count} '{object_class}' in image",
                              {"count": count, "class": object_class, "all_detections": result.data})
        except Exception as e:
            return ToolResult(False, f"✗ count_objects failed: {e}")

    @staticmethod
    def segment_image(image_path: str, model: str = "yolov8n-seg.pt", output: str = None) -> ToolResult:
        try:
            _ensure("ultralytics", "ultralytics")
            from ultralytics import YOLO
            seg = YOLO(model)
            results = seg(image_path)
            segments = []
            for r in results:
                if r.masks is not None:
                    for i, (cls, conf) in enumerate(zip(r.boxes.cls, r.boxes.conf)):
                        segments.append({"class": r.names[int(cls)], "confidence": round(float(conf), 3)})
                if output:
                    r.save(filename=output)
            return ToolResult(True, f"✓ Segmented {len(segments)} objects", segments)
        except Exception as e:
            return ToolResult(False, f"✗ segment_image failed: {e}")

    @staticmethod
    def measure_object(image_path: str, reference_object_size: float) -> ToolResult:
        """Estimate object sizes using a known reference object (in real-world units)."""
        try:
            import cv2, numpy as np
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (7, 7), 0)
            edges = cv2.Canny(blur, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                return ToolResult(False, "✗ No objects detected for measurement")
            # Use largest contour as reference
            ref_contour = max(contours, key=cv2.contourArea)
            ref_bbox = cv2.boundingRect(ref_contour)
            pixels_per_unit = ref_bbox[2] / reference_object_size  # width
            measurements = []
            for c in contours:
                x, y, w, h = cv2.boundingRect(c)
                measurements.append({
                    "width_units": round(w / pixels_per_unit, 2),
                    "height_units": round(h / pixels_per_unit, 2),
                    "area_sq_units": round((w * h) / (pixels_per_unit ** 2), 2),
                    "bbox_pixels": [x, y, w, h]
                })
            return ToolResult(True, f"✓ Measured {len(measurements)} objects",
                              {"measurements": measurements, "pixels_per_unit": pixels_per_unit})
        except Exception as e:
            return ToolResult(False, f"✗ measure_object failed: {e}")

    @staticmethod
    def extract_text_from_pdf_image(pdf_path: str, output: str = None) -> ToolResult:
        try:
            import pytesseract
            from PIL import Image
            _ensure("pdf2image", "pdf2image")
            from pdf2image import convert_from_path
            pages = convert_from_path(pdf_path, dpi=300)
            full_text = []
            for i, page in enumerate(pages):
                text = pytesseract.image_to_string(page)
                full_text.append(f"--- Page {i+1} ---\n{text}")
            combined = "\n".join(full_text)
            if output:
                Path(output).write_text(combined, encoding="utf-8")
            return ToolResult(True, f"✓ OCR'd {len(pages)} PDF pages: {len(combined)} chars",
                              {"text": combined, "pages": len(pages)})
        except ImportError:
            return ToolResult(False, "✗ pdf2image not installed. pip install pdf2image (also needs poppler)")
        except Exception as e:
            return ToolResult(False, f"✗ extract_text_from_pdf_image failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# 9. AutomationWorkflowTool
# ═══════════════════════════════════════════════════════════════════════════
class AutomationWorkflowTool:
    name = "automation_workflow"
    description = (
        "No-code workflows: create/run/schedule, file/email/webhook triggers, "
        "chain workflows, conditional branches, retry, parallel, loops"
    )

    _STORE_PATH = Path.home() / ".npmai_agent" / "workflows.json"
    _HISTORY_PATH = Path.home() / ".npmai_agent" / "workflow_history.json"
    _SCHEDULED: dict = {}

    @staticmethod
    def _load_store() -> dict:
        if AutomationWorkflowTool._STORE_PATH.exists():
            try:
                return json.loads(AutomationWorkflowTool._STORE_PATH.read_text())
            except Exception:
                pass
        return {}

    @staticmethod
    def _save_store(data: dict):
        AutomationWorkflowTool._STORE_PATH.parent.mkdir(exist_ok=True)
        AutomationWorkflowTool._STORE_PATH.write_text(json.dumps(data, indent=2))

    @staticmethod
    def create_workflow(name: str, trigger: dict, steps: list,
                        conditions: list = None) -> ToolResult:
        """
        trigger: {'type': 'manual'|'schedule'|'file'|'webhook', ...opts}
        steps: [{'action': 'run_command'|'call_tool', 'params': {...}}]
        conditions: [{'if': 'context.key == value', 'then': 'skip'|'abort'}]
        """
        try:
            store = AutomationWorkflowTool._load_store()
            workflow = {
                "name": name, "id": str(uuid.uuid4()), "trigger": trigger,
                "steps": steps, "conditions": conditions or [],
                "created": datetime.now().isoformat(), "enabled": True
            }
            store[name] = workflow
            AutomationWorkflowTool._save_store(store)
            return ToolResult(True, f"✓ Workflow '{name}' created with {len(steps)} steps", workflow)
        except Exception as e:
            return ToolResult(False, f"✗ create_workflow failed: {e}")

    @staticmethod
    def run_workflow(workflow_name_or_dict: Any, context: dict = None) -> ToolResult:
        try:
            ctx = context or {}
            if isinstance(workflow_name_or_dict, str):
                store = AutomationWorkflowTool._load_store()
                workflow = store.get(workflow_name_or_dict)
                if not workflow:
                    return ToolResult(False, f"✗ Workflow '{workflow_name_or_dict}' not found")
            else:
                workflow = workflow_name_or_dict
            step_results = []
            for i, step in enumerate(workflow.get("steps", [])):
                action = step.get("action", "")
                params = step.get("params", {})
                # Substitute context variables
                params_str = json.dumps(params)
                for k, v in ctx.items():
                    params_str = params_str.replace(f"{{ctx.{k}}}", str(v))
                params = json.loads(params_str)
                result = {"step": i + 1, "action": action, "status": "ok"}
                if action == "run_command":
                    r = subprocess.run(params.get("cmd", ""), shell=True, capture_output=True,
                                       text=True, timeout=params.get("timeout", 30))
                    result["output"] = r.stdout + r.stderr
                    result["status"] = "ok" if r.returncode == 0 else "error"
                    ctx[f"step_{i+1}_output"] = result["output"]
                elif action == "write_file":
                    Path(params["path"]).write_text(params.get("content", ""))
                    result["output"] = f"Written to {params['path']}"
                elif action == "log":
                    result["output"] = params.get("message", "")
                elif action == "http_request":
                    import requests as req
                    r = req.request(params.get("method", "GET"), params["url"],
                                    json=params.get("body"), headers=params.get("headers"),
                                    timeout=15)
                    result["output"] = r.text[:500]
                    ctx[f"step_{i+1}_status"] = r.status_code
                else:
                    result["output"] = f"Unknown action: {action}"
                    result["status"] = "skipped"
                step_results.append(result)
                if result["status"] == "error" and step.get("on_error") == "abort":
                    break
            AutomationWorkflowTool._log_history(workflow.get("name", "unnamed"), step_results, ctx)
            return ToolResult(True, f"✓ Workflow '{workflow.get('name', '')}' completed",
                              {"steps_run": len(step_results), "results": step_results, "context": ctx})
        except Exception as e:
            return ToolResult(False, f"✗ run_workflow failed: {e}")

    @staticmethod
    def _log_history(workflow_name: str, step_results: list, context: dict):
        try:
            path = AutomationWorkflowTool._HISTORY_PATH
            path.parent.mkdir(exist_ok=True)
            history = json.loads(path.read_text()) if path.exists() else []
            history.insert(0, {"workflow": workflow_name, "run_at": datetime.now().isoformat(),
                                "steps": step_results})
            path.write_text(json.dumps(history[:100], indent=2))
        except Exception:
            pass

    @staticmethod
    def schedule_workflow(workflow: Any, schedule_str: str,
                          timezone: str = "UTC") -> ToolResult:
        """schedule_str: 'every 5 minutes' | 'every day at 09:00' | 'every monday at 08:00'"""
        try:
            import schedule as sched
            wf_name = workflow if isinstance(workflow, str) else workflow.get("name", "unnamed")
            wf_id = str(uuid.uuid4())

            def run_job():
                AutomationWorkflowTool.run_workflow(workflow)

            parts = schedule_str.lower().split()
            if "minutes" in parts:
                n = int(parts[1])
                job = sched.every(n).minutes.do(run_job)
            elif "hours" in parts:
                n = int(parts[1])
                job = sched.every(n).hours.do(run_job)
            elif "day" in parts and "at" in parts:
                t = parts[parts.index("at") + 1]
                job = sched.every().day.at(t).do(run_job)
            elif any(d in parts for d in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]):
                day = next(d for d in ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"] if d in parts)
                t = parts[-1] if ":" in parts[-1] else "09:00"
                job = getattr(sched.every(), day).at(t).do(run_job)
            else:
                return ToolResult(False, f"✗ Unrecognised schedule: '{schedule_str}'")
            AutomationWorkflowTool._SCHEDULED[wf_id] = {"job": job, "workflow": wf_name, "schedule": schedule_str}

            def _runner():
                while wf_id in AutomationWorkflowTool._SCHEDULED:
                    sched.run_pending()
                    time.sleep(10)
            threading.Thread(target=_runner, daemon=True).start()
            return ToolResult(True, f"✓ Workflow '{wf_name}' scheduled: {schedule_str}",
                              {"workflow_id": wf_id, "schedule": schedule_str})
        except Exception as e:
            return ToolResult(False, f"✗ schedule_workflow failed: {e}")

    @staticmethod
    def list_scheduled_workflows() -> ToolResult:
        try:
            active = [{"id": wf_id, "workflow": data["workflow"], "schedule": data["schedule"]}
                      for wf_id, data in AutomationWorkflowTool._SCHEDULED.items()]
            return ToolResult(True, f"✓ {len(active)} scheduled workflows", active)
        except Exception as e:
            return ToolResult(False, f"✗ list_scheduled_workflows failed: {e}")

    @staticmethod
    def cancel_scheduled_workflow(workflow_id: str) -> ToolResult:
        try:
            import schedule as sched
            if workflow_id not in AutomationWorkflowTool._SCHEDULED:
                return ToolResult(False, f"✗ Workflow ID '{workflow_id}' not found")
            job = AutomationWorkflowTool._SCHEDULED[workflow_id].get("job")
            if job:
                sched.cancel_job(job)
            del AutomationWorkflowTool._SCHEDULED[workflow_id]
            return ToolResult(True, f"✓ Scheduled workflow {workflow_id} cancelled")
        except Exception as e:
            return ToolResult(False, f"✗ cancel_scheduled_workflow failed: {e}")

    @staticmethod
    def get_workflow_history(workflow_name: str, limit: int = 20) -> ToolResult:
        try:
            path = AutomationWorkflowTool._HISTORY_PATH
            history = json.loads(path.read_text()) if path.exists() else []
            filtered = [h for h in history if h.get("workflow") == workflow_name][:limit]
            return ToolResult(True, f"✓ {len(filtered)} history entries for '{workflow_name}'", filtered)
        except Exception as e:
            return ToolResult(False, f"✗ get_workflow_history failed: {e}")

    @staticmethod
    def create_trigger_on_file_change(path: str, pattern: str, workflow: Any) -> ToolResult:
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class Handler(FileSystemEventHandler):
                def on_any_event(self, event):
                    import fnmatch
                    if not event.is_directory and fnmatch.fnmatch(Path(event.src_path).name, pattern):
                        AutomationWorkflowTool.run_workflow(workflow, {"file": event.src_path,
                                                                        "event": event.event_type})

            obs = Observer()
            obs.schedule(Handler(), path, recursive=True)
            obs.start()
            return ToolResult(True, f"✓ File watcher started on {path} for pattern '{pattern}'")
        except Exception as e:
            return ToolResult(False, f"✗ create_trigger_on_file_change failed: {e}")

    @staticmethod
    def create_trigger_on_email(criteria: dict, workflow: Any) -> ToolResult:
        """criteria: {'subject_contains': '...', 'from_contains': '...', 'check_interval_seconds': 60}"""
        try:
            import imaplib, email as email_lib
            interval = criteria.get("check_interval_seconds", 60)

            def _check():
                creds = CredStore.load("gmail")
                user, pwd = creds.get("email", ""), creds.get("password", "")
                host = creds.get("imap_host", "imap.gmail.com")
                while True:
                    try:
                        mail = imaplib.IMAP4_SSL(host)
                        mail.login(user, pwd)
                        mail.select("inbox")
                        _, ids = mail.search(None, "UNSEEN")
                        for mid in ids[0].split()[-10:]:
                            _, data = mail.fetch(mid, "(RFC822)")
                            msg = email_lib.message_from_bytes(data[0][1])
                            subject = str(msg.get("Subject", ""))
                            from_addr = str(msg.get("From", ""))
                            subj_match = criteria.get("subject_contains", "") in subject
                            from_match = criteria.get("from_contains", "") in from_addr
                            if subj_match or from_match:
                                AutomationWorkflowTool.run_workflow(
                                    workflow, {"subject": subject, "from": from_addr})
                        mail.logout()
                    except Exception:
                        pass
                    time.sleep(interval)

            threading.Thread(target=_check, daemon=True).start()
            return ToolResult(True, f"✓ Email trigger active, checking every {interval}s")
        except Exception as e:
            return ToolResult(False, f"✗ create_trigger_on_email failed: {e}")

    @staticmethod
    def create_trigger_on_webhook(port: int, path: str, workflow: Any) -> ToolResult:
        """Starts a minimal HTTP server that triggers the workflow on POST."""
        try:
            from flask import Flask, request, jsonify
            app = Flask(f"webhook_{port}")

            @app.route(path, methods=["POST"])
            def handle():
                payload = request.get_json(silent=True) or {}
                AutomationWorkflowTool.run_workflow(workflow, payload)
                return jsonify({"status": "triggered"})

            threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False),
                             daemon=True).start()
            return ToolResult(True, f"✓ Webhook trigger listening on port {port}{path}")
        except Exception as e:
            return ToolResult(False, f"✗ create_trigger_on_webhook failed: {e}")

    @staticmethod
    def chain_workflows(workflows: list, pass_context: bool = True) -> ToolResult:
        """Run workflows sequentially, optionally passing context forward."""
        try:
            ctx: dict = {}
            all_results = []
            for wf in workflows:
                result = AutomationWorkflowTool.run_workflow(wf, ctx if pass_context else {})
                all_results.append({"workflow": wf if isinstance(wf, str) else wf.get("name"),
                                    "success": result.success, "output": result.output})
                if result.success and pass_context and isinstance(result.data, dict):
                    ctx.update(result.data.get("context", {}))
            success = all(r["success"] for r in all_results)
            return ToolResult(success, f"✓ Chain of {len(workflows)} workflows complete",
                              all_results)
        except Exception as e:
            return ToolResult(False, f"✗ chain_workflows failed: {e}")

    @staticmethod
    def create_conditional_branch(condition_func: Callable, true_workflow: Any,
                                   false_workflow: Any) -> dict:
        """Returns a workflow dict that branches based on condition_func(context)."""
        return {
            "name": "conditional_branch",
            "id": str(uuid.uuid4()),
            "_type": "conditional",
            "_condition": condition_func,
            "_true": true_workflow,
            "_false": false_workflow,
            "steps": []
        }

    @staticmethod
    def retry_on_failure(workflow: Any, max_retries: int = 3, delay: float = 5.0,
                         backoff: float = 2.0) -> ToolResult:
        """Run workflow with exponential backoff retry."""
        try:
            current_delay = delay
            for attempt in range(max_retries + 1):
                result = AutomationWorkflowTool.run_workflow(workflow)
                if result.success:
                    return ToolResult(True, f"✓ Workflow succeeded on attempt {attempt + 1}", result.data)
                if attempt < max_retries:
                    time.sleep(current_delay)
                    current_delay *= backoff
            return ToolResult(False, f"✗ Workflow failed after {max_retries + 1} attempts")
        except Exception as e:
            return ToolResult(False, f"✗ retry_on_failure failed: {e}")

    @staticmethod
    def run_parallel(workflows: list, max_concurrent: int = 5) -> ToolResult:
        """Run multiple workflows concurrently."""
        try:
            semaphore = threading.Semaphore(max_concurrent)
            results = [None] * len(workflows)

            def run_one(i, wf):
                with semaphore:
                    results[i] = AutomationWorkflowTool.run_workflow(wf)

            threads = [threading.Thread(target=run_one, args=(i, wf)) for i, wf in enumerate(workflows)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=120)

            successes = sum(1 for r in results if r and r.success)
            return ToolResult(True, f"✓ {successes}/{len(workflows)} parallel workflows succeeded",
                              [{"index": i, "success": r.success if r else False,
                                "output": r.output if r else "timeout"}
                               for i, r in enumerate(results)])
        except Exception as e:
            return ToolResult(False, f"✗ run_parallel failed: {e}")

    @staticmethod
    def create_loop_workflow(items_source: Any, item_workflow: Any,
                             collect_results: bool = True) -> ToolResult:
        """items_source: list or callable; item_workflow applied to each item."""
        try:
            items = items_source() if callable(items_source) else items_source
            results = []
            for item in items:
                ctx = {"item": item}
                r = AutomationWorkflowTool.run_workflow(item_workflow, ctx)
                if collect_results:
                    results.append({"item": str(item)[:100], "success": r.success, "output": r.output})
            return ToolResult(True, f"✓ Loop completed {len(items)} iterations", results)
        except Exception as e:
            return ToolResult(False, f"✗ create_loop_workflow failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# 10. KnowledgeBaseTool
# ═══════════════════════════════════════════════════════════════════════════
class KnowledgeBaseTool:
    name = "knowledge_base"
    description = (
        "AI knowledge management: create KB, add docs/URLs/text, "
        "semantic query, search, update/delete, stats, export/import, "
        "QA pair generation, answer with sources"
    )

    _KB_ROOT = Path.home() / ".npmai_agent" / "knowledge_bases"

    @staticmethod
    def _kb_path(kb_name: str) -> Path:
        p = KnowledgeBaseTool._KB_ROOT / kb_name
        p.mkdir(parents=True, exist_ok=True)
        return p

    @staticmethod
    def _load_meta(kb_name: str) -> dict:
        meta_path = KnowledgeBaseTool._kb_path(kb_name) / "meta.json"
        if meta_path.exists():
            try:
                return json.loads(meta_path.read_text())
            except Exception:
                pass
        return {"name": kb_name, "documents": {}, "created": datetime.now().isoformat()}

    @staticmethod
    def _save_meta(kb_name: str, meta: dict):
        (KnowledgeBaseTool._kb_path(kb_name) / "meta.json").write_text(json.dumps(meta, indent=2))

    @staticmethod
    def _get_embedder(model: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(model)

    @staticmethod
    def _load_index(kb_name: str):
        import faiss, numpy as np, pickle
        kb_path = KnowledgeBaseTool._kb_path(kb_name)
        index_path = kb_path / "index.faiss"
        chunks_path = kb_path / "chunks.pkl"
        if index_path.exists() and chunks_path.exists():
            index = faiss.read_index(str(index_path))
            with open(chunks_path, "rb") as f:
                chunks = pickle.load(f)
            return index, chunks
        return None, []

    @staticmethod
    def _save_index(kb_name: str, index, chunks: list):
        import faiss, pickle
        kb_path = KnowledgeBaseTool._kb_path(kb_name)
        faiss.write_index(index, str(kb_path / "index.faiss"))
        with open(kb_path / "chunks.pkl", "wb") as f:
            pickle.dump(chunks, f)

    @staticmethod
    def create_kb(name: str, path: str = None, embedding_model: str = "all-MiniLM-L6-v2") -> ToolResult:
        try:
            import faiss, numpy as np
            kb_path = KnowledgeBaseTool._kb_path(name)
            meta = {"name": name, "documents": {}, "embedding_model": embedding_model,
                    "created": datetime.now().isoformat(), "custom_path": path}
            KnowledgeBaseTool._save_meta(name, meta)
            # Create empty FAISS index (384-dim for MiniLM)
            dim = 384
            index = faiss.IndexFlatL2(dim)
            KnowledgeBaseTool._save_index(name, index, [])
            return ToolResult(True, f"✓ Knowledge base '{name}' created at {kb_path}")
        except Exception as e:
            return ToolResult(False, f"✗ create_kb failed: {e}")

    @staticmethod
    def add_documents(kb_name: str, paths: list, chunk_size: int = 500, overlap: int = 50) -> ToolResult:
        try:
            import faiss, numpy as np, pickle
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            meta = KnowledgeBaseTool._load_meta(kb_name)
            embedder = KnowledgeBaseTool._get_embedder(meta.get("embedding_model", "all-MiniLM-L6-v2"))
            index, chunks = KnowledgeBaseTool._load_index(kb_name)
            if index is None:
                index = faiss.IndexFlatL2(384)
            splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
            added = 0
            for file_path in paths:
                try:
                    p = Path(file_path)
                    if not p.exists():
                        continue
                    if p.suffix == ".pdf":
                        from pypdf import PdfReader
                        text = "\n".join(page.extract_text() or "" for page in PdfReader(str(p)).pages)
                    else:
                        text = p.read_text(errors="replace")
                    doc_chunks = splitter.split_text(text)
                    for i, chunk in enumerate(doc_chunks):
                        embedding = embedder.encode([chunk], normalize_embeddings=True)
                        index.add(np.array(embedding, dtype=np.float32))
                        chunks.append({"text": chunk, "source": str(p), "chunk_index": i,
                                       "doc_id": p.name})
                    meta["documents"][p.name] = {"path": str(p), "chunks": len(doc_chunks),
                                                  "added": datetime.now().isoformat()}
                    added += len(doc_chunks)
                except Exception as ex:
                    continue
            KnowledgeBaseTool._save_index(kb_name, index, chunks)
            KnowledgeBaseTool._save_meta(kb_name, meta)
            return ToolResult(True, f"✓ Added {len(paths)} docs ({added} chunks) to '{kb_name}'")
        except Exception as e:
            return ToolResult(False, f"✗ add_documents failed: {e}")

    @staticmethod
    def add_url_to_kb(kb_name: str, url: str, recursive: bool = False,
                      max_pages: int = 10) -> ToolResult:
        try:
            import requests
            from bs4 import BeautifulSoup
            from urllib.parse import urljoin, urlparse
            visited = set()
            to_visit = [url]
            texts = []

            def fetch_page(page_url):
                try:
                    r = requests.get(page_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
                    soup = BeautifulSoup(r.text, "html.parser")
                    for tag in soup(["script", "style", "nav", "footer"]):
                        tag.decompose()
                    text = soup.get_text(separator="\n", strip=True)
                    texts.append({"url": page_url, "text": text})
                    if recursive:
                        base = urlparse(url).netloc
                        for a in soup.find_all("a", href=True):
                            href = urljoin(page_url, a["href"])
                            if urlparse(href).netloc == base and href not in visited:
                                to_visit.append(href)
                except Exception:
                    pass

            while to_visit and len(visited) < max_pages:
                page_url = to_visit.pop(0)
                if page_url in visited:
                    continue
                visited.add(page_url)
                fetch_page(page_url)

            # Add texts to KB
            tmp_files = []
            for i, item in enumerate(texts):
                tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
                tmp.write(f"Source: {item['url']}\n\n{item['text']}")
                tmp.close()
                tmp_files.append(tmp.name)
            result = KnowledgeBaseTool.add_documents(kb_name, tmp_files)
            for f in tmp_files:
                try:
                    os.unlink(f)
                except Exception:
                    pass
            return ToolResult(True, f"✓ Added {len(visited)} URLs to KB '{kb_name}'",
                              {"pages_fetched": len(visited), "add_result": result.output})
        except Exception as e:
            return ToolResult(False, f"✗ add_url_to_kb failed: {e}")

    @staticmethod
    def add_text(kb_name: str, text: str, metadata: dict = None) -> ToolResult:
        try:
            import faiss, numpy as np
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            meta = KnowledgeBaseTool._load_meta(kb_name)
            embedder = KnowledgeBaseTool._get_embedder(meta.get("embedding_model", "all-MiniLM-L6-v2"))
            index, chunks = KnowledgeBaseTool._load_index(kb_name)
            if index is None:
                index = faiss.IndexFlatL2(384)
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            text_chunks = splitter.split_text(text)
            for i, chunk in enumerate(text_chunks):
                emb = embedder.encode([chunk], normalize_embeddings=True)
                index.add(np.array(emb, dtype=np.float32))
                chunks.append({"text": chunk, "source": "direct_text",
                               "metadata": metadata or {}, "chunk_index": i})
            doc_id = f"text_{int(time.time())}"
            meta["documents"][doc_id] = {"type": "text", "chunks": len(text_chunks),
                                          "added": datetime.now().isoformat(),
                                          "metadata": metadata or {}}
            KnowledgeBaseTool._save_index(kb_name, index, chunks)
            KnowledgeBaseTool._save_meta(kb_name, meta)
            return ToolResult(True, f"✓ Text added to KB '{kb_name}' ({len(text_chunks)} chunks)")
        except Exception as e:
            return ToolResult(False, f"✗ add_text failed: {e}")

    @staticmethod
    def query_kb(kb_name: str, question: str, top_k: int = 5, model: str = "llama3.2:3b",
                 temperature: float = 0.3) -> ToolResult:
        try:
            search_result = KnowledgeBaseTool.search_kb(kb_name, question, top_k)
            if not search_result.success or not search_result.data:
                return ToolResult(False, "✗ No relevant context found in KB")
            context_chunks = "\n\n---\n\n".join(
                f"[Source: {r['source']}]\n{r['text']}" for r in search_result.data
            )
            from agent_core import Ollama
            llm = Ollama(model=model, temperature=temperature, change=True, Models=["mistral:7b"])
            prompt = (f"Answer this question using ONLY the provided context.\n\n"
                      f"Context:\n{context_chunks}\n\n"
                      f"Question: {question}\n\n"
                      f"Answer:")
            answer = llm.invoke(prompt)
            return ToolResult(True, "✓ KB query answered",
                              {"answer": answer, "sources": [r["source"] for r in search_result.data],
                               "context_chunks_used": len(search_result.data)})
        except Exception as e:
            return ToolResult(False, f"✗ query_kb failed: {e}")

    @staticmethod
    def search_kb(kb_name: str, query: str, top_k: int = 5) -> ToolResult:
        try:
            import numpy as np
            meta = KnowledgeBaseTool._load_meta(kb_name)
            embedder = KnowledgeBaseTool._get_embedder(meta.get("embedding_model", "all-MiniLM-L6-v2"))
            index, chunks = KnowledgeBaseTool._load_index(kb_name)
            if index is None or index.ntotal == 0:
                return ToolResult(False, f"✗ KB '{kb_name}' is empty")
            query_emb = embedder.encode([query], normalize_embeddings=True)
            distances, indices = index.search(np.array(query_emb, dtype=np.float32), top_k)
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if 0 <= idx < len(chunks):
                    chunk = chunks[idx]
                    results.append({**chunk, "distance": float(dist),
                                    "relevance_score": round(1 / (1 + float(dist)), 4)})
            return ToolResult(True, f"✓ Found {len(results)} relevant chunks", results)
        except Exception as e:
            return ToolResult(False, f"✗ search_kb failed: {e}")

    @staticmethod
    def update_document(kb_name: str, doc_id: str, new_path: str) -> ToolResult:
        try:
            meta = KnowledgeBaseTool._load_meta(kb_name)
            if doc_id not in meta.get("documents", {}):
                return ToolResult(False, f"✗ Document '{doc_id}' not found in KB '{kb_name}'")
            # Delete old, re-add new
            KnowledgeBaseTool.delete_document(kb_name, doc_id)
            return KnowledgeBaseTool.add_documents(kb_name, [new_path])
        except Exception as e:
            return ToolResult(False, f"✗ update_document failed: {e}")

    @staticmethod
    def delete_document(kb_name: str, doc_id: str) -> ToolResult:
        """Rebuild index excluding chunks from this doc."""
        try:
            import faiss, numpy as np
            meta = KnowledgeBaseTool._load_meta(kb_name)
            if doc_id not in meta.get("documents", {}):
                return ToolResult(False, f"✗ Document '{doc_id}' not found")
            embedder = KnowledgeBaseTool._get_embedder(meta.get("embedding_model", "all-MiniLM-L6-v2"))
            _, chunks = KnowledgeBaseTool._load_index(kb_name)
            remaining = [c for c in chunks if c.get("doc_id") != doc_id and
                         c.get("source", "") != doc_id]
            new_index = faiss.IndexFlatL2(384)
            if remaining:
                texts = [c["text"] for c in remaining]
                embs = embedder.encode(texts, normalize_embeddings=True)
                new_index.add(np.array(embs, dtype=np.float32))
            KnowledgeBaseTool._save_index(kb_name, new_index, remaining)
            del meta["documents"][doc_id]
            KnowledgeBaseTool._save_meta(kb_name, meta)
            return ToolResult(True, f"✓ Document '{doc_id}' deleted from KB '{kb_name}'")
        except Exception as e:
            return ToolResult(False, f"✗ delete_document failed: {e}")

    @staticmethod
    def list_documents(kb_name: str) -> ToolResult:
        try:
            meta = KnowledgeBaseTool._load_meta(kb_name)
            docs = [{"id": k, **v} for k, v in meta.get("documents", {}).items()]
            return ToolResult(True, f"✓ {len(docs)} documents in '{kb_name}'", docs)
        except Exception as e:
            return ToolResult(False, f"✗ list_documents failed: {e}")

    @staticmethod
    def get_kb_stats(kb_name: str) -> ToolResult:
        try:
            meta = KnowledgeBaseTool._load_meta(kb_name)
            index, chunks = KnowledgeBaseTool._load_index(kb_name)
            total_text = sum(len(c.get("text", "")) for c in chunks)
            return ToolResult(True, f"✓ KB '{kb_name}' stats", {
                "name": kb_name,
                "documents": len(meta.get("documents", {})),
                "total_chunks": len(chunks),
                "total_text_chars": total_text,
                "index_size": index.ntotal if index else 0,
                "embedding_model": meta.get("embedding_model"),
                "created": meta.get("created"),
            })
        except Exception as e:
            return ToolResult(False, f"✗ get_kb_stats failed: {e}")

    @staticmethod
    def export_kb(kb_name: str, output: str, format: str = "json") -> ToolResult:
        try:
            import pickle
            meta = KnowledgeBaseTool._load_meta(kb_name)
            _, chunks = KnowledgeBaseTool._load_index(kb_name)
            if format == "json":
                data = {"meta": meta, "chunks": chunks}
                Path(output).write_text(json.dumps(data, indent=2), encoding="utf-8")
            elif format == "csv":
                with open(output, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["text", "source", "chunk_index"])
                    writer.writeheader()
                    writer.writerows({"text": c.get("text", ""), "source": c.get("source", ""),
                                      "chunk_index": c.get("chunk_index", 0)} for c in chunks)
            elif format == "pkl":
                with open(output, "wb") as f:
                    pickle.dump({"meta": meta, "chunks": chunks}, f)
            return ToolResult(True, f"✓ KB '{kb_name}' exported to {output} ({format})")
        except Exception as e:
            return ToolResult(False, f"✗ export_kb failed: {e}")

    @staticmethod
    def import_kb(kb_name: str, path: str) -> ToolResult:
        try:
            import faiss, numpy as np
            with open(path, "rb" if path.endswith(".pkl") else "r") as f:
                if path.endswith(".pkl"):
                    import pickle
                    data = pickle.load(f)
                else:
                    data = json.load(f)
            meta = data.get("meta", {})
            chunks = data.get("chunks", [])
            embedder = KnowledgeBaseTool._get_embedder(meta.get("embedding_model", "all-MiniLM-L6-v2"))
            index = faiss.IndexFlatL2(384)
            if chunks:
                texts = [c.get("text", "") for c in chunks]
                embs = embedder.encode(texts, normalize_embeddings=True)
                index.add(np.array(embs, dtype=np.float32))
            KnowledgeBaseTool._kb_path(kb_name)
            KnowledgeBaseTool._save_index(kb_name, index, chunks)
            meta["name"] = kb_name
            KnowledgeBaseTool._save_meta(kb_name, meta)
            return ToolResult(True, f"✓ KB '{kb_name}' imported: {len(chunks)} chunks")
        except Exception as e:
            return ToolResult(False, f"✗ import_kb failed: {e}")

    @staticmethod
    def create_qa_pairs(kb_name: str, n_questions: int = 10, model: str = "llama3.2:3b",
                        output: str = None) -> ToolResult:
        try:
            from agent_core import Ollama
            _, chunks = KnowledgeBaseTool._load_index(kb_name)
            if not chunks:
                return ToolResult(False, f"✗ KB '{kb_name}' is empty")
            llm = Ollama(model=model, temperature=0.7, change=True, Models=["mistral:7b"])
            qa_pairs = []
            sample_chunks = chunks[:min(n_questions * 2, len(chunks))]
            for chunk in sample_chunks[:n_questions]:
                text = chunk.get("text", "")
                prompt = (f"Generate 1 question and its answer from this text.\n"
                          f"Format:\nQ: [question]\nA: [answer]\n\nText: {text[:800]}")
                raw = llm.invoke(prompt)
                q_match = re.search(r'Q:\s*(.+)', raw)
                a_match = re.search(r'A:\s*(.+)', raw, re.DOTALL)
                if q_match and a_match:
                    qa_pairs.append({
                        "question": q_match.group(1).strip(),
                        "answer": a_match.group(1).strip()[:500],
                        "source": chunk.get("source", "")
                    })
            if output:
                Path(output).write_text(json.dumps(qa_pairs, indent=2), encoding="utf-8")
            return ToolResult(True, f"✓ Generated {len(qa_pairs)} QA pairs", qa_pairs)
        except Exception as e:
            return ToolResult(False, f"✗ create_qa_pairs failed: {e}")

    @staticmethod
    def answer_with_sources(kb_name: str, question: str, model: str = "llama3.2:3b",
                            max_context: int = 4000) -> ToolResult:
        try:
            search_result = KnowledgeBaseTool.search_kb(kb_name, question, top_k=10)
            if not search_result.success:
                return search_result
            chunks = search_result.data or []
            # Build context up to max_context chars
            context_parts = []
            total_chars = 0
            sources = []
            for chunk in chunks:
                text = chunk.get("text", "")
                source = chunk.get("source", "unknown")
                if total_chars + len(text) > max_context:
                    break
                context_parts.append(f"[Source: {source}]\n{text}")
                if source not in sources:
                    sources.append(source)
                total_chars += len(text)
            context = "\n\n---\n\n".join(context_parts)
            from agent_core import Ollama
            llm = Ollama(model=model, temperature=0.2, change=True, Models=["mistral:7b"])
            prompt = (f"Answer this question based ONLY on the provided sources.\n"
                      f"If the answer is not in the sources, say so.\n\n"
                      f"Sources:\n{context}\n\n"
                      f"Question: {question}\n\n"
                      f"Answer with citations (mention [Source: ...] when referencing):")
            answer = llm.invoke(prompt)
            return ToolResult(True, "✓ Answer generated with sources",
                              {"answer": answer, "sources": sources,
                               "context_chars_used": total_chars,
                               "chunks_referenced": len(context_parts)})
        except Exception as e:
            return ToolResult(False, f"✗ answer_with_sources failed: {e}")
