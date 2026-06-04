# -*- coding: utf-8 -*-
"""
Holt die aktuellen gemeinsamen Helfer vom Team-Repo (GitHub) und ueberschreibt sie lokal.
EIN Befehl statt einzelner curl-Kommandos -- damit alle Bruder denselben Stand haben.

Aufruf (im webcraft-Ordner):  py shared\\update.py
"""
import urllib.request, pathlib

BASE = 'https://raw.githubusercontent.com/escapedeutschland/webcraft-cockpit/main/shared/'
FILES = ['brain.py', 'roadmap.py', 'deploy.py', 'tresor.py', 'mailutil.py', 'widget.py', 'update.py']

root = pathlib.Path(__file__).resolve().parent          # .../shared
print('Aktualisiere gemeinsame Helfer aus dem Team-Repo ...')
for f in FILES:
    try:
        data = urllib.request.urlopen(BASE + f + '?t=now', timeout=30).read()
        (root / f).write_bytes(data)
        print('  aktualisiert:', f)
    except Exception as e:
        print('  uebersprungen:', f, '-', str(e)[:60])
print('Fertig. Alle Helfer (inkl. GitHub-Deploy) sind auf dem neuesten Stand.')
