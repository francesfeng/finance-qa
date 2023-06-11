import streamlit as st
import logging
from controller import Controller


# Configure the logging settings
logging.basicConfig(filename='debug.log', filemode='a', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


controller = Controller()
input = st.text_input(label="Questions", value="", label_visibility="collapsed", placeholder="Ask me anything about hydrogen")
topics = controller.run_topics(input)

col11, col12 = st.columns(2)
with col11: 
    st.caption(topics["1"]["Topic"])
    response = controller.run(topics["1"]["Question"])

    if response['type'] == 'sentence':
        st.subheader(response['response'])
    elif response['type'] == 'summary':
        st.write(response['response'])
    elif response['type'] == 'chart':
        st.write(response['response'])
        exec(response['response'])
    else:
        st.warning(response['response'])

with col12: 
    st.caption(topics["2"]["Topic"])
    response = controller.run(topics["2"]["Question"])

    if response['type'] == 'sentence':
        st.subheader(response['response'])
    elif response['type'] == 'summary':
        st.write(response['response'])
    elif response['type'] == 'chart':
        st.write(response['response'])
        exec(response['response'])
    else:
        st.warning(response['response'])

col21, col22 = st.columns(2)
with col21: 
    st.caption(topics["3"]["Topic"])
    response = controller.run(topics["3"]["Question"])

    if response['type'] == 'sentence':
        st.subheader(response['response'])
    elif response['type'] == 'summary':
        st.write(response['response'])
    elif response['type'] == 'chart':
        st.write(response['response'])
        exec(response['response'])
    else:
        st.warning(response['response'])

with col22: 
    st.caption(topics["4"]["Topic"])
    response = controller.run(topics["4"]["Question"])

    if response['type'] == 'sentence':
        st.subheader(response['response'])
    elif response['type'] == 'summary':
        st.write(response['response'])
    elif response['type'] == 'chart':
        st.write(response['response'])
        exec(response['response'])
    else:
        st.warning(response['response'])

col31, _ = st.columns(2)
with col31: 
    st.caption(topics["5"]["Topic"])
    response = controller.run(topics["5"]["Question"])

    if response['type'] == 'sentence':
        st.subheader(response['response'])
    elif response['type'] == 'summary':
        st.write(response['response'])
    elif response['type'] == 'chart':
        st.write(response['response']['explanation'])
        exec(response['response']['code'])
    else:
        st.warning(response['response'])