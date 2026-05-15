"""
XRP Visual Rule Builder - A Streamlit application for building targeting rules visually.
"""

from typing import List, Tuple, Dict, Optional
import streamlit as st

st.set_page_config(
    page_title="XRP DSL Builder",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.header-banner {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    padding: 2rem 2.5rem; border-radius: 16px; margin-bottom: 1.75rem;
}
.header-title { color: white; font-size: 2rem; font-weight: 700; margin: 0 0 0.4rem 0; letter-spacing: -0.5px; }
.header-sub { color: rgba(255,255,255,0.6); font-size: 0.9rem; margin: 0; }
.header-badge {
    display: inline-block;
    background: linear-gradient(90deg, #e94560, #7b2ff7);
    color: white; padding: 0.25rem 0.75rem; border-radius: 20px;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 1px;
    text-transform: uppercase; margin-left: 0.75rem; vertical-align: middle;
}
.section-title {
    font-size: 1rem; font-weight: 700; color: #1e293b;
    text-transform: uppercase; letter-spacing: 0.8px;
    padding-bottom: 0.5rem; border-bottom: 2px solid #6366f1;
    margin-bottom: 1.25rem; display: inline-block;
}
.condition-row {
    background: #fafbff; border: 1px solid #e2e8f0;
    border-left: 4px solid #6366f1; border-radius: 10px;
    padding: 0.85rem 1.1rem; margin-bottom: 0.75rem;
    transition: box-shadow 0.2s ease;
}
.condition-row:hover { box-shadow: 0 4px 18px rgba(99,102,241,0.12); border-color: #6366f1; }
.dsl-box {
    background: #0d1117; border: 1px solid #30363d; border-radius: 12px;
    padding: 1.25rem 1.5rem; font-family: 'Courier New', monospace;
    font-size: 0.88rem; color: #79c0ff; line-height: 1.7;
    word-break: break-all; min-height: 60px;
}
.dsl-empty { color: #6e7681; font-style: italic; }
.result-pass {
    background: linear-gradient(135deg, #052e16, #064e3b);
    border: 1px solid #22c55e; border-radius: 14px;
    padding: 1.5rem 2rem; text-align: center; color: white; margin-bottom: 1.25rem;
}
.result-fail {
    background: linear-gradient(135deg, #450a0a, #7f1d1d);
    border: 1px solid #ef4444; border-radius: 14px;
    padding: 1.5rem 2rem; text-align: center; color: white; margin-bottom: 1.25rem;
}
.result-icon { font-size: 2.5rem; margin-bottom: 0.3rem; }
.result-title { font-size: 1.3rem; font-weight: 700; }
.result-desc { font-size: 0.85rem; opacity: 0.75; margin-top: 0.25rem; }
.debug-pass {
    background: #f0fdf4; border-left: 3px solid #22c55e;
    padding: 0.6rem 1rem; border-radius: 8px; margin-bottom: 0.4rem;
    font-size: 0.875rem; color: #14532d;
}
.debug-fail {
    background: #fef2f2; border-left: 3px solid #ef4444;
    padding: 0.6rem 1rem; border-radius: 8px; margin-bottom: 0.4rem;
    font-size: 0.875rem; color: #7f1d1d;
}
.pill { display: inline-block; padding: 0.3rem 0.9rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin-right: 0.5rem; }
.pill-total { background: #e0e7ff; color: #3730a3; }
.pill-pass  { background: #dcfce7; color: #15803d; }
.pill-fail  { background: #fee2e2; color: #b91c1c; }
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    padding: 0.65rem 2rem !important; font-weight: 600 !important;
    font-size: 1rem !important; letter-spacing: 0.3px !important;
    width: 100% !important; transition: all 0.2s !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 8px 24px rgba(99,102,241,0.45) !important; }
section[data-testid="stSidebar"] { background: #f8faff !important; border-right: 1px solid #e2e8f0 !important; }
.sidebar-card { background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.9rem 1rem; margin-bottom: 0.85rem; }
.sidebar-card-title { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: #6366f1; margin-bottom: 0.6rem; }
.stTabs [data-baseweb="tab-list"] { background: #f1f5f9; padding: 0.35rem 0.4rem; border-radius: 12px; gap: 0.35rem; }
.stTabs [data-baseweb="tab"] { border-radius: 8px !important; font-weight: 500 !important; padding: 0.45rem 1.25rem !important; font-size: 0.9rem !important; }
.stTabs [aria-selected="true"] { background: white !important; box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important; font-weight: 600 !important; }
hr { border: none !important; border-top: 1px solid #e2e8f0 !important; margin: 1.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)


# ==================== CONFIGURATION ====================

RECOMMENDATIONS: Dict[str, Dict[str, str]] = {
    "XIT_AIQ_PREDICTIVE_WAN_SCORE": {
        "title": "WiFi Alert",
        "en-US": "An issue may be affecting your home internet. A technician can help.",
        "es-US": "Parece que hay un problema con el internet de tu hogar. Un técnico puede ayudarte."
    },
    "XIT_AIQ_PREDICTIVE_OUTSIDE_HOME": {
        "title": "Outside Technician",
        "en-US": "To fix an internet issue, a technician may access equipment outside your home.",
        "es-US": "Para solucionar el problema, un técnico podría acceder al equipo que se encuentra afuera de tu hogar."
    }
}

FACT_DSL_MAP: Dict[str, str] = {
    "Client Device Make": "facts.client.device.make",
    "Client Device Model": "facts.client.device.model",
    "Client Device OS Name": "facts.client.device.os.name",
    "Client Device OS Version": "facts.client.device.os.version",
    "Client Platform": "facts.client.platform",
    "Client App Version": "facts.client.version",
    "Service Account ID": "serviceAccount.id",
    "Service Account Partner": "serviceAccount.partner",
    "User Role": "facts.auth.user_role",
    "Has Multiple Accounts": "facts.auth.has_multiple_accounts",
    "Internet Backup On": "rule.is_internet_backup_on",
    "Power Backup On": "rule.is_power_backup_on",
    "Show Line Level Experience": "rule.should_show_line_level_experience",
    "Audience": "facts.xcdp.realized",
    "Experiment Treatment": "experiment.{experiment_name}.treatment",
    "Last Account Visit": "facts.visits_account.accessedOn",
    "Last Account2 Visit": "facts.visits_account2.accessedOn",
}

FACT_VALUES: Dict[str, List[str]] = {
    "Client Device Make": ["Samsung", "Apple"],
    "Client Device Model": ["SM-G955U", "iPhone", "Custom"],
    "Client Device OS Name": ["Android", "iOS"],
    "Client Device OS Version": ["Custom"],
    "Client Platform": ["MOBILE", "WEB"],
    "Client App Version": ["Custom"],
    "Service Account ID": ["Custom"],
    "Service Account Partner": ["comcast", "Custom"],
    "User Role": ["PRIMARY", "SECONDARY", "RESTRICTED_SECONDARY", "MEMBER", "SIM"],
    "Has Multiple Accounts": ["true", "false"],
    "Internet Backup On": ["true", "false"],
    "Power Backup On": ["true", "false"],
    "Show Line Level Experience": ["true", "false"],
    "Audience": ["HQ_Cust_XM_Income_Above50K_Legacy", "HQ_Cust_Digital_Soccer_Likely", "Custom"],
    "Experiment Treatment": ["on", "off", "control", "Custom"],
    "Last Account Visit": ["Custom"],
    "Last Account2 Visit": ["Custom"],
}


# ==================== UTILITY FUNCTIONS ====================

def generate_dsl(conditions: List[Tuple[str, str, str]], logic: str) -> str:
    if not conditions:
        return ""
    dsl_parts = []
    for fact, operator, value in conditions:
        if not value or not value.strip():
            raise ValueError(f"Empty value for fact '{fact}' — please fill in all values")
        dsl_path = FACT_DSL_MAP.get(fact, fact)
        is_rule_flag = dsl_path.startswith("rule.")
        is_boolean_value = value.lower() in ["true", "false"]
        if is_rule_flag and is_boolean_value:
            dsl_expr = f"!{dsl_path}" if operator == "is not" else dsl_path
        else:
            dsl_operator = "==" if operator == "is" else "!="
            dsl_expr = f'{dsl_path} {dsl_operator} "{value.strip()}"'
        dsl_parts.append(dsl_expr)
    logic_op = " && " if logic == "AND" else " || "
    return f"({logic_op.join(dsl_parts)})"


def get_test_value_for_fact(fact: str, test_values: Dict[str, str]) -> str:
    fact_map = {
        "Client Device Make": test_values.get("device_make"),
        "Client Device OS Name": test_values.get("device_os"),
        "User Role": test_values.get("user_role"),
        "Service Account ID": test_values.get("account_id"),
        "Has Multiple Accounts": test_values.get("has_multiple"),
        "Audience": test_values.get("audience") or "(empty)",
        "Internet Backup On": test_values.get("internet_backup"),
        "Power Backup On": test_values.get("power_backup"),
        "Show Line Level Experience": test_values.get("show_line_level"),
    }
    return fact_map.get(fact, "N/A (not supported in test)")


def evaluate_condition(fact: str, operator: str, expected_value: str, actual_value: str) -> bool:
    if actual_value.startswith("N/A"):
        return False
    match = (actual_value == expected_value)
    return (not match) if operator == "is not" else match


# ==================== SIDEBAR ====================

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem 0;">
        <div style="font-size:2rem;">⚡</div>
        <div style="font-weight:700;font-size:1.1rem;color:#1e293b;">XRP DSL Builder</div>
        <div style="font-size:0.75rem;color:#64748b;margin-top:0.2rem;">Test Scenario Configuration</div>
    </div>
    <hr style="margin:0.75rem 0 1rem 0 !important;">
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-card"><div class="sidebar-card-title"> Customer Profile</div>', unsafe_allow_html=True)
    test_device_make = st.selectbox("Device Make", ["Samsung", "Apple"])
    test_device_os = st.selectbox("Device OS", ["Android", "iOS"])
    test_user_role = st.selectbox("User Role", ["PRIMARY", "SECONDARY", "RESTRICTED_SECONDARY", "MEMBER", "SIM", "MANAGER"])
    test_account_id = st.text_input("Account ID", placeholder="Enter account ID...")
    test_has_multiple = st.selectbox("Multiple Accounts", ["true", "false"])
    test_audience = st.text_input("Audience Segment", placeholder="e.g. HQ_Cust_XM_Income_Above50K_Legacy")
    st.markdown('</div>', unsafe_allow_html=True)

    audience_display = test_audience if test_audience else '<i style="color:#94a3b8">Not set</i>'
    st.markdown(f"""
    <div class="sidebar-card" style="background:#f0f9ff;border-color:#bae6fd;">
        <div class="sidebar-card-title" style="color:#0284c7;">📊 Active Profile</div>
        <div style="font-size:0.8rem;color:#334155;line-height:1.8;">
            <b>Device:</b> {test_device_make} · {test_device_os}<br>
            <b>Role:</b> {test_user_role}<br>
            <b>Multi-Account:</b> {test_has_multiple}<br>
            <b>Audience:</b> {audience_display}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;padding:1.25rem 0 0.5rem 0;border-top:1px solid #e2e8f0;margin-top:0.5rem;">
        <div style="font-size:0.7rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:0.3rem;">Developed by</div>
        <div style="font-weight:700;font-size:0.9rem;color:#1e293b;">Sakthivel Viswanathan</div>
        <div style="font-size:0.75rem;color:#6366f1;font-weight:500;">Engineer II</div>
    </div>
    """, unsafe_allow_html=True)

test_internet_backup = "false"
test_power_backup = "false"
test_show_line_level = "false"


# ==================== HEADER ====================

st.markdown("""
<div class="header-banner">
    <div>
        <div style="margin-bottom:0.5rem;">
            <span class="header-title">⚡ XRP DSL Builder</span>
            <span class="header-badge">Visual Rule Engine</span>
        </div>
        <p class="header-sub">Build targeting rules visually &nbsp;·&nbsp; Generate DSL expressions &nbsp;·&nbsp; Test customer profiles</p>
    </div>
</div>
""", unsafe_allow_html=True)


# ==================== TABS ====================

tab1, tab2 = st.tabs(["🧩  Build Rule", "▶  Evaluate & Test"])


# ==================== TAB 1: BUILD RULE ====================

with tab1:
    col_main, col_preview = st.columns([3, 2], gap="large")

    with col_main:
        # Recommendation inputs at the top of Build Rule tab
        r1, r2 = st.columns([3, 1])
        with r1:
            selected_recommendation = st.text_input(
                "Recommendation ID",
                value="XIT_AIQ_PREDICTIVE_WAN_SCORE",
                help="Enter any recommendation name."
            )
        with r2:
            selected_locale = st.selectbox("Locale", ["en-US", "es-US"])

        rec_data = RECOMMENDATIONS.get(selected_recommendation, {})
        rec_message = rec_data.get(selected_locale, "")
        rec_title = rec_data.get("title", "Custom Recommendation")

        st.markdown("---")
        st.markdown('<div class="section-title">📋 Conditions</div>', unsafe_allow_html=True)

        with st.expander("📖 How to use the condition builder", expanded=False):
            st.markdown("""
**Example output:** `(facts.xcdp.realized == "HQ_Cust_Digital_Soccer_Likely" && facts.auth.user_role == "PRIMARY")`

| Fact | Operator | Value | DSL Output |
|---|---|---|---|
| Audience | is | HQ_Cust_Digital_Soccer_Likely | `facts.xcdp.realized == "..."` |
| Internet Backup On | is not | true | `!rule.is_internet_backup_on` |
| User Role | is | PRIMARY | `facts.auth.user_role == "PRIMARY"` |

**Tip:** Use `AND` to require all conditions, `OR` to require any one.
            """)

        num_conditions = st.slider("Number of conditions", min_value=1, max_value=8, value=1)

        conditions = []
        sidebar_fact_values = {
            "Client Device Make": test_device_make,
            "Client Device OS Name": test_device_os,
            "User Role": test_user_role,
            "Service Account ID": test_account_id,
            "Has Multiple Accounts": test_has_multiple,
            "Audience": test_audience,
        }

        for i in range(num_conditions):
            st.markdown(f'<div class="condition-row">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([2, 1, 2])
            with c1:
                st.caption(f"CONDITION {i+1} — FACT")
                fact_options = list(FACT_DSL_MAP.keys()) + ["Custom"]
                fact_selection = st.selectbox("Fact", fact_options, key=f"fact_{i}", label_visibility="collapsed")
                if fact_selection == "Custom":
                    fact = st.text_input("Custom fact path", key=f"custom_fact_{i}", placeholder="facts.custom.field", label_visibility="collapsed")
                else:
                    fact = fact_selection
            with c2:
                st.caption("OPERATOR")
                operator = st.selectbox("Operator", ["is", "is not"], key=f"op_{i}", label_visibility="collapsed")
            with c3:
                st.caption("VALUE")
                available_values = list(FACT_VALUES.get(fact, ["Custom"]))
                sidebar_val = sidebar_fact_values.get(fact, "")
                if sidebar_val and sidebar_val not in available_values:
                    available_values = [sidebar_val] + available_values
                if len(available_values) == 1 and available_values[0] == "Custom":
                    value = st.text_input("Value", key=f"val_{i}", placeholder="Enter value...", label_visibility="collapsed")
                else:
                    options = available_values + (["Custom"] if "Custom" not in available_values else [])
                    selected = st.selectbox("Value", options, key=f"val_{i}", label_visibility="collapsed")
                    if selected == "Custom":
                        value = st.text_input("Custom value", key=f"custom_val_{i}", placeholder="Enter custom value...", label_visibility="collapsed")
                    else:
                        value = selected
            conditions.append((fact, operator, value))
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        logic = st.radio("Combine conditions with:", ["AND", "OR"], horizontal=True,
                         help="AND = all conditions must match | OR = any condition must match")

    with col_preview:
        st.markdown('<div class="section-title">⚡ Live DSL Preview</div>', unsafe_allow_html=True)
        try:
            live_dsl = generate_dsl(conditions, logic)
            if live_dsl:
                st.markdown(f'<div class="dsl-box">{live_dsl}</div>', unsafe_allow_html=True)
                st.markdown("**Condition Breakdown**")
                for i, (f, op, v) in enumerate(conditions):
                    dsl_path = FACT_DSL_MAP.get(f, f)
                    is_flag = dsl_path.startswith("rule.")
                    if is_flag and v.lower() in ["true", "false"]:
                        expr = f"!{dsl_path}" if op == "is not" else dsl_path
                    else:
                        expr = f'{dsl_path} {"==" if op == "is" else "!="} "{v}"'
                    st.markdown(f"`{i+1}.` `{expr}`")
            else:
                st.markdown('<div class="dsl-box"><span class="dsl-empty">DSL will appear here as you build conditions...</span></div>', unsafe_allow_html=True)
        except ValueError:
            st.markdown('<div class="dsl-box"><span class="dsl-empty">Fill in all values to see DSL preview...</span></div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="section-title">📦 Payload</div>', unsafe_allow_html=True)
        try:
            payload_dsl = generate_dsl(conditions, logic) if conditions and all(v for _, _, v in conditions) else "No conditions defined"
        except ValueError:
            payload_dsl = "Invalid conditions"
        example_payload = {
            "resourceId": selected_recommendation,
            "renderType": "secondary_message",
            "locale": selected_locale,
            "message": rec_message if rec_message else "(Custom recommendation)",
            "dismissible": True,
            "ruleConditions": payload_dsl
        }
        st.json(example_payload)


# ==================== TAB 2: EVALUATE ====================

with tab2:
    st.markdown('<div class="section-title">▶ Rule Evaluation</div>', unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.info(f"**Device:** {test_device_make} · {test_device_os}")
    with col_b:
        st.info(f"**Role:** {test_user_role} · Multi: {test_has_multiple}")
    with col_c:
        st.info(f"**Audience:** {test_audience if test_audience else 'Not set'}")

    st.markdown("")
    run_clicked = st.button("▶  Run Rule Check", use_container_width=True)

    if run_clicked:
        st.markdown("---")
        try:
            test_values_dict = {
                "device_make": test_device_make,
                "device_os": test_device_os,
                "user_role": test_user_role,
                "account_id": test_account_id,
                "has_multiple": test_has_multiple,
                "audience": test_audience,
                "internet_backup": test_internet_backup,
                "power_backup": test_power_backup,
                "show_line_level": test_show_line_level,
            }
            results = []
            debug_info = []
            for fact, operator, value in conditions:
                actual_value = get_test_value_for_fact(fact, test_values_dict)
                match = evaluate_condition(fact, operator, value, actual_value)
                results.append(match)
                debug_info.append((fact, operator, value, actual_value, match))

            final_result = (all(results) if logic == "AND" else any(results)) if results else False
            pass_count = sum(results)
            fail_count = len(results) - pass_count

            col_res, col_meta = st.columns([2, 1])
            with col_res:
                if final_result:
                    st.markdown("""<div class="result-pass">
                        <div class="result-icon">✅</div>
                        <div class="result-title">RULE MATCHED</div>
                        <div class="result-desc">Card WILL be shown to this customer profile</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown("""<div class="result-fail">
                        <div class="result-icon">❌</div>
                        <div class="result-title">RULE FAILED</div>
                        <div class="result-desc">Card WILL NOT be shown to this customer profile</div>
                    </div>""", unsafe_allow_html=True)

            with col_meta:
                st.markdown(f"""
                <div style="padding:1rem;background:#f8faff;border:1px solid #e2e8f0;border-radius:12px;text-align:center;">
                    <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;margin-bottom:0.75rem;">Summary</div>
                    <span class="pill pill-total">{len(results)} Total</span><br><br>
                    <span class="pill pill-pass">✓ {pass_count} Passed</span>&nbsp;
                    <span class="pill pill-fail">✗ {fail_count} Failed</span>
                </div>""", unsafe_allow_html=True)

            st.markdown("##### 📄 Generated DSL")
            try:
                dsl_expr = generate_dsl(conditions, logic)
                st.code(dsl_expr, language="javascript")
            except ValueError as e:
                st.error(f"⚠️ {str(e)}")

            st.markdown("##### 🔍 Condition Debug")
            for i, (fact, operator, value, actual, matched) in enumerate(debug_info):
                css_class = "debug-pass" if matched else "debug-fail"
                icon = "✅" if matched else "❌"
                st.markdown(
                    f'<div class="{css_class}">{icon} &nbsp; <b>#{i+1} {fact}</b> &nbsp; '
                    f'<span style="opacity:0.75">{operator}</span> &nbsp; '
                    f'<code>"{value}"</code> &nbsp;|&nbsp; Actual: <code>"{actual}"</code></div>',
                    unsafe_allow_html=True
                )

        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            st.info("💡 Make sure all condition values are filled in before running.")
    else:
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem;color:#94a3b8;">
            <div style="font-size:3rem;margin-bottom:0.75rem;">🎯</div>
            <div style="font-weight:600;font-size:1rem;color:#64748b;">Ready to evaluate</div>
            <div style="font-size:0.85rem;margin-top:0.4rem;">Build your conditions in the <b>Build Rule</b> tab, then click <b>Run Rule Check</b></div>
        </div>
        """, unsafe_allow_html=True)
