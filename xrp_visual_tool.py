"""
XRP Visual Rule Builder - A Streamlit application for building targeting rules visually.

This tool allows users to:
- Define targeting conditions using a visual interface
- Generate DSL (Domain-Specific Language) expressions
- Test rules against customer profiles
- Debug rule evaluation

Features:
- Type hints for better code maintainability
- DRY principle: Eliminates code duplication
- Error handling: Graceful error messages
- Input validation: Validates empty values
"""

from typing import List, Tuple, Dict, Optional
import streamlit as st

st.set_page_config(page_title="XRP Visual Rule Builder", layout="wide")

st.title("🚀 XRP Visual Rule Builder")
st.markdown("Build targeting rules visually | Generate DSL expressions")

# ==================== CONFIGURATION ====================

# Comcast Recommendations Catalog
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

# Fact to DSL path mapping - from XRP Facts Catalog
FACT_DSL_MAP: Dict[str, str] = {
    # Client Facts (source "client")
    "Client Device Make": "facts.client.device.make",
    "Client Device Model": "facts.client.device.model",
    "Client Device OS Name": "facts.client.device.os.name",
    "Client Device OS Version": "facts.client.device.os.version",
    "Client Platform": "facts.client.platform",
    "Client App Version": "facts.client.version",
    
    # Service Account Facts
    "Service Account ID": "serviceAccount.id",
    "Service Account Partner": "serviceAccount.partner",
    
    # Authorization Identity Facts
    "User Role": "facts.auth.user_role",
    "Has Multiple Accounts": "facts.auth.has_multiple_accounts",
    
    # Rule Flags (feature toggles/business logic)
    "Internet Backup On": "rule.is_internet_backup_on",
    "Power Backup On": "rule.is_power_backup_on",
    "Show Line Level Experience": "rule.should_show_line_level_experience",
    
    # Audience Facts (dynamic, changes per card/stakeholder)
    "Audience": "facts.xcdp.realized",
    
    # Experiment Facts
    "Experiment Treatment": "experiment.{experiment_name}.treatment",
    
    # Channel Visitation Facts
    "Last Account Visit": "facts.visits_account.accessedOn",
    "Last Account2 Visit": "facts.visits_account2.accessedOn",
}

# Fact value options
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
    
    # Rule Flags
    "Internet Backup On": ["true", "false"],
    "Power Backup On": ["true", "false"],
    "Show Line Level Experience": ["true", "false"],
    
    # Audience examples (stakeholder-provided, changes per card)
    "Audience": ["HQ_Cust_XM_Income_Above50K_Legacy", "HQ_Cust_Digital_Soccer_Likely", "Custom"],
    
    "Experiment Treatment": ["on", "off", "control", "Custom"],
    
    "Last Account Visit": ["Custom"],
    "Last Account2 Visit": ["Custom"],
}

# ==================== UTILITY FUNCTIONS ====================

def generate_dsl(
    conditions: List[Tuple[str, str, str]], 
    logic: str
) -> str:
    """
    Generate DSL expression from visual conditions.
    
    Args:
        conditions: List of (fact, operator, value) tuples
        logic: Either "AND" or "OR" to combine conditions
        
    Returns:
        DSL expression string, or empty string if no conditions
        
    Raises:
        ValueError: If value is empty or invalid
    """
    if not conditions:
        return ""
    
    dsl_parts = []
    for fact, operator, value in conditions:
        if not value or not value.strip():
            raise ValueError(f"Empty value for fact '{fact}' - please fill in all values")
            
        dsl_path = FACT_DSL_MAP.get(fact, fact)
        
        # For rule flags (boolean facts), use negation syntax
        is_rule_flag = dsl_path.startswith("rule.")
        is_boolean_value = value.lower() in ["true", "false"]
        
        if is_rule_flag and is_boolean_value:
            # rule.flag_name for "is true"
            # !rule.flag_name for "is not true"
            if operator == "is not":
                dsl_expr = f"!{dsl_path}"
            else:
                dsl_expr = dsl_path
        else:
            # Standard comparison for other facts
            dsl_operator = "==" if operator == "is" else "!="
            formatted_value = f'"{value.strip()}"'
            dsl_expr = f"{dsl_path} {dsl_operator} {formatted_value}"
        
        dsl_parts.append(dsl_expr)
    
    # Combine with logic operator
    logic_op = " && " if logic == "AND" else " || "
    return f"({logic_op.join(dsl_parts)})"


