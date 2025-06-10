import streamlit as st
import json
from PIL import Image

st.set_page_config(page_title="GPA Jotter", layout="centered")

# Load and display logo
logo = Image.open("rit_logo.png")
st.image(logo, width=80)
st.markdown("<h2 style='color:#1E3A8A;margin-bottom:0'>Rajalakshmi Institute of Technology</h2>", unsafe_allow_html=True)
st.markdown("### GPA Jotter")
st.caption("Track your semester and cumulative GPA with ease.")

# Grade system
GRADE_POINTS = {
    "O": 10,
    "A+": 9,
    "A": 8,
    "B+": 7,
    "B": 6,
    "C+": 5,
    "C": 4
}

# Configure Streamlit page

# Initialize session state
if "semesters" not in st.session_state:
    st.session_state.semesters = []

if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

def calculate_gpa(courses):
    total_points = 0
    total_credits = 0
    for course in courses:
        grade = course.get("grade")
        credits = course.get("credits", 0)
        if grade in GRADE_POINTS and credits:
            total_points += GRADE_POINTS[grade] * credits
            total_credits += credits
    return round(total_points / total_credits, 2) if total_credits > 0 else 0.0

def calculate_cgpa():
    total_points = 0
    total_credits = 0
    for sem in st.session_state.semesters:
        for course in sem["courses"]:
            grade = course.get("grade")
            credits = course.get("credits", 0)
            if grade in GRADE_POINTS and credits:
                total_points += GRADE_POINTS[grade] * credits
                total_credits += credits
    return round(total_points / total_credits, 2) if total_credits > 0 else 0.0

# Display CGPA
st.markdown(f"### Cumulative GPA (CGPA):  \n<span style='color:green;font-size:38px'>{calculate_cgpa():.2f}</span>", unsafe_allow_html=True)

# Control buttons
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("➕ Add Semester"):
        st.session_state.semesters.append({"name": f"Semester {len(st.session_state.semesters) + 1}", "courses": []})

with col2:
    if st.download_button("💾 Save to File", json.dumps(st.session_state.semesters), file_name="gpa_data.json"):
        st.success("Saved successfully!")

with col3:
    uploaded_file = st.file_uploader("📂 Load from File", type=["json"])
    if uploaded_file and not st.session_state.data_loaded:
        st.session_state.semesters = json.load(uploaded_file)
        st.session_state.data_loaded = True
        st.experimental_rerun()

with col4:
    if st.button("🔁 Reset All Data"):
        st.session_state.semesters = []
        st.experimental_rerun()

# Semester & course inputs
for i, semester in enumerate(st.session_state.semesters):
    gpa = calculate_gpa(semester['courses'])
    with st.expander(f"{semester['name']} - GPA: {gpa}"):
        new_courses = []
        for j, course in enumerate(semester["courses"]):
            cols = st.columns([3, 2, 2, 1])
            with cols[0]:
                name = st.text_input("Course Name", course.get("name", ""), key=f"name_{i}_{j}")
            with cols[1]:
                grade = st.selectbox("Grade", list(GRADE_POINTS.keys()), index=list(GRADE_POINTS.keys()).index(course.get("grade", "O")), key=f"grade_{i}_{j}")
            with cols[2]:
                credits = st.number_input("Credits", min_value=1, max_value=10, value=course.get("credits", 3), key=f"credits_{i}_{j}")
            with cols[3]:
                if st.button("🗑️", key=f"delete_{i}_{j}"):
                    continue  # Skip adding this course (delete)
            new_courses.append({"name": name, "grade": grade, "credits": credits})

        st.session_state.semesters[i]["courses"] = new_courses

        if st.button("➕ Add Course", key=f"add_course_{i}"):
            semester["courses"].append({"name": "", "grade": "O", "credits": 3})
            st.experimental_rerun()
