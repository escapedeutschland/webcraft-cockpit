# -*- coding: utf-8 -*-
"""
widget.py - WebCraft Google-Bewertungs-Badge fuer die KUNDEN-WEBSITE.

Gemeinsamer Helfer (shared/), aufgerufen von Maximes Website-Pipeline und in den
Template-Slot @@WEBCRAFT_REVIEWS@@ eingesetzt (nur wenn bewertung == "ja").

    from widget import build_widget, fetch_reviews
    kunde["reviews"] = fetch_reviews(place_id, MAPS_KEY)      # optional (Stufe 2)
    html = build_widget(kunde, tokens)

  kunde  : {"firma","place_id","rating","review_count","reviews"(optional)}
  tokens : {"primary","accent","ink","font"}

"Aus einem Guss": font:inherit + var(--accent)/var(--ink) der Seite, tokens als Fallback.
Self-contained (nur Standardbibliothek), eigener CSS-Namespace .wcrev -> keine Konflikte.

Google-Konformitaet (Stufe 2 / Reviews):
  * Reviews unveraendert anzeigen, mit Autor-Name + Foto und Link zu Google (Attribution).
  * Regelmaessig auffrischen (Maximes Pipeline, monatlich) statt langfristig cachen.
"""
import html as _html

_STAR = ('<svg class="st" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 .587l3.668 7.431 '
         '8.2 1.192-5.934 5.787 1.401 8.169L12 18.896l-7.335 3.86 1.401-8.169L.132 9.21l8.2-1.192z"/></svg>')

_GOOGLE_G = (
    '<svg class="g" viewBox="0 0 48 48" aria-hidden="true">'
    '<path fill="#4285F4" d="M45.12 24.5c0-1.56-.14-3.06-.4-4.5H24v8.51h11.84c-.51 2.75-2.06 5.08-4.39 6.64'
    'v5.52h7.11c4.16-3.83 6.56-9.47 6.56-16.17z"/>'
    '<path fill="#34A853" d="M24 46c5.94 0 10.92-1.97 14.56-5.33l-7.11-5.52c-1.97 1.32-4.49 2.1-7.45 2.1'
    '-5.73 0-10.58-3.87-12.31-9.07H4.34v5.7C7.96 41.07 15.4 46 24 46z"/>'
    '<path fill="#FBBC05" d="M11.69 28.18C11.25 26.86 11 25.45 11 24s.25-2.86.69-4.18v-5.7H4.34'
    'C2.85 17.09 2 20.45 2 24s.85 6.91 2.34 9.88l7.35-5.7z"/>'
    '<path fill="#EA4335" d="M24 10.75c3.23 0 6.13 1.11 8.41 3.29l6.31-6.31C34.91 4.18 29.93 2 24 2'
    '15.4 2 7.96 6.93 4.34 14.12l7.35 5.7c1.73-5.2 6.58-9.07 12.31-9.07z"/></svg>')


def _view_link(place_id: str) -> str:
    return f"https://search.google.com/local/reviews?placeid={place_id}" if place_id else "#"


def _write_link(place_id: str) -> str:
    """Link zum SCHREIBEN einer Google-Bewertung (oeffnet Googles Bewertungs-Formular)."""
    return f"https://search.google.com/local/writereview?placeid={place_id}" if place_id else "#"


def _stars(rating) -> str:
    try:
        pct = max(0.0, min(100.0, float(rating) / 5.0 * 100.0))
    except (ValueError, TypeError):
        pct = 100.0
    base = '<span class="s-base">' + _STAR * 5 + "</span>"
    fill = f'<span class="s-fill" style="width:{pct:.1f}%">' + _STAR * 5 + "</span>"
    return '<span class="s-wrap">' + base + fill + "</span>"


# ── Reviews holen (Places API New) ───────────────────────────────────────────

def fetch_reviews(place_id: str, api_key: str, language: str = "de", limit: int = 5) -> list:
    """Holt bis zu `limit` Google-Reviews und normalisiert sie:
    [{author, photo, uri, rating, time, text}]. Braucht den Maps/Places-Key."""
    import json
    import urllib.request
    url = f"https://places.googleapis.com/v1/places/{place_id}?languageCode={language}"
    req = urllib.request.Request(url, headers={
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": ("reviews.rating,reviews.text,reviews.originalText,"
                             "reviews.relativePublishTimeDescription,reviews.authorAttribution"),
    })
    with urllib.request.urlopen(req, timeout=12) as r:
        data = json.loads(r.read().decode("utf-8"))
    out = []
    for rv in (data.get("reviews") or [])[:limit]:
        aa = rv.get("authorAttribution") or {}
        txt = (rv.get("text") or rv.get("originalText") or {}).get("text", "")
        out.append({
            "author": aa.get("displayName", ""),
            "photo": aa.get("photoUri", ""),
            "uri": aa.get("uri", ""),
            "rating": rv.get("rating"),
            "time": rv.get("relativePublishTimeDescription", ""),
            "text": txt,
        })
    return out


