# OSCP Prep Repository

Personal OSCP preparation notes, methodology, and retired-HTB machine writeups, with a small Flask web app to browse everything in one place.

> Authorized lab / OSCP learning use only (HTB retired machines, PWK labs, systems you own or are contracted to test).

---

## Repository Layout

```
.
├── OSCP-Methodology.md       # master methodology, port reference, tool notes, exam checklist
├── Notes/                    # per-topic reference notes
│   ├── Nmap.md   SMB.md   FTP.md   HTTP.md   DNS.md
│   ├── LDAP.md   MSSQL.md WinRM.md PrivEsc.md
│   ├── Metasploit.md  Reverse-Shells.md  File-Transfer.md
├── HTB/                      # retired machine writeups
│   ├── Lame.md   Legacy.md
│   └── samples/              # reference writeups (see note below)
└── webapp/                   # Flask notes viewer
```

---

## Running the Web App

The app reads every `.md` file in this repo and serves it with a grouped sidebar,
rendered tables, and syntax-highlighted code blocks.

### 1. One-time setup
```bash
cd webapp
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

### 2. Start the server
```bash
cd webapp
./.venv/bin/python app.py
```

Leave this terminal open. You should see:
```
 * Running on http://127.0.0.1:5000
```

### 3. Open in a browser
Go to **<http://127.0.0.1:5000>** — it redirects to the methodology guide, and the
sidebar links to every note. Stop the server anytime with **Ctrl+C**.

---

## Direct Page URLs

| Note | URL |
|------|-----|
| Methodology (home) | <http://127.0.0.1:5000/view/OSCP-Methodology.md> |
| HTB — Lame | <http://127.0.0.1:5000/view/HTB/Lame.md> |
| HTB — Legacy | <http://127.0.0.1:5000/view/HTB/Legacy.md> |
| Nmap | <http://127.0.0.1:5000/view/Notes/Nmap.md> |
| SMB | <http://127.0.0.1:5000/view/Notes/SMB.md> |
| FTP | <http://127.0.0.1:5000/view/Notes/FTP.md> |
| HTTP | <http://127.0.0.1:5000/view/Notes/HTTP.md> |
| DNS | <http://127.0.0.1:5000/view/Notes/DNS.md> |
| LDAP | <http://127.0.0.1:5000/view/Notes/LDAP.md> |
| MSSQL | <http://127.0.0.1:5000/view/Notes/MSSQL.md> |
| WinRM | <http://127.0.0.1:5000/view/Notes/WinRM.md> |
| Privilege Escalation | <http://127.0.0.1:5000/view/Notes/PrivEsc.md> |
| Metasploit | <http://127.0.0.1:5000/view/Notes/Metasploit.md> |
| Reverse Shells | <http://127.0.0.1:5000/view/Notes/Reverse-Shells.md> |
| File Transfer | <http://127.0.0.1:5000/view/Notes/File-Transfer.md> |

> New `.md` files are picked up automatically — just reload the page, no restart needed.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ERR_CONNECTION_REFUSED` | The server isn't running — start `app.py` first and keep the terminal open. |
| Port 5000 already in use (macOS AirPlay) | Change `port=5000` in [webapp/app.py](webapp/app.py) to e.g. `8000`, then open `127.0.0.1:8000`. Or disable AirPlay Receiver in System Settings. |
| `ModuleNotFoundError` | Run with the venv python: `./.venv/bin/python app.py` (not bare `python`). |

---

## Notes on `HTB/samples/`

The files under `HTB/samples/` are derived from a third-party public writeup
(originally by **svachal / @7h3rAm**) and were kept as a format reference.
`HTB/Lame.md` and `HTB/Legacy.md` are original notes. If you want a repo with no
third-party-derived content, delete the `samples/` folder.
