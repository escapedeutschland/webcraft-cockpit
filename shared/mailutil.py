"""
Gmail-Hilfsfunktionen (geteilt fuer alle Brueder): Versand + automatisches Label 'WebCraft'.
Findet config aus dem Tresor (auto_system/config.py) unabhaengig vom Aufrufer.
"""
import sys, pickle, base64
from pathlib import Path
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))                       # shared/
sys.path.insert(0, str(_HERE.parent / 'auto_system'))  # fuer config (aus dem Tresor)
import config
from googleapiclient.discovery import build

LABEL_NAME = "WebCraft"
_label_id = None

def get_gmail():
    with open(config.TOKEN_PICKLE, 'rb') as f:
        creds = pickle.load(f)
    return build('gmail', 'v1', credentials=creds)

def ensure_label(gmail):
    """Stellt sicher, dass das Label 'WebCraft' existiert; gibt seine ID zurueck (gecacht)."""
    global _label_id
    if _label_id:
        return _label_id
    labels = gmail.users().labels().list(userId='me').execute().get('labels', [])
    for l in labels:
        if l['name'] == LABEL_NAME:
            _label_id = l['id']
            return _label_id
    created = gmail.users().labels().create(userId='me', body={
        'name': LABEL_NAME,
        'labelListVisibility': 'labelShow',
        'messageListVisibility': 'show',
    }).execute()
    _label_id = created['id']
    return _label_id

def send(gmail, mime_msg):
    """Sendet eine fertige MIME-Nachricht und vergibt automatisch das WebCraft-Label."""
    raw = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode()
    sent = gmail.users().messages().send(userId='me', body={'raw': raw}).execute()
    try:
        lid = ensure_label(gmail)
        gmail.users().messages().modify(userId='me', id=sent['id'],
                                        body={'addLabelIds': [lid]}).execute()
    except Exception as e:
        print(f'  (Label konnte nicht gesetzt werden: {e})')
    return sent
