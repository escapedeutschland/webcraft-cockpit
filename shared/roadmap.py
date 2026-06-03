# -*- coding: utf-8 -*-
"""
WebCraft Roadmap — die EINE Wahrheit ueber das Gesamtprojekt (Tab "Roadmap" im CRM-Sheet).
Speist das Team-Dashboard: Fertigstellungs-%, Aufgaben-Panels, "Aufgabe uebernehmen".

Spalten (A-G):  id | titel | kind | owner | status | weight | note
  kind   : feature | automatisierung | empfehlung
  owner  : maxime | jean-pierre | jerome | frei
  status : fertig | in_arbeit | offen
  weight : Zahl (Gewicht fuer die %-Berechnung; empfehlung zaehlt NICHT mit)

Nutzung:
    import config, roadmap
    roadmap.ensure(config.CRM_SHEET_ID, config.TOKEN_PICKLE)        # Tab anlegen + seeden (idempotent)
    rows = roadmap.read_all(config.CRM_SHEET_ID, config.TOKEN_PICKLE)
    print(roadmap.progress(rows))                                   # {'percent':.., 'done':.., 'total':..}
    roadmap.claim("jerome", "R20", config.CRM_SHEET_ID, config.TOKEN_PICKLE)   # Aufgabe uebernehmen
    roadmap.set_status("R20", "fertig", config.CRM_SHEET_ID, config.TOKEN_PICKLE)
"""
import pickle

HEADER = ["id", "titel", "kind", "owner", "status", "weight", "note"]

# kind:feature|automatisierung|empfehlung  owner:maxime|jean-pierre|jerome|frei  status:fertig|in_arbeit|offen
DEFAULT_ROADMAP = [
    # --- FERTIG (Maxime / Website-Fabrik) ---
    ["R01", "Website-Generator (17+ Branchen, branchengenau)", "feature", "maxime", "fertig", 5, "website_generator.py"],
    ["R02", "Branchen-Templates Schneider & Blumen", "feature", "maxime", "fertig", 3, ""],
    ["R03", "Stufe-3 branchenspezifische Content-Sektionen", "feature", "maxime", "fertig", 3, "branch_services()"],
    ["R04", "Cinematic Hero (Scroll-Scrubbing, KFZ)", "feature", "maxime", "fertig", 5, "cinematic.py"],
    ["R05", "Mobile-scharfe Cinematic-Frames", "feature", "maxime", "fertig", 2, "1280px frame set"],
    ["R06", "Individualisierung Cinematic (Farben/Bilder/Text pro Kunde)", "feature", "maxime", "fertig", 3, ""],
    ["R07", "Auto-System Intake-Pipeline (Google -> Website)", "feature", "maxime", "fertig", 5, "intake.py"],
    ["R08", "Conversion-optimierte Vorschau-Mail", "feature", "maxime", "fertig", 3, "send_preview()"],
    ["R09", "Agentur-Website (Angebot, Hosting, SEO)", "feature", "maxime", "fertig", 4, "webcraft-agentur"],
    ["R10", "Gemeinsames Gehirn (brain.py + Sheet, 3 User)", "feature", "maxime", "fertig", 4, "Auto-Sync"],
    ["R11", "Lead-Priorisierung (864 Hoch / 1122 Mittel)", "feature", "maxime", "fertig", 2, "lead_priority.py"],
    ["R12", "Stripe Zahlung + Instagram-Abo-Link", "feature", "maxime", "fertig", 3, "payment_links"],
    # --- AUTOMATISIERUNG ---
    ["R13", "Netlify Auto-Deploy", "automatisierung", "maxime", "fertig", 3, "deploy.py"],
    ["R14", "Auto-Auslieferung ZIP bei Zahlung (Reply-Monitor)", "automatisierung", "maxime", "fertig", 4, "reply_monitor.py"],
    ["R15", "Team-Dashboard Auto-Build (Cron)", "automatisierung", "maxime", "in_arbeit", 3, "dashboard_build.py"],
    ["R16", "Batch-Versand Vorschau-Mails aus Lead-Liste", "automatisierung", "frei", "offen", 4, "Skalierungs-Hebel"],
    ["R17", "Bewertungs-Service Automatik (QR -> Mail -> Sheet)", "automatisierung", "jerome", "offen", 4, ""],
    # --- IN ARBEIT (Brueder) ---
    ["R18", "Instagram-Service Aufbau", "feature", "jean-pierre", "in_arbeit", 4, ""],
    ["R19", "Cinematic-Clips weitere Branchen (Start/Stop-Frames)", "feature", "jean-pierre", "in_arbeit", 3, "JP liefert Frames"],
    ["R20", "Bewertungs-Service (review_link.py)", "feature", "jerome", "in_arbeit", 4, ""],
    # --- OFFEN / FREI ---
    ["R21", "Mehr Clip-Varianten pro Branche", "feature", "frei", "offen", 3, ""],
    ["R22", "Dedizierte Themes (Garten, Schlosserei)", "feature", "frei", "offen", 2, "unter-versorgte Branchen"],
    ["R23", "Wartungs-Abo Prozess definieren", "feature", "frei", "offen", 2, "Was genau, wie abgewickelt"],
    ["R24", "sipgate Telefonnummer einrichten", "feature", "frei", "offen", 2, "Go-Live"],
    ["R25", "Rechtsform / Impressum / AGB / DSGVO", "feature", "frei", "offen", 3, "Anwalt"],
    # --- EMPFEHLUNGEN (zaehlen NICHT in %) ---
    ["R26", "Conversion-Validierung: ~200 Cold Calls vor Skalierung", "empfehlung", "frei", "offen", 0, "wichtigster Test"],
    ["R27", "Eigene Cinematic-Video-Sequenz fuer Agentur-Website", "empfehlung", "frei", "offen", 0, ""],
    ["R28", "A/B-Test Betreffzeilen Vorschau-Mail", "empfehlung", "frei", "offen", 0, ""],
    ["R29", "Google-Business-Profile-Anleitung als Mehrwert/Upsell", "empfehlung", "frei", "offen", 0, ""],
    ["R30", "Automatisches Kunden-Onboarding-PDF", "empfehlung", "frei", "offen", 0, ""],
]

