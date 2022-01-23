import streamlit as st
import random
from dataclasses import dataclass

WORKABLE_DAYS = 220

st.title('Why your project drags on so long..')

st.header("First about your dev team")
devs = st.slider('How many devs work on it?', 1, 10, 2)
st.header("Then about your task")
leadtime_estimate = st.slider('What is the initial time estimate (lead time in working days) you extracted from devs?', 1, 100, 10)
total_mandays_estimate = leadtime_estimate * devs
# fe_work = st.checkbox('Involves front-end work')
# be_work = st.checkbox('Involves back-end work')
# devops_work = st.checkbox('Involves devops work')
# manual_qa_work = st.checkbox('Involves manual QA')
# auto_qa_work = st.checkbox('Involves new QA automation')
# external_stakeholder = st.checkbox('Involves an external stakeholder\'s review')
# well_defined = st.checkbox('Is really well defined and well understood')


# if st.checkbox('Multifunctional team (anyone can pickup any ticket)'):
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

st.header("Availability stats (either % of the year or in days)")
# st.subheader('Spillover - % spent on previous unfinished work')
# spillover = st.slider('spillover', 0, 100, 25)
emergencies = st.slider('% time spent on emergencies', 0, 100, 25)
turnover = st.slider('turnover per year (% quitting per year)', 0, 100, 33)
replacement = st.slider('time till new hire starts', 0, 300, 60)
onboarding = st.slider('time it takes new hire to become productive', 0, 100, 5)
holidays = st.slider('number of holidays in a year (PTO)', 0, 40, 25)
sickness = st.slider('sickness %', 0, 100, 3)
meetings = st.slider('meetings %', 0, 100, 10)
st.subheader("Below availability modifiers are active only when there are unfilled positions or devs being onboarded")
helps_onbording = st.slider('Time spent helping onboarded devs', 0, 100, 1)
helps_recruiting = st.slider('Time spent participating in interviews', 0, 100, 1)

# st.subheader('Multitasking - how many different projects run at the same time')
# multitasking = st.slider('multitasking', 0, 10, 3)
@dataclass
class Contributor:
    name: str
    not_filled: bool = False
    onboarded: bool = True
    days_till_replacement:int = 0
    days_till_productive: int = 0

    worked_days: int = 0
    sick_days: int = 0
    used_pto: int = 0
    days_recruiting: int = 0
    days_onboarding: int = 0
    days_firefighting: int = 0
    days_notfilled:int = 0 
    days_meetings:int = 0
    
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

def is_helping_onboard(contr) -> bool:
    return random.randint(1, 100) <= helps_onbording

def is_helping_recruit(contr) -> bool:
    return random.randint(1, 100) <= helps_recruiting

def is_productive(contr: Contributor, onbording_needed:bool, recruitment_in_progress:bool) -> bool:
    if contr.not_filled:
        return False
    if not contr.onboarded:
        contr.days_onboarding += 1
        False
    if sick(contr):
        contr.sick_days += 1
        return False
    if on_holidays(contr):
        contr.used_pto += 1
        return False
    if on_emergency(contr):
        contr.days_firefighting += 1
        return False
    if in_meeting(contr):
        contr.days_meetings += 1
        return False
    if onbording_needed and is_helping_onboard(contr):
        contr.days_onboarding += 1
        return False
    if recruitment_in_progress and is_helping_recruit(contr):
        contr.days_recruiting += 1
        return False
    contr.worked_days += 1
    return True

worked_days = 0
lead_days = 0
_devs = [Contributor("dev") for _ in range(devs)]
while worked_days < total_mandays_estimate:
    recruiting_in_progress = any([dev.not_filled for dev in _devs])
    onboarding_in_progress = any([not dev.onboarded for dev in _devs])
    for dev in _devs:
        if is_productive(dev, onboarding_in_progress, recruiting_in_progress):
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
late_by = lead_days - leadtime_estimate
late_perc = round((late_by / leadtime_estimate)* 100)
st.write(f"Late by {late_by} days or {late_perc}% over the budget")
st.write(f"Lead days {lead_days}")
st.write(f"Worked days {worked_days}")
total_sick = sum([c.sick_days for c in _devs])
total_holidays = sum([c.used_pto for c in _devs])
st.write(f"sick days {total_sick}")
st.write(f"holidays days {total_holidays}")
