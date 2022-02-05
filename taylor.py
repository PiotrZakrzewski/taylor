import streamlit as st
import random
from dataclasses import dataclass
import pandas as pd

WORKABLE_DAYS = 220

st.title('Why your project drags on so long..')
st.markdown("""
# Simple Delay Calculator
This calculator conducts a simple simulation based on parameters you provide.
It may have too many assumptions, simplifications and omissions to be accurate 
but it can help you gain awareness of some forces that conspire against
your roadmap which people often claim they know about, but forget
when giving lead time estimates for their planned projects.
""")
st.header("First about your dev team")
st.markdown("""
- Devs are perfectly fungible (anyone can pick any task, no specialization)
- no difference in performance
""")
devs = st.slider('How many devs work on it?', 1, 10, 2)
st.header("Then about your task")
st.markdown("""
**Bufferless and Accurate Estimate**

The estimate you give here is assumed to be perfect - it will really take as long
in this simulation to complete the project. This simulation is mostly about all
factors other than just wrong estimates that contribute to delays.
""")
total_mandays_estimate = st.slider('What is the initial time estimate (total man-work-days) you extracted from devs?', 1, 100, 10)
leadtime_estimate = total_mandays_estimate / devs
st.markdown("""
**Is The Task Really Well Defined?**

Some tasks, like fixing a bug or completing a routine process require no iteration
and are not subject to uncertainty. Software development however, is famous for vague and shifting
requirements, or misunderstanding thereof. If you select that the task is well defined,
the team will finish the task after they rack up enough productive days (your estimate from above).
If the task is not well defined, you will need to specify when is the check-in point, imagine
for instance a demo to the stakeholder or end-to-end tests, this is the point when
the progress is reset to zero to simulate how the **real** requirements were discovered.
""")
well_defined = st.checkbox('The task is really well defined and understood')
if not well_defined:
    checkin_moment = 100
    last_moment_change = st.checkbox("Only at the end of the project we will know if it is the right thing to build", value=True)
    if not last_moment_change:
        checkin_moment = st.slider("What % of the project must be complete before you can verify if it is the right thing to build?", 1, 99, 80)
st.markdown("""
**Waiting on review**

If this task/project requires a team member to review before work can proceed, check the following box.
The review can only take place when the reviewer is available, same probabilities will be used
for determining if the reviewer is available for review as for the rest of the team (see later section "Availability")
""")        
review_needed = st.checkbox("Is there any sort of review involved? e.g. Pull Request review.", value=True)
if review_needed:
    review_frequency = st.slider("The (PR) review happens every X days (1=every day)", 1, 10, 5)
st.markdown("Requirement of an approval or input from some external stakeholder can also be a cause for waiting. Approval is simulated the exact same way as review.")
approval_needed = st.checkbox("Is there an external stakeholder who needs to approve anything?", value=True)
if approval_needed:
    approval_frequency = st.slider("Approval/input from an external stakeholder happens every X days (1=every day)", 1, 30, 10)
st.header("Availability stats for the team")
st.write("Spillover means that your devs are still preoccupied with leftovers from the previous project")
spillover = st.slider('spillover % time spent on previous unfinished work', 0, 100, 50)
st.write("Is your project team in any capacity involved in solving production issues? What % of the time more or less?")
emergencies = st.slider('% time spent on emergencies', 0, 100, 25)
st.write("Devs will leave your team, when it happens it is very disruptive. What was the turnover over the last 12 months?")
turnover = st.slider('turnover per year (% quitting per year)', 0, 100, 33)
st.write("What gap (in days) should the simulation use for the time between a leaving dev's last day and the new one starting?")
replacement = st.slider('time (days) till new hire starts', 0, 300, 60)
st.write("How long till an experienced dev on your team picks up their first independent ticket?")
onboarding = st.slider('time (days) it takes new hire to become productive', 0, 300, 15)
st.write("For sake of simplicity devs's chance of taking holidays increases with every day, but the total will never exceed the specified max PTOs")
holidays = st.slider('number of holidays in a year (PTO)', 0, 40, 25)
st.write("People get sick, devs too. Use % chance (per working day) of a dev calling in sick.")
sickness = st.slider('sickness %', 0, 100, 1)
st.write("Add up recurring meetings devs are involved in (not related to the project).")
meetings = st.slider('meetings %', 0, 100, 10)
st.write("Specify % of time a mentor / buddy spends when onboarding a new dev")
helps_onbording = st.slider('% Time spent helping onboarded devs (when there are new devs)', 0, 100, 10)
st.write("How time consuming is your recruiting process for your own devs? This will kick in only when recruiting.")
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
            "Absent (Role Not Filled)": self.days_notfilled,
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
    return True

worked_days = 0
lead_days = 0
_devs = [Contributor("dev") for _ in range(devs)]
reviewer = Contributor("reviewer")
ext_stakeholder = Contributor("external stakeholder")
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
    reviewer_available = is_productive(reviewer, onboarding_in_progress, recruiting_in_progress)
    stakeholder_available = is_productive(ext_stakeholder, onboarding_in_progress, recruiting_in_progress)
    for dev in _devs:
        if is_productive(dev, onboarding_in_progress, recruiting_in_progress):
            if review_needed and (lead_days % review_frequency) == 0 and not reviewer_available:
                dev.days_waiting += 1
            elif approval_needed and (lead_days % approval_frequency) == 0 and not stakeholder_available:
                dev.days_waiting += 1
            else:
                dev.worked_days += 1
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
st.markdown("""
# Results
- Lead time means: how many working days from the start till finish the project took.
In real life situation this would be calendar days, but this work obsessed simulation does not know weekends..
- Waste is any activity that did not progress the project (recruiting, onboarding, emergencies, PTO, sickness)
- Scope Change waste: component of the overall waste corresponding to the uncertainty / spec change
""")
col1, col2  = st.columns(2)
col3, col4 = st.columns(2)
col1.metric(label="Lead time", value=f"{lead_days} days", delta=f"{late_by} days", delta_color="inverse")
waste = (lead_days * devs) -(leadtime_estimate * devs)
col2.metric(label="Waste (multitasking/unavailable)", value=f"{waste} days")
col3.metric(label="Scope Change Waste", value=f"{scope_change_waste} days")
total_wait = sum([d.days_waiting for d in _devs])
col4.metric(label="Waiting", value=f"{total_wait} days")
report = [d.report() for d in _devs]
report = pd.DataFrame(report)
st.header("Individual Time Breakdown per Contributor")
st.dataframe(report)
