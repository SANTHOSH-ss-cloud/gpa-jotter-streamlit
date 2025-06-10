import streamlit as st
import json

GRADE_POINTS = {
    "O": 10,
    "A+": 9,
    "A": 8,
    "B+": 7,
    "B": 6,
    "C+": 5,
    "C": 4
}

st.set_page_config(page_title="GPA Jotter", layout="centered")
st.title("🧮 GPA Jotter")
st.subheader("Track your semester and cumulative GPA with ease.")

# Session state to hold semesters
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
col1, col2, col3, col4 = st.columns([1,1,1,1])
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
    with st.expander(f"{semester['name']} - GPA: {calculate_gpa(semester['courses'])}"):
        for j, course in enumerate(semester["courses"]):
            cols = st.columns([3, 2, 2, 1])
            with cols[0]:
                course["name"] = st.text_input("Course Name (Optional)", course.get("name", ""), key=f"name_{i}_{j}")
            with cols[1]:
                course["grade"] = st.selectbox("Grade", list(GRADE_POINTS.keys()), index=list(GRADE_POINTS.keys()).index(course.get("grade", "O")), key=f"grade_{i}_{j}")
            with cols[2]:
                course["credits"] = st.number_input("Credits", min_value=1, max_value=10, value=course.get("credits", 3), key=f"credits_{i}_{j}")
            with cols[3]:
                if st.button("🗑️", key=f"del_{i}_{j}"):
                    semester["courses"].pop(j)
                    st.experimental_rerun()

        if st.button("➕ Add Course", key=f"add_course_{i}"):
            semester["courses"].append({"name": "", "grade": "O", "credits": 3})
