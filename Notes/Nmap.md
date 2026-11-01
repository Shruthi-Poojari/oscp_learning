# Notes — Nmap

> Authorized lab/OSCP use only.

## Workflow

```bash
export IP=10.10.10.10
# 1) Find all open TCP ports fast
nmap -p- --min-rate 10000 -Pn -n --open -oN scans/all.txt $IP
# 2) Version + default scripts on just those ports
nmap -sC -sV -p<ports> -oN scans/detail.txt $IP
# 3) UDP top ports
sudo nmap -sU --top-ports 50 -oN scans/udp.txt $IP
# 4) Vuln scripts where relevant
nmap --script vuln -p<ports> -oN scans/vuln.txt $IP
```

## Key Flags

| Flag | Meaning |
|------|---------|
| `-p-` | All 65535 TCP ports |
| `-sC` | Default NSE scripts |
| `-sV` | Version detection |
| `-sU` | UDP scan (root) |
| `-O` | OS detection (root) |
| `-A` | Aggressive (`-sC -sV -O --traceroute`) |
| `-Pn` | Skip host discovery |
| `-n` | No DNS resolution |
| `--min-rate` | Minimum packets/sec |
| `-T0..T5` | Timing (T4 safe on labs) |
| `-oN/-oG/-oX/-oA` | Output normal/grepable/XML/all |

## Scan Types

| Type | Flag | Use |
|------|------|-----|
| TCP SYN | `-sS` | Default stealth (root) |
| TCP connect | `-sT` | No-root / pivot scans |
| UDP | `-sU` | SNMP/TFTP/DNS |
| Ping sweep | `-sn` | Host discovery only |

## NSE

```bash
ls /usr/share/nmap/scripts/ | grep <service>
nmap --script "smb-vuln*" -p445 $IP
nmap --script http-enum -p80 $IP
```

## Common Mistakes
- Skipping `-p-` → missing high ports.
- Running `-sV` on all 65535 ports first (slow). Discover, *then* version-scan.
- Forgetting `-Pn` when ICMP is filtered → "host down" false negative.
- Not saving output (`-oN`) → no reproducible evidence for the report.

## OSCP Tips
- Keep every scan in a `scans/` folder per box.
- Pipe versions into `searchsploit` immediately.
- UDP is slow — kick it off in parallel and keep working TCP.