def get_test_value_for_fact(fact: str, test_values: Dict[str, str]) -> str:
    """
    Get the actual test value for a specific fact.
    
    Args:
        fact: The fact name to look up
        test_values: Dictionary mapping fact types to test values
        
    Returns:
        The test value, or a placeholder message if not found
    """
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


def evaluate_condition(
    fact: str,
    operator: str,
    expected_value: str,
    actual_value: str
) -> bool:
    """
    Evaluate if a condition matches given values.
    
    Args:
        fact: The fact being evaluated
        operator: "is" or "is not"
        expected_value: The expected value
        actual_value: The actual value from test data
        
    Returns:
        True if condition matches, False otherwise
    """
    if actual_value.startswith("N/A"):
        return False
    
    match = (actual_value == expected_value)
    return (not match) if operator == "is not" else match


# ==================== SIDEBAR CONFIGURATION ====================

st.sidebar.header("🎯 Test Scenario")

st.sidebar.subheader("📋 Recommendation")
selected_recommendation = st.sidebar.text_input(
    "Recommendation Name (e.g., XIT_AIQ_PREDICTIVE_WAN_SCORE)",
    value="XIT_AIQ_PREDICTIVE_WAN_SCORE",
    help="Enter any recommendation name. New ones can be added anytime by stakeholders."
)
selected_locale = st.sidebar.selectbox("Language", ["en-US", "es-US"])

st.sidebar.subheader("👤 Customer Profile")
test_device_make = st.sidebar.selectbox("Device Make", ["Samsung", "Apple"])
test_device_os = st.sidebar.selectbox("Device OS", ["Android", "iOS"])
test_user_role = st.sidebar.selectbox("User Role", ["PRIMARY", "SECONDARY", "RESTRICTED_SECONDARY", "MEMBER", "SIM"])
test_account_id = st.sidebar.text_input("Account ID")
test_has_multiple = st.sidebar.selectbox("Multiple Accounts", ["true", "false"])
test_audience = st.sidebar.text_input("Audience (e.g., HQ_Cust_XM_Income_Above50K_Legacy)")

st.sidebar.subheader("⚙️ Rule Flags")
test_internet_backup = st.sidebar.selectbox("Internet Backup On", ["false", "true"])
test_power_backup = st.sidebar.selectbox("Power Backup On", ["false", "true"])
test_show_line_level = st.sidebar.selectbox("Show Line Level Experience", ["false", "true"])

# ==================== MAIN INTERFACE ====================

st.header("🧩 Build Rule Visually")

# Display recommendation preview
rec_data = RECOMMENDATIONS.get(selected_recommendation, {})
rec_message = rec_data.get(selected_locale, "")

col1, col2 = st.columns(2)
with col1:
    st.write(f"**Recommendation:** {selected_recommendation}")
with col2:
    st.write(f"**Language:** {selected_locale}")

if rec_message:
    st.write(f"**Message Preview:** {rec_message}")

st.markdown("---")
st.header("📋 Build Conditions")

with st.expander("📖 How to Build Your Expression", expanded=False):
    st.markdown("""
    **Example:** `facts.xcdp.realized == "HQ_Cust_Digital_Soccer_Likely" && !rule.is_internet_backup_on && !rule.is_power_backup_on && facts.auth.user_role == "PRIMARY"`
    
    **Step-by-step:**
    1. **Condition 1:** Audience `is` "HQ_Cust_Digital_Soccer_Likely"
    2. **Condition 2:** Internet Backup On `is not` true → generates `!rule.is_internet_backup_on`
    3. **Condition 3:** Power Backup On `is not` true → generates `!rule.is_power_backup_on`
    4. **Condition 4:** User Role `is` "PRIMARY"
    5. **Combine with:** AND (&&)
    
    **Key Rules:**
    - **Boolean facts** (rule flags): Use "is" for true, "is not" for false (generates negation `!`)
    - **String facts**: Use "is" for ==, "is not" for !=
    - **AND/OR**: Combine multiple conditions with logic operator
    """)