def _truncate(t: str, n: int = 200) -> str:
    t = " ".join((t or "").split())
    return t if len(t) <= n else t[:n].rstrip() + "…"


def _review_cards(reviews: list, max_reviews: int, min_rating) -> str:
    sel = reviews
    if min_rating:
        sel = [r for r in reviews if (r.get("rating") or 0) >= min_rating]
    sel = sel[:max_reviews]
    if not sel:
        return ""
    cards = ""
    for r in sel:
        photo = r.get("photo") or ""
        if photo:
            av = (f'<img class="rev-av" src="{_html.escape(photo, True)}" alt="" '
                  f'loading="lazy" referrerpolicy="no-referrer">')
        else:
            av = '<span class="rev-av rev-av--ph"></span>'
        name = _html.escape(r.get("author") or "Google-Nutzer")
        time = _html.escape(r.get("time") or "")
        txt = _html.escape(_truncate(r.get("text") or ""))
        cards += (
            f'<div class="rev"><div class="rev-h">{av}<div class="rev-id">'
            f'<span class="rev-name">{name}</span>'
            f'<span class="rev-meta">{_stars(r.get("rating"))}<span class="rev-time">{time}</span></span>'
            f'</div></div><div class="rev-txt">{txt}</div></div>'
        )
    return '<div class="wcrev-revs">' + cards + "</div>"


# ── Badge bauen ──────────────────────────────────────────────────────────────

