import streamlit as st
from OCR.fin_data import get_fin_data

st.title("Page 2")
st.write("Demo page to show data manipulate")

fin_data = get_fin_data()
st.dataframe(fin_data)