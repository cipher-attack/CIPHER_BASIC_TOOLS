# CIPHER_BASIC_TOOLS

Educational security-learning tools and a small vulnerable lab for hands-on practice. Use responsibly and only on systems you own or are explicitly permitted to test.

## Contents
- Tools (`tools/`):
  - `port_scanner.py`: Fast TCP port scanner (localhost by default)
  - `dir_discover.py`: HTTP directory discovery using a wordlist
  - `hash_cracker.py`: MD5/SHA1/SHA256 wordlist-based cracker
  - `jwt_inspector.py`: Decode JWTs and optionally verify HS256
- Wordlists (`wordlists/`): minimal demo wordlists for paths and passwords
- Lab (`lab/`): local-only Flask app with intentional SQLi and XSS vulnerabilities

## Quick start
1) Create a virtual environment and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) Start the vulnerable lab (localhost only):

```bash
python lab/app.py
```

Then open `http://127.0.0.1:8000` in a browser.

3) Try the tools against the lab:

```bash
# Port scan (defaults to localhost)
python tools/port_scanner.py --ports 8000-8010

# Directory discovery
python tools/dir_discover.py --url http://127.0.0.1:8000 --wordlist wordlists/paths.txt --status 200,301,302,403

# Hash cracker (example MD5 for "hello")
python tools/hash_cracker.py --hash 5d41402abc4b2a76b9719d911017c592 --alg md5 --wordlist wordlists/passwords.txt

# JWT inspector
python tools/jwt_inspector.py --token <your.jwt.here>
```

## Ethics and scope
- These tools are for learning and self-assessment only.
- Do not scan or attack networks or systems without explicit permission.
- The lab is intentionally vulnerable; never deploy it publicly.

## Notes
- Defaults are safe and target `127.0.0.1` to avoid accidental misuse.
- Wordlists are intentionally small to keep runs quick and controlled.
