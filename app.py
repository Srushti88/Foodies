import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.title("FoodieBot Chat")

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("Ask FoodieBot:")

if st.button("Send") and user_input:
    st.session_state.history.append({"user": user_input})

    response = requests.post(f"{API_BASE}/converse/", json={"user_text": user_input})
    if response.status_code == 200:
        data = response.json()
        score = data.get("interest_score", 0)
        products = data.get("recommended_products", [])

        st.session_state.history.append({"bot": f"Interest Score: {score}%"})
        if products:
            for prod in products:
                st.session_state.history.append({"bot": f"Try: {prod['name']} - ${prod['price']} - {prod['description']}"})
        else:
            st.session_state.history.append({"bot": "Sorry, no products found with your preferences."})
    else:
        st.session_state.history.append({"bot": "Error contacting FoodieBot API."})

for msg in st.session_state.history:
    if "user" in msg:
        st.markdown(f"**You:** {msg['user']}")
    else:
        st.markdown(f"**FoodieBot:** {msg['bot']}")
