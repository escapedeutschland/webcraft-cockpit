# -*- coding: utf-8 -*-
"""
Gemeinsames Gehirn — AUTOMATISCH über das CRM-Google-Sheet (Tab "Status").
Kein Datei-Schicken, kein Drive: jeder Claude liest/schreibt seinen Stand direkt ins Sheet.

Nutzung (in jedem Modul):
    import config_local as cfg
    import brain
    print(brain.pull(cfg.CRM_SHEET_ID, cfg.TOKEN_PICKLE))            # Stand ALLER lesen (Sitzungs-Start)
    brain.push("jerome", "review_link.py fertig, QR funktioniert.",  # eigenen Stand schreiben (Sitzungs-Ende)
               cfg.CRM_SHEET_ID, cfg.TOKEN_PICKLE)
"""
import pickle, datetime

ROWS = {"maxime": 2, "jean-pierre": 3, "jerome": 4}   # feste Zeilen je Bruder


def _svc(token_pickle):
    from googleapiclient.discovery import build
    creds = pickle.load(open(token_pickle, "rb"))
    return build("sheets", "v4", credentials=creds)


def ensure_tab(sheet_id, token_pickle):
    """Legt den Tab 'Status' + Kopfzeile + die drei Bruder-Zeilen an (idempotent)."""
    svc = _svc(token_pickle)
    meta = svc.spreadsheets().get(spreadsheetId=sheet_id).execute()
    tabs = [s["properties"]["title"] for s in meta["sheets"]]
    if "Status" not in tabs:
        svc.spreadsheets().batchUpdate(spreadsheetId=sheet_id,
            body={"requests": [{"addSheet": {"properties": {"title": "Status"}}}]}).execute()
    svc.spreadsheets().values().update(spreadsheetId=sheet_id, range="Status!A1:C1",
        valueInputOption="RAW", body={"values": [["Bruder", "Stand", "Status"]]}).execute()


def pull(sheet_id, token_pickle):
    """Liest den Stand ALLER Brüder als Dict {name: {'stand':..., 'status':...}}."""
    svc = _svc(token_pickle)
    res = svc.spreadsheets().values().get(spreadsheetId=sheet_id, range="Status!A2:C10").execute()
    out = {}
    for row in res.get("values", []):
        row = (row + ["", "", ""])[:3]
        if row[0]:
            out[row[0].lower()] = {"stand": row[1], "status": row[2]}
    return out


def push(name, text, sheet_id, token_pickle, stand=None):
    """Schreibt den eigenen Stand (überschreibt die eigene Zeile)."""
    name = name.lower()
    r = ROWS.get(name)
    if not r:
        raise ValueError("Unbekannter Name (erlaubt: maxime, jean-pierre, jerome): " + name)
    stand = stand or datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    svc = _svc(token_pickle)
    svc.spreadsheets().values().update(spreadsheetId=sheet_id, range=f"Status!A{r}:C{r}",
        valueInputOption="RAW", body={"values": [[name, stand, text]]}).execute()
    return True
