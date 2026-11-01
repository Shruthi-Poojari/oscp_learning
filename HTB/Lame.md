# HTB — Lame

> **Authorized lab only.** Lame is a *retired* Hack The Box machine used for OSCP-style learning. The vulnerabilities below are 15+ years old, patched, and publicly documented. Techniques apply only to this lab box or systems you are authorized to test.

---

## Machine Overview

| Field | Value |
|-------|-------|
| Machine Name | Lame |
| Operating System | Linux (Ubuntu, old) |
| Difficulty | Easy |
| Key Learning Objectives | Full-port enumeration, Samba version→CVE mapping, FTP/distcc analysis, manual vs. automated exploitation, direct-to-root service misconfig |
| Technologies Observed | vsftpd 2.3.4, OpenSSH 4.7p1, Samba 3.0.20, distcc |

---

## Initial Enumeration

### Host Discovery

```bash
export IP=10.10.10.3
ping -c1 $IP        # TTL ~64 → Linux
```
ICMP may be filtered; use `-Pn` if the host "appears down."

### Nmap Results

```bash
nmap -p- --min-rate 10000 -Pn -n --open -oN scans/allports.txt $IP
nmap -sC -sV -p21,22,139,445,3632 -oN scans/detail.txt $IP
```

| Port | Protocol | Service | Version | Notes |
|------|----------|---------|---------|-------|
| 21 | TCP | FTP | vsftpd 2.3.4 | Anonymous login allowed; version has a famous backdoor CVE |
| 22 | TCP | SSH | OpenSSH 4.7p1 | Old but not the intended path |
| 139 | TCP | NetBIOS-SSN | Samba smbd 3.0.20-Debian | **Primary vector** — username map script RCE |
| 445 | TCP | SMB | Samba smbd 3.0.20-Debian | Same service as 139 |
| 3632 | TCP | distccd | distccd v1 (GNU) | Distributed compiler daemon — CVE-2004-2687 RCE |

**Why each service matters:**
- **21 vsftpd 2.3.4** — this version shipped with a backdoor (CVE-2011-2523) triggered by a `:)` smiley in the username, opening a root shell on 6200. *On Lame this is a red herring* — the backdoor port is typically filtered/non-functional, teaching you not to assume a known-vuln version is always exploitable.
- **139/445 Samba 3.0.20** — vulnerable to CVE-2007-2447 ("username map script" command injection). This is the intended, cleanest foothold → **root directly**.
- **3632 distcc** — CVE-2004-2687 allows command execution; an alternative path that lands as the `daemon` user and then needs a privesc step.

---

## Service Analysis

### FTP (21) — vsftpd 2.3.4
- **What:** File Transfer Protocol daemon.
- **Why exposed:** Anonymous file sharing left enabled.
- **Security implication:** Known backdoored build; cleartext protocol.
- **Enumeration:**
  ```bash
  ftp $IP            # login: anonymous / <blank>
  ls -la
  ```
- **Observation:** Anonymous works but the directory is empty; the backdoor trigger generally fails on this box. **Lesson: verify, don't assume.**

### SSH (22) — OpenSSH 4.7p1
- **What:** Secure remote shell.
- **Why exposed:** Standard admin access.
- **Security implication:** Old version, but no usable credentials and no reliable pre-auth RCE here.
- **Role:** Not the entry point; note it and move on.

### SMB (139/445) — Samba 3.0.20
- **What:** Windows-style file sharing implemented by Samba on Linux.
- **Why exposed:** File-sharing service left on with a dangerous config.
- **Security implication:** CVE-2007-2447 — when `username map script` is enabled, the username field is passed to a shell, allowing command injection in the smbd process (**runs as root**).
- **Enumeration:**
  ```bash
  smbclient -L //$IP/ -N
  enum4linux -a $IP
  nmap --script "smb-os-discovery,smb-vuln*" -p139,445 $IP
  ```
- **Observation:** Version 3.0.20 is in the vulnerable range (3.0.0–3.0.25rc3). This is the headline finding.

### distcc (3632)
- **What:** Daemon that distributes C/C++ compilation across machines.
- **Why exposed:** Misconfigured to accept connections without restriction.
- **Security implication:** CVE-2004-2687 — crafted compile jobs execute arbitrary commands as the `daemon` user.
- **Enumeration:**
  ```bash
  nmap --script distcc-cve2004-2687 -p3632 $IP
  ```

---

## Attack Surface Assessment

| Category | Finding |
|----------|---------|
| Network services | FTP, SSH, SMB (x2), distcc exposed to the network |
| Authentication | Anonymous FTP; SMB reachable without valid creds via the vuln |
| Legacy software | Every service is years out of date (Samba 3.0.20, vsftpd 2.3.4, distcc v1) |
| Misconfigurations | Samba `username map script` enabled; distcc open to all |
| Security weaknesses | Multiple pre-auth RCE paths; smbd running as root |

---

## Enumeration Timeline

