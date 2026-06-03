# -*- coding: utf-8 -*-
"""
WebCraft TRESOR — verschluesselter Schluessel-Container fuer das Team.

Packt die sensiblen Dateien (alle API-Keys + Google-Token) in EINE verschluesselte
Datei `shared/tresor.enc` (AES via Fernet, Passwort -> PBKDF2-SHA256, 390k Iterationen).
Die `tresor.enc` darf geteilt werden (z. B. Cloud/Download) — sie ist ohne Passwort wertlos.
Das PASSWORT wird NIE gespeichert/verschickt: separat per Anruf/Signal an die Brueder geben.

Inhalt des Tresors:
  - auto_system/config.py            (alle Keys: Maps, Netlify, Pexels, Stripe, CRM-Sheet-ID, ...)
  - ~/.claude/google_token.pickle    (Google-Zugriff fuer Sheets/Gmail)

Bedienung:
  Maxime (einmal/aktualisieren):  python shared/tresor.py lock
  Bruder (Ersteinrichtung):       python shared/tresor.py unlock
  Pruefen, was drin ist:          python shared/tresor.py info
"""
import sys, os, json, base64, getpass
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ROOT = Path(__file__).resolve().parent.parent          # webcraft/
ENC  = ROOT / 'shared' / 'tresor.enc'
MAGIC = b'WCTRESOR1'
# Feste Download-Adresse der verschluesselten tresor.enc (ohne Passwort wertlos):
DEFAULT_TRESOR_URL = 'https://raw.githubusercontent.com/escapedeutschland/webcraft-cockpit/main/tresor.enc'

# (logischer Name, Ablageort) — 'repo' = relativ zum Projekt, 'home' = im Benutzerordner
ITEMS = [
    ('auto_system/config.py',          'repo'),
    ('.claude/google_token.pickle',    'home'),
]

def _path(rel, where):
    return (ROOT / rel) if where == 'repo' else (Path.home() / rel)

def _derive(passphrase, salt):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=390000)
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode('utf-8')))

def lock():
    bundle = []
    for rel, where in ITEMS:
        p = _path(rel, where)
        if p.exists():
            bundle.append({'rel': rel, 'where': where,
                           'data': base64.b64encode(p.read_bytes()).decode('ascii')})
            print(f"  + {rel}  ({p.stat().st_size} Bytes)")
        else:
            print(f"  ! uebersprungen (nicht gefunden): {p}")
    if not bundle:
        print("Nichts zu sichern."); return
    pw  = getpass.getpass("Tresor-Passwort setzen: ")
    pw2 = getpass.getpass("Passwort wiederholen:   ")
    if pw != pw2 or not pw:
        print("Passwoerter ungleich oder leer — abgebrochen."); return
    salt = os.urandom(16)
    token = Fernet(_derive(pw, salt)).encrypt(json.dumps(bundle).encode('utf-8'))
    ENC.write_bytes(MAGIC + salt + token)
    print(f"\nTresor gespeichert: {ENC}")
    print("Weitergabe: Datei teilen + Passwort SEPARAT (Anruf/Signal), nie im selben Kanal.")

def unlock():
    if not ENC.exists():
        print(f"Keine tresor.enc gefunden: {ENC}\nLege sie ins shared/-Verzeichnis und starte erneut."); return
    raw = ENC.read_bytes()
    if raw[:len(MAGIC)] != MAGIC:
        print("Ungueltige Tresor-Datei."); return
    salt = raw[len(MAGIC):len(MAGIC)+16]; token = raw[len(MAGIC)+16:]
    pw = getpass.getpass("Tresor-Passwort: ")
    try:
        data = Fernet(_derive(pw, salt)).decrypt(token)
    except InvalidToken:
        print("Falsches Passwort oder beschaedigte Datei."); return
    for it in json.loads(data):
        p = _path(it['rel'], it['where'])
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(base64.b64decode(it['data']))
        print(f"  -> wiederhergestellt: {p}")
    print("\nFertig. Alle Keys + Google-Token sind lokal eingerichtet.")
    print("Test:  python -c \"import sys;sys.path.insert(0,'auto_system');import config;print('OK', config.CRM_SHEET_ID[:6])\"")

def pull(url=None):
    """Laedt die verschluesselte tresor.enc von einer URL und entsperrt sie sofort.
    URL kann als Argument oder ueber config.TRESOR_URL kommen."""
    import urllib.request
    if not url:
        try:
            sys.path.insert(0, str(ROOT / 'auto_system')); import config
            url = getattr(config, 'TRESOR_URL', '')
        except Exception:
            url = ''
    if not url:
        url = DEFAULT_TRESOR_URL
    print(f"Lade Tresor von: {url}")
    try:
        data = urllib.request.urlopen(url, timeout=30).read()
    except Exception as ex:
        print(f"Download fehlgeschlagen: {str(ex)[:100]}"); return
    if data[:len(MAGIC)] != MAGIC:
        print("Heruntergeladene Datei ist kein gueltiger Tresor."); return
    ENC.write_bytes(data)
    print("Heruntergeladen ->", ENC)
    unlock()

def info():
    if not ENC.exists():
        print("Kein Tresor vorhanden."); return
    raw = ENC.read_bytes()
    ok = raw[:len(MAGIC)] == MAGIC
    print(f"Tresor: {ENC}\nFormat gueltig: {ok} | Groesse: {len(raw)} Bytes")
    print("Inhalt (nach Entschluesselung):", ', '.join(r for r, _ in ITEMS))
    print("Zum Entschluesseln Passwort noetig (python shared/tresor.py unlock).")

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if   cmd == 'lock':   lock()
    elif cmd == 'unlock': unlock()
    elif cmd == 'info':   info()
    else: print("Aufruf: python shared/tresor.py [lock|unlock|info]")
