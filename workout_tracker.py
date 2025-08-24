import streamlit as st
import pandas as pd
import datetime
from datetime import date
import json
import os
import requests

# Page configuration
st.set_page_config(
    page_title="Workout Tracker",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #ff4b4b;
        text-align: center;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4CAF50;
        margin-top: 20px;
    }
    .workout-card {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# File path for saving workouts
WORKOUT_FILE = "workouts.json"

# Predefined exercises based on categories
exercise_templates = {
    "Upper Push": ["Bench Press 4 x 4-6", "Overhead Press 4 x 4-6", "Incline Dumbbell Press 3 x 6-8", "Weighted Dips 3 x 6-8", "Tricep Rope Pushdown 3 x 10-12"],
    "Lower Body (Squat Focus)": ["Back Squat 4 x 4-6", "Romanian Deadlift 4 x 6-8", "Walking Lunges 3 x 8-10","Leg Press 3 x 8-10", "Calf Raise 3 x 12-15"],
    "Upper Pull": ["Deadlift 4 x 3-5", "Pull Ups 4 x 6-8", "Barbell Row 3 x 6-8", "Face Pulls 3 x 10-12", "Bicep Curl 3 x 10-12"],
    "Lower Body (Posterior Chain Focus)": ["Front/Box Squat 4 x 4-6", "Good Mornings/Hip Thrusts 3 x 6-8", "Bulgarian Split Squats 3 x 8-10","Glute Ham Raises/Nordic Curls 3 x 8-10", "Farmer's Carry 3 x 30-40s"],
    "Optional Conditioning": ["To be Added"]
}

# Ensure session state is initialized
if "page" not in st.session_state:
    st.session_state.page = "Add Workout"

if "workouts" not in st.session_state:
    st.session_state.workouts = []

# Function to send data to n8n
N8N_WEBHOOK_URL = st.secrets.get("N8N_WEBHOOK_URL")  # replace with your actual webhook URL
def send_to_n8n(workout_entry):
    try:
        response = requests.post(N8N_WEBHOOK_URL, json=workout_entry)
        if response.status_code == 200:
            st.success("Workout sent to automation successfully!")
        else:
            st.error(f"Failed to send workout to automation: {response.text}")
    except Exception as e:
        st.error(f"Error sending data to n8n: {str(e)}")

# Load workouts from file
def load_workouts():
    if os.path.exists(WORKOUT_FILE):
        with open(WORKOUT_FILE, "r") as f:
            return json.load(f)
    return []

# Save workouts to file
def save_workouts():
    with open(WORKOUT_FILE, "w") as f:
        json.dump(st.session_state.workouts, f, indent=4)

# Sidebar navigation
with st.sidebar:
    st.title("🏋️ Navigation")
    if st.button("➕ Add Workout"):
        st.session_state.page = "Add Workout"
    if st.button("📅 Workout History"):
        st.session_state.page = "Workout History"
    if st.button("📊 Progress Overview"):
        st.session_state.page = "Progress Overview"

# ------------------ PAGE 1: ADD WORKOUT ------------------
if st.session_state.page == "Add Workout":
    st.markdown("<h1 class='main-header'>Track Your Workout 💪</h1>", unsafe_allow_html=True)

    workout_date = st.date_input("Workout Date", date.today())
    workout_type = st.selectbox("Workout Type", list(exercise_templates.keys()))
    exercise = st.selectbox("Exercise", exercise_templates[workout_type])
    sets = st.number_input("Sets", min_value=1, max_value=10, value=3)
    reps = st.number_input("Reps", min_value=1, max_value=50, value=10)
    weight = st.number_input("Weight (kg)", min_value=0, max_value=500, value=0)

    if st.button("Save Workout ✅"):
        workout_entry = {
            "date": str(workout_date),
            "type": workout_type,
            "exercise": exercise,
            "sets": sets,
            "reps": reps,
            "weight": weight
        }
        st.session_state.workouts.append(workout_entry)
        save_workouts()
        send_to_n8n(workout_entry)
        st.success("Workout saved successfully!")

# ------------------ PAGE 2: WORKOUT HISTORY ------------------
elif st.session_state.page == "Workout History":
    st.markdown("<h1 class='main-header'>Workout History 📅</h1>", unsafe_allow_html=True)

    st.session_state.workouts = load_workouts()
    if st.session_state.workouts:
        df = pd.DataFrame(st.session_state.workouts)
        st.dataframe(df)
    else:
        st.info("No workouts logged yet.")

# ------------------ PAGE 3: PROGRESS OVERVIEW ------------------
elif st.session_state.page == "Progress Overview":
    st.markdown("<h1 class='main-header'>Progress Overview 📊</h1>", unsafe_allow_html=True)

    st.session_state.workouts = load_workouts()
    if st.session_state.workouts:
        df = pd.DataFrame(st.session_state.workouts)

        # Show personal best per exercise
        st.subheader("🏆 Personal Bests")
        bests = df.groupby("exercise")["weight"].max()
        st.table(bests)

        # Show total workouts logged
        st.subheader("📈 Summary")
        total_workouts = len(df)
        unique_exercises = df["exercise"].nunique()
        st.write(f"**Total Workouts Logged:** {total_workouts}")
        st.write(f"**Unique Exercises:** {unique_exercises}")
    else:
        st.info("No progress to show yet. Log some workouts!")
