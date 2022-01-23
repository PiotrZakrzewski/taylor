import streamlit as st
import random
from dataclasses import dataclass

st.title('Why your project drags on so long..')

st.header("First about your task")
# fe_work = st.checkbox('Involves front-end work')
# be_work = st.checkbox('Involves back-end work')
# devops_work = st.checkbox('Involves devops work')
# manual_qa_work = st.checkbox('Involves manual QA')
# auto_qa_work = st.checkbox('Involves new QA automation')
# external_stakeholder = st.checkbox('Involves an external stakeholder\'s review')
# well_defined = st.checkbox('Is really well defined and well understood')

st.subheader('What is the initial time estimate you extracted from devs?')
estimate = st.slider('estimate in working days', 1, 100, 1)


st.header("Then about your dev team")

# if st.checkbox('Multifunctional team (anyone can pickup any ticket)'):
devs = st.slider('devs', 1, 10, 1)
# else:
#     if be_work:
#         st.subheader('How many back-end developers?')
#         be = st.slider('Back-end', 0, 10, 1)
#     if fe_work:
#         st.subheader('How many front-end developers?')
#         fe = st.slider('Front-end', 0, 10, 1)
#     if devops_work:
#         st.subheader('How many dedicated devops?')
#         devops = st.slider('devops', 0, 10, 1)
#     if manual_qa_work or auto_qa_work:
#         st.subheader('How many dedicated QA?')
#         devops = st.slider('QAs', 0, 10, 1)

st.header("Availability stats")
# st.subheader('Spillover - % spent on previous unfinished work')
# spillover = st.slider('spillover', 0, 100, 25)

st.subheader('Chance given day will be spent fighting fires')
emergencies = st.slider('emergencies', 0, 100, 25)

# st.subheader('Dev turnover rate')
# turnover = st.slider('turnover', 0, 100, 33)

st.subheader('Holidays per year')
holidays = st.slider('holidays', 0, 40, 25)

st.subheader('sickness chance per day')
sickness = st.slider('sickness %', 0, 100, 3)

# st.subheader('Multitasking - how many different projects run at the same time')
# multitasking = st.slider('multitasking', 0, 10, 3)
@dataclass
class Contributor:
    name: str
    used_pto: int
    sick_days: int
    worked_days: int
    
def sick(contr: Contributor) -> bool:
    return random.randint(1, 100) <= sickness

def on_holidays(contr: Contributor) -> bool:
    chance_wants_off = (contr.worked_days - 100)/100
    return random.randint(1, 100) <= chance_wants_off

def on_emergency(contr: Contributor) -> bool:
    return random.randint(1, 100) <= emergencies

def is_productive(contr: Contributor) -> bool:
    if sick(contr):
        contr.sick_days += 1
        return False
    if on_holidays(contr):
        contr.used_pto += 1
        return False
    if on_emergency(contr):
        return False
    contr.worked_days += 1
    return True

worked_days = 0
lead_days = 0
_devs = [Contributor("dev", 0, 0, 0) for _ in range(devs)]
while worked_days < estimate:
    for dev in _devs:
        if is_productive(dev):
            worked_days += 1
    lead_days += 1
late_by = lead_days - estimate
late_perc = round((late_by / estimate)* 100)
st.write(f"Late by {late_by} days or {late_perc}% over the budget")
st.write(f"Lead days {lead_days}")
st.write(f"Worked days {worked_days}")
total_sick = sum([c.sick_days for c in _devs])
total_holidays = sum([c.used_pto for c in _devs])
st.write(f"sick days {total_sick}")
st.write(f"holidays days {total_holidays}")
