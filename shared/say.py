# -*- coding: utf-8 -*-
"""
Einfacher Gehirn-Zugriff DIREKT aus cmd (kein Claude noetig).

  py shared\\say.py read                       -> Stand aller drei lesen
  py shared\\say.py jean-pierre "nachricht"    -> eigenen Stand ins Gehirn schreiben
  py shared\\say.py maxime "nachricht"         -> (entsprechend fuer maxime / jerome)

Name = maxime | jean-pierre | jerome
"""
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'auto_system'))
sys.path.insert(0, str(ROOT / 'shared'))
import config, brain

NAMES = ('maxime', 'jean-pierre', 'jerome')
args = sys.argv[1:]

if not args or args[0] == 'read':
    data = brain.pull(config.CRM_SHEET_ID, config.TOKEN_PICKLE)
    print('=== Gemeinsames Gehirn ===')
    for k in NAMES:
        d = data.get(k, {})
        print('\n[' + k + ']  ' + str(d.get('stand', '-')))
        print('  ' + str(d.get('status', '(kein Eintrag)')))
    sys.exit(0)

if args[0] in NAMES and len(args) >= 2:
    text = ' '.join(args[1:])
    brain.push(args[0], text, config.CRM_SHEET_ID, config.TOKEN_PICKLE)
    print('OK - im Gehirn gespeichert als ' + args[0])
    sys.exit(0)

print('Benutzung:')
print('  py shared\\say.py read')
print('  py shared\\say.py jean-pierre "deine nachricht"')
