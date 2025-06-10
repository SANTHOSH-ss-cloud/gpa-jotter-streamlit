document.addEventListener('DOMContentLoaded', () => {
    // --- Grade System ---
    const GRADE_POINTS = { "O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C+": 5, "C": 4 };

    // --- DOM Elements ---
    const cgpaValueEl = document.getElementById('cgpa-value');
    const semestersContainer = document.getElementById('semesters-container');
    const addSemesterBtn = document.getElementById('add-semester-btn');
    const saveFileBtn = document.getElementById('save-file-btn');
    const loadFileInput = document.getElementById('load-file-input');
    const resetBtn = document.getElementById('reset-btn');

    // --- State ---
    let semesters = [];

    // --- Calculation Functions ---
    const calculateGPA = (courses) => {
        let totalPoints = 0;
        let totalCredits = 0;
        courses.forEach(course => {
            if (course.grade && course.credits > 0) {
                totalPoints += GRADE_POINTS[course.grade] * course.credits;
                totalCredits += course.credits;
            }
        });
        return totalCredits > 0 ? (totalPoints / totalCredits).toFixed(2) : '0.00';
    };

    const calculateCGPA = () => {
        let totalPoints = 0;
        let totalCredits = 0;
        semesters.forEach(sem => {
            sem.courses.forEach(course => {
                if (course.grade && course.credits > 0) {
                    totalPoints += GRADE_POINTS[course.grade] * course.credits;
                    totalCredits += course.credits;
                }
            });
        });
        return totalCredits > 0 ? (totalPoints / totalCredits).toFixed(2) : '0.00';
    };

    // --- Rendering Function ---
    const render = () => {
        semestersContainer.innerHTML = ''; // Clear existing content
        semesters.forEach((semester, semIndex) => {
            const gpa = calculateGPA(semester.courses);

            // Create Semester Element
            const semesterDetails = document.createElement('details');
            semesterDetails.className = 'semester-details';
            semesterDetails.open = true;

            // Semester Header (Summary)
            semesterDetails.innerHTML = `
                <summary class="semester-summary">
                    <span class="summary-content">Semester ${semIndex + 1} - GPA: ${gpa}</span>
                    <div class="semester-controls">
                        <button class="delete-semester-btn" data-sem-index="${semIndex}" title="Delete Semester"><i class="fas fa-trash-alt"></i></button>
                    </div>
                </summary>
                <div class="courses-container" data-sem-index="${semIndex}">
                    ${semester.courses.map((course, courseIndex) => `
                        <div class="course-row">
                            <input type="text" class="course-name" placeholder="Course Name" value="${course.name}" data-sem-index="${semIndex}" data-course-index="${courseIndex}">
                            <select class="course-grade" data-sem-index="${semIndex}" data-course-index="${courseIndex}">
                                ${Object.keys(GRADE_POINTS).map(grade => `<option value="${grade}" ${course.grade === grade ? 'selected' : ''}>${grade}</option>`).join('')}
                            </select>
                            <input type="number" class="course-credits" min="0" max="10" value="${course.credits}" data-sem-index="${semIndex}" data-course-index="${courseIndex}">
                            <div class="delete-course-btn-container">
                               <button class="delete-course-btn danger" data-sem-index="${semIndex}" data-course-index="${courseIndex}" title="Delete Course"><i class="fas fa-times-circle"></i></button>
                            </div>
                        </div>
                    `).join('')}
                    <button class="add-course-btn" data-sem-index="${semIndex}"><i class="fas fa-plus"></i> Add Course</button>
                </div>
            `;
            semestersContainer.appendChild(semesterDetails);
        });
        cgpaValueEl.textContent = calculateCGPA();
        saveToLocalStorage();
    };

    // --- Event Handlers ---
    const addSemester = () => {
        semesters.push({ courses: [{ name: '', grade: 'O', credits: 3 }] });
        render();
    };
    
    const addCourse = (semIndex) => {
        semesters[semIndex].courses.push({ name: '', grade: 'O', credits: 3 });
        render();
    };

    const deleteSemester = (semIndex) => {
        semesters.splice(semIndex, 1);
        render();
    };
    
    const deleteCourse = (semIndex, courseIndex) => {
        semesters[semIndex].courses.splice(courseIndex, 1);
        render();
    };

    const updateCourse = (semIndex, courseIndex, field, value) => {
        semesters[semIndex].courses[courseIndex][field] = value;
        // Credits must be a number
        if (field === 'credits') {
            semesters[semIndex].courses[courseIndex][field] = parseInt(value, 10) || 0;
        }
        render();
    };

    const resetAll = () => {
        if (confirm('Are you sure you want to reset all data? This cannot be undone.')) {
            semesters = [];
            render();
        }
    };
    
    const saveDataToFile = () => {
        const dataStr = JSON.stringify(semesters, null, 4);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'gpa_data.json';
        link.click();
        URL.revokeObjectURL(url);
    };

    const loadDataFromFile = (event) => {
        const file = event.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                if (Array.isArray(data)) { // Basic validation
                    semesters = data;
                    render();
                }
            } catch (error) {
                alert('Error parsing file. Please make sure it is a valid JSON file.');
            }
        };
        reader.readAsText(file);
    };

    // --- Local Storage for Persistence ---
    const saveToLocalStorage = () => {
        localStorage.setItem('gpaJotterData', JSON.stringify(semesters));
    };

    const loadFromLocalStorage = () => {
        const data = localStorage.getItem('gpaJotterData');
        if (data) {
            semesters = JSON.parse(data);
        }
    };
    
    // --- Event Listeners ---
    addSemesterBtn.addEventListener('click', addSemester);
    resetBtn.addEventListener('click', resetAll);
    saveFileBtn.addEventListener('click', saveDataToFile);
    loadFileInput.addEventListener('change', loadDataFromFile);

    semestersContainer.addEventListener('click', (e) => {
        const target = e.target.closest('button');
        if (!target) return;
        
        const semIndex = target.dataset.semIndex;
        if (target.classList.contains('add-course-btn')) {
            addCourse(parseInt(semIndex));
        }
        if (target.classList.contains('delete-semester-btn')) {
            deleteSemester(parseInt(semIndex));
        }
        if (target.classList.contains('delete-course-btn')) {
            const courseIndex = target.dataset.courseIndex;
            deleteCourse(parseInt(semIndex), parseInt(courseIndex));
        }
    });

    semestersContainer.addEventListener('input', (e) => {
        const semIndex = parseInt(e.target.dataset.semIndex);
        const courseIndex = parseInt(e.target.dataset.courseIndex);

        if (e.target.classList.contains('course-name')) {
            updateCourse(semIndex, courseIndex, 'name', e.target.value);
        } else if (e.target.classList.contains('course-grade')) {
            updateCourse(semIndex, courseIndex, 'grade', e.target.value);
        } else if (e.target.classList.contains('course-credits')) {
            updateCourse(semIndex, courseIndex, 'credits', e.target.value);
        }
    });

    // --- Initial Load ---
    loadFromLocalStorage();
    render();
});