# Build conditions UI
conditions = []
num_conditions = st.slider("How many conditions?", 1, 5, 1)

for i in range(num_conditions):
    col1, col2, col3 = st.columns(3)

    with col1:
        fact_options = list(FACT_DSL_MAP.keys()) + ["Custom"]
        fact_selection = st.selectbox(
            f"Fact {i+1}",
            fact_options,
            key=f"fact_{i}"
        )
        if fact_selection == "Custom":
            fact = st.text_input("Enter custom fact path (e.g. facts.custom.field)", key=f"custom_fact_{i}", label_visibility="collapsed")
        else:
            fact = fact_selection

    with col2:
        operator = st.selectbox("Operator", ["is", "is not"], key=f"op_{i}")

    with col3:
        available_values = FACT_VALUES.get(fact, ["Custom"])
        
        if len(available_values) == 1 and available_values[0] == "Custom":
            value = st.text_input("Value", key=f"val_{i}")
        else:
            options = available_values + (["Custom"] if "Custom" not in available_values else [])
            selected = st.selectbox("Value", options, key=f"val_{i}")
            
            if selected == "Custom":
                value = st.text_input("Enter custom value", key=f"custom_val_{i}", label_visibility="collapsed")
            else:
                value = selected

    conditions.append((fact, operator, value))

logic = st.radio("Combine conditions using:", ["AND", "OR"])

st.markdown("---")

# ==================== RULE EVALUATION ====================

if st.button("▶ Run Rule Check"):
    st.subheader("🔍 Rule Evaluation")

    try:
        # Prepare test values dictionary
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

        # Evaluate all conditions
        results = []
        debug_info = []
        
        for fact, operator, value in conditions:
            actual_value = get_test_value_for_fact(fact, test_values_dict)
            match = evaluate_condition(fact, operator, value, actual_value)
            results.append(match)
            debug_info.append((fact, operator, value, actual_value, match))

        # Calculate final result based on logic
        if logic == "AND":
            final_result = all(results) if results else False
        else:
            final_result = any(results) if results else False

        # Display result with visual feedback
        if final_result:
            st.success("✅ RULE MATCHED → Card WILL SHOW")
        else:
            st.error("❌ RULE FAILED → Card WILL NOT SHOW")

        # Display generated DSL expression
        st.markdown("### 📄 Generated DSL Expression")
        try:
            dsl_expr = generate_dsl(conditions, logic)
            st.code(dsl_expr, language="javascript")
        except ValueError as e:
            st.error(f"⚠️ Error generating DSL: {str(e)}")

        # Display detailed debug information
        st.markdown("### 🛠️ Debug Details")
        for i, (fact, operator, value, actual, matched) in enumerate(debug_info):
            status = "✅" if matched else "❌"
            st.write(f"{status} **Condition {i+1}:** {fact} {operator} '{value}' | Actual: '{actual}'")
    
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        st.info("💡 Tip: Make sure all condition values are filled in before running.")

st.markdown("---")

# ==================== PAYLOAD GENERATION ====================

st.subheader("📦 Recommendation Payload Example")
try:
    payload_dsl = generate_dsl(conditions, logic) if conditions and all(v for _, _, v in conditions) else "No conditions defined"
except ValueError:
    payload_dsl = "Invalid conditions (empty values)"

example_payload = {
    "resourceId": selected_recommendation,
    "renderType": "secondary_message",
    "locale": selected_locale,
    "message": rec_message if rec_message else "(Custom recommendation)",
    "dismissible": True,
    "ruleConditions": payload_dsl
}

st.json(example_payload)

st.markdown("---")
st.info("💡 **Tip:** Use this tool to debug production issues like 'Card not showing to customer' or 'Wrong audience seeing card'")
