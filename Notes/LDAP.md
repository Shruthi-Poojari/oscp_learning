# Notes — LDAP (389 / 636)

> Authorized lab/OSCP use only.

## What it is
Lightweight Directory Access Protocol. On Active Directory it exposes users, groups, computers, and policies. 389 = cleartext/StartTLS, 636 = LDAPS. A strong Domain Controller indicator.

## Enumeration
```bash
nmap -sC -sV -p389 $IP
nmap --script "ldap-rootdse,ldap-search" -p389 $IP

# Anonymous bind — find naming context
ldapsearch -x -H ldap://$IP -s base namingcontexts

# Dump everything under the base DN (anonymous)
ldapsearch -x -H ldap://$IP -b "DC=domain,DC=local"

# Authenticated
ldapsearch -x -H ldap://$IP -D "user@domain.local" -w pass -b "DC=domain,DC=local"
```

## Mass dump
```bash
ldapdomaindump -u 'domain\user' -p pass $IP -o loot/
```

## What to look for
| Item | Why |
|------|-----|
| `namingContexts` | Confirms domain DN to query |
| User objects | Usernames for spraying/roasting |
| `description` fields | Passwords are sometimes stored here |
| Group membership | Privilege mapping (Domain Admins) |
| `servicePrincipalName` | Kerberoasting targets |

## Common Mistakes
- Not testing anonymous bind.
- Forgetting the base DN (`-b`).
- Ignoring `description`/`info` attributes that leak secrets.

## OSCP Tips
- 389 + 88 + 445 together → Domain Controller; pivot to BloodHound.
- Feed enumerated users into `GetNPUsers.py` (AS-REP) and `GetUserSPNs.py` (Kerberoast).
