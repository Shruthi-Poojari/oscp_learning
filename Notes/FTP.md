# Notes — FTP (21)

> Authorized lab/OSCP use only.

## What it is
File Transfer Protocol. Cleartext by default. Common wins: anonymous login, writable directories, known-vuln daemon versions.

## Enumeration
```bash
nmap -sC -sV -p21 $IP
nmap --script "ftp-anon,ftp-syst,ftp-vsftpd-backdoor" -p21 $IP

ftp $IP
#   login: anonymous / <blank>  (or ftp/ftp)
#   ls -la
#   binary
#   get <file>   /   put <test.txt>   (check write access)
```

Non-interactive pull:
```bash
wget -r ftp://anonymous:anonymous@$IP/
```

## What to check
| Check | Why |
|-------|-----|
| Anonymous login | Free file access |
| Write access | Upload webshell if FTP root = web root |
| Version | e.g. vsftpd 2.3.4 backdoor (CVE-2011-2523) — *often a red herring*, verify |
| ProFTPD versions | mod_copy (CVE-2015-3306) in some boxes |

## Common Mistakes
- Forgetting `binary` mode → corrupted downloads.
- Not testing upload (writable FTP + known web root = RCE).
- Assuming a vulnerable banner is exploitable without testing (see HTB Lame vsftpd).

## OSCP Tips
- Always try anonymous first.
- Cross-check the FTP root against a discovered web root — upload path to RCE.
- Capture creds if combined with cleartext protocols.
