import streamlit as st
import pandas as pd
from thefuzz import process, fuzz


def load_data():
    return pd.read_csv("inventory.csv")


# --- Helper Function for Pagination ---
def list_items(df, page=0):
    start_idx = page * 10
    end_idx = start_idx + 10
    subset = df.iloc[start_idx:end_idx]

    if subset.empty:
        return "No more items to show.", False

    response = f"--- **Shop Inventory (Page {page + 1})** ---\n"
    for _, row in subset.iterrows():
        status = "✅ In Stock" if row['stock'] > 0 else "❌ Out of Stock"
        response += f"- **{row['item']}**: ${row['price']} ({status})\n"

    has_next = len(df) > end_idx
    if has_next:
        response += "\n*Type **'next'** to see more items.*"
    return response, has_next


def get_bot_response(user_input, df):
    user_input = user_input.lower().strip()

    # 1. Handle General Info
    if any(word in user_input for word in ["hours", "open", "time"]):
        return "We are open Monday to Friday, 9:00 AM to 6:00 PM."

    # 2. Handle Listing / Inventory
    if any(word in user_input for word in ["list", "inventory", "show all"]):
        st.session_state.current_page = 0  # Reset to first page
        response, _ = list_items(df, page=0)
        return response

    # 3. Handle "Next" Page
    if user_input == "next":
        if "current_page" not in st.session_state:
            st.session_state.current_page = 0

        st.session_state.current_page += 1
        response, has_next = list_items(df, page=st.session_state.current_page)

        if "No more items" in response:
            st.session_state.current_page = 0  # Reset if they reach the end
        return response

    # 4. Fuzzy Search Logic (for specific items)
    choices = df['item'].tolist()
    best_match, score = process.extractOne(user_input, choices, scorer=fuzz.partial_ratio)

    if score >= 70:
        row = df[df['item'] == best_match].iloc[0]
        if row['stock'] > 0:
            return f"Yes! We have **{best_match}** in stock for ${row['price']}. Current quantity: {row['stock']}."
        else:
            return f"I see you're looking for {best_match}, but we're currently out of stock."

    # 5. Handling Items Not Found
    keywords = ["do you have", "search", "buy", "stock"]
    if any(key in user_input for key in keywords):
        return "I'm sorry, I couldn't find that item in our inventory. Try typing 'list' to see everything we have."

    return "I'm not sure I understand. Try asking 'Do you have milk?' or type 'list' to see all items."


# --- Streamlit UI Setup ---
st.title("Gaurang Retail Assistant Pro v1")

# Initialize Session States
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_page" not in st.session_state:
    st.session_state.current_page = 0


# Sidebar/Clear Button
def clear_chat():
    st.session_state.messages = []
    st.session_state.current_page = 0


st.button("Clear Chat", on_click=clear_chat)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("How can I help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    inventory_df = load_data()
    response = get_bot_response(prompt, inventory_df)

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})