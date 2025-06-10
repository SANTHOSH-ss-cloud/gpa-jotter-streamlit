import streamlit as st
import json
import time
import pandas as pd
import io

# --- Page and Style Configuration ---
st.set_page_config(page_title="Calculate Your CGPA", layout="centered")

# Custom CSS (removing the expander specific styles as they won't apply)
st.markdown("""
<style>
/* You can add other general styles here if needed */
/* Removed specific expander styles as we are removing expanders */
</style>
""", unsafe_allow_html=True)


# --- Grade System ---
GRADE_POINTS = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C+": 5, "C": 4, "N/A": 0}

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

def add_semester():
    """Appends a new semester dictionary to the session state."""
    st.session_state.semesters.append({
        "name": f"Semester {len(st.session_state.semesters) + 1}",
        "courses": [] # Start with an empty course list
    })
    # Add one course to the new semester by default
    add_course(len(st.session_state.semesters) - 1)

def delete_semester(semester_index):
    """Deletes a semester at a given index."""
    del st.session_state.semesters[semester_index]

def add_course(semester_index):
    """Adds a new course with a unique ID to a specific semester."""
    new_course = {
        "id": time.time(), # Unique ID based on the current time
        "name": "",
        "grade": "O", # Default grade will still be 'O'
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
            if grade != "N/A":
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
                if grade != "N/A":
                    total_points += GRADE_POINTS[grade] * credits
                total_credits += credits
    return round(total_points / total_credits, 2) if total_credits > 0 else 0.0

# --- File Saving Function for CSV ---
def convert_to_csv(data):
    """
    Converts the semester data from session state into a CSV format.
    Each row will represent a course with its semester details.
    """
    rows = []
    for sem in data:
        semester_name = sem["name"]
        semester_gpa = calculate_gpa(sem["courses"]) # Calculate GPA for each semester
        for course in sem["courses"]:
            rows.append({
                "Semester": semester_name,
                "Semester GPA": semester_gpa,
                "Course Name": course.get("name", ""),
                "Grade": course.get("grade", ""),
                "Credits": course.get("credits", 0)
            })
    
    if not rows:
        return "" # Return empty string if no data

    df = pd.DataFrame(rows)
    # Convert DataFrame to CSV string
    return df.to_csv(index=False)

# --- Main App ---

# Initialize session state if it doesn't exist
if "semesters" not in st.session_state:
    st.session_state.semesters = []

# --- Institute Logo and Name ---
# Create columns for the logo and institute name
logo_col, name_col = st.columns([1, 4]) # Adjust column ratios as needed

with logo_col:
    # Ensure 'rit_logo.png' is in the same directory as your script
    st.image("rit_logo.png", width=100) # Adjust width as needed

with name_col:
    st.markdown("<h1>Rajalakshmi Institute of Technology</h1>", unsafe_allow_html=True)
    st.markdown("---") # Add a horizontal line for separation

# Header
st.markdown("### GPA Jotter") # This is the main display heading within the app
st.caption("Track your semester and cumulative GPA with ease.")

# Display CGPA
st.markdown(f"### Cumulative GPA (CGPA):  \n<span style='color:green;font-size:38px'>{calculate_cgpa():.2f}</span>", unsafe_allow_html=True)

# --- Top Level Controls ---
col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])

with col1:
    st.button("➕ Add Semester", on_click=add_semester, use_container_width=True)

with col2:
    # Save to JSON file (kept as an option)
    st.download_button(
        label="💾 Save (JSON)",
        data=json.dumps(st.session_state.semesters, indent=4),
        file_name="gpa_data.json",
        mime="application/json",
        use_container_width=True
    )

with col3:
    # Save to CSV file
    csv_string = convert_to_csv(st.session_state.semesters)
    st.download_button(
        label="📊 Save (CSV)",
        data=csv_string,
        file_name="gpa_data.csv",
        mime="text/csv",
        use_container_width=True
    )

with col4:
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
if not st.session_state.semesters:
    st.info("Click 'Add Semester' to get started!")

# Iterate backwards for safe deletion during the loop
for i in range(len(st.session_state.semesters) - 1, -1, -1):
    semester = st.session_state.semesters[i]
    gpa = calculate_gpa(semester["courses"])

    st.markdown(f"## {semester['name']} - GPA: {gpa:.2f}")
    st.markdown("---")

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
            current_grade_index = 0
            if course["grade"] in GRADE_POINTS:
                current_grade_index = list(GRADE_POINTS.keys()).index(course["grade"])
            
            course["grade"] = st.selectbox(
                "Grade", options=list(GRADE_POINTS.keys()), index=current_grade_index, key=f"grade_{course_id}", label_visibility="collapsed"
            )
        with cols[2]:
            course["credits"] = st.number_input(
                "Credits", min_value=0, max_value=10, value=int(course["credits"]), key=f"credits_{course_id}", label_visibility="collapsed"
            )
        with cols[3]:
            st.button(
                "🗑️", key=f"del_{course_id}", on_on_click=delete_course, args=[i, course_id]
            )

    # Semester-level action buttons
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.button("➕ Add Course", key=f"add_course_{i}", on_click=add_course, args=[i])
    with c2:
        st.button("❌ Delete Semester", key=f"del_sem_{i}", on_click=delete_semester, args=[i], type="secondary")
    
    st.markdown("<br>", unsafe_allow_html=True)