OWNERS = ("maxime", "jean-pierre", "jerome", "frei")
STATI = ("fertig", "in_arbeit", "offen")


def _svc(token_pickle):
    from googleapiclient.discovery import build
    creds = pickle.load(open(token_pickle, "rb"))
    return build("sheets", "v4", credentials=creds)


def ensure(sheet_id, token_pickle):
    """Legt Tab 'Roadmap' + Kopf an und seedet mit DEFAULT_ROADMAP, falls leer (idempotent)."""
    svc = _svc(token_pickle)
    meta = svc.spreadsheets().get(spreadsheetId=sheet_id).execute()
    tabs = [s["properties"]["title"] for s in meta["sheets"]]
    if "Roadmap" not in tabs:
        svc.spreadsheets().batchUpdate(spreadsheetId=sheet_id,
            body={"requests": [{"addSheet": {"properties": {"title": "Roadmap"}}}]}).execute()
    res = svc.spreadsheets().values().get(spreadsheetId=sheet_id, range="Roadmap!A2:G").execute()
    has_data = len([r for r in res.get("values", []) if r and r[0]]) > 0
    if not has_data:
        body = {"values": [HEADER] + [[str(c) for c in row] for row in DEFAULT_ROADMAP]}
        svc.spreadsheets().values().update(spreadsheetId=sheet_id, range="Roadmap!A1:G",
            valueInputOption="RAW", body=body).execute()
    else:
        svc.spreadsheets().values().update(spreadsheetId=sheet_id, range="Roadmap!A1:G1",
            valueInputOption="RAW", body={"values": [HEADER]}).execute()
    return True


