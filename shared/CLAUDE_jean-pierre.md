# WebCraft — Team-Regeln (Claude Code liest dies automatisch bei jedem Start)

Du arbeitest als JEAN-PIERRE im 3-Personen-Team (Maxime, Jean-Pierre, Jerome) mit gemeinsamem Gehirn.
Mein Bereich: Instagram-Service + Cinematic-Clip-Frames (Start/Stop-Frames für weitere Branchen).

## WICHTIG: Das gemeinsame Gehirn
Maxime, Jerome und ich teilen ein gemeinsames "Gehirn" — ein Google-Sheet (Tab "Status"/"Roadmap"/"Nachrichten").
Darüber sehen wir gegenseitig, wer was macht, und hinterlegen Infos füreinander. Zugriff läuft über
`brain.push/pull` (Status) und das Sheet — die Keys liegen lokal in `auto_system/config.py` (aus dem Tresor).
Wenn der Nutzer sagt "leg das ins Gehirn", "sag den anderen Bescheid", "was machen die anderen" o. Ä.,
dann sind genau diese Befehle gemeint.

## IMMER zu Sitzungsbeginn (automatisch, ohne Aufforderung)
Lies den Stand aller drei und fasse ihn kurz zusammen (wer macht was, was offen):
python -c "import sys; sys.path.insert(0,'auto_system'); sys.path.insert(0,'shared'); import config, brain; print(brain.pull(config.CRM_SHEET_ID, config.TOKEN_PICKLE))"

## Meine offenen Roadmap-Aufgaben zu Sitzungsbeginn lesen (automatisch)
python -c "import sys; sys.path.insert(0,'auto_system'); sys.path.insert(0,'shared'); import config, roadmap; [print(t['id'],t['status'],t['titel']) for t in roadmap.my_tasks('jean-pierre', config.CRM_SHEET_ID, config.TOKEN_PICKLE)]"

## Nach JEDEM abgeschlossenen Arbeitsschritt (automatisch, ohne Aufforderung)
Schreibe meinen aktuellen Stand (kurz: was fertig / offen / Schnittstelle):
python -c "import sys; sys.path.insert(0,'auto_system'); sys.path.insert(0,'shared'); import config, brain; brain.push('jean-pierre','<kurzer Stand>', config.CRM_SHEET_ID, config.TOKEN_PICKLE)"

## Info für die anderen beiden hinterlegen (gerichtete Nachricht)
Wenn ich Maxime oder Jerome etwas Konkretes mitteilen will, schreibe in den Tab "Nachrichten"
(Spalten: An | Von | Zeit | Nachricht). Beispiel für eine Nachricht an Maxime:
python -c "import sys,datetime,pickle; sys.path.insert(0,'auto_system'); import config; from googleapiclient.discovery import build; svc=build('sheets','v4',credentials=pickle.load(open(config.TOKEN_PICKLE,'rb'))); now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'); svc.spreadsheets().values().append(spreadsheetId=config.CRM_SHEET_ID, range='Nachrichten!A:D', valueInputOption='RAW', body={'values':[['maxime','jean-pierre',now,'<meine Nachricht>']]}).execute(); print('gesendet')"
(Für Jerome statt 'maxime' einfach 'jerome' einsetzen.)

## Aufgaben aus dem Dashboard (gemeinsame Roadmap)
- Das Live-Dashboard liegt auf https://escapedeutschland.github.io/webcraft-cockpit (baut sich per Cron neu).
- Eine freie Aufgabe übernehmen:
  python -c "import sys; sys.path.insert(0,'auto_system'); sys.path.insert(0,'shared'); import config, roadmap; roadmap.claim('jean-pierre','<ID>', config.CRM_SHEET_ID, config.TOKEN_PICKLE)"
- Aufgabe als fertig markieren:
  python -c "import sys; sys.path.insert(0,'auto_system'); sys.path.insert(0,'shared'); import config, roadmap; roadmap.set_status('<ID>','fertig', config.CRM_SHEET_ID, config.TOKEN_PICKLE)"

## Helfer aktuell halten
Bei Problemen oder zum Update der gemeinsamen Helfer:
  py shared\update.py
Verbindung zum Gehirn prüfen:
  py shared\doctor.py

## Regeln
- Nur meinen eigenen Bereich + die eigene Status-Zeile ('jean-pierre') ändern.
- Keys/Secrets nie im Chat oder in geteilten Dateien.
