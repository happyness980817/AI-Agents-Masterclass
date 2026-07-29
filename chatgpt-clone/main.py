import streamlit as st

if "is_admin" not in st.session_state:  # st.session_state 는 새로고침해도 유지
    st.session_state["is_admin"] = False

st.header("Hello")

name = st.text_input("What is your name?")

if name:
    st.write(f"Hello {name}")
    st.session_state["is_admin"] = True


print(st.session_state["is_admin"])
