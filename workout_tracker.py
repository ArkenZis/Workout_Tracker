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
    }
    .section-header {
        font-size: 2rem;
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    .exercise-card {
        background-color: #f0f2f6;
        padding: 1px;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background-color: #fff;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .nav-button {
        padding: 0.px 1.px;
        background-color: #1f77b4;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 1rem;
        margin: 0.5rem;
        width: 100%;
    }
    .nav-button:hover {
        background-color: #1668a5;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for workout data
if 'workouts' not in st.session_state:
    st.session_state.workouts = {}

if 'current_workout' not in st.session_state:
    st.session_state.current_workout = {}

# Function to send workout data to n8n webhook
def send_to_n8n(workout_data):
    try:
        # Get n8n webhook URL from secrets or use default
        n8n_webhook_url = st.secrets.get("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/webhook/workout")
        
        # Capitalize the first letter of each key in the workout data
        capitalized_data = {}
        for key, value in workout_data.items():
            # Capitalize the first letter of the key
            capitalized_key = key[0].upper() + key[1:] if key else key
            capitalized_data[capitalized_key] = value
        
        # For exercises, we need to capitalize the keys in each exercise as well
        if "Exercises" in capitalized_data:
            capitalized_exercises = {}
            for exercise_name, exercise_details in capitalized_data["Exercises"].items():
                capitalized_exercise = {}
                for detail_key, detail_value in exercise_details.items():
                    capitalized_detail_key = detail_key[0].upper() + detail_key[1:] if detail_key else detail_key
                    capitalized_exercise[capitalized_detail_key] = detail_value
                capitalized_exercises[exercise_name] = capitalized_exercise
            capitalized_data["Exercises"] = capitalized_exercises
        
        # Send data to n8n
        response = requests.post(n8n_webhook_url, json=capitalized_data, timeout=10)
        
        if response.status_code == 200:
            st.success("Workout data sent to n8n successfully!")
            return True
        else:
            st.warning(f"Failed to send data to n8n. Status code: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error sending data to n8n: {str(e)}")
        return False

# Function to save workout data
def save_workout():
    if st.session_state.current_workout:
        date_str = str(date.today())
        st.session_state.workouts[date_str] = st.session_state.current_workout.copy()
        
        # Prepare data for n8n
        workout_data = {
            "date": date_str,
            "type": st.session_state.current_workout.get("type", "Unknown"),
            "exercises": st.session_state.current_workout.get("exercises", {})
        }
        
        # Try to send to n8n
        n8n_success = send_to_n8n(workout_data)
        
        if not n8n_success:
            st.warning("Workout saved locally but could not sync to n8n.")
        
        st.session_state.current_workout = {}
        save_to_file()

# Function to load workout data
def load_workouts():
    try:
        if os.path.exists('workouts.json'):
            with open('workouts.json', 'r') as f:
                st.session_state.workouts = json.load(f)
    except:
        st.session_state.workouts = {}

# Function to save data to file
def save_to_file():
    with open('workouts.json', 'w') as f:
        json.dump(st.session_state.workouts, f)

# Load existing workouts
load_workouts()

# Exercise templates for each workout type
exercise_templates = {
    "Upper Body (Push)": [
        {"name": "Bench Press", "sets": 4, "reps": 8, "weight": 0},
        {"name": "Overhead Press", "sets": 3, "reps": 10, "weight": 0},
        {"name": "Incline Dumbbell Press", "sets": 3, "reps": 12, "weight": 0},
        {"name": "Weighted Dips", "sets": 3, "reps": 10, "weight": 0},
        {"name": "Tricep Rope Pushdown", "sets": 3, "reps": 15, "weight": 0}
    ],
    "Lower Body": [
        {"name": "Back Squat", "sets": 4, "reps": 8, "weight": 0},
        {"name": "Romanian Deadlift", "sets": 3, "reps": 10, "weight": 0},
        {"name": "Walking Lunges", "sets": 3, "reps": 12, "weight": 0},
        {"name": "Leg Press", "sets": 3, "reps": 15, "weight": 0},
        {"name": "Calf Raises", "sets": 4, "reps": 20, "weight": 0}
    ],
    "Upper Body (Pull)": [
        {"name": "Deadlift", "sets": 4, "reps": 5, "weight": 0},
        {"name": "Pull-ups", "sets": 4, "reps": 8, "weight": 0},
        {"name": "Barbell Rows", "sets": 3, "reps": 10, "weight": 0},
        {"name": "Face Pulls", "sets": 3, "reps": 15, "weight": 0},
        {"name": "Bicep Curls", "sets": 3, "reps": 12, "weight": 0}
    ],
    "Lower Body (Secondary)": [
        {"name": "Front Squat or Box Squat", "sets": 4, "reps": 8, "weight": 0},
        {"name": "Good Mornings or Hip Thrusts", "sets": 3, "reps": 10, "weight": 0},
        {"name": "Bulgarian Split Squats", "sets": 3, "reps": 12, "weight": 0},
        {"name": "Glute Ham Raises (or Nordic Curls)", "sets": 3, "reps": 10, "weight": 0},
        {"name": "Farmer's Carry", "sets": 3, "reps": 1, "weight": 0, "distance": "40m"}
    ],
    "Core": [
        {"name": "Plank", "sets": 3, "reps": 1, "time": "60s"},
        {"name": "Russian Twists", "sets": 3, "reps": 20, "weight": 0},
        {"name": "Hanging Leg Raises", "sets": 3, "reps": 12, "weight": 0},
        {"name": "Cable Crunches", "sets": 3, "reps": 15, "weight": 0},
        {"name": "Pallof Press", "sets": 3, "reps": 12, "weight": 0}
    ]
}

# Function to display workout section
def display_workout_section(workout_type):
    st.markdown(f'<h1 class="section-header">{workout_type}</h1>', unsafe_allow_html=True)
    
    # Initialize current workout if not set or if type has changed
    if not st.session_state.current_workout or st.session_state.current_workout.get("type") != workout_type:
        st.session_state.current_workout = {"type": workout_type, "exercises": {}}
    
    # Display exercises
    for exercise in exercise_templates[workout_type]:
        st.markdown('<div class="exercise-card">', unsafe_allow_html=True)
        st.subheader(exercise["name"])
        
        # Create columns for input
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            sets = st.number_input(f"Sets for {exercise['name']}", 
                                  min_value=1, max_value=10, value=exercise["sets"], key=f"{exercise['name']}_sets")
        
        with col2:
            if exercise.get("time"):
                reps = st.text_input(f"Time for {exercise['name']}", value=exercise["time"], key=f"{exercise['name']}_reps")
            elif exercise.get("distance"):
                reps = st.text_input(f"Distance for {exercise['name']}", value=exercise["distance"], key=f"{exercise['name']}_reps")
            else:
                reps = st.number_input(f"Reps for {exercise['name']}", 
                                      min_value=1, max_value=50, value=exercise["reps"], key=f"{exercise['name']}_reps")
        
        with col3:
            if exercise.get("time") or exercise.get("distance"):
                weight = st.text_input(f"Weight for {exercise['name']}", value="Bodyweight", key=f"{exercise['name']}_weight")
            else:
                weight = st.number_input(f"Weight for {exercise['name']} (kg)", 
                                       min_value=0, max_value=300, value=exercise["weight"], key=f"{exercise['name']}_weight")
        
        with col4:
            notes = st.text_input(f"Notes for {exercise['name']}", key=f"{exercise['name']}_notes")
        
        # Store exercise data
        exercise_data = {
            "sets": sets,
            "reps": reps,
            "weight": weight,
            "notes": notes
        }
        
        st.session_state.current_workout["exercises"][exercise["name"]] = exercise_data
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Add custom exercise
    st.markdown("### Add Custom Exercise")
    custom_col1, custom_col2, custom_col3, custom_col4, custom_col5 = st.columns(5)
    
    with custom_col1:
        custom_name = st.text_input("Exercise Name", key="custom_name")
    
    with custom_col2:
        custom_sets = st.number_input("Sets", min_value=1, max_value=10, value=3, key="custom_sets")
    
    with custom_col3:
        custom_reps = st.number_input("Reps", min_value=1, max_value=50, value=10, key="custom_reps")
    
    with custom_col4:
        custom_weight = st.number_input("Weight (kg)", min_value=0, max_value=300, value=0, key="custom_weight")
    
    with custom_col5:
        custom_notes = st.text_input("Notes", key="custom_notes")
    
    if st.button("Add Custom Exercise"):
        if custom_name:
            exercise_data = {
                "sets": custom_sets,
                "reps": custom_reps,
                "weight": custom_weight,
                "notes": custom_notes
            }
            
            st.session_state.current_workout["exercises"][custom_name] = exercise_data
            st.success(f"Added {custom_name} to your workout!")
        else:
            st.error("Please enter an exercise name")
    
    # Save workout button
    if st.button("Save Workout", type="primary"):
        save_workout()

# Function to display progress page
def display_progress_page():
    st.markdown('<h1 class="section-header">Progress & History</h1>', unsafe_allow_html=True)
    
    if not st.session_state.workouts:
        st.info("No workouts recorded yet. Start logging your workouts to see progress here!")
    else:
        # Display workout history
        st.subheader("Workout History")
        
        # Convert to DataFrame for easier display
        history_data = []
        for date_str, workout in st.session_state.workouts.items():
            for exercise, details in workout["exercises"].items():
                history_data.append({
                    "Date": date_str,
                    "Workout Type": workout["type"],
                    "Exercise": exercise,
                    "Sets": details["sets"],
                    "Reps": details["reps"],
                    "Weight": details["weight"],
                    "Notes": details["notes"]
                })
        
        history_df = pd.DataFrame(history_data)
        st.dataframe(history_df, use_container_width=True)
        
        # Progress charts
        st.subheader("Progress Charts")
        
        # Allow user to select exercise to track
        if not history_df.empty:
            exercises = history_df["Exercise"].unique()
            selected_exercise = st.selectbox("Select exercise to track progress", exercises)
            
            # Filter data for selected exercise
            exercise_data = history_df[history_df["Exercise"] == selected_exercise].copy()
            exercise_data["Date": pd.to_datetime(exercise_data["Date"])]
            exercise_data = exercise_data.sort_values("Date")
            
            # Display progress
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**{selected_exercise} Progress**")
                
                # Try to convert weight to numeric for charting
                try:
                    exercise_data["Weight"] = pd.to_numeric(exercise_data["Weight"])
                    st.line_chart(exercise_data, x="Date", y="Weight")
                except:
                    st.info("Weight data is not numeric for this exercise")
            
            with col2:
                st.write("**Recent Performance**")
                st.dataframe(exercise_data[["Date", "Sets", "Reps", "Weight", "Notes"]].tail(5), use_container_width=True)
        
        # Summary statistics
        st.subheader("Summary Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_workouts = len(st.session_state.workouts)
            st.metric("Total Workouts", total_workouts)
        
        with col2:
            workout_types = history_df["Workout Type"].value_counts()
            most_frequent = workout_types.index[0] if not workout_types.empty else "N/A"
            st.metric("Most Frequent Workout", most_frequent)
        
        with col3:
            if not history_df.empty:
                last_workout_date = history_df["Date"].max()
                st.metric("Last Workout", last_workout_date)
            else:
                st.metric("Last Workout", "N/A")

# Main page
def main_page():
    st.markdown('<h1 class="main-header">Workout Tracker</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Workouts", len(st.session_state.workouts))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        # Calculate last workout date
        if st.session_state.workouts:
            last_workout = max([datetime.datetime.strptime(d, '%Y-%m-%d').date() for d in st.session_state.workouts.keys()])
            days_since = (date.today() - last_workout).days
            st.metric("Days Since Last Workout", days_since)
        else:
            st.metric("Days Since Last Workout", "N/A")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Current Week Goal", "4 workouts")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.write("")
    st.write("## Welcome to Your Workout Tracker!")
    st.write("""
    This app helps you track your strength training workouts according to your specified program.
    
    **How to use:**
    1. Navigate to the specific workout section using the buttons below
    2. Enter your exercises, sets, reps, and weights
    3. Save your workout when completed
    4. View your progress and history in the Progress section
    
    **Your workout split:**
    - Upper Body (Push)
    - Lower Body
    - Upper Body (Pull)
    - Lower Body (Secondary)
    - Core
    """)
    
    # Navigation buttons to different pages
    st.write("## Navigate to Workout Section")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Upper Body (Push)", use_container_width=True):
            st.session_state.page = "Upper Body (Push)"
            st.rerun()
        
        if st.button("Lower Body", use_container_width=True):
            st.session_state.page = "Lower Body"
            st.rerun()
    
    with col2:
        if st.button("Upper Body (Pull)", use_container_width=True):
            st.session_state.page = "Upper Body (Pull)"
            st.rerun()
        
        if st.button("Lower Body (Secondary)", use_container_width=True):
            st.session_state.page = "Lower Body (Secondary)"
            st.rerun()
    
    with col3:
        if st.button("Core", use_container_width=True):
            st.session_state.page = "Core"
            st.rerun()
        
        if st.button("Progress & History", use_container_width=True):
            st.session_state.page = "Progress & History"
            st.rerun()

# Initialize page state
if 'page' not in st.session_state:
    st.session_state.page = "Main"

# Display the appropriate page based on navigation
if st.session_state.page == "Main":
    main_page()
elif st.session_state.page == "Upper Body (Push)":
    display_workout_section("Upper Body (Push)")
elif st.session_state.page == "Lower Body":
    display_workout_section("Lower Body")
elif st.session_state.page == "Upper Body (Pull)":
    display_workout_section("Upper Body (Pull)")
elif st.session_state.page == "Lower Body (Secondary)":
    display_workout_section("Lower Body (Secondary)")
elif st.session_state.page == "Core":
    display_workout_section("Core")
elif st.session_state.page == "Progress & History":
    display_progress_page()

# Sidebar with quick navigation
st.sidebar.title("💪 Workout Tracker")
st.sidebar.write("**Quick Navigation**")

if st.sidebar.button("Home"):
    st.session_state.page = "Main"
    st.rerun()

st.sidebar.write("**Workout Sections**")
if st.sidebar.button("Upper Body (Push)"):
    st.session_state.page = "Upper Body (Push)"
    st.rerun()

if st.sidebar.button("Lower Body"):
    st.session_state.page = "Lower Body"
    st.rerun()

if st.sidebar.button("Upper Body (Pull)"):
    st.session_state.page = "Upper Body (Pull)"
    st.rerun()

if st.sidebar.button("Lower Body (Secondary)"):
    st.session_state.page = "Lower Body (Secondary)"
    st.rerun()

if st.sidebar.button("Core"):
    st.session_state.page = "Core"
    st.rerun()

st.sidebar.write("**Progress**")
if st.sidebar.button("Progress & History"):
    st.session_state.page = "Progress & History"
    st.rerun()

# Display current workout status in sidebar
st.sidebar.write("---")
st.sidebar.write("**Current Workout**")
if st.session_state.current_workout:
    st.sidebar.write(f"Type: {st.session_state.current_workout.get('type', 'None')}")
    st.sidebar.write(f"Exercises: {len(st.session_state.current_workout.get('exercises', {}))}")
else:
    st.sidebar.write("No active workout")

# n8n integration info in sidebar
st.sidebar.write("---")
st.sidebar.write("**n8n Integration**")
st.sidebar.info("Workouts are automatically sent to n8n for processing")