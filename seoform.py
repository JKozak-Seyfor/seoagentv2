import streamlit as st
import requests
import json
from datetime import datetime

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SEO Article Request",
    page_icon="✍️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Import font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hide default Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }

    /* Page background */
    .stApp {
        background-color: #F7F6F3;
    }

    /* Main container */
    .block-container {
        max-width: 680px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    /* Header strip */
    .app-header {
        background: #1A1A2E;
        border-radius: 12px;
        padding: 24px 28px 20px;
        margin-bottom: 28px;
        color: white;
    }
    .app-header h1 {
        font-size: 20px;
        font-weight: 600;
        margin: 0 0 4px 0;
        color: white;
    }
    .app-header p {
        font-size: 13px;
        color: #9CA3AF;
        margin: 0;
    }

    /* Section labels */
    .section-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #6B7280;
        margin: 0 0 8px 2px;
    }

    /* Keyword pills container */
    .keyword-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 12px;
        min-height: 36px;
    }
    .keyword-pill {
        background: #1A1A2E;
        color: white;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 13px;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    .pill-remove {
        cursor: pointer;
        opacity: 0.6;
        font-size: 14px;
        line-height: 1;
    }

    /* Info box */
    .info-box {
        background: #EEF2FF;
        border: 1px solid #C7D2FE;
        border-radius: 8px;
        padding: 12px 14px;
        font-size: 12.5px;
        color: #4338CA;
        margin-bottom: 20px;
    }
    .info-box strong { color: #3730A3; }

    /* Config defaults preview */
    .defaults-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: 8px;
    }
    .default-item {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 8px 12px;
    }
    .default-item .label {
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #9CA3AF;
        font-weight: 600;
    }
    .default-item .value {
        font-size: 13px;
        color: #111827;
        font-weight: 500;
        margin-top: 2px;
    }

    /* Submit button */
    .stButton > button {
        background: #1A1A2E !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 28px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        width: 100% !important;
        height: auto !important;
        transition: opacity 0.15s !important;
    }
    .stButton > button:hover {
        opacity: 0.88 !important;
    }

    /* Success / error cards */
    .result-card {
        border-radius: 10px;
        padding: 18px 20px;
        margin-top: 20px;
        font-size: 14px;
    }
    .result-success {
        background: #ECFDF5;
        border: 1px solid #6EE7B7;
        color: #065F46;
    }
    .result-error {
        background: #FEF2F2;
        border: 1px solid #FCA5A5;
        color: #991B1B;
    }

    /* Divider */
    .custom-divider {
        border: none;
        border-top: 1px solid #E5E7EB;
        margin: 24px 0;
    }

    /* Expander styling */
    details summary {
        font-size: 13px !important;
        font-weight: 500 !important;
        color: #6B7280 !important;
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px !important;
        border: 1px solid #D1D5DB !important;
        font-size: 14px !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Configuration ──────────────────────────────────────────────────────────────
# Hodnoty se čtou ze Streamlit secrets (.streamlit/secrets.toml)
# Každý zákazník má vlastní deployment s vlastními secrets – kód se nemění.
#
# Příklad .streamlit/secrets.toml:
#   WEBHOOK_URL = "https://hook.eu2.make.com/TVŮJ_WEBHOOK_URL"
#   CLIENT_ID   = "seyfor"
#
try:
    WEBHOOK_URL = st.secrets["WEBHOOK_URL"]
    CLIENT_ID   = st.secrets["CLIENT_ID"]
except (KeyError, FileNotFoundError):
    # Fallback pro lokální vývoj bez secrets.toml
    WEBHOOK_URL = "https://hook.eu2.make.com/TVŮJ_WEBHOOK_URL"
    CLIENT_ID   = "dev_client"
    st.warning("⚠️  Secrets nejsou nastaveny – běžím v dev módu. Nastav `.streamlit/secrets.toml`.", icon="⚠️")

# Výchozí hodnoty ze seo_config (zobrazují se jako nápověda – nepřepisují config v datastoru)
SEO_CONFIG_PREVIEW = {
    "Jazyk": "cs",
    "Tón": "profesionální",
    "Publikum": "B2B, IT manažeři",
    "Délka": "1 500 slov",
    "Intent": "informational",
}


# ── Session state init ─────────────────────────────────────────────────────────
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "last_result" not in st.session_state:
    st.session_state.last_result = None


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-header">
    <h1>✍️ Nový SEO článek</h1>
    <p>Zadej klíčová slova a spusť tvorbu článku. Zbytek zařídí AI agent automaticky.</p>
    <p style="margin-top:8px;font-size:11px;opacity:0.5;font-family:monospace">client: {CLIENT_ID}</p>
</div>
""", unsafe_allow_html=True)


# ── Config defaults preview ────────────────────────────────────────────────────
with st.expander("ℹ️  Výchozí nastavení ze seo_config"):
    items_html = "".join([
        f'<div class="default-item"><div class="label">{k}</div><div class="value">{v}</div></div>'
        for k, v in SEO_CONFIG_PREVIEW.items()
    ])
    st.markdown(f'<div class="defaults-grid">{items_html}</div>', unsafe_allow_html=True)
    st.caption("Tato nastavení jsou platná pro všechny joby. Změnit je může admin přes Setup scénář.")


# ── Primární klíčové slovo ─────────────────────────────────────────────────────
st.markdown('<div class="section-label">Primární klíčové slovo ✱</div>', unsafe_allow_html=True)
primary_keyword = st.text_input(
    label="Primární klíčové slovo",
    placeholder="např. ERP systém pro výrobu",
    label_visibility="collapsed",
    key="primary_kw",
    help="Hlavní KW – agent ho použije v H1, URL slugu, meta title a prvním odstavci.",
)

# ── Sekundární klíčová slova ───────────────────────────────────────────────────
st.markdown('<br>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Sekundární klíčová slova (volitelné)</div>', unsafe_allow_html=True)
st.markdown(
    '<div style="font-size:12px;color:var(--color-text-secondary);margin-bottom:8px;">'
    'Každé KW na nový řádek nebo oddělená čárkou. Agent je přirozeně zapracuje do H2 nadpisů a těla článku.</div>',
    unsafe_allow_html=True,
)

sec_kw_raw = st.text_area(
    label="Sekundární klíčová slova",
    placeholder="cloudový ERP\nimplementace ERP\nERP pro výrobu",
    label_visibility="collapsed",
    height=100,
    key="sec_kw_raw",
)

# Parsování – rozdělení podle čárek nebo nových řádků, deduplikace, trim
def parse_keywords(raw: str) -> list:
    import re
    parts = re.split(r'[,\n]', raw)
    seen = set()
    result = []
    for p in parts:
        kw = p.strip()
        if kw and kw.lower() not in seen:
            seen.add(kw.lower())
            result.append(kw)
    return result

secondary_keywords_parsed = parse_keywords(sec_kw_raw)

if secondary_keywords_parsed:
    pills_html = "".join([
        f'<span style="display:inline-block;background:var(--color-background-secondary);'
        f'border:1px solid var(--color-border-tertiary);border-radius:20px;'
        f'padding:3px 10px;font-size:12px;margin:2px 3px 2px 0;">{kw}</span>'
        for kw in secondary_keywords_parsed
    ])
    st.markdown(
        f'<div style="margin-top:6px">{pills_html}</div>'
        f'<div style="font-size:11px;color:var(--color-text-tertiary);margin-top:5px;">'
        f'{len(secondary_keywords_parsed)} klíčových slov</div>',
        unsafe_allow_html=True,
    )

# ── Pracovní název článku ──────────────────────────────────────────────────────
st.markdown('<br>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Pracovní název článku (volitelné)</div>', unsafe_allow_html=True)
title_hint = st.text_input(
    label="Pracovní název",
    placeholder="např. Jak vybrat ERP systém pro výrobní firmu",
    label_visibility="collapsed",
    key="title_hint",
    help="Agent použije tento název jako výchozí bod pro navržené nadpisy. Může ho upravit, ale bude ho respektovat.",
)


# ── Seed links ─────────────────────────────────────────────────────────────────
st.markdown('<br>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Zdrojové URL (volitelné)</div>', unsafe_allow_html=True)
seed_links_raw = st.text_area(
    label="Zdrojové URL",
    placeholder="Každý odkaz na nový řádek\nhttps://example.com/zdroj-1\nhttps://example.com/zdroj-2",
    label_visibility="collapsed",
    height=90,
    key="seed_links",
)


# ── Advanced overrides ─────────────────────────────────────────────────────────
st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

with st.expander("⚙️  Přepsat výchozí nastavení (volitelné)"):
    st.caption("Tyto hodnoty mají přednost před seo_config pouze pro tento job.")

    ov_col1, ov_col2 = st.columns(2)
    with ov_col1:
        override_language = st.selectbox(
            "Jazyk",
            options=["— výchozí z config —", "cs", "en", "sk", "de", "pl"],
            key="ov_language",
        )
        override_intent = st.selectbox(
            "Search intent",
            options=["— výchozí z config —", "informational", "navigational", "transactional", "commercial"],
            key="ov_intent",
        )
    with ov_col2:
        override_tone = st.selectbox(
            "Tón",
            options=["— výchozí z config —", "profesionální", "neutrální", "přátelský", "odborný", "casual"],
            key="ov_tone",
        )
        override_length = st.number_input(
            "Délka článku (slov)",
            min_value=0,
            max_value=5000,
            value=0,
            step=100,
            key="ov_length",
            help="0 = použije se výchozí délka ze seo_config",
        )


# ── Submit ─────────────────────────────────────────────────────────────────────
st.markdown('<br>', unsafe_allow_html=True)

submit = st.button("🚀  Spustit tvorbu článku", key="submit_btn")

if submit:
    if not primary_keyword.strip():
        st.error("Vyplň primární klíčové slovo.")
    else:
        # Build payload
        payload = {
            "client_id":       CLIENT_ID,
            "primary_keyword": primary_keyword.strip(),
        }

        if secondary_keywords_parsed:
            payload["secondary_keywords"] = secondary_keywords_parsed

        if title_hint.strip():
            payload["title_hint"] = title_hint.strip()

        # Seed links
        seed_links = [l.strip() for l in seed_links_raw.splitlines() if l.strip()]
        if seed_links:
            payload["seed_links"] = seed_links

        # Optional overrides – přidávají se jen pokud jsou vyplněné
        if override_language != "— výchozí z config —":
            payload["language"] = override_language
        if override_tone != "— výchozí z config —":
            payload["override_tone"] = override_tone
        if override_intent != "— výchozí z config —":
            payload["override_intent"] = override_intent
        if override_length and override_length > 0:
            payload["length_words"] = int(override_length)

        # Send to Make webhook
        try:
            with st.spinner("Odesílám požadavek…"):
                response = requests.post(
                    WEBHOOK_URL,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=15,
                )

            if response.status_code in (200, 201, 202):
                st.session_state.last_result = {
                    "success": True,
                    "primary_keyword": primary_keyword.strip(),
                    "payload": payload,
                    "time": datetime.now().strftime("%H:%M:%S"),
                }
                # Reset formuláře — textarea se resetuje automaticky přes rerun
                st.rerun()
            else:
                st.session_state.last_result = {
                    "success": False,
                    "status_code": response.status_code,
                    "body": response.text[:300],
                }
                st.rerun()

        except requests.exceptions.Timeout:
            st.error("Požadavek vypršel (timeout 15 s). Ověř URL webhooku nebo to zkus znovu.")
        except requests.exceptions.ConnectionError:
            st.error("Nepodařilo se připojit k Make. Ověř WEBHOOK_URL v kódu aplikace.")
        except Exception as e:
            st.error(f"Neočekávaná chyba: {e}")


# ── Result feedback ────────────────────────────────────────────────────────────
if st.session_state.last_result:
    r = st.session_state.last_result
    if r["success"]:
        kw_list = r["primary_keyword"]
        st.markdown(f"""
        <div class="result-card result-success">
            <strong>✓ Článek je ve frontě</strong><br>
            Primární KW: <strong>{kw_list}</strong><br>
            <span style="font-size:12px;opacity:0.75">Odesláno v {r['time']}. Hotový článek přijde e-mailem.</span>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("Zobrazit odeslaný payload"):
            st.json(r["payload"])
    else:
        st.markdown(f"""
        <div class="result-card result-error">
            <strong>✗ Chyba při odesílání</strong><br>
            HTTP {r.get('status_code', '?')}: {r.get('body', 'Neznámá chyba')}
        </div>
        """, unsafe_allow_html=True)


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<hr class="custom-divider">
<div style="text-align:center; font-size:12px; color:#9CA3AF">
    SEO Article Agent · powered by Make &amp; Claude
</div>
""", unsafe_allow_html=True)
