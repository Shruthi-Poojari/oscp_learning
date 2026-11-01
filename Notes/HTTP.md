# Notes — HTTP / HTTPS (80 / 443 / 8080 / 8443)

> Authorized lab/OSCP use only.

## What it is
Web services — the richest attack surface on most boxes. Treat every web port as its own investigation.

## Fingerprint
```bash
whatweb http://$IP
curl -I http://$IP
nmap --script http-enum,http-title,http-headers -p80 $IP
```

## Content Discovery
```bash
feroxbuster -u http://$IP -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
gobuster dir -u http://$IP -w /usr/share/wordlists/dirb/common.txt -x php,txt,html
# always check:
curl http://$IP/robots.txt
curl http://$IP/sitemap.xml
```

## Vhost / Subdomain
```bash
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
     -H "Host: FUZZ.$DOMAIN" -u http://$IP -fs <baseline-size>
```

## Manual Review Checklist
- [ ] View page source + linked JS for comments, endpoints, keys
- [ ] Login forms → default/weak creds
- [ ] Parameters → injection (SQLi, LFI, command injection)
- [ ] File upload features → webshell
- [ ] Error messages → stack/version leaks
- [ ] `/robots.txt`, `/.git/`, backup files (`.bak`, `~`)

## CMS-specific
```bash
wpscan --url http://$IP -e vp,u
droopescan scan drupal -u http://$IP
joomscan -u http://$IP
```

## Common flaws → tools
| Flaw | Approach |
|------|----------|
| SQLi | manual, then `sqlmap` |
| LFI/RFI | `../` traversal, php filters/wrappers |
| Command injection | `;`, `|`, `` ` `` in params |
| Upload | bypass extension filters, hit the uploaded path |
| Default creds | admin panels, Tomcat `/manager/html`, Jenkins |

## Common Mistakes
- Only scanning 80 and ignoring 8080/8443 or HTTPS.
- Not reading source / JS.
- Giving up before recursive + extension-based brute force.

## OSCP Tips
- Use Burp Repeater for manual testing.
- Match wordlist extensions to the detected stack (`-x php` on PHP).
- Note the exact framework/CMS version → searchsploit.