def read_all(sheet_id, token_pickle):
    """Liest alle Roadmap-Zeilen als Liste von Dicts."""
    svc = _svc(token_pickle)
    res = svc.spreadsheets().values().get(spreadsheetId=sheet_id, range="Roadmap!A2:G").execute()
    out = []
    for row in res.get("values", []):
        row = (row + [""] * 7)[:7]
        if not row[0]:
            continue
        try:
            w = float(row[5]) if row[5] not in ("", None) else 0
        except ValueError:
            w = 0
        out.append({"id": row[0].strip(), "titel": row[1].strip(), "kind": (row[2] or "feature").strip(),
                    "owner": (row[3] or "frei").strip().lower(), "status": (row[4] or "offen").strip().lower(),
                    "weight": w, "note": row[6].strip()})
    return out


def progress(rows):
    """Gewichteter Fortschritt. fertig=voll, in_arbeit=40%. Empfehlungen zaehlen nicht."""
    core = [r for r in rows if r["kind"] in ("feature", "automatisierung")]
    total = sum(r["weight"] for r in core) or 1
    done = sum(r["weight"] for r in core if r["status"] == "fertig")
    done += sum(r["weight"] * 0.4 for r in core if r["status"] == "in_arbeit")
    pct = round(done / total * 100)
    return {
        "percent": pct,
        "done_count": len([r for r in core if r["status"] == "fertig"]),
        "in_arbeit_count": len([r for r in core if r["status"] == "in_arbeit"]),
        "total_count": len(core),
        "done_weight": round(done, 1),
        "total_weight": round(total, 1),
    }


def _row_index(svc, sheet_id, task_id):
    res = svc.spreadsheets().values().get(spreadsheetId=sheet_id, range="Roadmap!A2:A").execute()
    for i, row in enumerate(res.get("values", [])):
        if row and row[0].strip() == task_id:
            return i + 2  # +2: Zeile 1 = Kopf, 0-basiert -> 1-basiert
    return None


def set_status(task_id, status, sheet_id, token_pickle):
    if status not in STATI:
        raise ValueError("Status muss sein: " + ", ".join(STATI))
    svc = _svc(token_pickle)
    r = _row_index(svc, sheet_id, task_id)
    if not r:
        raise ValueError("Unbekannte Aufgabe: " + task_id)
    svc.spreadsheets().values().update(spreadsheetId=sheet_id, range=f"Roadmap!E{r}",
        valueInputOption="RAW", body={"values": [[status]]}).execute()
    return True


def claim(name, task_id, sheet_id, token_pickle):
    """Weist eine (freie) Aufgabe einem Bruder zu und setzt sie auf 'in_arbeit'."""
    name = name.lower()
    if name not in ("maxime", "jean-pierre", "jerome"):
        raise ValueError("Name muss sein: maxime, jean-pierre, jerome")
    svc = _svc(token_pickle)
    r = _row_index(svc, sheet_id, task_id)
    if not r:
        raise ValueError("Unbekannte Aufgabe: " + task_id)
    svc.spreadsheets().values().update(spreadsheetId=sheet_id, range=f"Roadmap!D{r}:E{r}",
        valueInputOption="RAW", body={"values": [[name, "in_arbeit"]]}).execute()
    return True


def my_tasks(name, sheet_id, token_pickle):
    """Alle offenen/laufenden Aufgaben eines Bruders (fuer seinen Claude-Sitzungsstart)."""
    name = name.lower()
    rows = read_all(sheet_id, token_pickle)
    return [r for r in rows if r["owner"] == name and r["status"] != "fertig"]


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "auto_system"))
    import config
    ensure(config.CRM_SHEET_ID, config.TOKEN_PICKLE)
    rows = read_all(config.CRM_SHEET_ID, config.TOKEN_PICKLE)
    print(progress(rows))
    for r in rows:
        print(f"  {r['id']:>4} [{r['status']:<9}] {r['owner']:<12} {r['titel']}")
