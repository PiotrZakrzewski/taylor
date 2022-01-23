import streamlit as st
import random
from dataclasses import dataclass

WORKABLE_DAYS = 220

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
estimate = st.slider('estimate in working days', 1, 100, 10)


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

st.subheader('Dev turnover rate')
turnover = st.slider('turnover', 0, 100, 33)

st.subheader('Days till replacement')
replacement = st.slider('replacement', 0, 300, 60)

st.subheader('Onboarding length')
onboarding = st.slider('onboarding', 0, 100, 5)

st.subheader('Holidays per year')
holidays = st.slider('holidays', 0, 40, 25)

st.subheader('sickness chance per day')
sickness = st.slider('sickness %', 0, 100, 3)

st.subheader('time spent on (non-project) meetings')
meetings = st.slider('meetings %', 0, 100, 10)

# st.subheader('Multitasking - how many different projects run at the same time')
# multitasking = st.slider('multitasking', 0, 10, 3)
@dataclass
class Contributor:
    name: str
    used_pto: int = 0
    sick_days: int = 0
    worked_days: int = 0
    not_filled: bool = False
    onboarded: bool = True
    days_till_replacement:int = 0
    days_till_productive: int = 0
    
def sick(contr: Contributor) -> bool:
    return random.randint(1, 100) <= sickness

def on_holidays(contr: Contributor) -> bool:
    chance_wants_off = (contr.worked_days - 100)/100
    return random.randint(1, 100) <= chance_wants_off

def on_emergency(contr: Contributor) -> bool:
    return random.randint(1, 100) <= emergencies

def last_day(contr: Contributor) -> bool:
    daily_chance = turnover / WORKABLE_DAYS
    fractionized_roll = (random.randint(1, 10000) / 100)
    return  fractionized_roll <= daily_chance

def in_meeting(contr: Contributor) -> bool:
    return random.randint(1, 100) <= meetings

def is_productive(contr: Contributor) -> bool:
    if contr.not_filled:
        return False
    if not contr.onboarded:
        False
    if sick(contr):
        contr.sick_days += 1
        return False
    if on_holidays(contr):
        contr.used_pto += 1
        return False
    if on_emergency(contr):
        return False
    if in_meeting(contr):
        return False
    contr.worked_days += 1
    return True

worked_days = 0
lead_days = 0
_devs = [Contributor("dev") for _ in range(devs)]
while worked_days < estimate:
    for dev in _devs:
        if is_productive(dev):
            worked_days += 1
        if not dev.onboarded and dev.days_till_productive < 1:
            dev.onboarded = True
        if not dev.onboarded:
            dev.days_till_productive -= 1
        if dev.not_filled and dev.days_till_replacement < 1:
            dev.not_filled = False
            dev.days_till_productive = onboarding
        if dev.not_filled:
            dev.days_till_replacement -= 1
        if not dev.not_filled and last_day(dev):
            dev.days_till_replacement = replacement
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
