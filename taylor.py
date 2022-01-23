import streamlit as st
import random
from dataclasses import dataclass
import pandas as pd

WORKABLE_DAYS = 220

st.title('Why your project drags on so long..')

st.header("First about your dev team")
devs = st.slider('How many devs work on it?', 1, 10, 2)
st.header("Then about your task")

total_mandays_estimate = st.slider('What is the initial time estimate (total man-work-days) you extracted from devs?', 1, 100, 10)
leadtime_estimate = total_mandays_estimate / devs
well_defined = st.checkbox('The task is really well defined and understood')
if not well_defined:
    checkin_moment = 100
    last_moment_change = st.checkbox("Only at the end of the project we will know if it is the right thing to build", value=True)
    if not last_moment_change:
        checkin_moment = st.slider("What % of the project must be complete before you can verify if it is the right thing to build?", 1, 99, 80)

st.header("Availability stats for the team")
st.write("Spillover means unfinished work from the previous project that still needs to be done")
st.subheader('Spillover - % time spent on previous unfinished work')
spillover = st.slider('spillover', 0, 100, 50)
emergencies = st.slider('% time spent on emergencies', 0, 100, 25)
turnover = st.slider('turnover per year (% quitting per year)', 0, 100, 33)
replacement = st.slider('time (days) till new hire starts', 0, 300, 60)
onboarding = st.slider('time (days) it takes new hire to become productive', 0, 300, 15)
holidays = st.slider('number of holidays in a year (PTO)', 0, 40, 25)
sickness = st.slider('sickness %', 0, 100, 1)
meetings = st.slider('meetings %', 0, 100, 10)
helps_onbording = st.slider('% Time spent helping onboarded devs (when there are new devs)', 0, 100, 10)
helps_recruiting = st.slider('% Time spent participating in interviews (when looking for new devs)', 0, 100, 5)

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
    other_work: int = 0
    sick_days: int = 0
    used_pto: int = 0
    days_recruiting: int = 0
    days_onboarding: int = 0
    days_firefighting: int = 0
    days_notfilled:int = 0 
    days_meetings:int = 0
    days_waiting:int = 0

    def report(self) -> dict:
        return {
            "Role": self.name,
            "Productive": self.worked_days,
            "Other work": self.other_work,
            "Firefighting": self.days_firefighting,
            "Sick": self.sick_days,
            "PTO": self.used_pto,
            "Onboarding": self.days_onboarding,
            "Recruiting": self.days_recruiting,
            "Meetings": self.days_meetings,
            "Not Filled": self.days_notfilled,
            "Waiting": self.days_waiting,
        }
    
def sick(contr: Contributor) -> bool:
    return random.randint(1, 100) <= sickness

def on_holidays(contr: Contributor) -> bool:
    if contr.used_pto >= holidays:
        return False
    return random.randint(1, 100) <= contr.worked_days

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

def busy_prev_work(contr) ->bool:
    return random.randint(1, 100) <= spillover

def is_productive(contr: Contributor, onbording_needed:bool, recruitment_in_progress:bool) -> bool:
    if contr.not_filled:
        contr.days_notfilled += 1
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
    if busy_prev_work(contr):
        contr.other_work += 1
        return False
    contr.worked_days += 1
    return True

worked_days = 0
lead_days = 0
_devs = [Contributor("dev") for _ in range(devs)]
perc_complete = 0
scope_change_waste = 0
while (worked_days < total_mandays_estimate) or not well_defined:
    perc_complete = (worked_days / total_mandays_estimate) * 100
    if not well_defined and perc_complete > checkin_moment:
        well_defined = True
        scope_change_waste = worked_days
        worked_days = 0
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
            dev.not_filled = True
    lead_days += 1
late_by = round(lead_days - leadtime_estimate, 1)
col1, col2, col3 = st.columns(3)
col1.metric(label="Lead time", value=f"{lead_days} days", delta=f"{late_by} days", delta_color="inverse")
waste = (lead_days * devs) -(leadtime_estimate * devs)
col2.metric(label="Waste", value=f"{waste} days")
col3.metric(label="Scope Change Waste", value=f"{scope_change_waste} days")
report = [d.report() for d in _devs]
report = pd.DataFrame(report)
st.dataframe(report)
