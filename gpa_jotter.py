import streamlit as st
import json
import time
import pandas as pd
import fitz  # PyMuPDF for PDF extraction

# --- Streamlit Page Config ---
st.set_page_config(page_title="Calculate Your CGPA", layout="centered")

# --- Grade Points ---
GRADE_POINTS = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C+": 5, "C": 4, "N/A": 0}

# --- Utility Functions ---
def ensure_course_ids(data):
    for semester in data:
        if "courses" in semester:
            for course in semester["courses"]:
                if "id" not in course:
                    course["id"] = time.time()
                    time.sleep(0.01)
    return data

def calculate_gpa(courses):
    total_points, total_credits = 0, 0
    for course in courses:
        grade = course.get("grade")
        credits = int(course.get("credits", 0))
        if grade in GRADE_POINTS and credits:
            if grade != "N/A":
                total_points += GRADE_POINTS[grade] * credits
            total_credits += credits
    return round(total_points / total_credits, 2) if total_credits > 0 else 0.0

def calculate_cgpa():
    total_points, total_credits = 0, 0
    for sem in st.session_state.semesters:
        for course in sem["courses"]:
            grade = course.get("grade")
            credits = int(course.get("credits", 0))
            if grade in GRADE_POINTS and credits:
                if grade != "N/A":
                    total_points += GRADE_POINTS[grade] * credits
                total_credits += credits
    return round(total_points / total_credits, 2) if total_credits > 0 else 0.0

def convert_to_csv(data):
    rows = []
    for sem in data:
        semester_name = sem["name"]
        semester_gpa = calculate_gpa(sem["courses"])
        for course in sem["courses"]:
            rows.append({
                "Semester": semester_name,
                "Semester GPA": semester_gpa,
                "Course Name": course.get("name", ""),
                "Grade": course.get("grade", ""),
                "Credits": course.get("credits", 0)
            })
    if not rows:
        return ""
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)

# --- New: Extract from PDF ---
def extract_courses_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    lines = text.splitlines()
    courses = []
    for line in lines:
        if any(code in line for code in ["EC", "GE", "HS", "MA", "PH"]):
            parts = line.strip().split()
            if len(parts) >= 3:
                code = parts[0]
                grade = parts[-2]
                name = " ".join(parts[1:-2])
                if grade in GRADE_POINTS:
                    courses.append({
                        "id": time.time(),
                        "name": name,
                        "grade": grade,
                        "credits": 3  # default to 3 credits
                    })
                    time.sleep(0.01)
    return {
        "name": f"Semester {len(st.session_state.semesters) + 1}",
        "courses": courses
    }

# --- State Initialization ---
if "semesters" not in st.session_state:
    st.session_state.semesters = []

# --- Header ---
st.markdown("### GPA Jotter")
st.caption("Track your semester and cumulative GPA with ease.")
st.markdown(f"### Cumulative GPA (CGPA):  \n<span style='color:green;font-size:38px'>{calculate_cgpa():.2f}</span>", unsafe_allow_html=True)

# --- Top Level Controls ---
col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])
with col1:
    def add_semester():
        st.session_state.semesters.append({
            "name": f"Semester {len(st.session_state.semesters) + 1}",
            "courses": []
        })
        add_course(len(st.session_state.semesters) - 1)
    st.button("➕ Add Semester", on_click=add_semester, use_container_width=True)

with col2:
    st.download_button(
        label="💾 Save (JSON)",
        data=json.dumps(st.session_state.semesters, indent=4),
        file_name="gpa_data.json",
        mime="application/json",
        use_container_width=True
    )

with col3:
    csv_string = convert_to_csv(st.session_state.semesters)
    st.download_button(
        label="📊 Save (CSV)",
        data=csv_string,
        file_name="gpa_data.csv",
        mime="text/csv",
        use_container_width=True
    )

with col4:
    uploaded_json = st.file_uploader("📂 Load JSON", type=["json"], label_visibility="collapsed")
    if uploaded_json:
        try:
            loaded_data = json.load(uploaded_json)
            migrated_data = ensure_course_ids(loaded_data)
            st.session_state.semesters = migrated_data
            st.rerun()
        except Exception as e:
            st.error(f"Error loading JSON: {e}")

# --- New Section: Upload Multiple PDFs ---
uploaded_pdfs = st.file_uploader("📥 Upload Result PDFs", type="pdf", accept_multiple_files=True)
if uploaded_pdfs:
    for pdf_file in uploaded_pdfs:
        try:
            sem_data = extract_courses_from_pdf(pdf_file)
            if sem_data["courses"]:
                st.session_state.semesters.append(sem_data)
                st.success(f"✅ Added {len(sem_data['courses'])} courses from {pdf_file.name}")
            else:
                st.warning(f"⚠️ No valid courses found in {pdf_file.name}")
        except Exception as e:
            st.error(f"❌ Failed to process {pdf_file.name}: {e}")

# --- Course and Semester UI ---
def add_course(semester_index):
    new_course = {
        "id": time.time(),
        "name": "",
        "grade": "O",
        "credits": 3
    }
    st.session_state.semesters[semester_index]["courses"].append(new_course)

def delete_course(semester_index, course_id):
    st.session_state.semesters[semester_index]["courses"] = [
        c for c in st.session_state.semesters[semester_index]["courses"] if c["id"] != course_id
    ]

def delete_semester(semester_index):
    del st.session_state.semesters[semester_index]

if not st.session_state.semesters:
    st.info("Click 'Add Semester' or upload PDFs to get started!")

for i in range(len(st.session_state.semesters) - 1, -1, -1):
    semester = st.session_state.semesters[i]
    gpa = calculate_gpa(semester["courses"])
    st.markdown(f"## {semester['name']} - GPA: {gpa:.2f}")
    st.markdown("---")

    st.markdown("""
    <div style="display: grid; grid-template-columns: 3fr 2fr 2fr 1fr; gap: 10px; font-weight: bold;">
        <div>Course Name</div><div>Grade</div><div>Credits</div><div>Action</div>
    </div>""", unsafe_allow_html=True)

    for course in semester["courses"]:
        course_id = course["id"]
        cols = st.columns([3, 2, 2, 1])
        with cols[0]:
            course["name"] = st.text_input("Course Name", value=course["name"], key=f"name_{course_id}", label_visibility="collapsed")
        with cols[1]:
            current_grade_index = list(GRADE_POINTS.keys()).index(course["grade"]) if course["grade"] in GRADE_POINTS else 0
            course["grade"] = st.selectbox("Grade", options=list(GRADE_POINTS.keys()), index=current_grade_index, key=f"grade_{course_id}", label_visibility="collapsed")
        with cols[2]:
            course["credits"] = st.number_input("Credits", min_value=0, max_value=10, value=int(course["credits"]), key=f"credits_{course_id}", label_visibility="collapsed")
        with cols[3]:
            st.button("🗑️", key=f"del_{course_id}", on_click=delete_course, args=[i, course_id])

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.button("➕ Add Course", key=f"add_course_{i}", on_click=add_course, args=[i])
    with c2:
        st.button("❌ Delete Semester", key=f"del_sem_{i}", on_click=delete_semester, args=[i], type="secondary")
    st.markdown("<br>", unsafe_allow_html=True)
