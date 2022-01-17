import streamlit as st

st.title('Why your ticket drags on..')

st.header("First about your task")
fe_work = st.checkbox('Involves front-end work')
be_work = st.checkbox('Involves back-end work')
devops_work = st.checkbox('Involves devops work')
manual_qa_work = st.checkbox('Involves manual QA')
auto_qa_work = st.checkbox('Involves new QA automation')
auto_qa_work = st.checkbox('Involves an external stakeholder\'s review')
st.subheader('What is the bufferless time in days estimate (continnous uninterrupted development)')
estimate = st.slider('estimate', 1, 100, 1)


st.header("Then about your dev team")

if st.checkbox('Multifunctional team (anyone can pickup any ticket)'):
    devs = st.slider('devs', 0, 10, 1)
else:
    st.subheader('How many back-end developers?')
    be = st.slider('Back-end', 0, 10, 1)

    st.subheader('How many front-end developers?')
    fe = st.slider('Front-end', 0, 10, 1)

    st.subheader('How many dedicated devops?')
    devops = st.slider('devops', 0, 10, 1)

st.header("Availability stats")
st.subheader('Spillover - % spent on previous unfinished work')
spillover = st.slider('spillover', 0, 100, 25)

st.subheader('Chance given day will be spent fighting fires')
emergencies = st.slider('emergencies', 0, 100, 25)

st.subheader('Dev turnover rate')
turnover = st.slider('turnover', 0, 100, 33)

st.subheader('Holidays per year')
holidays = st.slider('holidays', 0, 40, 25)

st.subheader('sickness chance per day')
holidays = st.slider('sickness %', 0, 100, 3)
