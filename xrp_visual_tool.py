"""
XRP Visual Rule Builder - A Streamlit application for building targeting rules visually.
"""

from typing import List, Tuple, Dict, Union
import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="XRP DSL Builder",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=block');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
/* Inherit Inter everywhere — but without !important so icon fonts (Material Symbols) can override */
* { font-family: inherit; }

.block-container { padding-top: 1.4rem !important; padding-bottom: 1rem !important; }

/* ═══ HEADER ═══ */
.header-banner {
    background: linear-gradient(120deg, #312e81 0%, #4f46e5 45%, #6366f1 75%, #818cf8 100%);
    padding: 1.2rem 2rem; border-radius: 18px; margin-bottom: 1.3rem;
    box-shadow: 0 10px 40px rgba(79,70,229,0.28), inset 0 1px 0 rgba(255,255,255,0.12);
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem;
}
.header-left {}
.header-title { color: white; font-size: 1.55rem; font-weight: 800; margin: 0; letter-spacing: -0.6px; }
.header-sub { color: rgba(255,255,255,0.62); font-size: 0.81rem; margin: 0.3rem 0 0 0; font-weight: 400; }
.header-badge {
    background: rgba(255,255,255,0.16); backdrop-filter: blur(10px);
    color: white; padding: 0.45rem 1.2rem; border-radius: 25px;
    font-size: 0.68rem; font-weight: 700; letter-spacing: 1.8px;
    text-transform: uppercase; border: 1px solid rgba(255,255,255,0.22);
    white-space: nowrap;
}

/* ═══ SECTION TITLE ═══ */
.section-title {
    font-size: 0.68rem; font-weight: 800; color: #4f46e5;
    text-transform: uppercase; letter-spacing: 1.4px; margin-bottom: 0.8rem;
    display: flex; align-items: center; gap: 0.55rem;
}
.section-title::after { content: ''; flex: 1; height: 1.5px; background: linear-gradient(to right, #e0e7ff, transparent); }

/* ═══ CONDITION CARD ═══ */
.condition-card {
    background: #ffffff; border: 1px solid #e0e7ff; border-left: 4px solid #6366f1;
    border-radius: 14px; padding: 1rem 1.15rem; margin-bottom: 0.45rem;
    box-shadow: 0 2px 8px rgba(99,102,241,0.07); transition: all 0.15s ease;
}
.condition-card:hover { box-shadow: 0 6px 24px rgba(99,102,241,0.14); border-left-color: #4f46e5; transform: translateY(-1px); }

.cond-badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 23px; height: 23px; background: linear-gradient(135deg, #6366f1, #4338ca);
    color: white; border-radius: 50%; font-size: 0.69rem; font-weight: 800;
    margin-right: 0.5rem; box-shadow: 0 2px 6px rgba(99,102,241,0.45); flex-shrink: 0;
}
.field-label {
    font-size: 0.62rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.9px; color: #94a3b8; margin-bottom: 0.18rem; display: block;
}
/* ═══ AND/OR CONNECTOR ═══ */
.logic-connector {
    display: flex; align-items: center; gap: 0.6rem; margin: 0.3rem 0 0.3rem 0.5rem;
}
.logic-line { flex: 1; height: 1px; background: linear-gradient(to right, #e0e7ff 60%, transparent); }
.logic-and-badge { background: #e0e7ff; color: #3730a3; font-size: 0.65rem; font-weight: 800; padding: 0.2rem 0.6rem; border-radius: 20px; letter-spacing: 0.5px; }
.logic-or-badge  { background: #fef3c7; color: #92400e; font-size: 0.65rem; font-weight: 800; padding: 0.2rem 0.6rem; border-radius: 20px; letter-spacing: 0.5px; }

/* ═══ DSL OUTPUT BOX ═══ */
.dsl-box {
    background: #0d1117; border: 1px solid #21262d; border-radius: 16px;
    padding: 1.3rem 1.5rem; font-family: 'Courier New', Courier, monospace;
    font-size: 0.84rem; color: #c9d1d9; line-height: 1.85;
    word-break: break-all; min-height: 90px;
    box-shadow: inset 0 2px 12px rgba(0,0,0,0.45), 0 4px 20px rgba(0,0,0,0.15);
}
.dsl-empty { color: #484f58; font-style: italic; font-size: 0.82rem; }

/* ═══ BUTTONS — primary (default) ═══ */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    color: white !important; border: none !important; border-radius: 9px !important;
    padding: 0.42rem 0.9rem !important; font-weight: 600 !important;
    font-size: 0.83rem !important; letter-spacing: 0.2px !important;
    transition: all 0.15s ease !important; width: 100% !important;
    min-height: 2.15rem !important; white-space: nowrap !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
}
.stButton > button:hover {
    filter: brightness(1.1) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.42) !important;
    transform: translateY(-1px) !important;
}
.stButton > button p, .stButton > button span { margin: 0 !important; color: white !important; font-weight: 600 !important; }

/* ═══ COMPACT ± BUTTONS — wrap with class="compact-btn-row" div ═══ */
.compact-btn-row .stButton > button {
    background: white !important; color: #4b5563 !important;
    border: 1.5px solid #d1d5db !important; border-radius: 7px !important;
    padding: 0.25rem 0.5rem !important; font-size: 1rem !important;
    font-weight: 700 !important; min-height: 1.9rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}
.compact-btn-row .stButton > button:hover {
    border-color: #6366f1 !important; color: #6366f1 !important;
    background: #f5f3ff !important; box-shadow: none !important; transform: none !important; filter: none !important;
}
.compact-btn-row .stButton > button p,
.compact-btn-row .stButton > button span { color: inherit !important; font-weight: 700 !important; }

/* ═══ ADD/REMOVE CONDITION buttons ═══ */
.add-cond-btn .stButton > button { background: #f5f3ff !important; color: #4f46e5 !important; border: 1.5px dashed #a5b4fc !important; }
.add-cond-btn .stButton > button:hover { background: #e0e7ff !important; border-color: #6366f1 !important; box-shadow: none !important; transform: none !important; filter: none !important; }
.add-cond-btn .stButton > button p,
.add-cond-btn .stButton > button span { color: #4f46e5 !important; }
.rem-cond-btn .stButton > button { background: #fff1f2 !important; color: #e11d48 !important; border: 1.5px solid #fecdd3 !important; }
.rem-cond-btn .stButton > button:hover { background: #ffe4e6 !important; border-color: #f43f5e !important; box-shadow: none !important; transform: none !important; filter: none !important; }
.rem-cond-btn .stButton > button p,
.rem-cond-btn .stButton > button span { color: #e11d48 !important; }

/* ═══ RESULT BOXES ═══ */
.result-pass {
    background: linear-gradient(135deg, #052e16, #065f46); border: 1px solid #34d399;
    border-radius: 14px; padding: 1rem 1.5rem; text-align: center; color: white;
    margin-bottom: 0.75rem; box-shadow: 0 4px 20px rgba(52,211,153,0.2);
}
.result-fail {
    background: linear-gradient(135deg, #450a0a, #7f1d1d); border: 1px solid #f87171;
    border-radius: 14px; padding: 1rem 1.5rem; text-align: center; color: white;
    margin-bottom: 0.75rem; box-shadow: 0 4px 20px rgba(248,113,113,0.2);
}
.result-icon { font-size: 2rem; margin-bottom: 0.3rem; }
.result-title { font-size: 1.25rem; font-weight: 800; }
.result-desc { font-size: 0.82rem; opacity: 0.75; margin-top: 0.2rem; }
.debug-pass { background: #f0fdf4; border-left: 4px solid #22c55e; padding: 0.45rem 0.9rem; border-radius: 0 8px 8px 0; margin-bottom: 0.3rem; font-size: 0.83rem; color: #14532d; }
.debug-fail { background: #fef2f2; border-left: 4px solid #ef4444; padding: 0.45rem 0.9rem; border-radius: 0 8px 8px 0; margin-bottom: 0.3rem; font-size: 0.83rem; color: #7f1d1d; }
.pill { display: inline-block; padding: 0.22rem 0.7rem; border-radius: 20px; font-size: 0.75rem; font-weight: 700; margin-right: 0.35rem; }
.pill-total { background: #e0e7ff; color: #3730a3; }
.pill-pass  { background: #dcfce7; color: #166534; }
.pill-fail  { background: #fee2e2; color: #991b1b; }

/* ═══ SIDEBAR ═══ */
section[data-testid="stSidebar"] { background: #f5f7ff !important; border-right: 1.5px solid #e0e7ff !important; }
.sidebar-card { background: white; border: 1px solid #e0e7ff; border-radius: 12px; padding: 0.8rem 0.95rem; margin-bottom: 0.5rem; box-shadow: 0 1px 4px rgba(99,102,241,0.05); }
.sidebar-card-title { font-size: 0.67rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1.1px; color: #4f46e5; margin-bottom: 0.5rem; padding-bottom: 0.4rem; border-bottom: 1.5px solid #f0f0fc; }

/* ═══ MISC ═══ */
hr { border: none !important; border-top: 1px solid #f0f0fc !important; margin: 0.75rem 0 !important; }
.stTabs [data-baseweb="tab-list"] { background: #eeeffc; padding: 0.2rem; border-radius: 10px; gap: 0.2rem; }
.stTabs [data-baseweb="tab"] { border-radius: 8px !important; font-weight: 500 !important; padding: 0.3rem 1rem !important; font-size: 0.87rem !important; }
.stTabs [aria-selected="true"] { background: white !important; box-shadow: 0 2px 8px rgba(0,0,0,0.09) !important; font-weight: 700 !important; color: #4f46e5 !important; }
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
    "Permissions (toArray)": "__toarray__",
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
    "EDP Auto Optimization": "rule.edp_state_features_auto_optimization",
    "Disconnected Customer": "rule.is_disconnected_customer",
    "Has GW Device": "rule.has_gw_device",
    "Bridge Mode Enabled": "rule.is_bridge_mode_enabled",
    "Device Priority Capable": "rule.device_priority_capable",
    "Permission: Device Prioritization View": "facts.permissions.device_prioritization.view",
    "Audience": "facts.xcdp.realized",
    "Experiment Treatment": "experiment.{experiment_name}.treatment",
    "Last Account Visit": "facts.visits_account.accessedOn",
    "Last Account2 Visit": "facts.visits_account2.accessedOn",
}

FACT_VALUES: Dict[str, List[str]] = {
    "Client Device Make": ["Samsung", "Apple", "Custom"],
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
    "EDP Auto Optimization": ["true", "false"],
    "Disconnected Customer": ["true", "false"],
    "Has GW Device": ["true", "false"],
    "Bridge Mode Enabled": ["true", "false"],
    "Device Priority Capable": ["true", "false"],
    "Permission: Device Prioritization View": ["true", "false"],
    "Audience": ["HQ_Cust_XM_Income_Above50K_Legacy", "HQ_Cust_Digital_Soccer_Likely", "Custom"],
    "Experiment Treatment": ["on", "off", "control", "Custom"],
    "Last Account Visit": ["Custom"],
    "Last Account2 Visit": ["Custom"],
}

TO_ARRAY_FACTS: Dict[str, str] = {
    "Permissions (toArray)": "facts.permissions",
}

# Maps human-readable operator labels to DSL symbols
COMPARISON_OP_MAP: Dict[str, str] = {
    "at least (>=)": ">=",
    "at most (<=)": "<=",
    "above (>)":    ">",
    "below (<)":    "<",
}

# Fact DSL paths that behave as boolean flags (truthy/falsy) but don't start with "rule."
TRUTHY_FACTS: set = {
    "facts.permissions.device_prioritization.view",
}

# Quick-start rule templates
RULE_TEMPLATES: Dict[str, dict] = {
    "iOS — Primary": {
        "num": 2, "logic": "AND",
        "conditions": [
            ("Client Device OS Name", "is", "iOS"),
            ("User Role", "is", "PRIMARY"),
        ]
    },
    "Android — Version Gate": {
        "num": 2, "logic": "AND",
        "conditions": [
            ("Client Device OS Name", "is", "Android"),
            ("Client App Version", "at least (>=)", "6.4"),
        ]
    },
    "Audience + Role": {
        "num": 2, "logic": "AND",
        "conditions": [
            ("Audience", "is", "HQ_Cust_Digital_Soccer_Likely"),
            ("User Role", "is", "PRIMARY"),
        ]
    },
    "Device Priority": {
        "num": 2, "logic": "AND",
        "conditions": [
            ("Device Priority Capable", "is", "true"),
            ("Has GW Device", "is", "true"),
        ]
    },
    "Disconnected Customer": {
        "num": 1, "logic": "AND",
        "conditions": [
            ("Disconnected Customer", "is", "true"),
        ]
    },
    "Restricted Account": {
        "num": 1, "logic": "AND",
        "conditions": [
            ("User Role", "is", "RESTRICTED_SECONDARY"),
        ]
    },
}


# ==================== UTILITY FUNCTIONS ====================

def _resolve_perm_paths(value: str, base: str) -> List[str]:
    """Expand comma-separated sub-paths into full permission paths."""
    result = []
    for p in (p.strip() for p in value.split(",") if p.strip()):
        if p.startswith("facts."):
            result.append(p)
        elif p.startswith("."):
            result.append(base + p)
        else:
            result.append(base + "." + p)
    return result

def generate_dsl(conditions: List[Tuple[str, str, str, str]], logic: Union[str, List[str]]) -> str:
    """Generate DSL. Each condition is (fact, operator, value, condition_logic).
    logic between items uses the operator stored on the NEXT condition (or global fallback)."""
    if not conditions:
        return ""
    dsl_parts = []
    for fact, operator, value, _cond_logic in conditions:
        if not value or not value.strip():
            raise ValueError(f"Empty value for fact '{fact}' — please fill in all values")
        dsl_path = FACT_DSL_MAP.get(fact, fact)
        # toArray() special handling
        if dsl_path == "__toarray__":
            base = TO_ARRAY_FACTS.get(fact, "facts.permissions")
            full_paths = _resolve_perm_paths(value, base)
            bool_val = "false" if operator == "is not" else "true"
            dsl_expr = f'toArray({", ".join(full_paths)}) == {bool_val}'
        else:
            is_rule_flag = dsl_path.startswith("rule.") or dsl_path in TRUTHY_FACTS or dsl_path.startswith("facts.permissions.")
            is_boolean_value = value.lower() in ["true", "false"]
            if is_rule_flag and is_boolean_value:
                dsl_expr = f"!{dsl_path}" if operator == "is not" else dsl_path
            elif dsl_path in ("facts.xcdp.realized", "facts.auth.user_role", "serviceAccount.id"):
                _vals = [v.strip() for v in value.split(",") if v.strip()]
                if len(_vals) > 1:
                    _vals_str = ", ".join(f'"{v}"' for v in _vals)
                    dsl_op = "!=" if operator == "is not" else "=="
                    dsl_expr = f'{dsl_path} {dsl_op} to_array({_vals_str})'
                else:
                    dsl_operator = "==" if operator == "is" else "!="
                    dsl_expr = f'{dsl_path} {dsl_operator} "{value.strip()}"'
            elif operator in COMPARISON_OP_MAP and dsl_path == "facts.client.version":
                sym = COMPARISON_OP_MAP[operator]
                dsl_expr = f'version_compare({dsl_path}, "{value.strip()}") {sym} 0'
            elif operator in COMPARISON_OP_MAP:
                dsl_expr = f'{dsl_path} {COMPARISON_OP_MAP[operator]} "{value.strip()}"'
            else:
                dsl_operator = "==" if operator == "is" else "!="
                dsl_expr = f'{dsl_path} {dsl_operator} "{value.strip()}"'
        dsl_parts.append(dsl_expr)

    # Build final DSL joining with per-condition logic operators
    if len(dsl_parts) == 1:
        return f"({dsl_parts[0]})"
    result = dsl_parts[0]
    for idx in range(1, len(dsl_parts)):
        # The operator joining condition idx-1 and idx is stored on condition idx
        cond_logic = conditions[idx][3] if len(conditions[idx]) > 3 else (logic if isinstance(logic, str) else "AND")
        op_str = " && " if cond_logic == "AND" else " || "
        result += op_str + dsl_parts[idx]
    return f"({result})"


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


def _parse_version(v: str) -> tuple:
    """Parse a version string like '6.4' or '10.2.1' into a comparable tuple."""
    try:
        return tuple(int(x) for x in v.strip().split("."))
    except ValueError:
        return (v.strip(),)


def evaluate_condition(fact: str, operator: str, expected_value: str, actual_value: str) -> bool:
    if actual_value.startswith("N/A"):
        return False
    if operator in COMPARISON_OP_MAP:
        sym = COMPARISON_OP_MAP[operator]
        av = _parse_version(actual_value)
        ev = _parse_version(expected_value)
        if sym == ">=": return av >= ev
        if sym == "<=": return av <= ev
        if sym == ">": return av > ev
        if sym == "<": return av < ev
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

    st.markdown('<div class="sidebar-card-title">👤 Customer Profile</div>', unsafe_allow_html=True)
    test_device_make_list = st.multiselect("Device Make", ["Samsung", "Apple", "Google", "Motorola", "Other"], default=["Samsung"], help="Select one or more device makes")
    test_device_make = ", ".join(test_device_make_list) if test_device_make_list else "Samsung"

    test_device_os_list = st.multiselect("Device OS", ["Android", "iOS"], default=["Android"])
    test_device_os = ", ".join(test_device_os_list) if test_device_os_list else "Android"

    test_user_role_list = st.multiselect("User Role", ["PRIMARY", "SECONDARY", "RESTRICTED_SECONDARY", "MEMBER", "SIM"], default=["PRIMARY"], help="Select one or more roles")
    test_user_role = ", ".join(test_user_role_list) if test_user_role_list else "PRIMARY"
    test_account_id = st.text_input("Account ID", placeholder="Enter account ID...")
    test_has_multiple = st.selectbox("Multiple Accounts", ["true", "false"])

    st.markdown('<div style="font-size:0.85rem;color:#374151;font-weight:500;margin-bottom:0.3rem;">Audience Segments</div>', unsafe_allow_html=True)
    if "audience_count" not in st.session_state:
        st.session_state["audience_count"] = 1
    _raw_audience_list = []
    for _ai in range(st.session_state["audience_count"]):
        _aud_val = st.text_input(
            f"Audience {_ai + 1}",
            key=f"audience_{_ai}",
            placeholder="e.g. HQ_Cust_XM_Income_Above50K_Legacy",
            label_visibility="collapsed",
        )
        _raw_audience_list.append(_aud_val)
    _ac1, _ac2 = st.columns(2)
    with _ac1:
        if st.button("＋ Add", key="aud_add", use_container_width=True, help="Add audience segment"):
            st.session_state["audience_count"] += 1
            st.rerun()
    with _ac2:
        if st.session_state["audience_count"] > 1:
            if st.button("－ Remove", key="aud_rem", use_container_width=True, help="Remove last segment"):
                st.session_state["audience_count"] -= 1
                st.rerun()
    test_audience_list = [a.strip() for a in _raw_audience_list if a.strip()]
    test_audience = ", ".join(test_audience_list)

    audience_display = test_audience if test_audience else '<i style="color:#94a3b8">Not set</i>'
    st.markdown(f"""
    <div class="sidebar-card" style="background:#f0f9ff;border-color:#bae6fd;">
        <div class="sidebar-card-title" style="color:#0284c7;">📊 Active Profile</div>
        <div style="font-size:0.8rem;color:#334155;line-height:1.8;">
            <b>Device Make:</b> {test_device_make}<br>
            <b>Device OS:</b> {test_device_os}<br>
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
    <div class="header-left">
        <div class="header-title">⚡ XRP DSL Builder</div>
        <p class="header-sub">Build targeting rules visually &nbsp;·&nbsp; Generate DSL expressions &nbsp;·&nbsp; Test customer profiles</p>
    </div>
    <div class="header-badge">Visual Rule Engine</div>
</div>
""", unsafe_allow_html=True)


# ==================== TABS ====================

tab1, = st.tabs(["🧩 Build Rule"])


# ==================== TAB 1: BUILD RULE ====================

with tab1:
    with st.expander("📖 How to use the condition builder", expanded=False):
        st.markdown("""
### ⚡ Quick Start
Select a **Fact → Operator → Value** for each condition. The DSL is generated live in the preview panel on the right.

---

### 🔢 Operators
| Operator | Meaning | Example DSL |
|---|---|---|
| `is` | Equals | `facts.auth.user_role == "PRIMARY"` |
| `is not` | Not equals | `facts.auth.user_role != "PRIMARY"` |
| `at least (>=)` | Greater than or equal | `facts.client.version >= "6.4"` |
| `at most (<=)` | Less than or equal | `facts.client.version <= "10.0"` |
| `above (>)` | Strictly greater | `facts.client.version > "6.4"` |
| `below (<)` | Strictly less | `facts.client.version < "10.0"` |

> **Note:** Version comparisons are version-aware — `6.10` is correctly treated as greater than `6.4`.

---

### 🏷️ Boolean Flag Facts
Facts under `rule.*` or `facts.permissions.*` are **boolean flags** — no value entry needed.

| Operator | DSL Output |
|---|---|
| `is` | `rule.is_disconnected_customer` |
| `is not` | `!rule.is_disconnected_customer` |

---

### 🧩 Custom Fact Types
| Selection | What to enter | DSL generated |
|---|---|---|
| **Custom Rule** | Rule name, e.g. `has_gw_device` | `rule.has_gw_device` |
| **Custom Permission** | Permission path, e.g. `device_prioritization.view` | `facts.permissions.device_prioritization.view` |
| **Custom** | Full fact path, e.g. `facts.custom.field` | `facts.custom.field == "value"` |
| **Permissions (toArray)** | One or more sub-paths | `toArray(facts.permissions.x, facts.permissions.y) == true` |

---

### 🔗 Logic Between Conditions
- Set **Default logic** (AND / OR) at the top — applies to all conditions
- Override per-condition using the **Join condition N → N+1 with** radio below each row
- Supports up to **20 conditions**

---

### 💡 Examples
```
(facts.xcdp.realized == "HQ_Cust_Digital_Soccer_Likely" && facts.auth.user_role == "PRIMARY")

(facts.client.version >= "6.4" && rule.has_gw_device)

(!rule.is_disconnected_customer && facts.client.device.os.name == "iOS")

(toArray(facts.permissions.device_prioritization.view) == true)
```
        """)

    col_main, col_preview = st.columns([3, 2], gap="medium")

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

        st.markdown('<div class="section-title">📋 Conditions</div>', unsafe_allow_html=True)

        if "num_conditions" not in st.session_state:
            st.session_state["num_conditions"] = 1
        num_conditions = st.session_state["num_conditions"]

        conditions = []
        sidebar_fact_values = {
            "Client Device Make": test_device_make,
            "Client Device OS Name": test_device_os,
            "User Role": test_user_role,
            "Service Account ID": test_account_id,
            "Has Multiple Accounts": test_has_multiple,
            "Audience": test_audience_list,
        }

        global_logic = st.radio("Default logic between conditions:", ["AND", "OR"], horizontal=True,
                         help="Default operator joining conditions. You can override per condition below.")

        for i in range(num_conditions):
            # AND/OR selector shown BETWEEN cards
            if i > 0:
                _sp1, _logic_col, _sp2 = st.columns([3, 2, 3])
                with _logic_col:
                    cond_logic = st.radio(
                        "logic",
                        ["AND", "OR"],
                        index=0 if global_logic == "AND" else 1,
                        key=f"cond_logic_{i}",
                        horizontal=True,
                        label_visibility="collapsed",
                    )
            else:
                cond_logic = global_logic

            st.markdown(
                f'<div style="display:flex;align-items:center;margin-bottom:0.5rem;padding:0.65rem 0.9rem 0 0.9rem;">'
                f'<span class="cond-badge">{i+1}</span>'
                f'<span style="font-size:0.74rem;font-weight:700;color:#374151;text-transform:uppercase;letter-spacing:0.6px;">Condition {i+1}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

            c1, c2, c3 = st.columns([3, 2, 2.2])
            with c1:
                st.markdown('<span class="field-label">Fact</span>', unsafe_allow_html=True)
                fact_options = [k for k in FACT_DSL_MAP.keys() if k != "Permissions (toArray)"] + ["Permissions (toArray)", "Custom Rule", "Custom Permission", "Custom"]
                fact_selection = st.selectbox("Fact", fact_options, key=f"fact_{i}", label_visibility="collapsed")
                if fact_selection == "Custom":
                    fact = st.text_input("Custom fact path", key=f"custom_fact_{i}", placeholder="facts.custom.field", label_visibility="collapsed")
                elif fact_selection == "Custom Rule":
                    rule_input = st.text_input("Rule name", key=f"custom_fact_{i}", placeholder="e.g. edp_state_features_auto_optimization", label_visibility="collapsed")
                    fact = f"rule.{rule_input.strip()}" if rule_input.strip() else "Custom Rule"
                elif fact_selection == "Custom Permission":
                    perm_input = st.text_input("Permission path", key=f"custom_fact_{i}", placeholder="e.g. device_prioritization.view", label_visibility="collapsed")
                    fact = f"facts.permissions.{perm_input.strip()}" if perm_input.strip() else "Custom Permission"
                else:
                    fact = fact_selection
            with c2:
                st.markdown('<span class="field-label">Operator</span>', unsafe_allow_html=True)
                operator = st.selectbox("Operator", ["is", "is not", "at least (>=)", "at most (<=)", "above (>)", "below (<)"], key=f"op_{i}", label_visibility="collapsed")
            with c3:
                st.markdown('<span class="field-label">Value</span>', unsafe_allow_html=True)
                if fact == "Permissions (toArray)":
                    st.markdown(
                        '<span style="font-size:0.75rem;color:#6366f1;font-weight:600;">Base: </span>'
                        '<code style="font-size:0.75rem;background:#e0e7ff;padding:0.1rem 0.4rem;border-radius:4px;">facts.permissions</code>'
                        '<span style="font-size:0.72rem;color:#64748b;"> — add each sub-path separately</span>',
                        unsafe_allow_html=True
                    )
                    perm_count_key = f"perm_count_{i}"
                    if perm_count_key not in st.session_state:
                        st.session_state[perm_count_key] = 1
                    perm_vals = []
                    for j in range(st.session_state[perm_count_key]):
                        perm_val = st.text_input(
                            f"Sub-path {j+1}",
                            key=f"perm_val_{i}_{j}",
                            placeholder=".advanced security_on the go.view all devices",
                            label_visibility="visible"
                        )
                        perm_vals.append(perm_val)
                    value = ", ".join(v.strip() for v in perm_vals if v.strip())
                elif fact == "Audience":
                    _aud_count_key = f"aud_count_cond_{i}"
                    if _aud_count_key not in st.session_state:
                        st.session_state[_aud_count_key] = 1
                    _aud_cond_vals = []
                    for _aj in range(st.session_state[_aud_count_key]):
                        _av = st.text_input(
                            f"Audience {_aj + 1}",
                            key=f"aud_cond_{i}_{_aj}",
                            placeholder="e.g. HQ_Cust_Digital_Soccer_Likely",
                            label_visibility="visible",
                        )
                        _aud_cond_vals.append(_av)
                    value = ", ".join(v.strip() for v in _aud_cond_vals if v.strip())
                elif fact == "Service Account ID":
                    _acct_count_key = f"acct_count_cond_{i}"
                    if _acct_count_key not in st.session_state:
                        st.session_state[_acct_count_key] = 1
                    _acct_cond_vals = []
                    for _aj in range(st.session_state[_acct_count_key]):
                        _av = st.text_input(
                            f"Account ID {_aj + 1}",
                            key=f"acct_cond_{i}_{_aj}",
                            placeholder="Enter account ID...",
                            label_visibility="visible",
                        )
                        _acct_cond_vals.append(_av)
                    value = ", ".join(v.strip() for v in _acct_cond_vals if v.strip())
                elif fact == "User Role":
                    _stored_role = st.session_state.get(f"val_{i}", "PRIMARY")
                    if isinstance(_stored_role, str) and _stored_role:
                        _default_roles = [r.strip() for r in _stored_role.split(",") if r.strip() in FACT_VALUES.get("User Role", [])]
                    else:
                        _default_roles = []
                    _selected_roles = st.multiselect(
                        "Role(s)",
                        FACT_VALUES.get("User Role", []),
                        default=_default_roles,
                        key=f"val_roles_{i}",
                        label_visibility="collapsed",
                    )
                    value = ", ".join(_selected_roles) if _selected_roles else ""
                else:
                    # Resolve DSL path to determine if this is a boolean flag fact
                    _dsl = FACT_DSL_MAP.get(fact, fact)
                    is_flag_fact = (
                        _dsl.startswith("rule.")
                        or _dsl.startswith("facts.permissions.")
                        or _dsl in TRUTHY_FACTS
                    )
                    if is_flag_fact:
                        value = "true"  # operator (is / is not) controls the ! prefix in DSL
                        st.markdown(
                            '<span style="font-size:0.8rem;color:#6366f1;font-weight:600;">Boolean flag</span>'
                            '<br><span style="font-size:0.75rem;color:#64748b;">Use <b>is</b> → <code>rule.X</code> &nbsp;|&nbsp; <b>is not</b> → <code>!rule.X</code></span>',
                            unsafe_allow_html=True
                        )
                    else:
                        available_values = list(FACT_VALUES.get(fact, ["Custom"]))
                        sidebar_val = sidebar_fact_values.get(fact, "")
                        if isinstance(sidebar_val, list):
                            for _sv in sidebar_val:
                                if _sv and _sv not in available_values:
                                    available_values = [_sv] + available_values
                        elif sidebar_val and sidebar_val not in available_values:
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
            # ＋ / － buttons for multi-value facts — placed outside columns
            if fact == "Permissions (toArray)":
                _pc1, _pc2, _ = st.columns([1, 1, 6])
                with _pc1:
                    if st.button("＋", key=f"perm_add_{i}", use_container_width=True, help="Add sub-path"):
                        st.session_state[f"perm_count_{i}"] += 1
                        st.rerun()
                with _pc2:
                    if st.session_state.get(f"perm_count_{i}", 1) > 1:
                        if st.button("－", key=f"perm_rem_{i}", use_container_width=True, help="Remove last sub-path"):
                            st.session_state[f"perm_count_{i}"] -= 1
                            st.rerun()

            if fact == "Audience":
                _ac1, _ac2, _ = st.columns([1, 1, 6])
                with _ac1:
                    if st.button("＋", key=f"aud_cond_add_{i}", use_container_width=True, help="Add audience"):
                        st.session_state[f"aud_count_cond_{i}"] = st.session_state.get(f"aud_count_cond_{i}", 1) + 1
                        st.rerun()
                with _ac2:
                    if st.session_state.get(f"aud_count_cond_{i}", 1) > 1:
                        if st.button("－", key=f"aud_cond_rem_{i}", use_container_width=True, help="Remove last audience"):
                            st.session_state[f"aud_count_cond_{i}"] -= 1
                            st.rerun()

            if fact == "Service Account ID":
                _sc1, _sc2, _ = st.columns([1, 1, 6])
                with _sc1:
                    if st.button("＋", key=f"acct_cond_add_{i}", use_container_width=True, help="Add account ID"):
                        st.session_state[f"acct_count_cond_{i}"] = st.session_state.get(f"acct_count_cond_{i}", 1) + 1
                        st.rerun()
                with _sc2:
                    if st.session_state.get(f"acct_count_cond_{i}", 1) > 1:
                        if st.button("－", key=f"acct_cond_rem_{i}", use_container_width=True, help="Remove last account ID"):
                            st.session_state[f"acct_count_cond_{i}"] -= 1
                            st.rerun()

            conditions.append((fact, operator, value, cond_logic))
            st.markdown('<hr style="margin:0.6rem 0 0 0;border-top:1px solid #e0e7ff;">', unsafe_allow_html=True)

        # ── Add / Remove Condition buttons ────────────────────
        st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
        _btn_add, _btn_rem, _ = st.columns([2, 2, 6])
        with _btn_add:
            if st.button("＋  Add Condition", key="add_cond_btn", use_container_width=True):
                if st.session_state["num_conditions"] < 20:
                    st.session_state["num_conditions"] += 1
                    st.rerun()
        with _btn_rem:
            if num_conditions > 1:
                if st.button("－  Remove Last", key="rem_cond_btn", use_container_width=True):
                    st.session_state["num_conditions"] -= 1
                    st.rerun()

        logic = global_logic

    with col_preview:
        st.markdown('<div class="section-title">⚡ Live DSL Preview</div>', unsafe_allow_html=True)
        try:
            live_dsl = generate_dsl(conditions, logic)
            payload_dsl = live_dsl or "No conditions defined"
        except ValueError:
            live_dsl = ""
            payload_dsl = "Invalid conditions"
        if live_dsl:
            st.markdown(f'<div class="dsl-box">{live_dsl}</div>', unsafe_allow_html=True)
            with st.expander("📋 Copy DSL", expanded=False):
                st.code(live_dsl, language="javascript")
            st.markdown("**Condition Breakdown**")
            for i, (f, op, v, cl) in enumerate(conditions):
                dsl_path = FACT_DSL_MAP.get(f, f)
                if dsl_path == "__toarray__":
                    base = TO_ARRAY_FACTS.get(f, "facts.permissions")
                    full_paths = _resolve_perm_paths(v, base)
                    bool_val = "false" if op == "is not" else "true"
                    expr = f'toArray({", ".join(full_paths)}) == {bool_val}'
                elif (dsl_path.startswith("rule.") or dsl_path in TRUTHY_FACTS or dsl_path.startswith("facts.permissions.")) and v.lower() in ["true", "false"]:
                    expr = f"!{dsl_path}" if op == "is not" else dsl_path
                elif dsl_path in ("facts.xcdp.realized", "facts.auth.user_role", "serviceAccount.id"):
                    _vals = [_v.strip() for _v in v.split(",") if _v.strip()]
                    if len(_vals) > 1:
                        _vals_str = ", ".join(f'"{_v}"' for _v in _vals)
                        _dsl_op = "!=" if op == "is not" else "=="
                        expr = f'{dsl_path} {_dsl_op} to_array({_vals_str})'
                    else:
                        expr = f'{dsl_path} {"==" if op == "is" else "!="} "{v}"'
                elif op in COMPARISON_OP_MAP and dsl_path == "facts.client.version":
                    expr = f'version_compare({dsl_path}, "{v}") {COMPARISON_OP_MAP[op]} 0'
                elif op in COMPARISON_OP_MAP:
                    expr = f'{dsl_path} {COMPARISON_OP_MAP[op]} "{v}"'
                else:
                    expr = f'{dsl_path} {"==" if op == "is" else "!="} "{v}"'
                join_label = f" **{cl}**" if i < len(conditions) - 1 else ""
                st.markdown(f"`{i+1}.` `{expr}`{join_label}")
        elif payload_dsl == "Invalid conditions":
            st.markdown('<div class="dsl-box"><span class="dsl-empty">Fill in all values to see DSL preview...</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="dsl-box"><span class="dsl-empty">DSL will appear here as you build conditions...</span></div>', unsafe_allow_html=True)

        # ── PAYLOAD SECTION temporarily hidden ──────────────
        # st.markdown('<div class="section-title">📦 Payload</div>', unsafe_allow_html=True)
        # render_type_options = [...]
        # st.json(example_payload)


# ==================== EVALUATE (COLLAPSED) ====================

with st.expander("🧪 Evaluate & Debug  —  Development in Progress", expanded=False):

    # ── Section 1: Customer Profile summary ──────────────────
    st.markdown('<div class="section-title">👤 Customer Profile (from sidebar)</div>', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.info(f"**Device Make:** {test_device_make}  \n**OS:** {test_device_os}")
    with col_b:
        st.info(f"**Role:** {test_user_role}  \n**Multi-Account:** {test_has_multiple}")
    with col_c:
        st.info(f"**Account ID:** {test_account_id or '—'}  \n**Audience:** {test_audience or 'Not set'}")

    # ── Section 2: Conditions summary ────────────────────────
    st.markdown('<div class="section-title" style="margin-top:0.75rem;">📋 Active Conditions</div>', unsafe_allow_html=True)
    for i, (f, op, v, cl) in enumerate(conditions):
        dsl_path = FACT_DSL_MAP.get(f, f)
        if dsl_path == "__toarray__":
            cond_text = f"toArray({v})"
        elif dsl_path.startswith("rule.") or dsl_path.startswith("facts.permissions.") or dsl_path in TRUTHY_FACTS:
            cond_text = f"!{dsl_path}" if op == "is not" else dsl_path
        elif dsl_path in ("facts.xcdp.realized", "facts.auth.user_role", "serviceAccount.id"):
            _vals = [_v.strip() for _v in v.split(",") if _v.strip()]
            if len(_vals) > 1:
                _vals_str = ", ".join(f'"{_v}"' for _v in _vals)
                _dsl_op = "!=" if op == "is not" else "=="
                cond_text = f'{dsl_path} {_dsl_op} to_array({_vals_str})'
            else:
                cond_text = f'{dsl_path} {"==" if op == "is" else "!="} "{v}"'
        elif op in COMPARISON_OP_MAP and dsl_path == "facts.client.version":
            cond_text = f'version_compare({dsl_path}, "{v}") {COMPARISON_OP_MAP[op]} 0'
        elif op in COMPARISON_OP_MAP:
            cond_text = f'{dsl_path} {COMPARISON_OP_MAP[op]} "{v}"'
        else:
            cond_text = f'{dsl_path} {"==" if op == "is" else "!="} "{v}"'
        join_label = f" **{cl}**" if i < len(conditions) - 1 else ""
        st.markdown(f'`{i+1}.` `{cond_text}`{join_label}')

    # ── Section 3: Rule/Permission flag overrides ─────────────
    # Detect any rule/permission facts in the conditions that need manual simulation values
    flag_facts_in_conditions = []
    for fact, operator, value, _cl in conditions:
        _dsl = FACT_DSL_MAP.get(fact, fact)
        if (_dsl.startswith("rule.") or _dsl.startswith("facts.permissions.") or _dsl in TRUTHY_FACTS) and fact not in [
            "Internet Backup On", "Power Backup On", "Show Line Level Experience"
        ]:
            if fact not in [f for f, *_ in flag_facts_in_conditions]:
                flag_facts_in_conditions.append((fact, _dsl))

    rule_flag_overrides: Dict[str, str] = {}
    if flag_facts_in_conditions:
        st.markdown('<div class="section-title" style="margin-top:0.75rem;">🔧 Simulate Rule / Permission Flags</div>', unsafe_allow_html=True)
        st.caption("These facts are not in the sidebar — set their simulated value below before running.")
        flag_cols = st.columns(min(len(flag_facts_in_conditions), 3))
        for idx, (fact, dsl_path) in enumerate(flag_facts_in_conditions):
            with flag_cols[idx % 3]:
                label = fact if fact not in ("Custom Rule", "Custom Permission") else dsl_path
                val = st.selectbox(label, ["true", "false"], key=f"flag_override_{idx}")
                rule_flag_overrides[fact] = val

    run_clicked = st.button("▶  Run Rule Check", use_container_width=True)

    if run_clicked:
        try:
            test_values_dict = {
                "device_make": test_device_make,
                "device_os": test_device_os,
                "user_role": test_user_role,
                "account_id": test_account_id,
                "has_multiple": test_has_multiple,
                "audience": test_audience if test_audience else "(empty)",
                "internet_backup": test_internet_backup,
                "power_backup": test_power_backup,
                "show_line_level": test_show_line_level,
            }

            results = []
            debug_info = []
            for fact, operator, value, _cl in conditions:
                _dsl = FACT_DSL_MAP.get(fact, fact)
                is_flag = _dsl.startswith("rule.") or _dsl.startswith("facts.permissions.") or _dsl in TRUTHY_FACTS

                if is_flag:
                    # Use manual override if provided, otherwise use sidebar-mapped value
                    actual_value = rule_flag_overrides.get(fact, test_values_dict.get(fact.lower().replace(" ", "_"), "true"))
                    # For flag facts: "is" means expect true, "is not" means expect false
                    expected = "false" if operator == "is not" else "true"
                    match = (actual_value == expected)
                else:
                    actual_value = get_test_value_for_fact(fact, test_values_dict)
                    if fact == "Audience":
                        _aud_parts_actual = [a.strip() for a in actual_value.split(",") if a.strip()]
                        _aud_parts_expected = [v.strip() for v in value.split(",") if v.strip()]
                        if operator == "is not":
                            match = not any(v in _aud_parts_actual for v in _aud_parts_expected)
                        else:
                            match = any(v in _aud_parts_actual for v in _aud_parts_expected)
                    elif fact == "User Role":
                        _role_parts_actual = [r.strip() for r in actual_value.split(",") if r.strip()]
                        _role_parts_expected = [v.strip() for v in value.split(",") if v.strip()]
                        if operator == "is not":
                            match = not any(v in _role_parts_actual for v in _role_parts_expected)
                        else:
                            match = any(v in _role_parts_actual for v in _role_parts_expected)
                    elif fact == "Service Account ID":
                        _acct_parts_expected = [v.strip() for v in value.split(",") if v.strip()]
                        if operator == "is not":
                            match = actual_value not in _acct_parts_expected
                        else:
                            match = actual_value in _acct_parts_expected
                    else:
                        match = evaluate_condition(fact, operator, value, actual_value)

                results.append(match)
                debug_info.append((fact, operator, value, actual_value, match))

            # Evaluate using per-condition logic operators
            if results:
                final_result = results[0]
                for idx in range(1, len(results)):
                    cond_logic = conditions[idx][3]
                    if cond_logic == "AND":
                        final_result = final_result and results[idx]
                    else:
                        final_result = final_result or results[idx]
            else:
                final_result = False

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
                <div style="padding:0.85rem;background:#f8faff;border:1px solid #e2e8f0;border-radius:12px;text-align:center;">
                    <div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;margin-bottom:0.6rem;">Summary</div>
                    <span class="pill pill-total">{len(results)} Conditions</span><br><br>
                    <span class="pill pill-pass">✓ {pass_count} Passed</span>&nbsp;
                    <span class="pill pill-fail">✗ {fail_count} Failed</span>
                </div>""", unsafe_allow_html=True)

            st.markdown("##### 📄 Generated DSL")
            try:
                dsl_expr = generate_dsl(conditions, logic)
                st.code(dsl_expr, language="javascript")
            except ValueError as e:
                st.error(f"⚠️ {str(e)}")

            st.markdown("##### 🔍 Condition-by-Condition Result")
            for i, (fact, operator, value, actual, matched) in enumerate(debug_info):
                css_class = "debug-pass" if matched else "debug-fail"
                icon = "✅" if matched else "❌"
                _dsl_p = FACT_DSL_MAP.get(fact, fact)
                is_flag = _dsl_p.startswith("rule.") or _dsl_p.startswith("facts.permissions.") or _dsl_p in TRUTHY_FACTS
                source_label = "🔧 simulated" if is_flag and fact in rule_flag_overrides else "👤 profile"
                st.markdown(
                    f'<div class="{css_class}">{icon} &nbsp; <b>#{i+1} {fact}</b> &nbsp; '
                    f'<span style="opacity:0.75">{operator}</span> &nbsp; '
                    f'<code>"{value}"</code> &nbsp;|&nbsp; '
                    f'Actual: <code>"{actual}"</code> &nbsp;'
                    f'<span style="font-size:0.72rem;opacity:0.65">({source_label})</span></div>',
                    unsafe_allow_html=True
                )

        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            st.info("💡 Make sure all condition values are filled in before running.")
