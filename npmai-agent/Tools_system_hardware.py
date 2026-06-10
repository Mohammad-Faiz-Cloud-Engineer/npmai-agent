"""
tools_system_hardware.py
NPM Agent — NPMAI ECOSYSTEM by Sonu Kumar
System & Hardware vertical: OS, Network, FileSystem, GUI Automation, Printers,
Clipboard, Hardware Monitor, Raspberry Pi, MQTT/IoT, Virtualization
"""

import sys, subprocess, platform

def _ensure(pkg: str, import_name: str = None):
    n = import_name or pkg
    try:
        __import__(n)
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", pkg, "-q"], check=False)

for _p, _i in [
    ("psutil",            "psutil"),
    ("py-cpuinfo",        "cpuinfo"),
    ("GPUtil",            "GPUtil"),
    ("scapy",             "scapy"),
    ("paramiko",          "paramiko"),
    ("requests",          "requests"),
    ("watchdog",          "watchdog"),
    ("cryptography",      "cryptography"),
    ("pyautogui",         "pyautogui"),
    ("pygetwindow",       "pygetwindow"),
    ("keyboard",          "keyboard"),
    ("mouse",             "mouse"),
    ("pynput",            "pynput"),
    ("pyperclip",         "pyperclip"),
    ("Pillow",            "PIL"),
    ("paho-mqtt",         "paho"),
    ("python-whois",      "whois"),
]:
    if _p:
        _ensure(_p, _i)

_OS = platform.system()
if _OS == "Windows":
    _ensure("pywin32", "win32api")

from agent_core import ToolResult, CredStore


# ─────────────────────────────────────────────────────────────────────────────
# 1. SystemAdvancedTool
# ─────────────────────────────────────────────────────────────────────────────