1. **Initial recon** — Full-port scan reveals 21, 22, 139, 445, 3632.
2. **Service investigation** — Version scan flags Samba 3.0.20 and distcc as high-value; vsftpd 2.3.4 noted as a possible (but likely dead) lead.
3. **Validation** — `searchsploit samba 3.0.20` and `searchsploit distcc` confirm public CVEs; test the vsftpd backdoor and find it non-functional.
4. **Findings** — CVE-2007-2447 (Samba) gives root directly; CVE-2004-2687 (distcc) gives a `daemon` shell as a backup.
5. **Lessons learned** — Always full-port scan (3632 is above the top-1000 default on some scans); a known-vuln banner isn't a guarantee; pick the cleanest path.

---

## User Access Learnings

On Lame there isn't a separate low-priv "user" stage for the Samba path — the misconfiguration lands you as **root immediately**. The `user.txt` and `root.txt` are both readable once you have the root shell.

- **Discovery process:** Map Samba 3.0.20 → CVE-2007-2447.
- **Enumeration logic:** The `username map script` option passes the SMB username to `/bin/sh -c`, so a username crafted with shell metacharacters executes commands.
- **Key indicator:** Samba version in the 3.0.x vulnerable range.
- **High-level exploitation:** Authenticate to the SMB service supplying a username that contains a shell command inside `` `...` `` / `"/=`...`"` style injection, so smbd runs the embedded command. A standard way to do this is via the Metasploit module `exploit/multi/samba/usermap_script`, or manually with a Python/smb client that lets you set a raw username field. The payload is simply a reverse shell back to your listener:
  ```bash
  # on attacker
  nc -lvnp 4444
  ```
  The injected command is a `nc`/`bash -i` reverse shell to your IP:4444. Because smbd runs as root, the returned shell is **root**.

> **OSCP note:** Practice this *without* Metasploit at least once — understanding that the username field reaches a shell is the real lesson. The `smbclient`/`impacket` manual method sets the malicious username and connects to any share.

---

## Privilege Escalation Learnings

- **Samba path:** No escalation needed — smbd runs as root, so the foothold **is** root.
- **distcc path (if used instead):** You land as `daemon`. From there, enumerate for escalation:
  ```bash
  id
  sudo -l
  find / -perm -4000 2>/dev/null       # SUID binaries
  uname -a
  ```
  On Lame, the classic distcc→root step abuses a SUID `nmap` (old interactive mode) or a kernel/`udev` issue depending on box state. The teaching point: a service-level RCE as a low-priv account still requires a separate local privesc.

**Misconfigurations observed:** service running as root (Samba), unrestricted compile daemon (distcc), legacy SUID binaries.

**Hardening opportunities:** patch/upgrade, drop privileges, disable dangerous config options, firewall internal services.

---

## Detection Opportunities (Blue Team)

| Signal | Where to look |
|--------|---------------|
| Log sources | `/var/log/samba/`, auth logs, distccd logs |
| Network indicators | Outbound connection from the server to an external IP:4444 (reverse shell); inbound to 3632 |
| Security events | smbd spawning `/bin/sh`, `nc`, or `bash -i` child processes |
| Monitoring recs | Alert on service daemons spawning shells; egress filtering to block reverse shells; IDS signatures for CVE-2007-2447 / CVE-2004-2687 patterns |

---

## Mitigations

| Area | Recommendation |
|------|----------------|
| Configuration | Remove/disable `username map script` in `smb.conf`; bind distcc to localhost or require auth; disable anonymous FTP |
| Hardening | Run services as unprivileged users; apply least privilege; network-segment internal services |
| Patching | Upgrade Samba to ≥3.0.25, vsftpd to a clean build, remove/upgrade distcc |
| Monitoring | Process-ancestry alerting, egress filtering, host IDS |

---

## OSCP Exam Takeaways

- **Enumeration lessons:** Full-port scan always (3632 would be missed otherwise); version→CVE mapping via `searchsploit`.
- **Common exam patterns:** A single misconfigured service giving direct root; a tempting red-herring version (vsftpd) that doesn't pan out.
- **Similar machine types:** Any box with legacy Samba, exposed compile/build daemons, or anonymous services.
- **Key commands worth remembering:**
  ```bash
  nmap -p- --min-rate 10000 -Pn $IP
  searchsploit samba 3.0.20
  enum4linux -a $IP
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
- Manual (no-MSF) Samba usermap exploitation:
- distcc path writeup:

### Additional Research
- CVE-2007-2447 advisory:
- CVE-2004-2687 details:

### Sample Writeups (reference)
- [7h3rAm / svachal writeup](samples/Lame-7h3rAm-writeup.md) — concise enumeration→exploitation→post-exploitation flow; manual (non-MSF) `usermap_script` PoC.
- teckk2: <https://teckk2.github.io/writeup/2017/12/17/Lame.html>
- System Weakness (no-MSF): <https://medium.com/system-weakness/htb-lame-walkthrough-w-o-metasploit-66531deb8a88>
- dev.to (no-MSF): <https://dev.to/micheaol/htb-lame-no-metasploit-walkthrough-1g34>
