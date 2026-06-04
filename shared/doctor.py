# -*- coding: utf-8 -*-
"""
Gehirn-Verbindung pruefen (Selbstdiagnose fuer alle Brueder).
Sagt Zeile fuer Zeile, was OK ist und was fehlt -- und gibt am Ende einen klaren Tipp.

Aufruf (im webcraft-Ordner):  py shared\\doctor.py
"""
import os, sys, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'auto_system'))
sys.path.insert(0, str(ROOT / 'shared'))

def ok(b): return 'OK ' if b else 'FEHLT '

print('=== WebCraft Gehirn-Check ===')
print('Arbeitsordner :', os.getcwd())
print('Projekt-Root  :', ROOT)

# 1) config.py
cfg = None
try:
    import config as cfg
    has_sheet = bool(getattr(cfg, 'CRM_SHEET_ID', ''))
    print('[%s] config.py geladen, CRM_SHEET_ID %s' % (ok(has_sheet), 'vorhanden' if has_sheet else 'fehlt'))
except Exception as e:
    print('[FEHLER] config.py nicht ladbar:', str(e)[:90])

# 2) Google-Token
tok_ok = False
if cfg is not None:
    tp = getattr(cfg, 'TOKEN_PICKLE', '')
    exists = bool(tp) and os.path.exists(tp)
    print('[%s] Google-Token-Datei: %s' % (ok(exists), tp))
    if exists:
        try:
            import pickle
            creds = pickle.load(open(tp, 'rb'))
            exp = getattr(creds, 'expiry', None)
            valid = getattr(creds, 'valid', None)
            print('      Token gueltig:', valid, '| Ablauf:', exp)
            tok_ok = True
        except Exception as e:
            print('      Token nicht lesbar:', str(e)[:80])

# 3) Helfer vorhanden
for mod in ('brain', 'roadmap'):
    print('[%s] %s.py' % (ok((ROOT / 'shared' / (mod + '.py')).exists()), mod))

# 4) Gehirn LESEN
read_ok = False
if cfg is not None and tok_ok:
    try:
        import brain
        data = brain.pull(cfg.CRM_SHEET_ID, cfg.TOKEN_PICKLE)
        read_ok = bool(data)
        print('[%s] Gehirn lesen (brain.pull): %d Eintraege' % (ok(read_ok), len(data or {})))
    except Exception as e:
        print('[FEHLER] brain.pull:', str(e)[:90])

# 5) Gehirn SCHREIBEN (Heartbeat fuer jean-pierre)
if cfg is not None and tok_ok and read_ok:
    try:
        import brain
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        brain.push('jean-pierre', 'Verbindungstest erfolgreich (' + now + ') - wieder online.',
                   cfg.CRM_SHEET_ID, cfg.TOKEN_PICKLE)
        print('[OK ] Gehirn schreiben (brain.push) - jean-pierre-Status aktualisiert. ALLES GRUEN.')
    except Exception as e:
        print('[FEHLER] brain.push:', str(e)[:90])

print('\n--- Tipp ---')
print('Fehlt config.py ODER Token: einmal neu aus dem Tresor holen (neues Passwort von Maxime per Anruf):')
print('   py shared\\tresor.py pull "NEUES-PASSWORT"')
print('Fehlt brain.py/roadmap.py: Helfer aktualisieren:')
print('   py shared\\update.py')
print('Laeuft alles gruen: im Dashboard erscheinst du binnen ~10 Min wieder als online.')
