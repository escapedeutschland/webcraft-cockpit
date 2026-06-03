# -*- coding: utf-8 -*-
"""
Gemeinsamer Deploy fuer ALLE Module -> GitHub Pages.
Alle Seiten landen im Repo 'webcraft-sites' unter einem Unterordner = site_name:
    https://<owner>.github.io/webcraft-sites/<site_name>/

Signatur bleibt ABWAERTSKOMPATIBEL: der frueher 3. Parameter (netlify_key) wird ignoriert,
damit bestehender Aufrufer-Code (z. B. der Brueder) ohne Aenderung weiterlaeuft.

    from deploy import deploy
    url = deploy(html, "bewerten-kfz-mueller", binary_files={"qr.png": qr_bytes})
"""
import sys, base64, pathlib, requests

_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / 'auto_system'))
sys.path.insert(0, str(_ROOT / 'shared'))
try:
    import config_local as _cfg          # falls vorhanden
except ImportError:
    import config as _cfg                # aus dem Tresor: auto_system/config.py

_OWNER = _cfg.GITHUB_REPO.split('/')[0]
_REPO = _OWNER + '/webcraft-sites'

def _h():
    return {'Authorization': 'Bearer ' + _cfg.GITHUB_TOKEN,
            'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}

def _ensure():
    if requests.get('https://api.github.com/repos/' + _REPO, headers=_h()).status_code == 200:
        return
    requests.post('https://api.github.com/user/repos', headers=_h(),
                  json={'name': 'webcraft-sites', 'private': False, 'auto_init': True,
                        'description': 'WebCraft Kundenseiten'})
    requests.put('https://api.github.com/repos/' + _REPO + '/contents/.nojekyll',
                 headers=_h(), json={'message': 'nojekyll', 'content': ''})
    try:
        requests.post('https://api.github.com/repos/' + _REPO + '/pages',
                      headers=_h(), json={'source': {'branch': 'main', 'path': '/'}})
    except Exception:
        pass

def _put(path, data_bytes, msg):
    url = 'https://api.github.com/repos/' + _REPO + '/contents/' + path
    g = requests.get(url, headers=_h())
    sha = g.json().get('sha') if g.status_code == 200 else None
    body = {'message': msg, 'content': base64.b64encode(data_bytes).decode('ascii')}
    if sha:
        body['sha'] = sha
    requests.put(url, headers=_h(), json=body).raise_for_status()

def deploy(html: str, site_name: str, netlify_key=None,
           extra_files: dict = None, binary_files: dict = None) -> str:
    """Deployt eine Seite nach GitHub Pages. extra_files: {name: text}, binary_files: {name: bytes}.
    netlify_key wird ignoriert (Kompatibilitaet). Gibt die Live-URL zurueck."""
    _ensure()
    _put(f'{site_name}/index.html', html.encode('utf-8'), 'deploy ' + site_name)
    for fn, fc in (extra_files or {}).items():
        _put(f'{site_name}/{fn}', fc.encode('utf-8'), f'deploy {site_name} {fn}')
    for fn, data in (binary_files or {}).items():
        _put(f'{site_name}/{fn}', data, f'deploy {site_name} {fn}')
    return f'https://{_OWNER}.github.io/webcraft-sites/{site_name}/'
