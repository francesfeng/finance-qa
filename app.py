import streamlit as st
import os
import requests
from requests.adapters import HTTPAdapter, Retry


BEARER_TOKEN = os.environ.get("BEARER_TOKEN") or "BEARER_TOKEN_HERE"
headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

endpoint_url = "http://localhost:8000"
s = requests.Session()

# we setup a retry strategy to retry on 5xx errors
retries = Retry(
    total=5,  # number of retries before raising error
    backoff_factor=0.1,
    status_forcelist=[500, 502, 503, 504]
)
s.mount('http://', HTTPAdapter(max_retries=retries))

query = st.text_input('Ask me anything about hydrogen!', '')

res = requests.post(
        f"{endpoint_url}/query",
        headers=headers,
        json={'query': query}
    )

st.text(res.json())