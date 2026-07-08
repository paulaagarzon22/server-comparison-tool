import streamlit as st

st.title("Minimal Test")
st.write("This is a minimal test to see if Streamlit works at all")

# Test basic functionality
if st.button("Click me"):
    st.write("Button clicked!")

st.write("If you can see this, Streamlit is working")
