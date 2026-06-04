# -*- coding: utf-8 -*-
"""
widget.py - WebCraft Google-Bewertungs-Badge fuer die KUNDEN-WEBSITE.

Gemeinsamer Helfer (shared/), wird von Maximes Website-Pipeline aufgerufen und
in den Template-Slot @@WEBCRAFT_REVIEWS@@ eingesetzt (nur wenn bewertung == "ja").

    from widget import build_widget
    html = build_widget(kunde, tokens)

  kunde  : {"firma", "place_id", "rating", "review_count"}        (Daten)
  tokens : {"primary", "accent", "ink", "font"}                    (Design pro Kunde)

"Aus einem Guss": das Badge nutzt font:inherit und die CSS-Variablen der Seite
(var(--accent), var(--ink)); die uebergebenen tokens dienen als Fallback.
Self-contained (nur Standardbibliothek), eigener CSS-Namespace .wcrev -> keine Konflikte.
"""

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
    """Link zum LESEN der Google-Bewertungen (fuer Website-Besucher)."""
    return f"https://search.google.com/local/reviews?placeid={place_id}" if place_id else "#"


def _stars(rating) -> str:
    try:
        pct = max(0.0, min(100.0, float(rating) / 5.0 * 100.0))
    except (ValueError, TypeError):
        pct = 100.0
    base = '<span class="s-base">' + _STAR * 5 + "</span>"
    fill = f'<span class="s-fill" style="width:{pct:.1f}%">' + _STAR * 5 + "</span>"
    return '<span class="s-wrap">' + base + fill + "</span>"


def build_widget(kunde: dict, tokens: dict = None) -> str:
    """Gibt das design-adaptive Bewertungs-Badge als HTML-Snippet (style + markup) zurueck."""
    tokens = tokens or {}
    primary = tokens.get("primary", "#0f172a")
    accent = tokens.get("accent", "#3b82f6")
    ink = tokens.get("ink", "#1f2430")

    firma = kunde.get("firma", "")
    place_id = kunde.get("place_id", "")
    rating = kunde.get("rating")
    count = kunde.get("review_count")

    rating_de = (f"{float(rating):.1f}".replace(".", ",")) if rating else "–"
    count_txt = f"{count} Google-Bewertungen" if count else "Google-Bewertungen"
    link = _view_link(place_id)

    gold_defs = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
                 '<linearGradient id="wcrevgold" x1="0" y1="0" x2="0" y2="1">'
                 '<stop offset="0" stop-color="#ffd86b"/><stop offset="0.55" stop-color="#f3b71e"/>'
                 '<stop offset="1" stop-color="#dd9b0c"/></linearGradient></defs></svg>')

    # var(--accent/--ink) der Seite nutzen, tokens als Fallback
    css = (
        ".wcrev{font-family:inherit;display:inline-flex;align-items:center;gap:14px;"
        "background:#fff;border:1px solid rgba(17,24,39,.08);border-radius:16px;padding:14px 20px;"
        "box-shadow:0 1px 2px rgba(17,24,39,.04),0 10px 30px rgba(17,24,39,.08);"
        f"text-decoration:none;color:var(--ink,{ink});line-height:1.2;"
        "transition:transform .15s,box-shadow .15s}"
        ".wcrev:hover{transform:translateY(-1px);box-shadow:0 2px 4px rgba(17,24,39,.05),0 16px 40px rgba(17,24,39,.12)}"
        ".wcrev *{box-sizing:border-box}"
        ".wcrev .g{width:30px;height:30px;flex:none}"
        ".wcrev .body{display:flex;flex-direction:column;gap:3px}"
        ".wcrev .row1{display:flex;align-items:center;gap:9px}"
        f".wcrev .score{{font-size:24px;font-weight:800;letter-spacing:-.5px;color:var(--ink,{ink})}}"
        ".wcrev .s-wrap{position:relative;display:inline-flex;line-height:0}"
        ".wcrev .s-base,.wcrev .s-fill{display:inline-flex;gap:2px}"
        ".wcrev .s-fill{position:absolute;top:0;left:0;overflow:hidden;white-space:nowrap;"
        "filter:drop-shadow(0 1px 1px rgba(0,0,0,.15))}"
        ".wcrev .st{width:17px;height:17px;display:block}"
        ".wcrev .s-base .st path{fill:#e4e7ec}"
        ".wcrev .s-fill .st path{fill:url(#wcrevgold)}"
        ".wcrev .row2{font-size:12.5px;color:#6b7280;display:flex;align-items:center;gap:6px}"
        f".wcrev .more{{color:var(--accent,{accent});font-weight:600;white-space:nowrap}}"
    )
    # primary aktuell nicht direkt genutzt (ink fuehrt die Typo); bleibt fuer kuenftige Varianten verfuegbar
    _ = primary

    return (
        f"<style>{css}</style>{gold_defs}"
        f'<a class="wcrev" href="{link}" target="_blank" rel="noopener noreferrer" '
        f'aria-label="Google-Bewertungen von {firma} ansehen">'
        f'{_GOOGLE_G}'
        f'<span class="body">'
        f'<span class="row1"><span class="score">{rating_de}</span>{_stars(rating)}</span>'
        f'<span class="row2">{count_txt} <span class="more">ansehen &rsaquo;</span></span>'
        f'</span></a>'
    )


if __name__ == "__main__":
    demo_k = {"firma": "KFZ Meisterbetrieb DM Auto", "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
              "rating": "4.8", "review_count": "127"}
    demo_t = {"primary": "#0d1b2a", "accent": "#e63946", "ink": "#1f2430", "font": "Inter"}
    print(build_widget(demo_k, demo_t))