def build_widget(kunde: dict, tokens: dict = None,
                 max_reviews: int = 3, min_rating=4, invite: bool = True) -> str:
    """Design-adaptives Bewertungs-Badge (+ optional Rezensions-Karten) als HTML-Snippet.

    Zeigt Rezensionen, wenn kunde['reviews'] gesetzt ist (siehe fetch_reviews).
    min_rating=4 -> nur 4-5-Sterne aus dem gelieferten Satz; None -> alle.
    invite=True -> interaktiver "Bewerten Sie uns"-Block: klickbare 1-5 Sterne, die zur
    Google-Bewertungsseite fuehren (Google-konform; echte Bewertung entsteht bei Google).
    """
    tokens = tokens or {}
    accent = tokens.get("accent", "#3b82f6")
    ink = tokens.get("ink", "#1f2430")

    firma = kunde.get("firma", "")
    place_id = kunde.get("place_id", "")
    rating = kunde.get("rating")
    count = kunde.get("review_count")

    rating_de = (f"{float(rating):.1f}".replace(".", ",")) if rating else "–"
    count_txt = f"{count} Google-Bewertungen" if count else "Google-Bewertungen"
    link = _view_link(place_id)

    cards = _review_cards(kunde.get("reviews") or [], max_reviews, min_rating)
    foot = (f'<div class="wcrev-foot"><a href="{link}" target="_blank" rel="noopener noreferrer">'
            f'Alle Bewertungen auf Google ansehen ›</a></div>') if cards else ""

    # Interaktiver "Bewerten Sie uns"-Block (klickbare Sterne -> Google-Bewertungsformular)
    rate_block = ""
    if invite and place_id:
        write = _write_link(place_id)
        star_links = "".join(
            f'<a href="{write}" target="_blank" rel="noopener noreferrer" '
            f'aria-label="Mit {n} Sternen bei Google bewerten">{_STAR}</a>'
            for n in (5, 4, 3, 2, 1)  # row-reverse: Fuellung bis zum gehoverten Stern
        )
        rate_block = (
            '<div class="wcrev-rate"><span class="wcrev-rate-label">Waren Sie schon da? '
            'Jetzt bewerten</span>'
            f'<span class="rate">{star_links}</span></div>'
        )

    gold_defs = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
                 '<linearGradient id="wcrevgold" x1="0" y1="0" x2="0" y2="1">'
                 '<stop offset="0" stop-color="#ffd86b"/><stop offset="0.55" stop-color="#f3b71e"/>'
                 '<stop offset="1" stop-color="#dd9b0c"/></linearGradient></defs></svg>')

    css = (
        ".wcrev-wrap{font-family:inherit;display:inline-block;max-width:430px;width:100%}"
        ".wcrev-wrap *{box-sizing:border-box}"
        ".wcrev{display:inline-flex;align-items:center;gap:14px;"
        "background:#fff;border:1px solid rgba(17,24,39,.08);border-radius:16px;padding:14px 20px;"
        "box-shadow:0 1px 2px rgba(17,24,39,.04),0 10px 30px rgba(17,24,39,.08);"
        f"text-decoration:none;color:var(--ink,{ink});line-height:1.2;"
        "transition:transform .15s,box-shadow .15s}"
        ".wcrev:hover{transform:translateY(-1px);box-shadow:0 2px 4px rgba(17,24,39,.05),0 16px 40px rgba(17,24,39,.12)}"
        ".wcrev .g{width:30px;height:30px;flex:none}"
        ".wcrev .body{display:flex;flex-direction:column;gap:3px}"
        ".wcrev .row1{display:flex;align-items:center;gap:9px}"
        f".wcrev .score{{font-size:24px;font-weight:800;letter-spacing:-.5px;color:var(--ink,{ink})}}"
        ".s-wrap{position:relative;display:inline-flex;line-height:0}"
        ".s-base,.s-fill{display:inline-flex;gap:2px}"
        ".s-fill{position:absolute;top:0;left:0;overflow:hidden;white-space:nowrap;"
        "filter:drop-shadow(0 1px 1px rgba(0,0,0,.15))}"
        ".wcrev .st{width:17px;height:17px;display:block}"
        ".s-base .st path{fill:#e4e7ec}"
        ".s-fill .st path{fill:url(#wcrevgold)}"
        ".wcrev .row2{font-size:12.5px;color:#6b7280;display:flex;align-items:center;gap:6px}"
        f".wcrev .more{{color:var(--accent,{accent});font-weight:600;white-space:nowrap}}"
        # Reviews
        ".wcrev-revs{margin-top:14px;display:flex;flex-direction:column;gap:10px}"
        ".rev{background:#fff;border:1px solid rgba(17,24,39,.08);border-radius:14px;padding:14px 16px;"
        "box-shadow:0 1px 2px rgba(17,24,39,.04)}"
        ".rev-h{display:flex;align-items:center;gap:10px;margin-bottom:9px}"
        ".rev-av{width:36px;height:36px;border-radius:50%;flex:none;object-fit:cover;background:#eef0f2}"
        ".rev-id{display:flex;flex-direction:column;gap:3px}"
        f".rev-name{{font-weight:700;font-size:13.5px;color:var(--ink,{ink})}}"
        ".rev-meta{display:flex;align-items:center;gap:7px}"
        ".rev-meta .st{width:12px;height:12px}"
        ".rev-time{font-size:11.5px;color:#9aa1ab}"
        ".rev-txt{font-size:13px;line-height:1.55;color:#4b5563}"
        ".wcrev-foot{margin-top:11px;text-align:right}"
        f".wcrev-foot a{{font-size:12px;font-weight:600;text-decoration:none;color:var(--accent,{accent})}}"
        # Interaktiver Bewerten-Block
        ".wcrev-rate{margin-top:14px;padding-top:14px;border-top:1px dashed rgba(17,24,39,.12);"
        "display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}"
        f".wcrev-rate-label{{font-size:13px;font-weight:600;color:var(--ink,{ink})}}"
        ".rate{display:inline-flex;flex-direction:row-reverse}"
        ".rate a{color:#dfe3e8;line-height:0;padding:1px;text-decoration:none}"
        ".rate a .st{width:26px;height:26px;display:block;transition:transform .1s}"
        ".rate a .st path{fill:currentColor}"
        ".rate a:hover .st{transform:scale(1.12)}"
        ".rate a:hover,.rate a:hover ~ a{color:#f3b71e}"
    )

    badge = (
        f'<a class="wcrev" href="{link}" target="_blank" rel="noopener noreferrer" '
        f'aria-label="Google-Bewertungen von {firma} ansehen">'
        f'{_GOOGLE_G}'
        f'<span class="body">'
        f'<span class="row1"><span class="score">{rating_de}</span>{_stars(rating)}</span>'
        f'<span class="row2">{count_txt} <span class="more">ansehen ›</span></span>'
        f'</span></a>'
    )

    return (f"<style>{css}</style>{gold_defs}"
            f'<div class="wcrev-wrap">{badge}{cards}{foot}{rate_block}</div>')


if __name__ == "__main__":
    demo_k = {"firma": "KFZ Meisterbetrieb DM Auto", "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
              "rating": "4.8", "review_count": "127",
              "reviews": [{"author": "Max M.", "photo": "", "uri": "", "rating": 5,
                           "time": "vor 2 Wochen", "text": "Top Service, schnell und freundlich."}]}
    demo_t = {"primary": "#0d1b2a", "accent": "#e63946", "ink": "#1f2430", "font": "Inter"}
    print(build_widget(demo_k, demo_t)[:300], "...")
