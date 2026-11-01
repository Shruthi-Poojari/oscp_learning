# Notes — DNS (53)

> Authorized lab/OSCP use only.

## What it is
Domain Name System (TCP+UDP 53). Interesting for zone transfers, hostname discovery, and identifying Domain Controllers.

## Enumeration
```bash
nmap -sC -sV -p53 $IP
nmap --script dns-zone-transfer --script-args dns-zone-transfer.domain=<domain> -p53 $IP

# Identify the nameserver / records
dig @$IP <domain>
dig @$IP <domain> ANY
nslookup
#   > server $IP
#   > <domain>
```

## Zone Transfer (AXFR)
```bash
dig axfr @$IP <domain>
host -l <domain> $IP
```
A successful AXFR dumps all records — subdomains, internal hosts, mail servers.

## Subdomain brute (when DNS is authoritative)
```bash
gobuster dns -d <domain> -r $IP -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
```

## Tips
- Add discovered hostnames to `/etc/hosts` so vhosts/TLS resolve.
- DNS + Kerberos (88) + LDAP (389) on one host = Domain Controller.

## Common Mistakes
- Not trying AXFR.
- Forgetting to specify the domain to `dig`/nmap.
- Missing `/etc/hosts` entries, breaking name-based web vhosts.