class SystemAdvancedTool:
    name = "system_advanced"
    description = (
        "Deep OS operations cross-platform: system info, services, cron, firewall, startup, "
        "hosts file, DNS, programs, restore points, volume, battery, USB, drives."
    )

    @staticmethod
    def get_full_system_info() -> ToolResult:
        try:
            import psutil, cpuinfo

            cpu   = cpuinfo.get_cpu_info()
            vmem  = psutil.virtual_memory()
            disk  = psutil.disk_usage("/")
            boot  = psutil.boot_time()
            from datetime import datetime
            info = {
                "os":            platform.platform(),
                "hostname":      platform.node(),
                "cpu_brand":     cpu.get("brand_raw", ""),
                "cpu_cores_phys": psutil.cpu_count(logical=False),
                "cpu_cores_log":  psutil.cpu_count(logical=True),
                "cpu_freq_mhz":  psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                "ram_total_gb":  round(vmem.total / 1e9, 2),
                "ram_used_gb":   round(vmem.used  / 1e9, 2),
                "disk_total_gb": round(disk.total / 1e9, 2),
                "disk_free_gb":  round(disk.free  / 1e9, 2),
                "boot_time":     datetime.fromtimestamp(boot).isoformat(),
                "python":        platform.python_version(),
            }
            return ToolResult(True, "✓ Full system info fetched", info)
        except Exception as e:
            return ToolResult(False, f"✗ get_full_system_info failed: {e}")

    @staticmethod
    def get_hardware_info(detail_level: str = "basic") -> ToolResult:
        try:
            import psutil

            data: dict = {}
            # CPU
            data["cpu"] = {
                "logical_cores":  psutil.cpu_count(logical=True),
                "physical_cores": psutil.cpu_count(logical=False),
                "percent":        psutil.cpu_percent(interval=1, percpu=True),
                "freq":           psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
            }
            # Memory
            vm = psutil.virtual_memory()
            sw = psutil.swap_memory()
            data["memory"] = {"virtual": vm._asdict(), "swap": sw._asdict()}
            # Disks
            data["disks"] = [
                {"device": p.device, "mountpoint": p.mountpoint,
                 "fstype": p.fstype, "usage": psutil.disk_usage(p.mountpoint)._asdict()}
                for p in psutil.disk_partitions(all=False)
            ]
            # Network
            nics = psutil.net_if_addrs()
            data["network"] = {k: [a._asdict() for a in v] for k, v in nics.items()}
            if detail_level == "full":
                data["sensors"] = {}
                try:
                    temps = psutil.sensors_temperatures()
                    data["sensors"]["temperatures"] = {k: [t._asdict() for t in v] for k, v in (temps or {}).items()}
                    fans = psutil.sensors_fans()
                    data["sensors"]["fans"] = {k: [f._asdict() for f in v] for k, v in (fans or {}).items()}
                except Exception:
                    pass
            return ToolResult(True, "✓ Hardware info fetched", data)
        except Exception as e:
            return ToolResult(False, f"✗ get_hardware_info failed: {e}")

    @staticmethod
    def manage_service(name: str, action: str, os_platform: str = None) -> ToolResult:
        try:
            os_platform = os_platform or platform.system()
            if os_platform == "Windows":
                r = subprocess.run(["sc", action, name], capture_output=True, text=True)
            elif os_platform == "Darwin":
                r = subprocess.run(["launchctl", action, name], capture_output=True, text=True)
            else:
                r = subprocess.run(["systemctl", action, name], capture_output=True, text=True)
            out = r.stdout + r.stderr
            return ToolResult(r.returncode == 0, f"✓ Service '{name}' {action}" if r.returncode == 0 else out.strip())
        except Exception as e:
            return ToolResult(False, f"✗ manage_service failed: {e}")

    @staticmethod
    def list_services(os_platform: str = None, status_filter: str = "") -> ToolResult:
        try:
            os_platform = os_platform or platform.system()
            if os_platform == "Windows":
                r = subprocess.run(["sc", "query", "type=", "all", "state=", "all"],
                                   capture_output=True, text=True)
            elif os_platform == "Darwin":
                r = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
            else:
                r = subprocess.run(["systemctl", "list-units", "--type=service", "--no-pager"],
                                   capture_output=True, text=True)
            lines = r.stdout.splitlines()
            if status_filter:
                lines = [l for l in lines if status_filter.lower() in l.lower()]
            return ToolResult(True, f"✓ {len(lines)} service lines found", lines)
        except Exception as e:
            return ToolResult(False, f"✗ list_services failed: {e}")

    @staticmethod
    def create_cron_job(command: str, schedule: str, user: str = None) -> ToolResult:
        try:
            if platform.system() == "Windows":
                parts  = schedule.split()
                minute = parts[0] if len(parts) > 0 else "0"
                hour   = parts[1] if len(parts) > 1 else "*"
                r = subprocess.run(
                    ["schtasks", "/create", "/tn", command[:20], "/tr", command,
                     "/sc", "DAILY", "/st", f"{hour.zfill(2)}:{minute.zfill(2)}", "/f"],
                    capture_output=True, text=True,
                )
                return ToolResult(r.returncode == 0, r.stdout + r.stderr)
            import tempfile, os
            r = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            existing = r.stdout if r.returncode == 0 else ""
            new_entry = f"{schedule} {command}\n"
            if new_entry.strip() in existing:
                return ToolResult(True, "✓ Cron job already exists")
            with tempfile.NamedTemporaryFile(mode="w", suffix=".cron", delete=False) as tmp:
                tmp.write(existing + new_entry)
                tmp_path = tmp.name
            r2 = subprocess.run(["crontab", tmp_path], capture_output=True, text=True)
            os.unlink(tmp_path)
            return ToolResult(r2.returncode == 0, f"✓ Cron job created: {schedule} {command}")
        except Exception as e:
            return ToolResult(False, f"✗ create_cron_job failed: {e}")

    @staticmethod
    def list_cron_jobs(user: str = None) -> ToolResult:
        try:
            if platform.system() == "Windows":
                r = subprocess.run(["schtasks", "/query", "/fo", "LIST"], capture_output=True, text=True)
                return ToolResult(True, "✓ Scheduled tasks fetched", r.stdout.splitlines())
            cmd = ["crontab", "-l"]
            if user:
                cmd = ["crontab", "-l", "-u", user]
            r = subprocess.run(cmd, capture_output=True, text=True)
            lines = [l for l in r.stdout.splitlines() if l.strip() and not l.startswith("#")]
            return ToolResult(True, f"✓ {len(lines)} cron job(s)", lines)
        except Exception as e:
            return ToolResult(False, f"✗ list_cron_jobs failed: {e}")

    @staticmethod
    def remove_cron_job(command: str) -> ToolResult:
        try:
            if platform.system() == "Windows":
                r = subprocess.run(["schtasks", "/delete", "/tn", command[:20], "/f"],
                                   capture_output=True, text=True)
                return ToolResult(r.returncode == 0, r.stdout + r.stderr)
            import tempfile, os
            r = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            lines = [l for l in r.stdout.splitlines() if command not in l]
            with tempfile.NamedTemporaryFile(mode="w", suffix=".cron", delete=False) as tmp:
                tmp.write("\n".join(lines) + "\n")
                tmp_path = tmp.name
            r2 = subprocess.run(["crontab", tmp_path], capture_output=True, text=True)
            os.unlink(tmp_path)
            return ToolResult(r2.returncode == 0, f"✓ Cron job removed: {command}")
        except Exception as e:
            return ToolResult(False, f"✗ remove_cron_job failed: {e}")

    @staticmethod
    def manage_firewall(
        action: str,
        port: int = None,
        protocol: str = "tcp",
        source_ip: str = "any",
        os_platform: str = None,
    ) -> ToolResult:
        try:
            os_platform = os_platform or platform.system()
            if os_platform == "Windows":
                if action == "allow" and port:
                    r = subprocess.run([
                        "netsh", "advfirewall", "firewall", "add", "rule",
                        f"name=NPMAgent_{port}", "dir=in", "action=allow",
                        f"protocol={protocol}", f"localport={port}",
                    ], capture_output=True, text=True)
                elif action == "deny" and port:
                    r = subprocess.run([
                        "netsh", "advfirewall", "firewall", "add", "rule",
                        f"name=NPMAgent_BLOCK_{port}", "dir=in", "action=block",
                        f"protocol={protocol}", f"localport={port}",
                    ], capture_output=True, text=True)
                elif action == "status":
                    r = subprocess.run(["netsh", "advfirewall", "show", "allprofiles"],
                                       capture_output=True, text=True)
                else:
                    return ToolResult(False, f"✗ Unknown firewall action: {action}")
            elif os_platform == "Darwin":
                if action in ("allow", "deny"):
                    r = subprocess.run(["pfctl", "-f", "/etc/pf.conf"], capture_output=True, text=True)
                else:
                    r = subprocess.run(["pfctl", "-s", "all"], capture_output=True, text=True)
            else:
                if action == "allow" and port:
                    r = subprocess.run(["ufw", "allow", f"{port}/{protocol}"], capture_output=True, text=True)
                elif action == "deny" and port:
                    r = subprocess.run(["ufw", "deny", f"{port}/{protocol}"], capture_output=True, text=True)
                elif action == "status":
                    r = subprocess.run(["ufw", "status", "verbose"], capture_output=True, text=True)
                else:
                    return ToolResult(False, f"✗ Unknown firewall action: {action}")
            return ToolResult(r.returncode == 0, r.stdout + r.stderr)
        except Exception as e:
            return ToolResult(False, f"✗ manage_firewall failed: {e}")

    @staticmethod
    def create_startup_item(name: str, command: str, os_platform: str = None) -> ToolResult:
        try:
            os_platform = os_platform or platform.system()
            if os_platform == "Windows":
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                     r"Software\Microsoft\Windows\CurrentVersion\Run",
                                     0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, command)
                winreg.CloseKey(key)
            elif os_platform == "Darwin":
                import plistlib
                from pathlib import Path
                plist = {
                    "Label": f"com.npmai.{name}",
                    "ProgramArguments": command.split(),
                    "RunAtLoad": True,
                }
                dest = Path.home() / "Library" / "LaunchAgents" / f"com.npmai.{name}.plist"
                dest.parent.mkdir(parents=True, exist_ok=True)
                with open(dest, "wb") as f:
                    plistlib.dump(plist, f)
                subprocess.run(["launchctl", "load", str(dest)], capture_output=True)
            else:
                from pathlib import Path
                service = f"""[Unit]
Description={name}
After=network.target

[Service]
ExecStart={command}
Restart=always

[Install]
WantedBy=multi-user.target
"""
                dest = Path(f"/etc/systemd/system/{name}.service")
                dest.write_text(service)
                subprocess.run(["systemctl", "enable", name], capture_output=True)
            return ToolResult(True, f"✓ Startup item '{name}' created")
        except Exception as e:
            return ToolResult(False, f"✗ create_startup_item failed: {e}")

    @staticmethod
    def remove_startup_item(name: str, os_platform: str = None) -> ToolResult:
        try:
            os_platform = os_platform or platform.system()
            if os_platform == "Windows":
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                     r"Software\Microsoft\Windows\CurrentVersion\Run",
                                     0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, name)
                winreg.CloseKey(key)
            elif os_platform == "Darwin":
                from pathlib import Path
                dest = Path.home() / "Library" / "LaunchAgents" / f"com.npmai.{name}.plist"
                subprocess.run(["launchctl", "unload", str(dest)], capture_output=True)
                dest.unlink(missing_ok=True)
            else:
                subprocess.run(["systemctl", "disable", name], capture_output=True)
                from pathlib import Path
                Path(f"/etc/systemd/system/{name}.service").unlink(missing_ok=True)
            return ToolResult(True, f"✓ Startup item '{name}' removed")
        except Exception as e:
            return ToolResult(False, f"✗ remove_startup_item failed: {e}")

    @staticmethod
    def manage_hosts_file(action: str, ip: str = "", hostname: str = "") -> ToolResult:
        try:
            import re
            from pathlib import Path
            hosts_path = Path("C:/Windows/System32/drivers/etc/hosts") if platform.system() == "Windows" \
                else Path("/etc/hosts")
            content = hosts_path.read_text()
            if action == "add":
                entry = f"\n{ip}\t{hostname}"
                if hostname in content:
                    return ToolResult(True, f"✓ Entry already exists for {hostname}")
                hosts_path.write_text(content + entry)
                return ToolResult(True, f"✓ Added {ip} → {hostname} to hosts file")
            elif action == "remove":
                new_content = re.sub(rf".*\s+{re.escape(hostname)}\s*\n?", "", content)
                hosts_path.write_text(new_content)
                return ToolResult(True, f"✓ Removed {hostname} from hosts file")
            elif action == "list":
                lines = [l for l in content.splitlines() if l.strip() and not l.startswith("#")]
                return ToolResult(True, f"✓ {len(lines)} hosts entries", lines)
            return ToolResult(False, f"✗ Unknown action: {action}")
        except Exception as e:
            return ToolResult(False, f"✗ manage_hosts_file failed: {e}")

    @staticmethod
    def flush_dns() -> ToolResult:
        try:
            os_name = platform.system()
            if os_name == "Windows":
                r = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True)
            elif os_name == "Darwin":
                r = subprocess.run(["dscacheutil", "-flushcache"], capture_output=True, text=True)
                subprocess.run(["killall", "-HUP", "mDNSResponder"], capture_output=True)
            else:
                r = subprocess.run(["systemd-resolve", "--flush-caches"], capture_output=True, text=True)
                if r.returncode != 0:
                    r = subprocess.run(["service", "dns-clean", "restart"], capture_output=True, text=True)
            return ToolResult(True, "✓ DNS cache flushed")
        except Exception as e:
            return ToolResult(False, f"✗ flush_dns failed: {e}")

    @staticmethod
    def get_installed_programs(os_platform: str = None) -> ToolResult:
        try:
            os_platform = os_platform or platform.system()
            programs = []
            if os_platform == "Windows":
                import winreg
                for hive in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                    for path in [
                        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
                    ]:
                        try:
                            key = winreg.OpenKey(hive, path)
                            for i in range(winreg.QueryInfoKey(key)[0]):
                                try:
                                    subkey_name = winreg.EnumKey(key, i)
                                    subkey = winreg.OpenKey(key, subkey_name)
                                    name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                                    programs.append(name)
                                except Exception:
                                    pass
                        except Exception:
                            pass
            elif os_platform == "Darwin":
                r = subprocess.run(["ls", "/Applications"], capture_output=True, text=True)
                programs = [l.replace(".app", "") for l in r.stdout.splitlines() if l.endswith(".app")]
            else:
                r = subprocess.run(["dpkg", "--get-selections"], capture_output=True, text=True)
                if r.returncode == 0:
                    programs = [l.split()[0] for l in r.stdout.splitlines() if "install" in l]
                else:
                    r2 = subprocess.run(["rpm", "-qa"], capture_output=True, text=True)
                    programs = r2.stdout.splitlines()
            return ToolResult(True, f"✓ {len(programs)} installed programs found", programs)
        except Exception as e:
            return ToolResult(False, f"✗ get_installed_programs failed: {e}")

    @staticmethod
    def uninstall_program(name: str, os_platform: str = None) -> ToolResult:
        try:
            os_platform = os_platform or platform.system()
            if os_platform == "Windows":
                r = subprocess.run(
                    ["wmic", "product", "where", f'name="{name}"', "call", "uninstall", "/nointeractive"],
                    capture_output=True, text=True,
                )
            elif os_platform == "Darwin":
                from pathlib import Path
                app_path = f"/Applications/{name}.app"
                r = subprocess.run(["rm", "-rf", app_path], capture_output=True, text=True)
            else:
                r = subprocess.run(["apt-get", "remove", "-y", name], capture_output=True, text=True)
                if r.returncode != 0:
                    r = subprocess.run(["yum", "remove", "-y", name], capture_output=True, text=True)
            return ToolResult(r.returncode == 0, f"✓ Uninstalled: {name}" if r.returncode == 0 else r.stderr)
        except Exception as e:
            return ToolResult(False, f"✗ uninstall_program failed: {e}")

    @staticmethod
    def create_restore_point(description: str) -> ToolResult:
        try:
            if platform.system() != "Windows":
                return ToolResult(False, "✗ Restore points are Windows-only.")
            r = subprocess.run(
                ["powershell", "-Command",
                 f'Checkpoint-Computer -Description "{description}" -RestorePointType MODIFY_SETTINGS'],
                capture_output=True, text=True,
            )
            return ToolResult(r.returncode == 0, f"✓ Restore point created: {description}")
        except Exception as e:
            return ToolResult(False, f"✗ create_restore_point failed: {e}")

    @staticmethod
    def list_restore_points() -> ToolResult:
        try:
            if platform.system() != "Windows":
                return ToolResult(False, "✗ Restore points are Windows-only.")
            r = subprocess.run(
                ["powershell", "-Command", "Get-ComputerRestorePoint | Select-Object Description,CreationTime"],
                capture_output=True, text=True,
            )
            return ToolResult(True, "✓ Restore points listed", r.stdout.splitlines())
        except Exception as e:
            return ToolResult(False, f"✗ list_restore_points failed: {e}")

    @staticmethod
    def set_system_volume(percent: int) -> ToolResult:
        try:
            percent = max(0, min(100, percent))
            os_name = platform.system()
            if os_name == "Windows":
                r = subprocess.run(
                    ["powershell", "-Command",
                     f"$obj = New-Object -ComObject WScript.Shell; $obj.SendKeys([char]174*{(100-percent)//2})"],
                    capture_output=True,
                )
            elif os_name == "Darwin":
                r = subprocess.run(["osascript", "-e", f"set volume output volume {percent}"],
                                   capture_output=True, text=True)
            else:
                r = subprocess.run(["amixer", "-D", "pulse", "sset", "Master", f"{percent}%"],
                                   capture_output=True, text=True)
            return ToolResult(True, f"✓ Volume set to {percent}%")
        except Exception as e:
            return ToolResult(False, f"✗ set_system_volume failed: {e}")

    @staticmethod
    def get_battery_info() -> ToolResult:
        try:
            import psutil
            battery = psutil.sensors_battery()
            if not battery:
                return ToolResult(False, "✗ No battery detected.")
            return ToolResult(True, f"✓ Battery: {battery.percent:.1f}%", {
                "percent":    round(battery.percent, 1),
                "plugged_in": battery.power_plugged,
                "secs_left":  battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "Unlimited",
            })
        except Exception as e:
            return ToolResult(False, f"✗ get_battery_info failed: {e}")

    @staticmethod
    def set_screen_brightness(percent: int) -> ToolResult:
        try:
            percent = max(0, min(100, percent))
            os_name = platform.system()
            if os_name == "Windows":
                r = subprocess.run(
                    ["powershell", "-Command",
                     f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{percent})"],
                    capture_output=True, text=True,
                )
            elif os_name == "Darwin":
                r = subprocess.run(["osascript", "-e", f"tell application \"System Events\" to set brightness to {percent/100}"],
                                   capture_output=True, text=True)
            else:
                r = subprocess.run(["xrandr", "--output", "eDP-1", "--brightness", str(percent / 100)],
                                   capture_output=True, text=True)
            return ToolResult(True, f"✓ Brightness set to {percent}%")
        except Exception as e:
            return ToolResult(False, f"✗ set_screen_brightness failed: {e}")

    @staticmethod
    def list_usb_devices() -> ToolResult:
        try:
            os_name = platform.system()
            if os_name == "Windows":
                r = subprocess.run(
                    ["powershell", "-Command",
                     "Get-PnpDevice -Class USB | Select-Object FriendlyName, Status | ConvertTo-Json"],
                    capture_output=True, text=True,
                )
                import json
                try:
                    data = json.loads(r.stdout)
                    return ToolResult(True, f"✓ {len(data) if isinstance(data,list) else 1} USB device(s)", data)
                except Exception:
                    return ToolResult(True, "✓ USB devices listed", r.stdout.splitlines())
            elif os_name == "Darwin":
                r = subprocess.run(["system_profiler", "SPUSBDataType"], capture_output=True, text=True)
            else:
                r = subprocess.run(["lsusb"], capture_output=True, text=True)
            return ToolResult(True, "✓ USB devices listed", r.stdout.splitlines())
        except Exception as e:
            return ToolResult(False, f"✗ list_usb_devices failed: {e}")

    @staticmethod
    def eject_drive(drive_path: str) -> ToolResult:
        try:
            os_name = platform.system()
            if os_name == "Windows":
                r = subprocess.run(
                    ["powershell", "-Command",
                     f"$vol = [System.IO.DriveInfo]'{drive_path}'; $shell = New-Object -ComObject Shell.Application; $shell.Namespace(17).ParseName('{drive_path}').InvokeVerb('Eject')"],
                    capture_output=True, text=True,
                )
            elif os_name == "Darwin":
                r = subprocess.run(["diskutil", "eject", drive_path], capture_output=True, text=True)
            else:
                r = subprocess.run(["eject", drive_path], capture_output=True, text=True)
            return ToolResult(True, f"✓ Drive ejected: {drive_path}")
        except Exception as e:
            return ToolResult(False, f"✗ eject_drive failed: {e}")

    @staticmethod
    def format_drive(drive_path: str, filesystem: str = "ext4", label: str = "") -> ToolResult:
        try:
            os_name = platform.system()
            if os_name == "Windows":
                label_arg = f"label={label}" if label else ""
                r = subprocess.run(
                    ["format", drive_path, f"/FS:{filesystem}", "/Q", "/Y"] +
                    ([f"/V:{label}"] if label else []),
                    capture_output=True, text=True, input="Y\n",
                )
            elif os_name == "Darwin":
                fs_map = {"ext4": "JHFS+", "fat32": "FAT32", "exfat": "ExFAT", "ntfs": "NTFS"}
                fs = fs_map.get(filesystem.lower(), "JHFS+")
                cmd = ["diskutil", "eraseDisk", fs, label or "DISK", drive_path]
                r = subprocess.run(cmd, capture_output=True, text=True)
            else:
                cmd = [f"mkfs.{filesystem}", drive_path] + (["-L", label] if label else [])
                r = subprocess.run(cmd, capture_output=True, text=True)
            return ToolResult(r.returncode == 0, r.stdout + r.stderr)
        except Exception as e:
            return ToolResult(False, f"✗ format_drive failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. NetworkAdvancedTool
# ─────────────────────────────────────────────────────────────────────────────

class NetworkAdvancedTool:
    name = "network_advanced"
    description = (
        "Network diagnostics and management: ping, traceroute, port scan, DNS, WHOIS, "
        "SSL, HTTP test, bandwidth, ARP, routing, uptime monitoring, SSH tunnels."
    )

    @staticmethod
    def ping(host: str, count: int = 4, timeout: int = 5) -> ToolResult:
        try:
            os_name = platform.system()
            flag    = "-n" if os_name == "Windows" else "-c"
            r = subprocess.run(["ping", flag, str(count), host], capture_output=True, text=True, timeout=timeout * count + 5)
            success = r.returncode == 0
            return ToolResult(success, r.stdout + r.stderr, {"reachable": success, "output": r.stdout})
        except Exception as e:
            return ToolResult(False, f"✗ ping failed: {e}")

    @staticmethod
    def traceroute(host: str, max_hops: int = 30, timeout: int = 5) -> ToolResult:
        try:
            cmd = ["tracert", host] if platform.system() == "Windows" else ["traceroute", "-m", str(max_hops), host]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return ToolResult(True, "✓ Traceroute complete", r.stdout.splitlines())
        except Exception as e:
            return ToolResult(False, f"✗ traceroute failed: {e}")

    @staticmethod
    def port_scan(
        host: str,
        ports: list = None,
        timeout: float = 1.0,
        method: str = "connect",
    ) -> ToolResult:
        try:
            import socket

            ports = ports or list(range(1, 1025))
            open_ports = []
            for port in ports:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(timeout)
                        result = s.connect_ex((host, port))
                        if result == 0:
                            try:
                                service = socket.getservbyport(port)
                            except Exception:
                                service = "unknown"
                            open_ports.append({"port": port, "service": service})
                except Exception:
                    pass
            return ToolResult(True, f"✓ {len(open_ports)} open port(s) on {host}", open_ports)
        except Exception as e:
            return ToolResult(False, f"✗ port_scan failed: {e}")

    @staticmethod
    def check_port_open(host: str, port: int, timeout: float = 3.0) -> ToolResult:
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                result = s.connect_ex((host, port))
            open_ = result == 0
            return ToolResult(open_, f"✓ Port {port} is {'open' if open_ else 'closed'} on {host}", {"open": open_})
        except Exception as e:
            return ToolResult(False, f"✗ check_port_open failed: {e}")

    @staticmethod
    def dns_lookup(domain: str, record_type: str = "A") -> ToolResult:
        try:
            r = subprocess.run(
                ["nslookup", "-type=" + record_type, domain],
                capture_output=True, text=True, timeout=15,
            )
            return ToolResult(True, f"✓ DNS lookup: {domain} ({record_type})", r.stdout.splitlines())
        except Exception as e:
            return ToolResult(False, f"✗ dns_lookup failed: {e}")

    @staticmethod
    def reverse_dns(ip: str) -> ToolResult:
        try:
            import socket
            hostname = socket.gethostbyaddr(ip)[0]
            return ToolResult(True, f"✓ Reverse DNS: {ip} → {hostname}", {"hostname": hostname})
        except Exception as e:
            return ToolResult(False, f"✗ reverse_dns failed: {e}")

    @staticmethod
    def whois_lookup(domain: str) -> ToolResult:
        try:
            import whois
            w = whois.whois(domain)
            return ToolResult(True, f"✓ WHOIS for {domain}", dict(w))
        except Exception as e:
            return ToolResult(False, f"✗ whois_lookup failed: {e}")

    @staticmethod
    def get_local_ip() -> ToolResult:
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ToolResult(True, f"✓ Local IP: {ip}", {"local_ip": ip})
        except Exception as e:
            return ToolResult(False, f"✗ get_local_ip failed: {e}")

    @staticmethod
    def get_public_ip() -> ToolResult:
        try:
            import requests
            ip = requests.get("https://api.ipify.org", timeout=10).text.strip()
            return ToolResult(True, f"✓ Public IP: {ip}", {"public_ip": ip})
        except Exception as e:
            return ToolResult(False, f"✗ get_public_ip failed: {e}")

    @staticmethod
    def get_network_interfaces() -> ToolResult:
        try:
            import psutil
            interfaces = {}
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            for name, addr_list in addrs.items():
                interfaces[name] = {
                    "addresses": [a._asdict() for a in addr_list],
                    "is_up":     stats[name].isup if name in stats else False,
                    "speed":     stats[name].speed if name in stats else 0,
                }
            return ToolResult(True, f"✓ {len(interfaces)} network interface(s)", interfaces)
        except Exception as e:
            return ToolResult(False, f"✗ get_network_interfaces failed: {e}")

    @staticmethod
    def check_ssl_certificate(domain: str, port: int = 443) -> ToolResult:
        try:
            import ssl, socket
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
                s.settimeout(10)
                s.connect((domain, port))
                cert = s.getpeercert()
            return ToolResult(True, f"✓ SSL certificate valid for {domain}", cert)
        except ssl.SSLCertVerificationError as e:
            return ToolResult(False, f"✗ SSL verification failed: {e}")
        except Exception as e:
            return ToolResult(False, f"✗ check_ssl_certificate failed: {e}")

    @staticmethod
    def get_ssl_expiry(domain: str, port: int = 443) -> ToolResult:
        try:
            import ssl, socket
            from datetime import datetime

            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
                s.settimeout(10)
                s.connect((domain, port))
                cert = s.getpeercert()
            expiry_str = cert["notAfter"]
            expiry     = datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y %Z")
            days_left  = (expiry - datetime.utcnow()).days
            return ToolResult(True, f"✓ SSL expires in {days_left} days ({expiry_str})", {"expiry": expiry_str, "days_left": days_left})
        except Exception as e:
            return ToolResult(False, f"✗ get_ssl_expiry failed: {e}")

    @staticmethod
    def http_test(
        url: str,
        method: str = "GET",
        headers: dict = None,
        data: dict = None,
        timeout: int = 15,
        follow_redirects: bool = True,
        verify_ssl: bool = True,
    ) -> ToolResult:
        try:
            import requests
            fn = getattr(requests, method.lower())
            r  = fn(url, headers=headers or {}, json=data, timeout=timeout,
                    allow_redirects=follow_redirects, verify=verify_ssl)
            return ToolResult(
                r.status_code < 400,
                f"✓ {method} {url} → {r.status_code} ({r.elapsed.total_seconds():.3f}s)",
                {
                    "status_code":  r.status_code,
                    "headers":      dict(r.headers),
                    "elapsed_ms":   round(r.elapsed.total_seconds() * 1000, 1),
                    "content_type": r.headers.get("Content-Type", ""),
                    "body_preview": r.text[:500],
                },
            )
        except Exception as e:
            return ToolResult(False, f"✗ http_test failed: {e}")

    @staticmethod
    def bandwidth_test(server_url: str = "https://httpbin.org/bytes/1048576", duration: int = 5) -> ToolResult:
        try:
            import requests, time

            download_bytes = 0
            start = time.time()
            while time.time() - start < duration:
                r = requests.get(server_url, timeout=10, stream=True)
                for chunk in r.iter_content(65536):
                    download_bytes += len(chunk)
                    if time.time() - start >= duration:
                        break
            elapsed = time.time() - start
            speed_mbps = round((download_bytes * 8) / (elapsed * 1e6), 2)
            return ToolResult(True, f"✓ Download speed: ~{speed_mbps} Mbps", {"speed_mbps": speed_mbps, "bytes": download_bytes})
        except Exception as e:
            return ToolResult(False, f"✗ bandwidth_test failed: {e}")

    @staticmethod
    def capture_packets(
        interface: str = "eth0",
        count: int = 10,
        filter: str = "",
        output_pcap: str = "capture.pcap",
    ) -> ToolResult:
        try:
            from scapy.all import sniff, wrpcap
            packets = sniff(iface=interface, count=count, filter=filter, timeout=30)
            wrpcap(output_pcap, packets)
            return ToolResult(True, f"✓ Captured {len(packets)} packets → {output_pcap}", {"count": len(packets)})
        except Exception as e:
            return ToolResult(False, f"✗ capture_packets failed: {e}")

    @staticmethod
    def get_arp_table() -> ToolResult:
        try:
            if platform.system() == "Windows":
                r = subprocess.run(["arp", "-a"], capture_output=True, text=True)
            else:
                r = subprocess.run(["arp", "-n"], capture_output=True, text=True)
            return ToolResult(True, "✓ ARP table fetched", r.stdout.splitlines())
        except Exception as e:
            return ToolResult(False, f"✗ get_arp_table failed: {e}")

    @staticmethod
    def get_routing_table() -> ToolResult:
        try:
            if platform.system() == "Windows":
                r = subprocess.run(["route", "print"], capture_output=True, text=True)
            else:
                r = subprocess.run(["netstat", "-rn"], capture_output=True, text=True)
            return ToolResult(True, "✓ Routing table fetched", r.stdout.splitlines())
        except Exception as e:
            return ToolResult(False, f"✗ get_routing_table failed: {e}")

    @staticmethod
    def set_dns_servers(servers: list, interface: str = "") -> ToolResult:
        try:
            os_name = platform.system()
            if os_name == "Windows":
                iface = interface or "Ethernet"
                for i, server in enumerate(servers):
                    index = "primary" if i == 0 else "secondary"
                    subprocess.run(
                        ["netsh", "interface", "ipv4", "set", "dns",
                         f"name={iface}", "static" if i == 0 else "add", server],
                        capture_output=True,
                    )
            elif os_name == "Darwin":
                for server in servers:
                    subprocess.run(
                        ["networksetup", "-setdnsservers", interface or "Wi-Fi", server],
                        capture_output=True,
                    )
            else:
                from pathlib import Path
                content = "\n".join(f"nameserver {s}" for s in servers) + "\n"
                Path("/etc/resolv.conf").write_text(content)
            return ToolResult(True, f"✓ DNS servers set: {', '.join(servers)}")
        except Exception as e:
            return ToolResult(False, f"✗ set_dns_servers failed: {e}")

    @staticmethod
    def check_domain_health(domain: str) -> ToolResult:
        try:
            import requests, ssl, socket

            results: dict = {}
            # HTTP reachability
            try:
                r = requests.get(f"https://{domain}", timeout=10, verify=True)
                results["http_status"]   = r.status_code
                results["https_reachable"] = True
            except Exception as ex:
                results["https_reachable"] = False
                results["http_error"]      = str(ex)
            # SSL
            try:
                from datetime import datetime
                ctx = ssl.create_default_context()
                with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
                    s.settimeout(5); s.connect((domain, 443))
                    cert = s.getpeercert()
                expiry = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                results["ssl_valid"]    = True
                results["ssl_days_left"] = (expiry - datetime.utcnow()).days
            except Exception as ex:
                results["ssl_valid"] = False; results["ssl_error"] = str(ex)
            # DNS
            try:
                socket.gethostbyname(domain)
                results["dns_resolves"] = True
            except Exception:
                results["dns_resolves"] = False
            return ToolResult(True, f"✓ Domain health check for {domain}", results)
        except Exception as e:
            return ToolResult(False, f"✗ check_domain_health failed: {e}")

    @staticmethod
    def monitor_uptime(
        url: str,
        interval: int = 60,
        alert_threshold: int = 3,
        callback=None,
    ) -> ToolResult:
        try:
            import threading, requests, time

            failures = [0]

            def _watch():
                while True:
                    try:
                        r = requests.get(url, timeout=10)
                        if r.status_code >= 400:
                            failures[0] += 1
                        else:
                            failures[0] = 0
                    except Exception:
                        failures[0] += 1
                    if failures[0] >= alert_threshold and callback:
                        callback({"url": url, "failures": failures[0]})
                    time.sleep(interval)

            threading.Thread(target=_watch, daemon=True).start()
            return ToolResult(True, f"✓ Monitoring uptime for {url} every {interval}s")
        except Exception as e:
            return ToolResult(False, f"✗ monitor_uptime failed: {e}")

    @staticmethod
    def create_ssh_tunnel(
        local_port: int,
        remote_host: str,
        remote_port: int,
        ssh_host: str,
        ssh_user: str,
        ssh_key: str = None,
        cred_key: str = "ssh",
    ) -> ToolResult:
        try:
            import threading
            import paramiko

            creds   = CredStore.load(cred_key)
            key_path = ssh_key or creds.get("key_path", None)
            password = creds.get("password", None)

            transport = paramiko.Transport((ssh_host, 22))
            if key_path:
                pkey = paramiko.RSAKey.from_private_key_file(key_path)
                transport.connect(username=ssh_user, pkey=pkey)
            else:
                transport.connect(username=ssh_user, password=password)

            import socket

            def _accept():
                server = socket.socket()
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.bind(("127.0.0.1", local_port))
                server.listen(5)
                while True:
                    client, _ = server.accept()
                    chan = transport.open_channel("direct-tcpip",
                                                  (remote_host, remote_port),
                                                  ("127.0.0.1", local_port))
                    def bridge(src, dst):
                        while True:
                            data = src.recv(1024)
                            if not data: break
                            dst.sendall(data)
                    threading.Thread(target=bridge, args=(client, chan), daemon=True).start()
                    threading.Thread(target=bridge, args=(chan, client), daemon=True).start()

            threading.Thread(target=_accept, daemon=True).start()
            return ToolResult(True, f"✓ SSH tunnel: localhost:{local_port} → {remote_host}:{remote_port} via {ssh_host}")
        except Exception as e:
            return ToolResult(False, f"✗ create_ssh_tunnel failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. FileSystemAdvancedTool
# ─────────────────────────────────────────────────────────────────────────────

class FileSystemAdvancedTool:
    name = "filesystem_advanced"
    description = (
        "Advanced file operations: folder watch/sync, duplicate detection/removal, "
        "encryption, secure delete, split/join, compression, malware scan, permissions."
    )

    @staticmethod
    def watch_folder(
        path: str,
        callback,
        patterns: list = None,
        recursive: bool = True,
        ignore_patterns: list = None,
    ) -> ToolResult:
        try:
            import threading
            from watchdog.observers import Observer
            from watchdog.events import PatternMatchingEventHandler

            handler = PatternMatchingEventHandler(
                patterns=patterns or ["*"],
                ignore_patterns=ignore_patterns or [],
                ignore_directories=False,
                case_sensitive=True,
            )
            handler.on_any_event = lambda event: callback(event)
            observer = Observer()
            observer.schedule(handler, path, recursive=recursive)
            observer.start()
            return ToolResult(True, f"✓ Watching folder: {path}")
        except Exception as e:
            return ToolResult(False, f"✗ watch_folder failed: {e}")

    @staticmethod
    def sync_folders(
        source: str,
        destination: str,
        bidirectional: bool = False,
        delete_extra: bool = False,
        dry_run: bool = False,
    ) -> ToolResult:
        try:
            import shutil, filecmp
            from pathlib import Path

            def _sync(src: Path, dst: Path) -> int:
                dst.mkdir(parents=True, exist_ok=True)
                count = 0
                for item in src.iterdir():
                    d = dst / item.name
                    if item.is_dir():
                        count += _sync(item, d)
                    else:
                        if not d.exists() or item.stat().st_mtime > d.stat().st_mtime:
                            if not dry_run:
                                shutil.copy2(str(item), str(d))
                            count += 1
                if delete_extra:
                    for item in dst.iterdir():
                        if not (src / item.name).exists():
                            if not dry_run:
                                if item.is_dir(): shutil.rmtree(str(item))
                                else: item.unlink()
                return count

            src_p = Path(source)
            dst_p = Path(destination)
            count = _sync(src_p, dst_p)
            if bidirectional:
                count += _sync(dst_p, src_p)
            mode = "(dry run) " if dry_run else ""
            return ToolResult(True, f"✓ {mode}Synced {count} file(s)")
        except Exception as e:
            return ToolResult(False, f"✗ sync_folders failed: {e}")

    @staticmethod
    def find_duplicates(
        paths: list, method: str = "md5", output: str = None
    ) -> ToolResult:
        try:
            import hashlib, json
            from pathlib import Path
            from collections import defaultdict

            def file_hash(filepath: str) -> str:
                h = hashlib.new(method)
                with open(filepath, "rb") as f:
                    for chunk in iter(lambda: f.read(65536), b""):
                        h.update(chunk)
                return h.hexdigest()

            hashes: dict = defaultdict(list)
            for path in paths:
                p = Path(path)
                for f in (p.rglob("*") if p.is_dir() else [p]):
                    if f.is_file():
                        try:
                            hashes[file_hash(str(f))].append(str(f))
                        except Exception:
                            pass

            duplicates = {h: files for h, files in hashes.items() if len(files) > 1}
            if output:
                Path(output).write_text(json.dumps(duplicates, indent=2))
            return ToolResult(True, f"✓ Found {len(duplicates)} duplicate group(s)", duplicates)
        except Exception as e:
            return ToolResult(False, f"✗ find_duplicates failed: {e}")

    @staticmethod
    def remove_duplicates(
        paths: list, keep: str = "first", method: str = "md5"
    ) -> ToolResult:
        try:
            result = FileSystemAdvancedTool.find_duplicates(paths, method)
            if not result.success:
                return result
            removed = 0
            for hash_val, files in (result.data or {}).items():
                to_remove = files[1:] if keep == "first" else files[:-1]
                for f in to_remove:
                    from pathlib import Path
                    Path(f).unlink()
                    removed += 1
            return ToolResult(True, f"✓ Removed {removed} duplicate file(s)")
        except Exception as e:
            return ToolResult(False, f"✗ remove_duplicates failed: {e}")

    @staticmethod
    def encrypt_file(
        input: str,
        output: str,
        password: str,
        algorithm: str = "AES",
    ) -> ToolResult:
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
            from pathlib import Path
            import os

            salt = os.urandom(16)
            kdf  = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
            key  = kdf.derive(password.encode())
            nonce = os.urandom(12)
            aesgcm = AESGCM(key)
            plaintext  = Path(input).read_bytes()
            ciphertext = aesgcm.encrypt(nonce, plaintext, None)
            Path(output).write_bytes(salt + nonce + ciphertext)
            return ToolResult(True, f"✓ File encrypted: {output}")
        except Exception as e:
            return ToolResult(False, f"✗ encrypt_file failed: {e}")

    @staticmethod
    def decrypt_file(input: str, output: str, password: str) -> ToolResult:
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
            from pathlib import Path

            data  = Path(input).read_bytes()
            salt  = data[:16]
            nonce = data[16:28]
            ct    = data[28:]
            kdf   = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
            key   = kdf.derive(password.encode())
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(nonce, ct, None)
            Path(output).write_bytes(plaintext)
            return ToolResult(True, f"✓ File decrypted: {output}")
        except Exception as e:
            return ToolResult(False, f"✗ decrypt_file failed: {e}")

    @staticmethod
    def secure_delete(path: str, passes: int = 3) -> ToolResult:
        try:
            import os
            from pathlib import Path

            p = Path(path)
            if not p.exists():
                return ToolResult(False, f"✗ File not found: {path}")
            size = p.stat().st_size
            with open(path, "r+b") as f:
                for _ in range(passes):
                    f.seek(0)
                    f.write(os.urandom(size))
                    f.flush()
            p.unlink()
            return ToolResult(True, f"✓ Securely deleted: {path} ({passes} passes)")
        except Exception as e:
            return ToolResult(False, f"✗ secure_delete failed: {e}")

    @staticmethod
    def split_file(path: str, chunk_size: int = 10485760, output_folder: str = None) -> ToolResult:
        try:
            from pathlib import Path

            src  = Path(path)
            dest = Path(output_folder) if output_folder else src.parent / (src.stem + "_parts")
            dest.mkdir(parents=True, exist_ok=True)
            count = 0
            with open(path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    part_path = dest / f"{src.name}.part{count:04d}"
                    part_path.write_bytes(chunk)
                    count += 1
            return ToolResult(True, f"✓ Split into {count} parts in {dest}")
        except Exception as e:
            return ToolResult(False, f"✗ split_file failed: {e}")

    @staticmethod
    def join_files(parts_folder: str, output: str, extension: str = ".part") -> ToolResult:
        try:
            from pathlib import Path

            parts = sorted(Path(parts_folder).glob(f"*{extension}*"))
            if not parts:
                return ToolResult(False, f"✗ No parts found in {parts_folder}")
            with open(output, "wb") as out_f:
                for part in parts:
                    out_f.write(part.read_bytes())
            return ToolResult(True, f"✓ Joined {len(parts)} parts → {output}")
        except Exception as e:
            return ToolResult(False, f"✗ join_files failed: {e}")

    @staticmethod
    def compress_folder(
        path: str, output: str = None, algorithm: str = "zip", level: int = 6
    ) -> ToolResult:
        try:
            import shutil, zipfile, tarfile
            from pathlib import Path

            src  = Path(path)
            dest = output or str(src) + (".zip" if algorithm == "zip" else ".tar.gz")
            if algorithm == "zip":
                with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED, compresslevel=level) as zf:
                    for f in src.rglob("*"):
                        if f.is_file():
                            zf.write(f, f.relative_to(src.parent))
            else:
                mode = "w:gz" if algorithm in ("gz", "gzip", "tar.gz") else "w:bz2"
                with tarfile.open(dest, mode) as tf:
                    tf.add(path, arcname=src.name)
            return ToolResult(True, f"✓ Compressed to {dest}")
        except Exception as e:
            return ToolResult(False, f"✗ compress_folder failed: {e}")

    @staticmethod
    def scan_for_malware(path: str, patterns: list = None) -> ToolResult:
        try:
            from pathlib import Path
            import re

            suspicious_patterns = patterns or [
                r"eval\(base64_decode", r"exec\(base64",
                r"<\?php.*system\(",   r"cmd\.exe /c",
                r"powershell -enc",    r"wget.*http.*\|.*bash",
                r"curl.*\|.*sh",       r"rm -rf /",
                r"nc -e /bin/sh",
            ]
            found = []
            p = Path(path)
            files = list(p.rglob("*")) if p.is_dir() else [p]
            for f in files:
                if not f.is_file():
                    continue
                try:
                    content = f.read_text(errors="replace")
                    for pattern in suspicious_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            found.append({"file": str(f), "pattern": pattern})
                except Exception:
                    pass
            return ToolResult(True, f"✓ Scan complete: {len(found)} suspicious match(es)", found)
        except Exception as e:
            return ToolResult(False, f"✗ scan_for_malware failed: {e}")

    @staticmethod
    def find_large_files(
        path: str, min_size_mb: float = 100, recursive: bool = True
    ) -> ToolResult:
        try:
            from pathlib import Path

            threshold = int(min_size_mb * 1024 * 1024)
            p      = Path(path)
            search = p.rglob("*") if recursive else p.glob("*")
            large  = [
                {"path": str(f), "size_mb": round(f.stat().st_size / 1e6, 2)}
                for f in search
                if f.is_file() and f.stat().st_size >= threshold
            ]
            large.sort(key=lambda x: x["size_mb"], reverse=True)
            return ToolResult(True, f"✓ {len(large)} file(s) >= {min_size_mb} MB", large)
        except Exception as e:
            return ToolResult(False, f"✗ find_large_files failed: {e}")

    @staticmethod
    def change_permissions_recursive(path: str, mode: int = 0o755) -> ToolResult:
        try:
            import os
            from pathlib import Path

            count = 0
            for f in Path(path).rglob("*"):
                os.chmod(str(f), mode)
                count += 1
            return ToolResult(True, f"✓ Changed permissions on {count} item(s) to {oct(mode)}")
        except Exception as e:
            return ToolResult(False, f"✗ change_permissions_recursive failed: {e}")

    @staticmethod
    def change_owner_recursive(path: str, user: str, group: str = None) -> ToolResult:
        try:
            import shutil
            r = subprocess.run(
                ["chown", "-R", f"{user}:{group}" if group else user, path],
                capture_output=True, text=True,
            )
            return ToolResult(r.returncode == 0, r.stdout + r.stderr or f"✓ Owner changed to {user}")
        except Exception as e:
            return ToolResult(False, f"✗ change_owner_recursive failed: {e}")

    @staticmethod
    def mount_remote_folder(
        host: str, remote_path: str, local_path: str, credentials: dict = None, cred_key: str = "ssh"
    ) -> ToolResult:
        try:
            import paramiko, os
            from pathlib import Path

            Path(local_path).mkdir(parents=True, exist_ok=True)
            creds    = credentials or CredStore.load(cred_key)
            transport = paramiko.Transport((host, 22))
            transport.connect(username=creds.get("user", ""), password=creds.get("password", ""))
            sftp = paramiko.SFTPClient.from_transport(transport)
            files = sftp.listdir(remote_path)
            sftp.close(); transport.close()
            return ToolResult(True, f"✓ Remote folder accessible: {host}:{remote_path} ({len(files)} items)", files)
        except Exception as e:
            return ToolResult(False, f"✗ mount_remote_folder failed: {e}")

    @staticmethod
    def verify_checksum(file: str, expected: str, algorithm: str = "sha256") -> ToolResult:
        try:
            import hashlib
            h = hashlib.new(algorithm)
            with open(file, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
            actual  = h.hexdigest()
            matched = actual.lower() == expected.lower()
            return ToolResult(matched, f"✓ Checksum {'matches' if matched else 'MISMATCH'}: {actual}", {"actual": actual, "expected": expected, "match": matched})
        except Exception as e:
            return ToolResult(False, f"✗ verify_checksum failed: {e}")

    @staticmethod
    def generate_checksum_file(
        folder: str, algorithm: str = "sha256", output: str = "checksums.txt"
    ) -> ToolResult:
        try:
            import hashlib
            from pathlib import Path

            lines = []
            for f in sorted(Path(folder).rglob("*")):
                if not f.is_file():
                    continue
                h = hashlib.new(algorithm)
                with open(f, "rb") as fh:
                    for chunk in iter(lambda: fh.read(65536), b""):
                        h.update(chunk)
                lines.append(f"{h.hexdigest()}  {f.relative_to(folder)}")
            Path(output).write_text("\n".join(lines))
            return ToolResult(True, f"✓ Checksums written for {len(lines)} files → {output}")
        except Exception as e:
            return ToolResult(False, f"✗ generate_checksum_file failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# 4. ProcessAutomationTool
# ─────────────────────────────────────────────────────────────────────────────

class ProcessAutomationTool:
    name = "process_automation"
    description = (
        "Windows/Mac GUI automation: window management, mouse/keyboard control, "
        "screen image finding, application control, macro record/play."
    )

    @staticmethod
    def find_window(title: str = "", process_name: str = "") -> ToolResult:
        try:
            import pygetwindow as gw
            windows = gw.getAllWindows()
            results = []
            for w in windows:
                title_match   = title.lower() in w.title.lower() if title else True
                if title_match:
                    results.append({"title": w.title, "left": w.left, "top": w.top, "width": w.width, "height": w.height})
            return ToolResult(bool(results), f"✓ Found {len(results)} window(s)", results)
        except Exception as e:
            return ToolResult(False, f"✗ find_window failed: {e}")

    @staticmethod
    def focus_window(title: str) -> ToolResult:
        try:
            import pygetwindow as gw
            wins = gw.getWindowsWithTitle(title)
            if not wins:
                return ToolResult(False, f"✗ Window not found: {title}")
            wins[0].activate()
            return ToolResult(True, f"✓ Focused window: {title}")
        except Exception as e:
            return ToolResult(False, f"✗ focus_window failed: {e}")

    @staticmethod
    def minimize_window(title: str) -> ToolResult:
        try:
            import pygetwindow as gw
            wins = gw.getWindowsWithTitle(title)
            if not wins:
                return ToolResult(False, f"✗ Window not found: {title}")
            wins[0].minimize()
            return ToolResult(True, f"✓ Minimized: {title}")
        except Exception as e:
            return ToolResult(False, f"✗ minimize_window failed: {e}")

    @staticmethod
    def maximize_window(title: str) -> ToolResult:
        try:
            import pygetwindow as gw
            wins = gw.getWindowsWithTitle(title)
            if not wins:
                return ToolResult(False, f"✗ Window not found: {title}")
            wins[0].maximize()
            return ToolResult(True, f"✓ Maximized: {title}")
        except Exception as e:
            return ToolResult(False, f"✗ maximize_window failed: {e}")

    @staticmethod
    def click_at(
        x: int, y: int, button: str = "left", clicks: int = 1
    ) -> ToolResult:
        try:
            import pyautogui
            pyautogui.click(x, y, button=button, clicks=clicks)
            return ToolResult(True, f"✓ Clicked at ({x}, {y}) with {button} button × {clicks}")
        except Exception as e:
            return ToolResult(False, f"✗ click_at failed: {e}")

    @staticmethod
    def type_text(text: str, interval: float = 0.05) -> ToolResult:
        try:
            import pyautogui
            pyautogui.typewrite(text, interval=interval)
            return ToolResult(True, f"✓ Typed {len(text)} characters")
        except Exception as e:
            return ToolResult(False, f"✗ type_text failed: {e}")

    @staticmethod
    def press_key(key: str, modifiers: list = None) -> ToolResult:
        try:
            import pyautogui
            if modifiers:
                pyautogui.hotkey(*modifiers, key)
            else:
                pyautogui.press(key)
            return ToolResult(True, f"✓ Pressed key: {key}")
        except Exception as e:
            return ToolResult(False, f"✗ press_key failed: {e}")

    @staticmethod
    def drag_and_drop(
        from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 0.5
    ) -> ToolResult:
        try:
            import pyautogui
            pyautogui.moveTo(from_x, from_y)
            pyautogui.dragTo(to_x, to_y, duration=duration, button="left")
            return ToolResult(True, f"✓ Dragged from ({from_x},{from_y}) to ({to_x},{to_y})")
        except Exception as e:
            return ToolResult(False, f"✗ drag_and_drop failed: {e}")

    @staticmethod
    def scroll(x: int, y: int, clicks: int = 3, direction: str = "down") -> ToolResult:
        try:
            import pyautogui
            pyautogui.moveTo(x, y)
            amount = -clicks if direction == "down" else clicks
            pyautogui.scroll(amount)
            return ToolResult(True, f"✓ Scrolled {direction} {abs(clicks)} clicks at ({x},{y})")
        except Exception as e:
            return ToolResult(False, f"✗ scroll failed: {e}")

    @staticmethod
    def take_screenshot_region(
        x: int, y: int, width: int, height: int, output: str = "region.png"
    ) -> ToolResult:
        try:
            import pyautogui
            img = pyautogui.screenshot(region=(x, y, width, height))
            img.save(output)
            return ToolResult(True, f"✓ Screenshot region saved: {output}")
        except Exception as e:
            return ToolResult(False, f"✗ take_screenshot_region failed: {e}")

    @staticmethod
    def find_image_on_screen(image_path: str, confidence: float = 0.8) -> ToolResult:
        try:
            import pyautogui
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                return ToolResult(True, f"✓ Image found at ({center.x}, {center.y})", {"x": center.x, "y": center.y, "region": location})
            return ToolResult(False, f"✗ Image not found on screen: {image_path}")
        except Exception as e:
            return ToolResult(False, f"✗ find_image_on_screen failed: {e}")

    @staticmethod
    def click_image(
        image_path: str, confidence: float = 0.8, button: str = "left"
    ) -> ToolResult:
        try:
            import pyautogui
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if not location:
                return ToolResult(False, f"✗ Image not found: {image_path}")
            pyautogui.click(location, button=button)
            return ToolResult(True, f"✓ Clicked image at ({location.x}, {location.y})")
        except Exception as e:
            return ToolResult(False, f"✗ click_image failed: {e}")

    @staticmethod
    def wait_for_image(
        image_path: str, timeout: int = 30, confidence: float = 0.8
    ) -> ToolResult:
        try:
            import pyautogui, time
            start = time.time()
            while time.time() - start < timeout:
                try:
                    loc = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
                    if loc:
                        return ToolResult(True, f"✓ Image appeared at ({loc.x}, {loc.y})", {"x": loc.x, "y": loc.y})
                except Exception:
                    pass
                time.sleep(0.5)
            return ToolResult(False, f"✗ Image not found within {timeout}s: {image_path}")
        except Exception as e:
            return ToolResult(False, f"✗ wait_for_image failed: {e}")

    @staticmethod
    def run_application(
        path_or_name: str, args: list = None, wait: bool = False
    ) -> ToolResult:
        try:
            cmd = [path_or_name] + (args or [])
            if wait:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                return ToolResult(r.returncode == 0, r.stdout + r.stderr)
            subprocess.Popen(cmd)
            return ToolResult(True, f"✓ Launched: {path_or_name}")
        except Exception as e:
            return ToolResult(False, f"✗ run_application failed: {e}")

    @staticmethod
    def close_application(name_or_pid) -> ToolResult:
        try:
            import psutil
            killed = 0
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    if str(name_or_pid).isdigit():
                        if proc.pid == int(name_or_pid):
                            proc.kill(); killed += 1
                    else:
                        if name_or_pid.lower() in proc.name().lower():
                            proc.kill(); killed += 1
                except Exception:
                    pass
            return ToolResult(killed > 0, f"✓ Closed {killed} process(es) matching '{name_or_pid}'")
        except Exception as e:
            return ToolResult(False, f"✗ close_application failed: {e}")

    @staticmethod
    def get_active_window() -> ToolResult:
        try:
            import pygetwindow as gw
            w = gw.getActiveWindow()
            if not w:
                return ToolResult(False, "✗ No active window detected.")
            return ToolResult(True, f"✓ Active window: {w.title}", {"title": w.title, "left": w.left, "top": w.top})
        except Exception as e:
            return ToolResult(False, f"✗ get_active_window failed: {e}")

    @staticmethod
    def get_all_windows() -> ToolResult:
        try:
            import pygetwindow as gw
            windows = [{"title": w.title, "left": w.left, "top": w.top, "width": w.width, "height": w.height}
                       for w in gw.getAllWindows() if w.title]
            return ToolResult(True, f"✓ {len(windows)} windows found", windows)
        except Exception as e:
            return ToolResult(False, f"✗ get_all_windows failed: {e}")

    @staticmethod
    def send_hotkey(hotkey_string: str) -> ToolResult:
        try:
            import pyautogui
            keys = hotkey_string.replace("+", " ").split()
            pyautogui.hotkey(*keys)
            return ToolResult(True, f"✓ Hotkey sent: {hotkey_string}")
        except Exception as e:
            return ToolResult(False, f"✗ send_hotkey failed: {e}")

    @staticmethod
    def record_macro(output_file: str, duration: int = 10) -> ToolResult:
        try:
            import time, json
            from pynput import mouse, keyboard

            events = []
            stop_time = [time.time() + duration]

            def on_click(x, y, button, pressed):
                if time.time() > stop_time[0]:
                    return False
                events.append({"type": "click", "x": x, "y": y, "button": str(button), "pressed": pressed, "time": time.time()})

            def on_press(key):
                if time.time() > stop_time[0]:
                    return False
                try:
                    events.append({"type": "keypress", "key": key.char, "time": time.time()})
                except AttributeError:
                    events.append({"type": "keypress", "key": str(key), "time": time.time()})

            from pynput.mouse import Listener as ML
            from pynput.keyboard import Listener as KL

            with ML(on_click=on_click), KL(on_press=on_press):
                time.sleep(duration)

            import json
            from pathlib import Path
            Path(output_file).write_text(json.dumps(events, indent=2))
            return ToolResult(True, f"✓ Macro recorded: {len(events)} events → {output_file}")
        except Exception as e:
            return ToolResult(False, f"✗ record_macro failed: {e}")

    @staticmethod
    def play_macro(macro_file: str, speed: float = 1.0) -> ToolResult:
        try:
            import json, time, pyautogui
            from pathlib import Path

            events = json.loads(Path(macro_file).read_text())
            for i, event in enumerate(events):
                if i > 0:
                    delay = (event["time"] - events[i - 1]["time"]) / speed
                    time.sleep(max(0, delay))
                if event["type"] == "click" and event["pressed"]:
                    pyautogui.click(event["x"], event["y"])
                elif event["type"] == "keypress":
                    pyautogui.press(event.get("key", ""))
            return ToolResult(True, f"✓ Macro played: {len(events)} events at {speed}× speed")
        except Exception as e:
            return ToolResult(False, f"✗ play_macro failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# 5. PrinterTool
# ─────────────────────────────────────────────────────────────────────────────

class PrinterTool:
    name = "printer"
    description = (
        "Print management: list printers, print files/PDFs/images, manage print queue, "
        "cancel jobs, get printer status, install printers, export to PDF."
    )

    @staticmethod
    def list_printers() -> ToolResult:
        try:
            os_name = platform.system()
            if os_name == "Windows":
                import win32print
                printers = [p[2] for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
            elif os_name == "Darwin":
                r = subprocess.run(["lpstat", "-p"], capture_output=True, text=True)
                printers = [l.split()[1] for l in r.stdout.splitlines() if l.startswith("printer")]
            else:
                r = subprocess.run(["lpstat", "-p"], capture_output=True, text=True)
                printers = [l.split()[1] for l in r.stdout.splitlines() if l.startswith("printer")]
            return ToolResult(True, f"✓ {len(printers)} printer(s) found", printers)
        except Exception as e:
            return ToolResult(False, f"✗ list_printers failed: {e}")

    @staticmethod
    def get_default_printer() -> ToolResult:
        try:
            os_name = platform.system()
            if os_name == "Windows":
                import win32print
                printer = win32print.GetDefaultPrinter()
            else:
                r = subprocess.run(["lpstat", "-d"], capture_output=True, text=True)
                printer = r.stdout.strip().split(":")[-1].strip()
            return ToolResult(True, f"✓ Default printer: {printer}", {"printer": printer})
        except Exception as e:
            return ToolResult(False, f"✗ get_default_printer failed: {e}")

    @staticmethod
    def set_default_printer(name: str) -> ToolResult:
        try:
            os_name = platform.system()
            if os_name == "Windows":
                import win32print
                win32print.SetDefaultPrinter(name)
            else:
                subprocess.run(["lpoptions", "-d", name], capture_output=True)
            return ToolResult(True, f"✓ Default printer set to: {name}")
        except Exception as e:
            return ToolResult(False, f"✗ set_default_printer failed: {e}")

    @staticmethod
    def print_file(
        file_path: str,
        printer: str = None,
        copies: int = 1,
        orientation: str = "portrait",
        paper_size: str = "A4",
        duplex: bool = False,
    ) -> ToolResult:
        try:
            os_name = platform.system()
            if os_name == "Windows":
                import win32print, win32api
                printer_name = printer or win32print.GetDefaultPrinter()
                win32api.ShellExecute(0, "print", file_path, f'/d:"{printer_name}"', ".", 0)
            else:
                cmd = ["lp"]
                if printer:  cmd += ["-d", printer]
                if copies > 1: cmd += ["-n", str(copies)]
                cmd.append(file_path)
                subprocess.run(cmd, capture_output=True)
            return ToolResult(True, f"✓ Print job sent: {file_path}")
        except Exception as e:
            return ToolResult(False, f"✗ print_file failed: {e}")

    @staticmethod
    def print_pdf(
        pdf_path: str,
        printer: str = None,
        pages: str = None,
        copies: int = 1,
        fit_to_page: bool = True,
    ) -> ToolResult:
        try:
            os_name = platform.system()
            if os_name == "Windows":
                import win32print, win32api
                printer_name = printer or win32print.GetDefaultPrinter()
                win32api.ShellExecute(0, "print", pdf_path, f'/d:"{printer_name}"', ".", 0)
            else:
                cmd = ["lp"]
                if printer:  cmd += ["-d", printer]
                if copies > 1: cmd += ["-n", str(copies)]
                if pages:    cmd += ["-P", pages]
                if fit_to_page: cmd += ["-o", "fit-to-page"]
                cmd.append(pdf_path)
                subprocess.run(cmd, capture_output=True)
            return ToolResult(True, f"✓ PDF print job sent: {pdf_path}")
        except Exception as e:
            return ToolResult(False, f"✗ print_pdf failed: {e}")

    @staticmethod
    def print_image(
        image_path: str, printer: str = None, copies: int = 1, fit: bool = True
    ) -> ToolResult:
        try:
            cmd = ["lp"]
            if printer:  cmd += ["-d", printer]
            if copies > 1: cmd += ["-n", str(copies)]
            if fit:      cmd += ["-o", "fit-to-page"]
            cmd.append(image_path)
            r = subprocess.run(cmd, capture_output=True, text=True)
            return ToolResult(r.returncode == 0, f"✓ Image print job sent: {image_path}")
        except Exception as e:
            return ToolResult(False, f"✗ print_image failed: {e}")

    @staticmethod
    def get_print_queue(printer: str = None) -> ToolResult:
        try:
            if platform.system() == "Windows":
                import win32print
                pname = printer or win32print.GetDefaultPrinter()
                hPrinter = win32print.OpenPrinter(pname)
                jobs = win32print.EnumJobs(hPrinter, 0, -1, 1)
                win32print.ClosePrinter(hPrinter)
                return ToolResult(True, f"✓ {len(jobs)} job(s) in queue", jobs)
            else:
                cmd = ["lpq"] + (["-P", printer] if printer else [])
                r   = subprocess.run(cmd, capture_output=True, text=True)
                return ToolResult(True, "✓ Print queue fetched", r.stdout.splitlines())
        except Exception as e:
            return ToolResult(False, f"✗ get_print_queue failed: {e}")

    @staticmethod
    def cancel_job(job_id: str, printer: str = None) -> ToolResult:
        try:
            if platform.system() == "Windows":
                import win32print
                pname = printer or win32print.GetDefaultPrinter()
                hPrinter = win32print.OpenPrinter(pname)
                win32print.SetJob(hPrinter, int(job_id), 0, None, win32print.JOB_CONTROL_DELETE)
                win32print.ClosePrinter(hPrinter)
            else:
                r = subprocess.run(["cancel", job_id] + (["-P", printer] if printer else []),
                                   capture_output=True, text=True)
            return ToolResult(True, f"✓ Job {job_id} cancelled")
        except Exception as e:
            return ToolResult(False, f"✗ cancel_job failed: {e}")

    @staticmethod
    def get_printer_status(printer: str) -> ToolResult:
        try:
            if platform.system() == "Windows":
                import win32print
                h = win32print.OpenPrinter(printer)
                info = win32print.GetPrinter(h, 2)
                win32print.ClosePrinter(h)
                return ToolResult(True, f"✓ Printer status fetched", {"status": info["Status"], "jobs": info["cJobs"]})
            else:
                r = subprocess.run(["lpstat", "-p", printer], capture_output=True, text=True)
                return ToolResult(True, "✓ Printer status fetched", r.stdout.strip())
        except Exception as e:
            return ToolResult(False, f"✗ get_printer_status failed: {e}")

    @staticmethod
    def install_printer(name: str, driver: str = "", port: str = "USB001") -> ToolResult:
        try:
            if platform.system() == "Windows":
                r = subprocess.run(
                    ["rundll32", "printui.dll,PrintUIEntry", "/if", "/b", name, "/r", port, "/m", driver],
                    capture_output=True, text=True,
                )
                return ToolResult(r.returncode == 0, r.stdout + r.stderr)
            else:
                r = subprocess.run(["lpadmin", "-p", name, "-E", "-v", port] + (["-m", driver] if driver else []),
                                   capture_output=True, text=True)
                return ToolResult(r.returncode == 0, f"✓ Printer '{name}' installed")
        except Exception as e:
            return ToolResult(False, f"✗ install_printer failed: {e}")

    @staticmethod
    def export_to_pdf(file_path: str, output: str = None) -> ToolResult:
        try:
            from pathlib import Path
            dest = output or str(Path(file_path).with_suffix(".pdf"))
            os_name = platform.system()
            if os_name == "Windows":
                r = subprocess.run(
                    ["powershell", "-Command",
                     f'$word = New-Object -ComObject Word.Application; $doc = $word.Documents.Open("{file_path}"); $doc.ExportAsFixedFormat("{dest}", 17); $word.Quit()'],
                    capture_output=True, text=True,
                )
            elif os_name == "Darwin":
                r = subprocess.run(["cupsfilter", file_path, "-o", dest], capture_output=True, text=True)
            else:
                r = subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", file_path, "--outdir", str(Path(dest).parent)],
                                   capture_output=True, text=True)
            return ToolResult(True, f"✓ Exported to PDF: {dest}")
        except Exception as e:
            return ToolResult(False, f"✗ export_to_pdf failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# 6. ClipboardAdvancedTool
# ─────────────────────────────────────────────────────────────────────────────

class ClipboardAdvancedTool:
    name = "clipboard_advanced"
    description = (
        "Advanced clipboard: text, image, files, HTML, history, monitoring, "
        "formatted tables, rich text, and clipboard transforms."
    )

    _history: list = []

    @staticmethod
    def get_text() -> ToolResult:
        try:
            import pyperclip
            text = pyperclip.paste()
            return ToolResult(True, f"✓ Clipboard text: {len(text)} chars", text)
        except Exception as e:
            return ToolResult(False, f"✗ get_text failed: {e}")

    @staticmethod
    def set_text(text: str) -> ToolResult:
        try:
            import pyperclip
            pyperclip.copy(text)
            ClipboardAdvancedTool._history.append({"type": "text", "content": text[:200]})
            return ToolResult(True, f"✓ Text copied to clipboard ({len(text)} chars)")
        except Exception as e:
            return ToolResult(False, f"✗ set_text failed: {e}")

    @staticmethod
    def get_image(output: str = "clipboard_image.png") -> ToolResult:
        try:
            from PIL import ImageGrab
            img = ImageGrab.grabclipboard()
            if img is None:
                return ToolResult(False, "✗ No image in clipboard.")
            img.save(output)
            return ToolResult(True, f"✓ Clipboard image saved: {output}", {"path": output})
        except Exception as e:
            return ToolResult(False, f"✗ get_image failed: {e}")

    @staticmethod
    def set_image(path: str) -> ToolResult:
        try:
            os_name = platform.system()
            if os_name == "Windows":
                import win32clipboard
                from PIL import Image
                import io
                img = Image.open(path).convert("RGB")
                buf = io.BytesIO()
                img.save(buf, format="BMP")
                data = buf.getvalue()[14:]
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()
            elif os_name == "Darwin":
                r = subprocess.run(["osascript", "-e",
                                    f'set the clipboard to (read (POSIX file "{path}") as JPEG picture)'],
                                   capture_output=True, text=True)
            else:
                r = subprocess.run(["xclip", "-selection", "clipboard", "-t", "image/png", "-i", path],
                                   capture_output=True, text=True)
            return ToolResult(True, f"✓ Image copied to clipboard: {path}")
        except Exception as e:
            return ToolResult(False, f"✗ set_image failed: {e}")

    @staticmethod
    def get_files() -> ToolResult:
        try:
            os_name = platform.system()
            if os_name == "Windows":
                import win32clipboard
                win32clipboard.OpenClipboard()
                try:
                    files = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
                finally:
                    win32clipboard.CloseClipboard()
                return ToolResult(True, f"✓ {len(files)} file(s) in clipboard", list(files))
            return ToolResult(False, "✗ get_files only supported on Windows currently.")
        except Exception as e:
            return ToolResult(False, f"✗ get_files failed: {e}")

    @staticmethod
    def set_files(paths: list) -> ToolResult:
        try:
            import pyperclip
            pyperclip.copy("\n".join(paths))
            return ToolResult(True, f"✓ {len(paths)} file path(s) copied to clipboard")
        except Exception as e:
            return ToolResult(False, f"✗ set_files failed: {e}")

    @staticmethod
    def get_html() -> ToolResult:
        try:
            os_name = platform.system()
            if os_name == "Windows":
                import win32clipboard
                HTML_FORMAT = win32clipboard.RegisterClipboardFormat("HTML Format")
                win32clipboard.OpenClipboard()
                try:
                    html = win32clipboard.GetClipboardData(HTML_FORMAT).decode("utf-8", errors="replace")
                finally:
                    win32clipboard.CloseClipboard()
                return ToolResult(True, "✓ HTML clipboard content fetched", html)
            return ToolResult(False, "✗ get_html only supported on Windows currently.")
        except Exception as e:
            return ToolResult(False, f"✗ get_html failed: {e}")

    @staticmethod
    def set_html(html: str) -> ToolResult:
        try:
            import pyperclip
            pyperclip.copy(html)
            return ToolResult(True, "✓ HTML copied to clipboard (as plain text)")
        except Exception as e:
            return ToolResult(False, f"✗ set_html failed: {e}")

    @staticmethod
    def monitor(callback, interval: float = 1.0) -> ToolResult:
        try:
            import threading, pyperclip

            last = [pyperclip.paste()]

            def _watch():
                while True:
                    import time
                    time.sleep(interval)
                    current = pyperclip.paste()
                    if current != last[0]:
                        last[0] = current
                        ClipboardAdvancedTool._history.append({"type": "text", "content": current[:200]})
                        if callback:
                            callback(current)

            threading.Thread(target=_watch, daemon=True).start()
            return ToolResult(True, f"✓ Clipboard monitor started (interval={interval}s)")
        except Exception as e:
            return ToolResult(False, f"✗ monitor failed: {e}")

    @staticmethod
    def get_history(limit: int = 20) -> ToolResult:
        try:
            hist = ClipboardAdvancedTool._history[-limit:]
            return ToolResult(True, f"✓ {len(hist)} clipboard history item(s)", hist)
        except Exception as e:
            return ToolResult(False, f"✗ get_history failed: {e}")

    @staticmethod
    def clear_history() -> ToolResult:
        try:
            ClipboardAdvancedTool._history.clear()
            return ToolResult(True, "✓ Clipboard history cleared")
        except Exception as e:
            return ToolResult(False, f"✗ clear_history failed: {e}")

    @staticmethod
    def copy_formatted_table(data: list, headers: list = None) -> ToolResult:
        try:
            import pyperclip
            if headers:
                rows = ["\t".join(str(h) for h in headers)]
            else:
                rows = []
            for row in data:
                if isinstance(row, dict):
                    rows.append("\t".join(str(v) for v in row.values()))
                else:
                    rows.append("\t".join(str(v) for v in row))
            text = "\n".join(rows)
            pyperclip.copy(text)
            return ToolResult(True, f"✓ Table copied ({len(data)} rows, {len(rows[0].split(chr(9)))} cols)")
        except Exception as e:
            return ToolResult(False, f"✗ copy_formatted_table failed: {e}")

    @staticmethod
    def copy_rich_text(text: str, formatting: dict = None) -> ToolResult:
        try:
            import pyperclip
            pyperclip.copy(text)
            return ToolResult(True, f"✓ Rich text copied ({len(text)} chars)")
        except Exception as e:
            return ToolResult(False, f"✗ copy_rich_text failed: {e}")

    @staticmethod
    def paste_as_plain_text() -> ToolResult:
        try:
            import pyperclip, re
            text = pyperclip.paste()
            plain = re.sub(r"<[^>]+>", "", text)
            pyperclip.copy(plain)
            return ToolResult(True, f"✓ Pasted as plain text ({len(plain)} chars)", plain)
        except Exception as e:
            return ToolResult(False, f"✗ paste_as_plain_text failed: {e}")

    @staticmethod
    def transform_clipboard(operation: str) -> ToolResult:
        try:
            import pyperclip
            text = pyperclip.paste()
            ops = {
                "upper":      text.upper(),
                "lower":      text.lower(),
                "title":      text.title(),
                "strip":      text.strip(),
                "reverse":    text[::-1],
                "word_count": str(len(text.split())),
                "char_count": str(len(text)),
                "lines":      str(len(text.splitlines())),
                "dedup_lines": "\n".join(dict.fromkeys(text.splitlines())),
            }
            if operation not in ops:
                return ToolResult(False, f"✗ Unknown operation: {operation}. Available: {list(ops.keys())}")
            result = ops[operation]
            if operation not in ("word_count", "char_count", "lines"):
                pyperclip.copy(result)
            return ToolResult(True, f"✓ Clipboard transformed: {operation}", result)
        except Exception as e:
            return ToolResult(False, f"✗ transform_clipboard failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# 7. HardwareMonitorTool
# ─────────────────────────────────────────────────────────────────────────────

class HardwareMonitorTool:
    name = "hardware_monitor"
    description = (
        "Deep hardware monitoring: CPU/GPU/disk temperatures, fans, voltages, power, "
        "memory slots, SMART data, benchmarks, event log, threshold monitoring."
    )

    @staticmethod
    def get_cpu_temperature() -> ToolResult:
        try:
            import psutil
            temps = psutil.sensors_temperatures()
            if not temps:
                return ToolResult(False, "✗ Temperature sensors not available.")
            cpu_keys = [k for k in temps if "cpu" in k.lower() or "core" in k.lower() or "k10" in k.lower()]
            data = {}
            for k in (cpu_keys or list(temps.keys())[:2]):
                data[k] = [t._asdict() for t in temps[k]]
            return ToolResult(True, "✓ CPU temperatures fetched", data)
        except Exception as e:
            return ToolResult(False, f"✗ get_cpu_temperature failed: {e}")

    @staticmethod
    def get_gpu_temperature() -> ToolResult:
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if not gpus:
                return ToolResult(False, "✗ No GPU detected by GPUtil.")
            data = [{"id": g.id, "name": g.name, "temperature": g.temperature, "load": g.load, "memory_used": g.memoryUsed} for g in gpus]
            return ToolResult(True, f"✓ {len(data)} GPU(s) found", data)
        except Exception as e:
            return ToolResult(False, f"✗ get_gpu_temperature failed: {e}")

    @staticmethod
    def get_disk_temperature() -> ToolResult:
        try:
            import psutil
            temps = psutil.sensors_temperatures() or {}
            disk_keys = [k for k in temps if "nvme" in k.lower() or "disk" in k.lower() or "ssd" in k.lower()]
            if disk_keys:
                data = {k: [t._asdict() for t in temps[k]] for k in disk_keys}
                return ToolResult(True, "✓ Disk temperatures fetched", data)
            r = subprocess.run(["smartctl", "-A", "/dev/sda"], capture_output=True, text=True)
            lines = [l for l in r.stdout.splitlines() if "Temperature" in l]
            return ToolResult(bool(lines), "✓ Disk temperatures (SMART)" if lines else "✗ No disk temp data", lines)
        except Exception as e:
            return ToolResult(False, f"✗ get_disk_temperature failed: {e}")

    @staticmethod
    def get_fan_speeds() -> ToolResult:
        try:
            import psutil
            fans = psutil.sensors_fans() or {}
            if not fans:
                return ToolResult(False, "✗ Fan sensors not available on this system.")
            data = {k: [f._asdict() for f in v] for k, v in fans.items()}
            return ToolResult(True, "✓ Fan speeds fetched", data)
        except Exception as e:
            return ToolResult(False, f"✗ get_fan_speeds failed: {e}")

    @staticmethod
    def get_voltages() -> ToolResult:
        try:
            r = subprocess.run(["sensors"], capture_output=True, text=True)
            voltage_lines = [l for l in r.stdout.splitlines() if "V" in l and ("+" in l or "-" in l)]
            return ToolResult(bool(voltage_lines), "✓ Voltages read", voltage_lines)
        except Exception as e:
            return ToolResult(False, f"✗ get_voltages failed: {e}")

    @staticmethod
    def get_power_consumption() -> ToolResult:
        try:
            import psutil
            battery = psutil.sensors_battery()
            data: dict = {}
            if battery:
                data["battery_percent"] = battery.percent
                data["plugged_in"]      = battery.power_plugged
            r = subprocess.run(["sensors"], capture_output=True, text=True)
            power_lines = [l for l in r.stdout.splitlines() if "Watt" in l or "watt" in l or "power" in l.lower()]
            data["power_lines"] = power_lines
            return ToolResult(True, "✓ Power consumption data fetched", data)
        except Exception as e:
            return ToolResult(False, f"✗ get_power_consumption failed: {e}")

    @staticmethod
    def get_memory_slots() -> ToolResult:
        try:
            os_name = platform.system()
            if os_name == "Windows":
                r = subprocess.run(
                    ["powershell", "-Command",
                     "Get-WmiObject Win32_PhysicalMemory | Select-Object DeviceLocator,Capacity,Speed,Manufacturer | ConvertTo-Json"],
                    capture_output=True, text=True,
                )
                import json
                try:
                    data = json.loads(r.stdout)
                    return ToolResult(True, "✓ Memory slots fetched", data)
                except Exception:
                    return ToolResult(True, "✓ Memory info", r.stdout.splitlines())
            else:
                r = subprocess.run(["dmidecode", "-t", "17"], capture_output=True, text=True)
                slots = [l.strip() for l in r.stdout.splitlines() if any(k in l for k in ["Size", "Speed", "Manufacturer", "Locator"])]
                return ToolResult(True, "✓ Memory slots fetched", slots)
        except Exception as e:
            return ToolResult(False, f"✗ get_memory_slots failed: {e}")

    @staticmethod
    def get_storage_devices_smart(drive: str = "/dev/sda") -> ToolResult:
        try:
            r = subprocess.run(["smartctl", "-a", drive], capture_output=True, text=True)
            if r.returncode not in (0, 4):
                return ToolResult(False, f"✗ SMART failed: {r.stderr}")
            lines = r.stdout.splitlines()
            return ToolResult(True, f"✓ SMART data for {drive}", lines)
        except Exception as e:
            return ToolResult(False, f"✗ get_storage_devices_smart failed: {e}")

    @staticmethod
    def benchmark_cpu(duration: int = 5) -> ToolResult:
        try:
            import time, math

            ops = 0
            start = time.time()
            while time.time() - start < duration:
                for i in range(10000):
                    math.sqrt(i * 3.14159)
                ops += 10000
            elapsed = time.time() - start
            rate = round(ops / elapsed / 1e6, 2)
            return ToolResult(True, f"✓ CPU benchmark: {rate}M ops/sec over {duration}s", {"ops_per_sec_m": rate})
        except Exception as e:
            return ToolResult(False, f"✗ benchmark_cpu failed: {e}")

    @staticmethod
    def benchmark_memory() -> ToolResult:
        try:
            import time

            size    = 100 * 1024 * 1024
            data    = bytearray(size)
            start   = time.time()
            for i in range(0, size, 4096):
                data[i] = (i % 256)
            write_time = time.time() - start
            start = time.time()
            _ = sum(data[i] for i in range(0, size, 4096))
            read_time = time.time() - start
            write_mbps = round((size / 1e6) / write_time, 1)
            read_mbps  = round((size / 1e6) / read_time, 1)
            return ToolResult(True, f"✓ Memory: write {write_mbps} MB/s, read {read_mbps} MB/s", {"write_mbps": write_mbps, "read_mbps": read_mbps})
        except Exception as e:
            return ToolResult(False, f"✗ benchmark_memory failed: {e}")

    @staticmethod
    def benchmark_disk(path: str = "/tmp") -> ToolResult:
        try:
            import time, os
            from pathlib import Path

            test_file = Path(path) / "npm_disk_bench.tmp"
            data = os.urandom(50 * 1024 * 1024)

            start = time.time()
            test_file.write_bytes(data)
            write_time = time.time() - start

            start = time.time()
            _ = test_file.read_bytes()
            read_time = time.time() - start

            test_file.unlink(missing_ok=True)
            write_mbps = round(50 / write_time, 1)
            read_mbps  = round(50 / read_time,  1)
            return ToolResult(True, f"✓ Disk: write {write_mbps} MB/s, read {read_mbps} MB/s", {"write_mbps": write_mbps, "read_mbps": read_mbps})
        except Exception as e:
            return ToolResult(False, f"✗ benchmark_disk failed: {e}")

    @staticmethod
    def get_system_events_log(
        level: str = "ERROR", count: int = 50, source: str = "", hours_back: int = 24
    ) -> ToolResult:
        try:
            os_name = platform.system()
            if os_name == "Windows":
                r = subprocess.run(
                    ["powershell", "-Command",
                     f'Get-EventLog -LogName System -Newest {count} -EntryType {level} | Select-Object TimeGenerated,Source,Message | ConvertTo-Json'],
                    capture_output=True, text=True,
                )
                import json
                try:
                    return ToolResult(True, "✓ Event log fetched", json.loads(r.stdout))
                except Exception:
                    return ToolResult(True, "✓ Event log fetched", r.stdout.splitlines())
            else:
                r = subprocess.run(
                    ["journalctl", f"-p", level.lower(), f"--since={hours_back} hours ago", f"-n", str(count), "--no-pager"],
                    capture_output=True, text=True,
                )
                return ToolResult(True, f"✓ {len(r.stdout.splitlines())} log lines", r.stdout.splitlines())
        except Exception as e:
            return ToolResult(False, f"✗ get_system_events_log failed: {e}")

    @staticmethod
    def monitor_thresholds(
        thresholds: dict,
        interval: int = 30,
        alert_callback=None,
    ) -> ToolResult:
        try:
            import threading, psutil, time

            def _watch():
                while True:
                    alerts = []
                    cpu = psutil.cpu_percent(interval=1)
                    if "cpu_percent" in thresholds and cpu > thresholds["cpu_percent"]:
                        alerts.append({"metric": "cpu_percent", "value": cpu, "threshold": thresholds["cpu_percent"]})
                    vm = psutil.virtual_memory()
                    if "memory_percent" in thresholds and vm.percent > thresholds["memory_percent"]:
                        alerts.append({"metric": "memory_percent", "value": vm.percent, "threshold": thresholds["memory_percent"]})
                    for part in psutil.disk_partitions():
                        try:
                            usage = psutil.disk_usage(part.mountpoint)
                            if "disk_percent" in thresholds and usage.percent > thresholds["disk_percent"]:
                                alerts.append({"metric": "disk_percent", "mountpoint": part.mountpoint, "value": usage.percent})
                        except Exception:
                            pass
                    if alerts and alert_callback:
                        alert_callback(alerts)
                    time.sleep(interval)

            threading.Thread(target=_watch, daemon=True).start()
            return ToolResult(True, f"✓ Hardware threshold monitoring started (interval={interval}s)", thresholds)
        except Exception as e:
            return ToolResult(False, f"✗ monitor_thresholds failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# 8. RaspberryPiTool
# ─────────────────────────────────────────────────────────────────────────────

class RaspberryPiTool:
    name = "raspberry_pi"
    description = (
        "Full RPi GPIO and hardware: pin setup/read/write, PWM, I2C, SPI, "
        "sensors, servo, stepper, ultrasonic, LCD, buttons, camera."
    )

    _pwm_channels: dict = {}

    @staticmethod
    def _gpio():
        try:
            import RPi.GPIO as GPIO
            return GPIO
        except ImportError:
            raise ImportError("RPi.GPIO not available. This tool requires a Raspberry Pi.")

    @staticmethod
    def setup_pin(pin: int, mode: str = "OUT", pull_up_down: str = "OFF") -> ToolResult:
        try:
            GPIO = RaspberryPiTool._gpio()
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            direction = GPIO.OUT if mode.upper() == "OUT" else GPIO.IN
            pud_map   = {"UP": GPIO.PUD_UP, "DOWN": GPIO.PUD_DOWN, "OFF": GPIO.PUD_OFF}
            pud       = pud_map.get(pull_up_down.upper(), GPIO.PUD_OFF)
            GPIO.setup(pin, direction, pull_up_down=pud)
            return ToolResult(True, f"✓ Pin {pin} set as {mode}")
        except Exception as e:
            return ToolResult(False, f"✗ setup_pin failed: {e}")

    @staticmethod
    def read_pin(pin: int) -> ToolResult:
        try:
            GPIO = RaspberryPiTool._gpio()
            value = GPIO.input(pin)
            return ToolResult(True, f"✓ Pin {pin} = {value}", {"pin": pin, "value": value})
        except Exception as e:
            return ToolResult(False, f"✗ read_pin failed: {e}")

    @staticmethod
    def write_pin(pin: int, value: int) -> ToolResult:
        try:
            GPIO = RaspberryPiTool._gpio()
            GPIO.output(pin, value)
            return ToolResult(True, f"✓ Pin {pin} set to {value}")
        except Exception as e:
            return ToolResult(False, f"✗ write_pin failed: {e}")

    @staticmethod
    def setup_pwm(pin: int, frequency: float = 50.0) -> ToolResult:
        try:
            GPIO = RaspberryPiTool._gpio()
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin, GPIO.OUT)
            pwm = GPIO.PWM(pin, frequency)
            pwm.start(0)
            RaspberryPiTool._pwm_channels[pin] = pwm
            return ToolResult(True, f"✓ PWM started on pin {pin} at {frequency} Hz")
        except Exception as e:
            return ToolResult(False, f"✗ setup_pwm failed: {e}")

    @staticmethod
    def set_pwm_duty(pin: int, duty_cycle: float) -> ToolResult:
        try:
            pwm = RaspberryPiTool._pwm_channels.get(pin)
            if not pwm:
                return ToolResult(False, f"✗ PWM not set up on pin {pin}. Call setup_pwm first.")
            pwm.ChangeDutyCycle(max(0, min(100, duty_cycle)))
            return ToolResult(True, f"✓ PWM duty cycle on pin {pin} set to {duty_cycle}%")
        except Exception as e:
            return ToolResult(False, f"✗ set_pwm_duty failed: {e}")

    @staticmethod
    def read_i2c(device_address: int, register: int, length: int = 1) -> ToolResult:
        try:
            import smbus2
            bus  = smbus2.SMBus(1)
            data = bus.read_i2c_block_data(device_address, register, length)
            bus.close()
            return ToolResult(True, f"✓ I2C read from 0x{device_address:02X} reg 0x{register:02X}", data)
        except Exception as e:
            return ToolResult(False, f"✗ read_i2c failed: {e}")

    @staticmethod
    def write_i2c(device_address: int, register: int, data: list) -> ToolResult:
        try:
            import smbus2
            bus = smbus2.SMBus(1)
            bus.write_i2c_block_data(device_address, register, data)
            bus.close()
            return ToolResult(True, f"✓ I2C write to 0x{device_address:02X} reg 0x{register:02X}: {data}")
        except Exception as e:
            return ToolResult(False, f"✗ write_i2c failed: {e}")

    @staticmethod
    def read_spi(device: int = 0, speed: int = 500000, mode: int = 0, length: int = 4) -> ToolResult:
        try:
            import spidev
            spi = spidev.SpiDev()
            spi.open(0, device)
            spi.max_speed_hz = speed
            spi.mode = mode
            data = spi.readbytes(length)
            spi.close()
            return ToolResult(True, f"✓ SPI read: {data}", data)
        except Exception as e:
            return ToolResult(False, f"✗ read_spi failed: {e}")

    @staticmethod
    def write_spi(device: int = 0, speed: int = 500000, mode: int = 0, data: list = None) -> ToolResult:
        try:
            import spidev
            spi = spidev.SpiDev()
            spi.open(0, device)
            spi.max_speed_hz = speed
            spi.mode = mode
            spi.xfer2(data or [0x00])
            spi.close()
            return ToolResult(True, f"✓ SPI write: {data}")
        except Exception as e:
            return ToolResult(False, f"✗ write_spi failed: {e}")

    @staticmethod
    def read_temperature_sensor(sensor_id: str = "28-", protocol: str = "1wire") -> ToolResult:
        try:
            if protocol == "1wire":
                from pathlib import Path
                base = Path("/sys/bus/w1/devices")
                sensors = list(base.glob(f"{sensor_id}*"))
                if not sensors:
                    return ToolResult(False, f"✗ No 1-wire sensor found matching '{sensor_id}'")
                raw = (sensors[0] / "w1_slave").read_text()
                temp_line = [l for l in raw.splitlines() if "t=" in l]
                if not temp_line:
                    return ToolResult(False, "✗ Could not parse temperature.")
                temp_c = int(temp_line[0].split("t=")[1]) / 1000.0
                return ToolResult(True, f"✓ Temperature: {temp_c}°C", {"celsius": temp_c, "fahrenheit": round(temp_c * 9/5 + 32, 1)})
            return ToolResult(False, f"✗ Protocol not supported: {protocol}")
        except Exception as e:
            return ToolResult(False, f"✗ read_temperature_sensor failed: {e}")

    @staticmethod
    def control_servo(pin: int, angle: float) -> ToolResult:
        try:
            if pin not in RaspberryPiTool._pwm_channels:
                RaspberryPiTool.setup_pwm(pin, 50)
            duty = 2.5 + (angle / 180.0) * 10.0
            RaspberryPiTool._pwm_channels[pin].ChangeDutyCycle(duty)
            return ToolResult(True, f"✓ Servo on pin {pin} moved to {angle}°")
        except Exception as e:
            return ToolResult(False, f"✗ control_servo failed: {e}")

    @staticmethod
    def control_stepper(
        pins: list, steps: int, direction: int = 1, speed: float = 0.001
    ) -> ToolResult:
        try:
            import time
            GPIO = RaspberryPiTool._gpio()
            GPIO.setmode(GPIO.BCM)
            for p in pins:
                GPIO.setup(p, GPIO.OUT)
            seq = [
                [1, 0, 0, 1], [1, 0, 0, 0], [1, 1, 0, 0],
                [0, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 0],
                [0, 0, 1, 1], [0, 0, 0, 1],
            ]
            for _ in range(steps):
                for step in (seq if direction == 1 else seq[::-1]):
                    for i, p in enumerate(pins):
                        GPIO.output(p, step[i % len(step)])
                    time.sleep(speed)
            return ToolResult(True, f"✓ Stepper moved {steps} steps {'CW' if direction == 1 else 'CCW'}")
        except Exception as e:
            return ToolResult(False, f"✗ control_stepper failed: {e}")

    @staticmethod
    def read_hcsr04_distance(trig: int, echo: int) -> ToolResult:
        try:
            import time
            GPIO = RaspberryPiTool._gpio()
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(trig, GPIO.OUT)
            GPIO.setup(echo, GPIO.IN)
            GPIO.output(trig, False)
            time.sleep(0.2)
            GPIO.output(trig, True)
            time.sleep(0.00001)
            GPIO.output(trig, False)
            timeout = time.time() + 1
            pulse_start = time.time()
            while GPIO.input(echo) == 0:
                pulse_start = time.time()
                if time.time() > timeout: break
            pulse_end = time.time()
            while GPIO.input(echo) == 1:
                pulse_end = time.time()
                if time.time() > timeout: break
            distance_cm = round((pulse_end - pulse_start) * 17150, 2)
            return ToolResult(True, f"✓ Distance: {distance_cm} cm", {"cm": distance_cm, "inches": round(distance_cm / 2.54, 2)})
        except Exception as e:
            return ToolResult(False, f"✗ read_hcsr04_distance failed: {e}")

    @staticmethod
    def display_on_lcd(i2c_address: int, text: str, row: int = 0) -> ToolResult:
        try:
            import smbus2, time
            bus = smbus2.SMBus(1)

            def _write_byte(data):
                bus.write_byte(i2c_address, data)
                time.sleep(0.0001)

            def _write_cmd(cmd):
                _write_byte(cmd & 0xF0 | 0x04)
                _write_byte(cmd & 0xF0)
                _write_byte((cmd << 4) & 0xF0 | 0x04)
                _write_byte((cmd << 4) & 0xF0)

            def _write_char(char):
                _write_byte(ord(char) & 0xF0 | 0x05)
                _write_byte(ord(char) & 0xF0 | 0x01)
                _write_byte((ord(char) << 4) & 0xF0 | 0x05)
                _write_byte((ord(char) << 4) & 0xF0 | 0x01)

            row_offsets = [0x00, 0x40]
            _write_cmd(0x80 | (row_offsets[row % len(row_offsets)]))
            for char in text[:16]:
                _write_char(char)
            bus.close()
            return ToolResult(True, f"✓ LCD row {row}: '{text[:16]}'")
        except Exception as e:
            return ToolResult(False, f"✗ display_on_lcd failed: {e}")

    @staticmethod
    def read_button(pin: int, debounce: float = 0.05) -> ToolResult:
        try:
            import time
            GPIO = RaspberryPiTool._gpio()
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            pressed = GPIO.input(pin) == GPIO.LOW
            if pressed:
                time.sleep(debounce)
                pressed = GPIO.input(pin) == GPIO.LOW
            return ToolResult(True, f"✓ Button on pin {pin}: {'PRESSED' if pressed else 'RELEASED'}", {"pressed": pressed})
        except Exception as e:
            return ToolResult(False, f"✗ read_button failed: {e}")

    @staticmethod
    def capture_camera(
        output: str = "photo.jpg", width: int = 1920, height: int = 1080, duration: int = 0
    ) -> ToolResult:
        try:
            if duration > 0:
                r = subprocess.run(["raspivid", "-o", output, "-t", str(duration * 1000),
                                    "-w", str(width), "-h", str(height)], capture_output=True)
            else:
                r = subprocess.run(["libcamera-still", "-o", output, "--width", str(width), "--height", str(height)],
                                   capture_output=True)
            return ToolResult(r.returncode == 0, f"✓ Camera capture saved: {output}")
        except Exception as e:
            return ToolResult(False, f"✗ capture_camera failed: {e}")

    @staticmethod
    def stream_camera(port: int = 8080) -> ToolResult:
        try:
            proc = subprocess.Popen(
                ["libcamera-vid", "-t", "0", "--inline", "--listen", "-o", f"tcp://0.0.0.0:{port}"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            return ToolResult(True, f"✓ Camera streaming on port {port} (PID: {proc.pid})", {"pid": proc.pid})
        except Exception as e:
            return ToolResult(False, f"✗ stream_camera failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# 9. MQTTIoTTool
# ─────────────────────────────────────────────────────────────────────────────

class MQTTIoTTool:
    name = "mqtt_iot"
    description = (
        "IoT communication via MQTT: connect, publish/subscribe, JSON payloads, "
        "sensor data, device commands, Home Assistant, automations, log replay."
    )

    _clients: dict = {}
    _messages: list = []

    @staticmethod
    def connect(
        broker: str,
        port: int = 1883,
        username: str = None,
        password: str = None,
        client_id: str = "npm_agent",
        tls: bool = False,
        cred_key: str = "mqtt",
    ) -> ToolResult:
        try:
            import paho.mqtt.client as mqtt

            creds = CredStore.load(cred_key)
            user  = username or creds.get("username", "")
            pwd   = password or creds.get("password", "")

            client = mqtt.Client(client_id=client_id)
            if user:
                client.username_pw_set(user, pwd)
            if tls:
                client.tls_set()

            client.connect(broker, port, keepalive=60)
            client.loop_start()
            MQTTIoTTool._clients[client_id] = client
            return ToolResult(True, f"✓ MQTT connected to {broker}:{port} as '{client_id}'", {"client_id": client_id})
        except Exception as e:
            return ToolResult(False, f"✗ MQTT connect failed: {e}")

    @staticmethod
    def publish(
        topic: str,
        payload: str,
        qos: int = 0,
        retain: bool = False,
        client_id: str = "npm_agent",
    ) -> ToolResult:
        try:
            client = MQTTIoTTool._clients.get(client_id)
            if not client:
                return ToolResult(False, f"✗ No MQTT client '{client_id}'. Call connect() first.")
            result = client.publish(topic, payload, qos=qos, retain=retain)
            return ToolResult(result.rc == 0, f"✓ Published to '{topic}': {str(payload)[:80]}")
        except Exception as e:
            return ToolResult(False, f"✗ MQTT publish failed: {e}")

    @staticmethod
    def subscribe(
        topics: list,
        callback=None,
        qos: int = 0,
        client_id: str = "npm_agent",
    ) -> ToolResult:
        try:
            client = MQTTIoTTool._clients.get(client_id)
            if not client:
                return ToolResult(False, f"✗ No MQTT client '{client_id}'. Call connect() first.")

            def _on_message(cl, userdata, msg):
                entry = {"topic": msg.topic, "payload": msg.payload.decode("utf-8", errors="replace"), "qos": msg.qos}
                MQTTIoTTool._messages.append(entry)
                if callback:
                    callback(entry)

            client.on_message = _on_message
            for topic in topics:
                client.subscribe(topic, qos)
            return ToolResult(True, f"✓ Subscribed to {topics}")
        except Exception as e:
            return ToolResult(False, f"✗ MQTT subscribe failed: {e}")

    @staticmethod
    def publish_json(
        topic: str, data: dict, qos: int = 0, client_id: str = "npm_agent"
    ) -> ToolResult:
        try:
            import json
            return MQTTIoTTool.publish(topic, json.dumps(data), qos=qos, client_id=client_id)
        except Exception as e:
            return ToolResult(False, f"✗ MQTT publish_json failed: {e}")

    @staticmethod
    def listen_once(
        topic: str, timeout: int = 10, client_id: str = "npm_agent"
    ) -> ToolResult:
        try:
            import paho.mqtt.subscribe as subscribe

            client_info = MQTTIoTTool._clients.get(client_id)
            if not client_info:
                return ToolResult(False, f"✗ No MQTT client '{client_id}'.")
            received = [None]
            original_msg_handler = client_info._on_message

            def _once(cl, userdata, msg):
                received[0] = {"topic": msg.topic, "payload": msg.payload.decode("utf-8", errors="replace")}

            client_info.message_callback_add(topic, _once)
            import time
            start = time.time()
            while received[0] is None and time.time() - start < timeout:
                time.sleep(0.1)
            client_info.message_callback_remove(topic)
            if received[0]:
                return ToolResult(True, f"✓ Received on '{topic}'", received[0])
            return ToolResult(False, f"✗ No message received on '{topic}' within {timeout}s")
        except Exception as e:
            return ToolResult(False, f"✗ MQTT listen_once failed: {e}")

    @staticmethod
    def publish_sensor_data(
        topic: str,
        sensor_type: str,
        value: float,
        unit: str,
        device_id: str,
        client_id: str = "npm_agent",
    ) -> ToolResult:
        try:
            from datetime import datetime
            import json

            payload = {
                "device_id":   device_id,
                "sensor_type": sensor_type,
                "value":       value,
                "unit":        unit,
                "timestamp":   datetime.utcnow().isoformat() + "Z",
            }
            return MQTTIoTTool.publish(topic, json.dumps(payload), client_id=client_id)
        except Exception as e:
            return ToolResult(False, f"✗ MQTT publish_sensor_data failed: {e}")

    @staticmethod
    def send_command(
        device_topic: str,
        command: str,
        params: dict = None,
        client_id: str = "npm_agent",
    ) -> ToolResult:
        try:
            import json
            payload = {"command": command, "params": params or {}}
            return MQTTIoTTool.publish(f"{device_topic}/command", json.dumps(payload), client_id=client_id)
        except Exception as e:
            return ToolResult(False, f"✗ MQTT send_command failed: {e}")

    @staticmethod
    def get_device_state(
        device_topic: str, timeout: int = 5, client_id: str = "npm_agent"
    ) -> ToolResult:
        try:
            MQTTIoTTool.publish(f"{device_topic}/get", "state", client_id=client_id)
            return MQTTIoTTool.listen_once(f"{device_topic}/state", timeout=timeout, client_id=client_id)
        except Exception as e:
            return ToolResult(False, f"✗ MQTT get_device_state failed: {e}")

    @staticmethod
    def control_home_assistant_entity(
        entity_id: str,
        action: str,
        attributes: dict = None,
        cred_key: str = "home_assistant",
    ) -> ToolResult:
        try:
            import requests
            creds   = CredStore.load(cred_key)
            base_url = creds.get("base_url", "http://homeassistant.local:8123")
            token    = creds.get("token", "")
            headers  = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            domain   = entity_id.split(".")[0]
            payload  = {"entity_id": entity_id, **(attributes or {})}
            r = requests.post(f"{base_url}/api/services/{domain}/{action}", headers=headers, json=payload, timeout=10)
            return ToolResult(r.status_code < 300, f"✓ HA entity '{entity_id}' action '{action}' sent", r.json() if r.content else {})
        except Exception as e:
            return ToolResult(False, f"✗ MQTT control_home_assistant_entity failed: {e}")

    @staticmethod
    def create_automation(
        trigger_topic: str,
        trigger_value: str,
        action_topic: str,
        action_payload: str,
        client_id: str = "npm_agent",
    ) -> ToolResult:
        try:
            def _on_trigger(msg):
                payload = msg.get("payload", "")
                if trigger_value in payload:
                    MQTTIoTTool.publish(action_topic, action_payload, client_id=client_id)

            MQTTIoTTool.subscribe([trigger_topic], callback=_on_trigger, client_id=client_id)
            return ToolResult(True, f"✓ Automation created: '{trigger_topic}' → '{action_topic}'")
        except Exception as e:
            return ToolResult(False, f"✗ MQTT create_automation failed: {e}")

    @staticmethod
    def monitor_topics(
        topics: list, log_file: str = "mqtt_log.jsonl", duration: int = 60, client_id: str = "npm_agent"
    ) -> ToolResult:
        try:
            import threading, time, json
            from pathlib import Path

            stop_event = threading.Event()

            def _log(msg):
                with open(log_file, "a") as f:
                    f.write(json.dumps(msg) + "\n")

            MQTTIoTTool.subscribe(topics, callback=_log, client_id=client_id)

            def _stop():
                time.sleep(duration)
                stop_event.set()

            threading.Thread(target=_stop, daemon=True).start()
            return ToolResult(True, f"✓ Monitoring {topics} for {duration}s → {log_file}")
        except Exception as e:
            return ToolResult(False, f"✗ MQTT monitor_topics failed: {e}")

    @staticmethod
    def replay_messages(
        log_file: str,
        broker: str,
        port: int = 1883,
        client_id: str = "replayer",
    ) -> ToolResult:
        try:
            import json, time
            from pathlib import Path

            lines = Path(log_file).read_text().splitlines()
            if not lines:
                return ToolResult(False, "✗ Log file is empty.")
            connect_result = MQTTIoTTool.connect(broker, port, client_id=client_id)
            if not connect_result.success:
                return connect_result
            count = 0
            for line in lines:
                try:
                    msg = json.loads(line)
                    MQTTIoTTool.publish(msg["topic"], msg["payload"], client_id=client_id)
                    count += 1
                    time.sleep(0.05)
                except Exception:
                    pass
            return ToolResult(True, f"✓ Replayed {count} messages from {log_file}")
        except Exception as e:
            return ToolResult(False, f"✗ MQTT replay_messages failed: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# 10. VirtualizationTool
# ─────────────────────────────────────────────────────────────────────────────

class VirtualizationTool:
    name = "virtualization"
    description = (
        "VM management: list, start/stop/restart/suspend/resume VMs, snapshots, "
        "info, resources, clone, export, run commands in VM, copy files to VM. "
        "Supports VirtualBox, libvirt/KVM, and VMware."
    )

    @staticmethod
    def _vbox(cmd: list) -> tuple:
        r = subprocess.run(["VBoxManage"] + cmd, capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    @staticmethod
    def _libvirt_conn(uri: str = "qemu:///system"):
        import libvirt
        conn = libvirt.open(uri)
        if not conn:
            raise RuntimeError("Failed to open libvirt connection.")
        return conn

    @staticmethod
    def list_vms(hypervisor: str = "virtualbox") -> ToolResult:
        try:
            if hypervisor == "virtualbox":
                rc, out = VirtualizationTool._vbox(["list", "vms"])
                vms = [line.split('"')[1] for line in out.splitlines() if '"' in line]
                return ToolResult(rc == 0, f"✓ {len(vms)} VirtualBox VM(s)", vms)
            elif hypervisor == "libvirt":
                conn = VirtualizationTool._libvirt_conn()
                domains = conn.listAllDomains()
                vms = [{"name": d.name(), "state": d.isActive()} for d in domains]
                conn.close()
                return ToolResult(True, f"✓ {len(vms)} libvirt VM(s)", vms)
            elif hypervisor == "vmware":
                r = subprocess.run(["vmrun", "list"], capture_output=True, text=True)
                return ToolResult(True, "✓ VMware VMs listed", r.stdout.splitlines())
            return ToolResult(False, f"✗ Unknown hypervisor: {hypervisor}")
        except Exception as e:
            return ToolResult(False, f"✗ list_vms failed: {e}")

    @staticmethod
    def start_vm(name: str, hypervisor: str = "virtualbox") -> ToolResult:
        try:
            if hypervisor == "virtualbox":
                rc, out = VirtualizationTool._vbox(["startvm", name, "--type", "headless"])
            elif hypervisor == "libvirt":
                conn = VirtualizationTool._libvirt_conn()
                dom  = conn.lookupByName(name)
                rc   = dom.create()
                out  = f"libvirt start returned {rc}"
                conn.close()
            elif hypervisor == "vmware":
                r  = subprocess.run(["vmrun", "start", name, "nogui"], capture_output=True, text=True)
                rc, out = r.returncode, r.stdout + r.stderr
            else:
                return ToolResult(False, f"✗ Unknown hypervisor: {hypervisor}")
            return ToolResult(rc == 0, f"✓ Started VM: {name}" if rc == 0 else out.strip())
        except Exception as e:
            return ToolResult(False, f"✗ start_vm failed: {e}")

    @staticmethod
    def stop_vm(name: str, hypervisor: str = "virtualbox", force: bool = False) -> ToolResult:
        try:
            if hypervisor == "virtualbox":
                action = "poweroff" if force else "acpipowerbutton"
                rc, out = VirtualizationTool._vbox(["controlvm", name, action])
            elif hypervisor == "libvirt":
                conn = VirtualizationTool._libvirt_conn()
                dom  = conn.lookupByName(name)
                rc   = dom.destroy() if force else dom.shutdown()
                out  = ""
                conn.close()
            elif hypervisor == "vmware":
                mode = "hard" if force else "soft"
                r  = subprocess.run(["vmrun", "stop", name, mode], capture_output=True, text=True)
                rc, out = r.returncode, r.stdout + r.stderr
            else:
                return ToolResult(False, f"✗ Unknown hypervisor: {hypervisor}")
            return ToolResult(rc == 0, f"✓ Stopped VM: {name}")
        except Exception as e:
            return ToolResult(False, f"✗ stop_vm failed: {e}")

    @staticmethod
    def restart_vm(name: str, hypervisor: str = "virtualbox") -> ToolResult:
        try:
            VirtualizationTool.stop_vm(name, hypervisor)
            import time; time.sleep(3)
            return VirtualizationTool.start_vm(name, hypervisor)
        except Exception as e:
            return ToolResult(False, f"✗ restart_vm failed: {e}")

    @staticmethod
    def suspend_vm(name: str, hypervisor: str = "virtualbox") -> ToolResult:
        try:
            if hypervisor == "virtualbox":
                rc, out = VirtualizationTool._vbox(["controlvm", name, "savestate"])
            elif hypervisor == "libvirt":
                conn = VirtualizationTool._libvirt_conn()
                dom  = conn.lookupByName(name)
                dom.managedSave()
                conn.close(); rc = 0; out = ""
            elif hypervisor == "vmware":
                r  = subprocess.run(["vmrun", "suspend", name], capture_output=True, text=True)
                rc, out = r.returncode, r.stdout
            else:
                return ToolResult(False, f"✗ Unknown hypervisor: {hypervisor}")
            return ToolResult(rc == 0, f"✓ Suspended VM: {name}")
        except Exception as e:
            return ToolResult(False, f"✗ suspend_vm failed: {e}")

    @staticmethod
    def resume_vm(name: str, hypervisor: str = "virtualbox") -> ToolResult:
        try:
            if hypervisor == "virtualbox":
                rc, out = VirtualizationTool._vbox(["startvm", name, "--type", "headless"])
            elif hypervisor == "libvirt":
                conn = VirtualizationTool._libvirt_conn()
                dom  = conn.lookupByName(name)
                dom.create()
                conn.close(); rc = 0; out = ""
            elif hypervisor == "vmware":
                r  = subprocess.run(["vmrun", "start", name], capture_output=True, text=True)
                rc, out = r.returncode, r.stdout
            else:
                return ToolResult(False, f"✗ Unknown hypervisor: {hypervisor}")
            return ToolResult(rc == 0, f"✓ Resumed VM: {name}")
        except Exception as e:
            return ToolResult(False, f"✗ resume_vm failed: {e}")

    @staticmethod
    def create_snapshot(
        name: str, snapshot_name: str, hypervisor: str = "virtualbox"
    ) -> ToolResult:
        try:
            if hypervisor == "virtualbox":
                rc, out = VirtualizationTool._vbox(["snapshot", name, "take", snapshot_name])
            elif hypervisor == "libvirt":
                import xml.etree.ElementTree as ET
                conn = VirtualizationTool._libvirt_conn()
                dom  = conn.lookupByName(name)
                snap_xml = f"<domainsnapshot><name>{snapshot_name}</name></domainsnapshot>"
                dom.snapshotCreateXML(snap_xml, 0)
                conn.close(); rc = 0; out = ""
            elif hypervisor == "vmware":
                r  = subprocess.run(["vmrun", "snapshot", name, snapshot_name], capture_output=True, text=True)
                rc, out = r.returncode, r.stdout
            else:
                return ToolResult(False, f"✗ Unknown hypervisor: {hypervisor}")
            return ToolResult(rc == 0, f"✓ Snapshot '{snapshot_name}' created for VM '{name}'")
        except Exception as e:
            return ToolResult(False, f"✗ create_snapshot failed: {e}")

    @staticmethod
    def restore_snapshot(
        name: str, snapshot_name: str, hypervisor: str = "virtualbox"
    ) -> ToolResult:
        try:
            if hypervisor == "virtualbox":
                rc, out = VirtualizationTool._vbox(["snapshot", name, "restore", snapshot_name])
            elif hypervisor == "libvirt":
                conn = VirtualizationTool._libvirt_conn()
                dom  = conn.lookupByName(name)
                snap = dom.snapshotLookupByName(snapshot_name, 0)
                dom.revertToSnapshot(snap, 0)
                conn.close(); rc = 0; out = ""
            elif hypervisor == "vmware":
                r  = subprocess.run(["vmrun", "revertToSnapshot", name, snapshot_name], capture_output=True, text=True)
                rc, out = r.returncode, r.stdout
            else:
                return ToolResult(False, f"✗ Unknown hypervisor: {hypervisor}")
            return ToolResult(rc == 0, f"✓ Restored snapshot '{snapshot_name}' for VM '{name}'")
        except Exception as e:
            return ToolResult(False, f"✗ restore_snapshot failed: {e}")

    @staticmethod
    def delete_snapshot(
        name: str, snapshot_name: str, hypervisor: str = "virtualbox"
    ) -> ToolResult:
        try:
            if hypervisor == "virtualbox":
                rc, out = VirtualizationTool._vbox(["snapshot", name, "delete", snapshot_name])
            elif hypervisor == "libvirt":
                conn = VirtualizationTool._libvirt_conn()
                dom  = conn.lookupByName(name)
                snap = dom.snapshotLookupByName(snapshot_name, 0)
                snap.delete(0)
                conn.close(); rc = 0; out = ""
            elif hypervisor == "vmware":
                r  = subprocess.run(["vmrun", "deleteSnapshot", name, snapshot_name], capture_output=True, text=True)
                rc, out = r.returncode, r.stdout
            else:
                return ToolResult(False, f"✗ Unknown hypervisor: {hypervisor}")
            return ToolResult(rc == 0, f"✓ Snapshot '{snapshot_name}' deleted")
        except Exception as e:
            return ToolResult(False, f"✗ delete_snapshot failed: {e}")

    @staticmethod
    def list_snapshots(name: str, hypervisor: str = "virtualbox") -> ToolResult:
        try:
            if hypervisor == "virtualbox":
                rc, out = VirtualizationTool._vbox(["snapshot", name, "list"])
                return ToolResult(rc == 0, f"✓ Snapshots for '{name}'", out.splitlines())
            elif hypervisor == "libvirt":
                conn = VirtualizationTool._libvirt_conn()
                dom  = conn.lookupByName(name)
                snaps = [s.getName() for s in dom.listAllSnapshots()]
                conn.close()
                return ToolResult(True, f"✓ {len(snaps)} snapshot(s)", snaps)
            elif hypervisor == "vmware":
                r  = subprocess.run(["vmrun", "listSnapshots", name], capture_output=True, text=True)
                return ToolResult(True, "✓ Snapshots listed", r.stdout.splitlines())
            return ToolResult(False, f"✗ Unknown hypervisor: {hypervisor}")
        except Exception as e:
            return ToolResult(False, f"✗ list_snapshots failed: {e}")

    @staticmethod
    def get_vm_info(name: str, hypervisor: str = "virtualbox") -> ToolResult:
        try:
            if hypervisor == "virtualbox":
                rc, out = VirtualizationTool._vbox(["showvminfo", name, "--machinereadable"])
                info = dict(line.split("=", 1) for line in out.splitlines() if "=" in line)
                return ToolResult(rc == 0, f"✓ VM info: {name}", info)
            elif hypervisor == "libvirt":
                conn = VirtualizationTool._libvirt_conn()
                dom  = conn.lookupByName(name)
                info = {"name": dom.name(), "state": dom.isActive(), "max_memory": dom.maxMemory(), "vcpus": dom.maxVcpus()}
                conn.close()
                return ToolResult(True, f"✓ VM info: {name}", info)
            elif hypervisor == "vmware":
                r  = subprocess.run(["vmrun", "getGuestIPAddress", name], capture_output=True, text=True)
                return ToolResult(True, "✓ VM info", {"ip": r.stdout.strip()})
            return ToolResult(False, f"✗ Unknown hypervisor: {hypervisor}")
        except Exception as e:
            return ToolResult(False, f"✗ get_vm_info failed: {e}")

    @staticmethod
    def set_vm_resources(
        name: str, cpus: int = None, memory_mb: int = None, hypervisor: str = "virtualbox"
    ) -> ToolResult:
        try:
            if hypervisor == "virtualbox":
                if cpus:
                    VirtualizationTool._vbox(["modifyvm", name, "--cpus", str(cpus)])
                if memory_mb:
                    VirtualizationTool._vbox(["modifyvm", name, "--memory", str(memory_mb)])
            elif hypervisor == "libvirt":
                conn = VirtualizationTool._libvirt_conn()
                dom  = conn.lookupByName(name)
                if memory_mb:
                    dom.setMaxMemory(memory_mb * 1024)
                    dom.setMemory(memory_mb * 1024)
                if cpus:
                    dom.setVcpus(cpus)
                conn.close()
            elif hypervisor == "vmware":
                if cpus:
                    subprocess.run(["vmrun", "writeVariable", name, "runtimeConfig", "numvcpus", str(cpus)], capture_output=True)
            return ToolResult(True, f"✓ VM resources updated: {name} (CPU={cpus}, RAM={memory_mb}MB)")
        except Exception as e:
            return ToolResult(False, f"✗ set_vm_resources failed: {e}")

    @staticmethod
    def clone_vm(
        source: str, destination: str, hypervisor: str = "virtualbox"
    ) -> ToolResult:
        try:
            if hypervisor == "virtualbox":
                rc, out = VirtualizationTool._vbox(["clonevm", source, "--name", destination, "--register"])
            elif hypervisor == "libvirt":
                r  = subprocess.run(["virt-clone", "--original", source, "--name", destination, "--auto-clone"], capture_output=True, text=True)
                rc, out = r.returncode, r.stdout + r.stderr
            else:
                return ToolResult(False, f"✗ clone_vm not supported for {hypervisor}")
            return ToolResult(rc == 0, f"✓ Cloned '{source}' → '{destination}'")
        except Exception as e:
            return ToolResult(False, f"✗ clone_vm failed: {e}")

    @staticmethod
    def export_vm(
        name: str,
        output_path: str,
        format: str = "ova",
        hypervisor: str = "virtualbox",
    ) -> ToolResult:
        try:
            if hypervisor == "virtualbox":
                rc, out = VirtualizationTool._vbox(["export", name, "--output", output_path])
            elif hypervisor == "libvirt":
                r  = subprocess.run(
                    ["virsh", "dumpxml", name], capture_output=True, text=True
                )
                from pathlib import Path
                Path(output_path).write_text(r.stdout)
                rc, out = r.returncode, output_path
            else:
                return ToolResult(False, f"✗ export_vm not supported for {hypervisor}")
            return ToolResult(rc == 0, f"✓ VM '{name}' exported to {output_path}")
        except Exception as e:
            return ToolResult(False, f"✗ export_vm failed: {e}")

    @staticmethod
    def run_in_vm(name: str, command: str, hypervisor: str = "virtualbox") -> ToolResult:
        try:
            if hypervisor == "virtualbox":
                rc, out = VirtualizationTool._vbox([
                    "guestcontrol", name, "run",
                    "--exe", "/bin/bash", "--", "bash", "-c", command,
                ])
            elif hypervisor == "vmware":
                creds  = CredStore.load("vmware")
                r  = subprocess.run(
                    ["vmrun", "-gu", creds.get("user", ""), "-gp", creds.get("password", ""),
                     "runProgramInGuest", name, "/bin/bash", "-c", command],
                    capture_output=True, text=True,
                )
                rc, out = r.returncode, r.stdout + r.stderr
            else:
                return ToolResult(False, f"✗ run_in_vm not supported for {hypervisor}")
            return ToolResult(rc == 0, f"✓ Command ran in VM '{name}'", out.strip())
        except Exception as e:
            return ToolResult(False, f"✗ run_in_vm failed: {e}")

    @staticmethod
    def copy_to_vm(
        name: str, local_path: str, vm_path: str, hypervisor: str = "virtualbox"
    ) -> ToolResult:
        try:
            if hypervisor == "virtualbox":
                rc, out = VirtualizationTool._vbox([
                    "guestcontrol", name, "copyto", local_path, vm_path, "--recursive",
                ])
            elif hypervisor == "vmware":
                creds  = CredStore.load("vmware")
                r  = subprocess.run(
                    ["vmrun", "-gu", creds.get("user", ""), "-gp", creds.get("password", ""),
                     "copyFileFromHostToGuest", name, local_path, vm_path],
                    capture_output=True, text=True,
                )
                rc, out = r.returncode, r.stdout + r.stderr
            else:
                return ToolResult(False, f"✗ copy_to_vm not supported for {hypervisor}")
            return ToolResult(rc == 0, f"✓ Copied '{local_path}' to VM '{name}':{vm_path}")
        except Exception as e:
            return ToolResult(False, f"✗ copy_to_vm failed: {e}")

    @staticmethod
    def create_vm(
        name: str,
        os: str = "Ubuntu_64",
        cpus: int = 2,
        memory: int = 2048,
        disk_size: int = 20000,
        iso_path: str = "",
        hypervisor: str = "virtualbox",
    ) -> ToolResult:
        try:
            if hypervisor == "virtualbox":
                for cmd in [
                    ["createvm", "--name", name, "--ostype", os, "--register"],
                    ["modifyvm", name, "--memory", str(memory), "--cpus", str(cpus), "--nic1", "nat"],
                    ["createhd", "--filename", f"{name}.vdi", "--size", str(disk_size)],
                    ["storagectl", name, "--name", "SATA", "--add", "sata"],
                    ["storageattach", name, "--storagectl", "SATA", "--port", "0", "--type", "hdd", "--medium", f"{name}.vdi"],
                ]:
                    rc, out = VirtualizationTool._vbox(cmd)
                    if rc != 0:
                        return ToolResult(False, f"✗ VBox create_vm step failed: {out}")
                if iso_path:
                    VirtualizationTool._vbox([
                        "storageattach", name, "--storagectl", "SATA",
                        "--port", "1", "--type", "dvddrive", "--medium", iso_path,
                    ])
            elif hypervisor == "libvirt":
                r  = subprocess.run([
                    "virt-install", "--name", name, "--memory", str(memory),
                    "--vcpus", str(cpus), "--disk", f"size={disk_size // 1024}",
                    "--os-type", "linux", "--os-variant", os.lower(),
                    "--noautoconsole",
                ] + (["--cdrom", iso_path] if iso_path else ["--import"]),
                    capture_output=True, text=True,
                )
                return ToolResult(r.returncode == 0, r.stdout + r.stderr)
            else:
                return ToolResult(False, f"✗ create_vm not supported for {hypervisor}")
            return ToolResult(True, f"✓ VM '{name}' created ({os}, {cpus} CPUs, {memory}MB RAM, {disk_size}MB disk)")
        except Exception as e:
            return ToolResult(False, f"✗ create_vm failed: {e}")
