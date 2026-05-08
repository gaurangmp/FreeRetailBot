import streamlit as st
import pandas as pd
from thefuzz import process, fuzz


def load_data():
    return pd.read_csv("inventory.csv")


def get_bot_response(user_input, df):
    user_input = user_input.lower()

    # 1. Handle General Info
    if any(word in user_input for word in ["hours", "open", "time"]):
        return "We are open Monday to Friday, 9:00 AM to 6:00 PM."



    # 2. Fuzzy Search Logic
    choices = df['item'].tolist()
    # Extract the best match, the score, and the index
    # process.extractOne returns: (matched_string, score)
    best_match, score = process.extractOne(user_input, choices, scorer=fuzz.partial_ratio)

    # Threshold: If the match is 70% or higher, we consider it a hit
    if score >= 70:
        # Find the specific row for this match
        row = df[df['item'] == best_match].iloc[0]

        if row['stock'] > 0:
            return f"Yes ! {best_match}. Yes, we have it in stock for ${row['price']} We have quantity of  {row['stock']} left ."
        else:
            return f"I see you're looking for {best_match}, but we're currently out of stock."

    # 3. Handling Items Not Found
    keywords = ["do you have", "search", "buy", "stock", ""]
    if any(key in user_input for key in keywords):
        return "I'm sorry, I couldn't find that item in our inventory."

    return "I'm not sure I understand. Try asking 'Do you have milk?'"


# ... (rest of your Streamlit UI code remains the same)
# 3. Streamlit UI Setup
st.title("Retail Assistant Bot")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("How can I help you today?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    inventory_df = load_data()
    response = get_bot_response(prompt, inventory_df)

    # Add bot response to history
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})


    # 2. Define clearing function
    def clear_chat():
        st.session_state.messages = []


    # 3. Add button with callback
    st.button("Clear Chat", on_click=clear_chat)