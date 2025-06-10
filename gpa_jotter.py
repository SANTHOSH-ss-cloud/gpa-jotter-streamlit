import streamlit as st
import json
import time # We'll use time to generate unique IDs for courses

# --- Page and Style Configuration ---
st.set_page_config(page_title="GPA Jotter", layout="centered")

# Custom CSS to make the semester expanders look better
st.markdown("""
<style>
div[data-testid="stExpander"] summary {
    background-color: #262730 !important;
    color: #FFFFFF !important;
    font-size: 1.1rem !important;
    padding: 1rem !important;
    border-radius: 0.5rem !important;
    border: 1px solid #262730 !important;
}
div[data-testid="stExpander"] summary svg {
    color: #FFFFFF !important;
}
div[data-testid="stExpander"][open] > summary {
    border-bottom-left-radius: 0 !important;
    border-bottom-right-radius: 0 !important;
}
</style>
""", unsafe_allow_html=True)


# --- Grade System ---
GRADE_POINTS = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C+": 5, "C": 4}

# --- Data Migration Function (THE FIX) ---
def ensure_course_ids(data):
    """
    Scans loaded data and adds unique IDs to any courses that are missing them.
    This ensures compatibility with older data files.
    """
    for semester in data:
        if "courses" in semester:
            for course in semester["courses"]:
                if "id" not in course:
                    # Add a unique ID if it doesn't exist
                    course["id"] = time.time()
                    time.sleep(0.01) # Sleep briefly to ensure unique timestamps
    return data

# --- State Management Callbacks ---

# Removed add_semester and delete_semester functions as semesters are fixed.

def add_course(semester_index):
    """Adds a new course with a unique ID to a specific semester."""
    new_course = {
        "id": time.time(), # Unique ID based on the current time
        "name": "",
        "grade": "O",
        "credits": 3
    }
    st.session_state.semesters[semester_index]["courses"].append(new_course)

def delete_course(semester_index, course_id):
    """Deletes a course from a semester by its unique ID."""
    courses = st.session_state.semesters[semester_index]["courses"]
    # Find the course with the matching ID and remove it
    st.session_state.semesters[semester_index]["courses"] = [c for c in courses if c["id"] != course_id]


# --- Calculation Functions ---
def calculate_gpa(courses):
    total_points = 0
    total_credits = 0
    for course in courses:
        grade = course.get("grade")
        credits = int(course.get("credits", 0))
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
            credits = int(course.get("credits", 0))
            if grade in GRADE_POINTS and credits:
                total_points += GRADE_POINTS[grade] * credits
                total_credits += credits
    return round(total_points / total_credits, 2) if total_credits > 0 else 0.0

# --- Main App ---

# Initialize session state if it doesn't exist
if "semesters" not in st.session_state:
    # Initialize with a fixed number of semesters, e.g., 8
    st.session_state.semesters = []
    for i in range(1, 9): # Create 8 fixed semesters
        st.session_state.semesters.append({
            "name": f"Semester {i}",
            "courses": []
        })
        # Optionally, add one default course to each semester
        add_course(i - 1)


# Header
st.markdown("### GPA Jotter")
st.caption("Track your semester and cumulative GPA with ease.")

# Display CGPA
st.markdown(f"### Cumulative GPA (CGPA):  \n<span style='color:green;font-size:38px'>{calculate_cgpa():.2f}</span>", unsafe_allow_html=True)

# --- Top Level Controls (Modified) ---
col1, col2 = st.columns([1, 1])

with col1:
    # Save to file
    st.download_button(
        label="💾 Save",
        data=json.dumps(st.session_state.semesters, indent=4),
        file_name="gpa_data.json",
        mime="application/json",
        use_container_width=True
    )
with col2:
    # --- UPDATED FILE LOADING LOGIC ---
    uploaded_file = st.file_uploader("📂 Load", type=["json"], label_visibility="collapsed")
    if uploaded_file:
        try:
            # Load data from the uploaded file
            loaded_data = json.load(uploaded_file)
            
            # **FIX:** Ensure all courses have an 'id' for backward compatibility
            migrated_data = ensure_course_ids(loaded_data)
            
            # Assign the fixed data to the session state
            st.session_state.semesters = migrated_data
            
            st.rerun() # Rerun to display the loaded data
        except json.JSONDecodeError:
            st.error("Invalid JSON file. Please upload a valid JSON file.")
        except Exception as e:
            st.error(f"An error occurred while loading the file: {e}")


# --- Semester and Course Rendering Loop ---
# Iterate backwards for safe deletion during the loop (still needed for course deletion)
for i in range(len(st.session_state.semesters) - 1, -1, -1):
    semester = st.session_state.semesters[i]
    gpa = calculate_gpa(semester["courses"])

    with st.expander(f"{semester['name']} - GPA: {gpa:.2f}"):
        # Header for the course list
        st.markdown("""
        <div style="display: grid; grid-template-columns: 3fr 2fr 2fr 1fr; gap: 10px; font-weight: bold; margin-bottom: 10px;">
            <div>Course Name</div>
            <div>Grade</div>
            <div>Credits</div>
            <div>Action</div>
        </div>
        """, unsafe_allow_html=True)

        # Loop through courses and create their widgets
        for course in semester["courses"]:
            course_id = course["id"] 
            cols = st.columns([3, 2, 2, 1])
            
            with cols[0]:
                course["name"] = st.text_input(
                    "Course Name", value=course["name"], key=f"name_{course_id}", label_visibility="collapsed"
                )
            with cols[1]:
                course["grade"] = st.selectbox(
                    "Grade", options=GRADE_POINTS.keys(), index=list(GRADE_POINTS.keys()).index(course["grade"]), key=f"grade_{course_id}", label_visibility="collapsed"
                )
            with cols[2]:
                course["credits"] = st.number_input(
                    "Credits", min_value=0, max_value=10, value=int(course["credits"]), key=f"credits_{course_id}", label_visibility="collapsed"
                )
            with cols[3]:
                st.button(
                    "🗑️", key=f"del_{course_id}", on_click=delete_course, args=[i, course_id]
                )

        # Semester-level action buttons (only Add Course remains)
        st.markdown("---")
        st.button("➕ Add Course", key=f"add_course_{i}", on_click=add_course, args=[i])
