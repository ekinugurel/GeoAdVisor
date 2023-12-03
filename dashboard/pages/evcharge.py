import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.title('EV Chargers Use Case 🔋')

#### TUTORIAL CODE ###
st.title('Session State')
"st.session_state_object: ", st.session_state
number = st.slider('A number', 1, 10, key = 'slider')
st.write(st.session_state)

col1, buff, col2 = st.columns([1, 0.5, 3])
option_names = ['a', 'b', 'c']
next = st.button("next option")

if next:
    if st.session_state['radio_option'] == 'a':
        st.session_state.radio_option = 'b'
    elif st.session_state['radio_option'] == 'b':
        st.session_state.radio_option = 'c'

option = col1.radio("Pick an option", option_names, key = "radio_option")
st.session_state

if option == "A":
    col2.write("You picked 'a' :smile: ")

elif option == "B":
    col2.write("you picked 'b' :heart: ")

else:
    col2.write("hi ")
