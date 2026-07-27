import streamlit as st
import time

st.header("Hello World!")

st.button("Click me please!")

st.text_input(
    "Write your API KEY",
    max_chars=100,
)

st.feedback("faces")

with st.sidebar:
    st.badge("Badge 1")

tab1, tab2, tab3 = st.tabs(["Agent", "Chat", "Output"])

with tab1:
    st.header("Agent")
with tab2:
    st.header("Chat")
with tab3:
    st.header("Output")

with st.chat_message("ai"):
    st.text("Hello!")
    with st.status("Agent is using tools...") as status:
        time.sleep(1)
        status.update(label="Agent is searching the web...")
        time.sleep(2)
        status.update(label="Agent is reading the pages...")
        time.sleep(3)
        status.update(label="Task Done.")
        status.update(state="complete")

st.chat_input("Write a message for the assistant.")
