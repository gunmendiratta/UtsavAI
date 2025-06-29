import streamlit as st
import json

# ----------------- Load Vendor Data ----------------- #
with open("services.json", "r") as file:
    services = json.load(file)

# ----------------- Streamlit Page Setup ----------------- #
st.set_page_config(page_title="Utsav AI", layout="centered")
st.title("Utsav AI: Wiser with your budget 💸")
st.write("Welcome to Utsav AI, your personal financial assistant for event planning!")

# ----------------- User Input ----------------- #
budget = st.number_input("💰 Enter your total budget:", min_value=0, step=100)

st.markdown("### ✅ Choose the services you want to include:")
selected_services = []
for s in ["Catering", "Decoration", "Photography", "DJ & Music", "Lighting"]:
    if st.checkbox(s):
        selected_services.append(s)

# ----------------- Phase 1: Estimated Base Cost ----------------- #
if selected_services:
    st.subheader("💰 Estimated Cost Based on Base Prices")

    base_total = 0
    for service in selected_services:
        vendor = next((v for v in services if v["service"].lower() == service.lower()), None)
        if vendor:
            st.markdown(f"**{service}** — {vendor['vendor_name']}")
            st.write(f"Base Price: ₹{vendor['base_price']}")
            base_total += vendor["base_price"]

    st.subheader(f"🧾 Total Estimated Base Cost: ₹{base_total}")

    # Show button to continue to negotiation
    if "show_bill" not in st.session_state:
        st.session_state["show_bill"] = False

    if st.button("📄 Generate Bill with Negotiation"):
        st.session_state["show_bill"] = True

# ----------------- Phase 2: Negotiation & Final Bill ----------------- #
if st.session_state.get("show_bill", False):
    st.subheader("📋 Service Negotiation")

    total_cost = 0

    for service in selected_services:
        vendor = next((v for v in services if v["service"].lower() == service.lower()), None)
        if not vendor:
            continue

        # Keys for session tracking
        key_suffix = service.replace(' ', '_')
        negotiate_key = f"negotiate_{key_suffix}"
        offer_input_key = f"offer_{key_suffix}"
        submit_key = f"submit_{key_suffix}"
        final_price_key = f"final_price_{key_suffix}"

        # Display service info
        st.markdown(f"### {service}")
        st.write(f"**Vendor:** {vendor['vendor_name']}")
        st.write(f"Base Price: ₹{vendor['base_price']}")

        # Negotiate button
        if st.button(f"🤝 Negotiate {service}", key=negotiate_key):
            st.session_state[f"show_input_{key_suffix}"] = True

        # Show input if button was clicked
        if st.session_state.get(f"show_input_{key_suffix}", False):
            user_offer = st.number_input(
                f"Enter your offer for {service}",
                min_value=0,
                step=500,
                key=offer_input_key
            )

            if st.button(f"Submit Offer for {service}", key=submit_key):
                base = vendor["base_price"]
                min_price = vendor["min_price"]

                if user_offer >= base:
                    st.success("✅ Vendor happily accepts your offer!")
                    st.session_state[final_price_key] = user_offer
                elif user_offer >= min_price:
                    st.info("🤝 Vendor agrees after negotiation.")
                    st.session_state[final_price_key] = user_offer
                else:
                    st.error(f"❌ Offer too low.")
                    st.session_state[final_price_key] = base  # fallback

        # Get final price (negotiated or base)
        final_price = st.session_state.get(final_price_key, vendor["base_price"])
        st.write(f"💰 Final Price for {service}: ₹{final_price}")
        total_cost += final_price

        st.divider()

    # Final bill total
    st.subheader(f"💳 Final Total After Negotiation: ₹{total_cost}")
    if total_cost <= budget:
        st.success("✅ You’re within your budget!")
    else:
        st.warning("⚠️ You're over budget. ")
