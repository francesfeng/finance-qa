import streamlit as st
import pandas as pd

code = """
data = pd.read_csv('data/data.csv')\ndata.plot(kind='bar')
"""

st.write(code)
exec(code)
