import streamlit as st

st.title("🎯 Set and Track Your Recycling Goals")

# Define material types
materials = ["Plastic", "Metal", "Paper", "Cardboard"]

# Initialize session state
for mat in materials:
    st.session_state.setdefault(f"{mat}_goal", 0.0)
    st.session_state.setdefault(f"{mat}_recycled", 0.0)

# User sets goals
st.header("Set Goals by Material")
for mat in materials:
    st.session_state[f"{mat}_goal"] = st.number_input(
        f"Set your {mat} recycling goal (kg):",
        min_value=0.0,
        value=st.session_state[f"{mat}_goal"],
        step=0.1,
        key=f"{mat}_goal_input"
    )

# Simulated update: Replace with model detection later
st.header("Track Your Progress")
for mat in materials:
    st.subheader(f"{mat}")
    
    # This is where your model updates the recycled amount
    st.session_state[f"{mat}_recycled"] = st.slider(
        f"{mat} recycled so far (kg):",
        min_value=0.0,
        max_value=st.session_state[f"{mat}_goal"] if st.session_state[f"{mat}_goal"] > 0 else 100.0,
        value=st.session_state[f"{mat}_recycled"],
        step=0.1,
        key=f"{mat}_recycled_slider"
    )
    
    # Progress bar and status
    goal = st.session_state[f"{mat}_goal"]
    progress = st.session_state[f"{mat}_recycled"]
    
    if goal > 0:
        percent = min(int((progress / goal) * 100), 100)
        st.progress(percent)
        if progress >= goal:
            st.success(f"✅ Goal achieved for {mat}!")
        else:
            st.info(f"{percent}% of your {mat} goal reached.")

# Reset button
if st.button("🔄 Reset All Goals and Progress"):
    for mat in materials:
        st.session_state[f"{mat}_goal"] = 0.0
        st.session_state[f"{mat}_recycled"] = 0.0
    st.success("All recycling goals have been reset.")
