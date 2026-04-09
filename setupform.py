import streamlit as st
import requests
import json
from datetime import datetime

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SEO Agent – Setup",
    page_icon="⚙️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }

    .stApp { background-color: #F4F4F5; }
    .block-container { max-width: 720px; padding-top: 2rem; padding-bottom: 3rem; }

    .app-header {
        background: #18181B;
        border-radius: 12px;
        padding: 22px 28px 18px;
        margin-bottom: 28px;
    }
    .app-header h1 { font-size: 19px; font-weight: 600; color: white; margin: 0 0 4px 0; }
    .app-header p  { font-size: 13px; color: #A1A1AA; margin: 0; }
    .app-header .meta { font-size: 11px; color: #52525B; margin-top: 8px; font-family: monospace; }

    .section-label {
        font-size: 10.5px; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.08em; color: #71717A; margin: 0 0 6px 2px;
    }

    .stButton > button {
        border-radius: 8px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        width: 100% !important;
        height: auto !important;
        padding: 11px 24px !important;
        border: none !important;
        transition: opacity .15s !important;
    }
    .stButton > button:hover { opacity: 0.88 !important; }

    div[data-testid="stHorizontalBlock"] div:first-child .stButton > button {
        background: #18181B !important;
        color: white !important;
    }

    .btn-danger .stButton > button {
        background: #DC2626 !important;
        color: white !important;
    }

    .result-card { border-radius: 10px; padding: 16px 20px; margin-top: 18px; font-size: 13.5px; }
    .result-success { background: #F0FDF4; border: 1px solid #86EFAC; color: #166534; }
    .result-error   { background: #FEF2F2; border: 1px solid #FCA5A5; color: #991B1B; }
    .result-delete  { background: #FFF7ED; border: 1px solid #FCD34D; color: #92400E; }

    .divider { border: none; border-top: 1px solid #E4E4E7; margin: 22px 0; }

    .field-hint { font-size: 11.5px; color: #A1A1AA; margin: -6px 0 12px 2px; line-height: 1.5; }

    .json-valid   { font-size: 11px; color: #16A34A; margin-top: 3px; }
    .json-invalid { font-size: 11px; color: #DC2626; margin-top: 3px; }

    .required-star { color: #DC2626; }

    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px !important;
        border: 1px solid #D4D4D8 !important;
        font-size: 13.5px !important;
    }
    .stCheckbox { margin-top: 4px; }
</style>
""", unsafe_allow_html=True)


# ── Config ─────────────────────────────────────────────────────────────────────
# .streamlit/secrets.toml:
#   SETUP_WEBHOOK_URL = "https://hook.eu2.make.com/SETUP_WEBHOOK"
#
try:
    WEBHOOK_URL = st.secrets["SETUP_WEBHOOK_URL"]
except (KeyError, FileNotFoundError):
    WEBHOOK_URL = "https://hook.eu2.make.com/TVŮJ_SETUP_WEBHOOK"
    st.warning("⚠️  SETUP_WEBHOOK_URL není v secrets.toml – běžím v dev módu.", icon="⚠️")


# ── Helpers ────────────────────────────────────────────────────────────────────
def is_valid_json(text: str) -> bool:
    if not text.strip():
        return True  # prázdné = OK, není povinné
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False

def json_hint(text: str, field_name: str):
    if not text.strip():
        return
    if is_valid_json(text):
        st.markdown(f'<div class="json-valid">✓ {field_name} – validní JSON</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="json-invalid">✗ {field_name} – nevalidní JSON</div>', unsafe_allow_html=True)

def send_to_webhook(payload: dict) -> tuple[bool, str]:
    try:
        r = requests.post(WEBHOOK_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        if r.status_code in (200, 201, 202):
            return True, ""
        return False, f"HTTP {r.status_code}: {r.text[:300]}"
    except requests.exceptions.Timeout:
        return False, "Timeout (15 s) – ověř URL webhooku."
    except requests.exceptions.ConnectionError:
        return False, "Nepodařilo se připojit – ověř SETUP_WEBHOOK_URL."
    except Exception as e:
        return False, str(e)


# ── Session state ──────────────────────────────────────────────────────────────
if "setup_result" not in st.session_state:
    st.session_state.setup_result = None
if "delete_result" not in st.session_state:
    st.session_state.delete_result = None


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <h1>⚙️  SEO Agent – Setup</h1>
    <p>Správa klientských konfigurací. Změny se projeví u všech nových jobů okamžitě.</p>
</div>
""", unsafe_allow_html=True)


# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_config, tab_delete = st.tabs(["⚙️  Nastavit klienta", "🗑️  Smazat klienta"])


# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 – UPSERT
# ════════════════════════════════════════════════════════════════════════════════
with tab_config:

    st.markdown("##### Identifikace")

    col_id, col_email = st.columns(2)
    with col_id:
        client_id = st.text_input(
            "Client ID ✱",
            placeholder="seyfor",
            help="Malá písmena, bez mezer. Musí odpovídat CLIENT_ID v secrets.toml Streamlit formu.",
        )
    with col_email:
        notification_email = st.text_input(
            "Notification email ✱",
            placeholder="marketing@firma.cz",
            help="Na tento e-mail přijde potvrzení setupu i hotové články.",
        )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("##### Základní informace o firmě")

    col_name, col_url = st.columns(2)
    with col_name:
        company_name = st.text_input("Název firmy ✱", placeholder="Seyfor a.s.")
    with col_url:
        website_url = st.text_input("Web ✱", placeholder="https://seyfor.com")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("##### Výchozí parametry článků")

    col1, col2 = st.columns(2)
    with col1:
        default_language = st.selectbox(
            "Výchozí jazyk ✱",
            options=["cs", "en", "sk", "de", "pl", "hu"],
        )
        default_tone = st.selectbox(
            "Výchozí tón ✱",
            options=["profesionální", "neutrální", "odborný", "přátelský", "casual"],
        )
        default_intent = st.selectbox(
            "Výchozí search intent ✱",
            options=["informational", "commercial", "transactional", "navigational"],
        )
    with col2:
        default_length = st.number_input(
            "Výchozí délka článku (slov) ✱",
            min_value=300, max_value=5000, value=1500, step=100,
        )
        default_audience = st.text_input(
            "Výchozí publikum ✱",
            placeholder="B2B, IT manažeři, střední a velké firmy",
        )
        requires_review = st.checkbox(
            "Vyžadovat manuální schválení pro všechny joby",
            value=False,
            help="Přepíše automatický routing – každý job půjde na ruční kontrolu před generováním.",
        )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("##### Brand obsah")

    brand_voice = st.text_area(
        "Brand voice rules ✱",
        height=120,
        placeholder=(
            "Popište styl a pravidla psaní:\n"
            "– Vyhýbej se žargonu, piš srozumitelně\n"
            "– Nepoužívej superlativy bez důkazů\n"
            "– Vždy uváděj konkrétní příklady\n"
            "– Nepropaguj konkrétní produkty"
        ),
    )

    company_context = st.text_area(
        "Company context ✱",
        height=100,
        placeholder=(
            "Kontext pro social media planner:\n"
            "Seyfor je česká technologická firma specializující se na ERP, "
            "cloudová řešení a digitální transformaci pro střední a velké podniky."
        ),
        help="Používá Agent_6 (social planner) při generování příspěvků a UTM parametrů.",
    )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("##### Výstupy")

    drive_folder_id = st.text_input(
        "Google Drive Folder ID ✱",
        placeholder="1SXPSbAgiDpSZDPo5_N6pRkBWT3NrKmxc",
        help="ID složky v Google Drive, kam Agent_6 ukládá hotové články a social posty.",
    )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    with st.expander("🔧  Pokročilá nastavení"):
        st.caption("Volitelné. Pokud zůstanou prázdná, Agent_6 (social planner) použije výchozí hodnoty.")

        # ── Channels ───────────────────────────────────────────────────────────
        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        enable_social = st.checkbox(
            "Generovat doporučení pro sociální sítě",
            value=bool(st.session_state.get("channels")),
            key="enable_social",
            help="Pokud vypnuto, Agent_6 přeskočí social planner a rovnou uloží článek do Drive.",
        )

        if "channels" not in st.session_state:
            st.session_state.channels = []

        CHANNEL_OPTIONS = ["LinkedIn", "Twitter/X", "Facebook", "Instagram", "YouTube", "TikTok", "Newsletter"]
        FORMAT_OPTIONS  = [
            "thought leadership post",
            "short post, max 280 chars",
            "carousel post",
            "video script teaser",
            "newsletter blurb",
            "story / reel caption",
        ]
        LANG_OPTIONS = ["cs", "en", "sk", "de", "pl"]

        if enable_social:
            st.markdown(
                '<div class="field-hint">Kanály, pro které agent připraví příspěvky. Max. 3 kanály.</div>',
                unsafe_allow_html=True,
            )

            to_remove = None
            for i, ch in enumerate(st.session_state.channels):
                with st.container():
                    st.markdown(f'<div style="background:var(--background-color,#F9F9F9);border:1px solid #E4E4E7;border-radius:8px;padding:12px 14px;margin-bottom:8px;">', unsafe_allow_html=True)
                    c1, c2, c3 = st.columns([2, 2, 1])
                    with c1:
                        ch["channel"] = st.selectbox(
                            "Kanál",
                            options=CHANNEL_OPTIONS,
                            index=CHANNEL_OPTIONS.index(ch["channel"]) if ch["channel"] in CHANNEL_OPTIONS else 0,
                            key=f"ch_name_{i}",
                        )
                    with c2:
                        ch["language"] = st.selectbox(
                            "Jazyk příspěvku",
                            options=LANG_OPTIONS,
                            index=LANG_OPTIONS.index(ch["language"]) if ch["language"] in LANG_OPTIONS else 0,
                            key=f"ch_lang_{i}",
                        )
                    with c3:
                        st.markdown("<div style='margin-top:24px'>", unsafe_allow_html=True)
                        if st.button("✕ Odebrat", key=f"ch_remove_{i}"):
                            to_remove = i
                        st.markdown("</div>", unsafe_allow_html=True)

                    ch["format"] = st.selectbox(
                        "Formát příspěvku",
                        options=FORMAT_OPTIONS,
                        index=FORMAT_OPTIONS.index(ch["format"]) if ch["format"] in FORMAT_OPTIONS else 0,
                        key=f"ch_fmt_{i}",
                        help="Styl a délka příspěvku, který agent napíše pro tento kanál.",
                    )
                    hashtags_raw = st.text_input(
                        "Hashtags (oddělené mezerou)",
                        value=" ".join(ch.get("hashtags", [])),
                        key=f"ch_tags_{i}",
                        placeholder="#digitalnítransformace #ERP #cloud",
                        help="Volitelné. Hashtags agent přidá na konec příspěvku.",
                    )
                    ch["hashtags"] = [t.strip() for t in hashtags_raw.split() if t.strip()]
                    st.markdown('</div>', unsafe_allow_html=True)

            if to_remove is not None:
                st.session_state.channels.pop(to_remove)
                st.rerun()

            if len(st.session_state.channels) < 3:
                if st.button("＋ Přidat kanál", key="add_channel"):
                    st.session_state.channels.append({
                        "channel": "LinkedIn",
                        "language": "cs",
                        "format": "thought leadership post",
                        "hashtags": [],
                    })
                    st.rerun()
            else:
                st.caption("Dosažen maximální počet kanálů (3).")

            channels_json = json.dumps(st.session_state.channels, ensure_ascii=False)
            if st.session_state.channels:
                st.markdown(
                    f'<div class="json-valid">✓ {len(st.session_state.channels)} kanál(y) nastaven(y)</div>',
                    unsafe_allow_html=True,
                )
        else:
            # Social vypnut – vyčistit kanály a poslat prázdné pole
            st.session_state.channels = []
            channels_json = "[]"
            st.caption("Social planner bude přeskočen. Agent uloží článek do Drive a pošle email.")

        # ── UTM defaults ───────────────────────────────────────────────────────
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("**UTM parametry**")
        st.markdown(
            '<div class="field-hint">'
            'Výchozí UTM parametry přidávané ke všem odkazům v příspěvcích. '
            'Agent doplní <code>utm_campaign</code> o slug článku automaticky. '
            'Bez mezer, pouze malá písmena a pomlčky.'
            '</div>',
            unsafe_allow_html=True,
        )
        utm_col1, utm_col2, utm_col3 = st.columns(3)
        with utm_col1:
            utm_source = st.text_input("utm_source", value="blog", placeholder="blog", key="utm_source")
        with utm_col2:
            utm_medium = st.text_input("utm_medium", value="organic", placeholder="organic", key="utm_medium")
        with utm_col3:
            utm_campaign = st.text_input(
                "utm_campaign (základ)",
                value="seo",
                placeholder="seo",
                key="utm_campaign",
                help="Agent doplní slug článku, např. 'seo' → 'seo-erp-pro-vyrobu'",
            )
        utm_defaults_json = json.dumps({
            "utm_source":   utm_source.strip() or "blog",
            "utm_medium":   utm_medium.strip() or "organic",
            "utm_campaign": utm_campaign.strip() or "seo",
        }, ensure_ascii=False)

        # ── Employee advocacy ──────────────────────────────────────────────────
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("**Employee advocacy**")
        st.markdown(
            '<div class="field-hint">'
            'Pravidla pro interní šíření článku mezi zaměstnanci.'
            '</div>',
            unsafe_allow_html=True,
        )

        adv_who_raw = st.text_input(
            "Kdo má sdílet (role nebo jména, oddělená čárkou)",
            placeholder="marketing tým, CEO, produktoví manažeři",
            key="adv_who",
            help="Agent doporučí těmto lidem, aby článek sdíleli na svých profilech.",
        )
        adv_template = st.text_area(
            "Šablona DM zprávy",
            height=80,
            placeholder="Ahoj, právě jsme publikovali článek o {topic}. Sdílej ho na svém LinkedIn!",
            key="adv_template",
            help="Použij {topic} jako zástupný symbol — agent ho nahradí tématem článku.",
        )
        adv_timing = st.text_input(
            "Kdy sdílet",
            placeholder="do 2 hodin po publikaci",
            key="adv_timing",
            help="Agent toto doporučení uvede v plánu.",
        )
        adv_who_list = [r.strip() for r in adv_who_raw.split(",") if r.strip()]
        employee_advocacy = json.dumps({
            "who_to_involve": adv_who_list,
            "dm_template":    adv_template.strip() or "Ahoj, podívej se na náš nový článek o {topic}!",
            "timing":         adv_timing.strip() or "do 24 hodin po publikaci",
        }, ensure_ascii=False)

    # ── Validation & Submit ──
    st.markdown('<br>', unsafe_allow_html=True)

    required_fields = {
        "Client ID": client_id,
        "Notification email": notification_email,
        "Název firmy": company_name,
        "Web": website_url,
        "Publikum": default_audience,
        "Brand voice rules": brand_voice,
        "Company context": company_context,
        "Google Drive Folder ID": drive_folder_id,
    }

    missing = [k for k, v in required_fields.items() if not v.strip()]
    invalid_json = []  # channels, utm, advocacy jsou sestaveny programaticky – vždy validní JSON

    if missing:
        st.caption(f"✱ Povinná pole: {', '.join(missing)}")
    if invalid_json:
        st.caption(f"⚠️  Oprav JSON v: {', '.join(invalid_json)}")

    submit_disabled = bool(missing or invalid_json)

    if st.button(
        "💾  Uložit konfiguraci" + (" (chybí povinná pole)" if submit_disabled else ""),
        key="submit_upsert",
        disabled=submit_disabled,
    ):
        payload = {
            "action": "upsert",
            "client_id": client_id.strip(),
            "notification_email": notification_email.strip(),
            "company_name": company_name.strip(),
            "website_url": website_url.strip(),
            "default_language": default_language,
            "default_tone": default_tone,
            "default_audience": default_audience.strip(),
            "default_intent": default_intent,
            "default_length_words": int(default_length),
            "requires_manual_review": requires_review,
            "brand_voice_rules": brand_voice.strip(),
            "company_context": company_context.strip(),
            "drive_folder_id": drive_folder_id.strip(),
            "channels_json": channels_json.strip() or "[]",
            "utm_defaults_json": utm_defaults_json.strip() or "{}",
            "employee_advocacy": employee_advocacy.strip() or "{}",
        }
        with st.spinner("Ukládám konfiguraci…"):
            ok, err = send_to_webhook(payload)
        st.session_state.setup_result = {
            "success": ok,
            "error": err,
            "client_id": client_id,
            "company_name": company_name,
            "time": datetime.now().strftime("%H:%M:%S"),
            "payload": payload,
        }
        st.rerun()

    if st.session_state.setup_result:
        r = st.session_state.setup_result
        if r["success"]:
            st.markdown(f"""
            <div class="result-card result-success">
                <strong>✓ Konfigurace uložena</strong><br>
                Klient <strong>{r['client_id']}</strong> ({r['company_name']}) je nastaven a aktivní.<br>
                <span style="font-size:11.5px;opacity:0.7">Uloženo v {r['time']} · Potvrzení odesláno na {notification_email}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-card result-error">
                <strong>✗ Chyba při odesílání</strong><br>{r['error']}
            </div>
            """, unsafe_allow_html=True)
        with st.expander("Zobrazit odeslaný payload"):
            st.json(st.session_state.setup_result.get("payload", {}))


# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 – DELETE
# ════════════════════════════════════════════════════════════════════════════════
with tab_delete:

    st.markdown("##### Smazat klienta ze seo_config")
    st.markdown(
        '<div class="field-hint">Smaže celý konfigurační záznam z datastoru. '
        'Již spuštěné joby nejsou ovlivněny – mají config uložený v job record.</div>',
        unsafe_allow_html=True,
    )

    col_del_id, col_del_email = st.columns(2)
    with col_del_id:
        delete_client_id = st.text_input(
            "Client ID ke smazání",
            placeholder="seyfor",
            key="del_client_id",
        )
    with col_del_email:
        delete_email = st.text_input(
            "Notification email",
            placeholder="admin@firma.cz",
            key="del_email",
            help="Na tento e-mail přijde potvrzení smazání.",
        )

    st.markdown('<br>', unsafe_allow_html=True)

    confirm_delete = st.checkbox(
        f"Rozumím, že tato akce je nevratná a chci smazat klienta **{delete_client_id or '…'}**",
        key="confirm_delete",
    )

    delete_ready = bool(delete_client_id.strip() and delete_email.strip() and confirm_delete)

    st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
    delete_clicked = st.button(
        "🗑️  Smazat klienta" + ("" if delete_ready else " (potvrď výše)"),
        key="submit_delete",
        disabled=not delete_ready,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if delete_clicked and delete_ready:
        payload = {
            "action": "delete",
            "client_id": delete_client_id.strip(),
            "notification_email": delete_email.strip(),
        }
        with st.spinner("Mažu klienta…"):
            ok, err = send_to_webhook(payload)
        st.session_state.delete_result = {
            "success": ok,
            "error": err,
            "client_id": delete_client_id,
            "time": datetime.now().strftime("%H:%M:%S"),
        }
        st.rerun()

    if st.session_state.delete_result:
        r = st.session_state.delete_result
        if r["success"]:
            st.markdown(f"""
            <div class="result-card result-delete">
                <strong>✓ Klient smazán</strong><br>
                Konfigurace <strong>{r['client_id']}</strong> byla odstraněna z datastoru.<br>
                <span style="font-size:11.5px;opacity:0.7">Smazáno v {r['time']}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-card result-error">
                <strong>✗ Chyba</strong><br>{r['error']}
            </div>
            """, unsafe_allow_html=True)


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<hr class="divider">
<div style="text-align:center;font-size:12px;color:#A1A1AA;">
    SEO Agent Setup · pouze pro administrátory
</div>
""", unsafe_allow_html=True)
