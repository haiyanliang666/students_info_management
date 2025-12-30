import streamlit as st
import pandas as pd
import io
import sqlite3
from datetime import datetime

# --- DATABASE SETUP (Same as before) ---
def get_connection():
    return sqlite3.connect('school.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                sid TEXT PRIMARY KEY, name TEXT, school TEXT, grade TEXT, 
                p_contact TEXT, s_contact TEXT, math_score REAL, chi_score REAL, status TEXT DEFAULT 'Active')''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, sid TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, sid TEXT, change_type TEXT, notes TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS courses (
                course_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                course_name TEXT, 
                teacher TEXT, 
                schedule TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                sid TEXT, 
                course_id INTEGER,
                FOREIGN KEY (sid) REFERENCES students (sid),
                FOREIGN KEY (course_id) REFERENCES courses (course_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS exam_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                sid TEXT, 
                exam_name TEXT, 
                date TEXT, 
                subject TEXT, 
                score REAL,
                FOREIGN KEY (sid) REFERENCES students (sid))''')
    conn.commit()
    conn.close()

init_db()

# --- PAGE CONFIG ---
st.set_page_config(page_title="School System", layout="wide")

# Custom CSS to make the interface cleaner
st.markdown("""
    <style>
    .main {
        padding-top: 0rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        font-weight: bold;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏫 Afterschool Management System")

# --- TOP NAVIGATION BAR (Using Tabs) ---
# We create 5 main categories at the top
tab_info, tab_enroll, tab_tracking, tab_attendance, tab_analytics = st.tabs([
    "👤 Student Info", 
    "📚 Enrollment", 
    "🔄 Tracking", 
    "📅 Attendance", 
    "📊 Analytics"
])

# # --- MODULE 1: STUDENT INFO ---
# with tab_info:
#     # Use a dropdown at the top of the page for features
#     sub_feature = st.selectbox("Select Action:", ["View Student List", "Add New Student", "Bulk Import/Export"], key="info_box")
#     st.divider()

#     if sub_feature == "View Student List":
#         conn = get_connection()
#         df = pd.read_sql("SELECT * FROM students", conn)
#         conn.close()
#         if not df.empty:
#             search = st.text_input("Search Name/ID")
#             if search:
#                 df = df[df['name'].str.contains(search, case=False) | df['sid'].str.contains(search)]
#             st.dataframe(df, use_container_width=True)
#         else:
#             st.info("No data found.")

#     elif sub_feature == "Add New Student":
#         with st.form("add_form", clear_on_submit=True):
#             col1, col2 = st.columns(2)
#             with col1:
#                 sid = st.text_input("Student ID")
#                 name = st.text_input("Name")
#                 school = st.text_input("School")
#                 grade = st.selectbox("Grade", ["G1", "G2", "G3", "G4", "G5", "G6"])
#             with col2:
#                 p_contact = st.text_input("Parent Contact")
#                 s_contact = st.text_input("School Contact")
#                 m_score = st.number_input("Math", 0, 100)
#                 c_score = st.number_input("Chinese", 0, 100)
#             if st.form_submit_button("Save Student"):
#                 try:
#                     conn = get_connection()
#                     conn.execute("INSERT INTO students VALUES (?,?,?,?,?,?,?,?,?)", 
#                                  (sid, name, school, grade, p_contact, s_contact, m_score, c_score, 'Active'))
#                     conn.commit()
#                     conn.close()
#                     st.success("Saved!")
#                 except Exception as e:
#                     st.error(f"Error: {e}")

#     elif sub_feature == "Bulk Import/Export":
#         col_ex, col_im = st.columns(2)
#         with col_ex:
#             st.write("### Export")
#             conn = get_connection()
#             df_all = pd.read_sql("SELECT * FROM students", conn)
#             conn.close()
#             output = io.BytesIO()
#             with pd.ExcelWriter(output, engine='openpyxl') as writer:
#                 df_all.to_excel(writer, index=False)
#             st.download_button("Download Excel", output.getvalue(), "students.xlsx")
#         with col_im:
#             st.write("### Import")
#             up = st.file_uploader("Upload Excel", type=["xlsx"])
#             if up and st.button("Confirm"):
#                 import_df = pd.read_excel(up)
#                 conn = get_connection()
#                 import_df.to_sql('students', conn, if_exists='append', index=False)
#                 conn.commit()
#                 conn.close()
#                 st.success("Imported!")

# --- MODULE 1: STUDENT INFO ---
with tab_info:
    # Added "Manage (Edit/Delete)" to the list
    sub_feature = st.selectbox("Select Action:", 
                               ["View Student List", "Add New Student", "Manage (Edit/Delete)", "Bulk Import/Export"], 
                               key="info_box")
    st.divider()

    # 1. VIEW LIST
    if sub_feature == "View Student List":
        conn = get_connection()
        df = pd.read_sql("SELECT * FROM students", conn)
        conn.close()
        if not df.empty:
            search = st.text_input("Search Name/ID")
            if search:
                df = df[df['name'].str.contains(search, case=False) | df['sid'].str.contains(search)]
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No data found.")

    # 2. ADD STUDENT
    elif sub_feature == "Add New Student":
        with st.form("add_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                sid = st.text_input("Student ID")
                name = st.text_input("Name")
                school = st.text_input("School")
                grade = st.selectbox("Grade", ["G1", "G2", "G3", "G4", "G5", "G6"])
            with col2:
                p_contact = st.text_input("Parent Contact")
                s_contact = st.text_input("School Contact")
                m_score = st.number_input("Math", 0, 100)
                c_score = st.number_input("Chinese", 0, 100)
            
            if st.form_submit_button("Save Student"):
                try:
                    conn = get_connection()
                    conn.execute("INSERT INTO students VALUES (?,?,?,?,?,?,?,?,?)", 
                                 (sid, name, school, grade, p_contact, s_contact, m_score, c_score, 'Active'))
                    conn.commit()
                    conn.close()
                    st.success("Saved!")
                except sqlite3.IntegrityError:
                    st.error("Error: Student ID already exists.")
                except Exception as e:
                    st.error(f"Error: {e}")

    # 3. MANAGE (EDIT / DELETE) - NEW FEATURE
    elif sub_feature == "Manage (Edit/Delete)":
        conn = get_connection()
        students = pd.read_sql("SELECT sid, name FROM students", conn)
        conn.close()

        if not students.empty:
            # Dropdown to select student
            selected_student = st.selectbox("Select Student to Manage", 
                                            students.apply(lambda x: f"{x['sid']} - {x['name']}", axis=1))
            
            # Extract ID from selection
            target_sid = selected_student.split(" - ")[0]

            # Fetch current details
            conn = get_connection()
            curr_data = pd.read_sql(f"SELECT * FROM students WHERE sid = '{target_sid}'", conn).iloc[0]
            conn.close()

            # Create Tabs for Edit vs Delete
            t_edit, t_delete = st.tabs(["✏️ Edit Information", "🗑️ Delete Student"])

            # --- EDIT TAB ---
            with t_edit:
                with st.form("edit_form"):
                    c1, c2 = st.columns(2)
                    with c1:
                        # Disable ID editing to prevent database errors
                        st.text_input("Student ID (Cannot be changed)", value=curr_data['sid'], disabled=True)
                        new_name = st.text_input("Name", value=curr_data['name'])
                        new_school = st.text_input("School", value=curr_data['school'])
                        new_grade = st.selectbox("Grade", ["G1", "G2", "G3", "G4", "G5", "G6"], 
                                                 index=["G1", "G2", "G3", "G4", "G5", "G6"].index(curr_data['grade']))
                    with c2:
                        new_p_con = st.text_input("Parent Contact", value=curr_data['p_contact'])
                        new_s_con = st.text_input("School Contact", value=curr_data['s_contact'])
                        new_m = st.number_input("Math", 0, 100, int(curr_data['math_score']))
                        new_c = st.number_input("Chinese", 0, 100, int(curr_data['chi_score']))
                    
                    if st.form_submit_button("Update Profile"):
                        conn = get_connection()
                        conn.execute('''UPDATE students SET 
                                        name=?, school=?, grade=?, p_contact=?, s_contact=?, math_score=?, chi_score=? 
                                        WHERE sid=?''', 
                                     (new_name, new_school, new_grade, new_p_con, new_s_con, new_m, new_c, target_sid))
                        conn.commit()
                        conn.close()
                        st.success(f"Profile for {new_name} updated successfully!")

            # --- DELETE TAB ---
            with t_delete:
                st.error("⚠️ Danger Zone")
                st.write(f"Are you sure you want to permanently delete **{curr_data['name']}**?")
                st.write("This will also remove their enrollment records.")
                
                if st.button("Yes, Delete Permanently", type="primary"):
                    conn = get_connection()
                    # Delete from Students table
                    conn.execute("DELETE FROM students WHERE sid = ?", (target_sid,))
                    # Clean up Enrollment table (Optional but recommended)
                    conn.execute("DELETE FROM enrollments WHERE sid = ?", (target_sid,))
                    # Clean up Attendance table (Optional)
                    conn.execute("DELETE FROM attendance WHERE sid = ?", (target_sid,))
                    
                    conn.commit()
                    conn.close()
                    st.success("Student deleted.")
                    st.rerun() # Refresh app to update list

        else:
            st.warning("No students available to manage.")

    # 4. EXPORT / IMPORT
    elif sub_feature == "Bulk Import/Export":
        col_ex, col_im = st.columns(2)
        with col_ex:
            st.write("### Export")
            conn = get_connection()
            df_all = pd.read_sql("SELECT * FROM students", conn)
            conn.close()
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_all.to_excel(writer, index=False)
            st.download_button("Download Excel", output.getvalue(), "students.xlsx")
        with col_im:
            st.write("### Import")
            up = st.file_uploader("Upload Excel", type=["xlsx"])
            if up and st.button("Confirm"):
                import_df = pd.read_excel(up)
                conn = get_connection()
                import_df.to_sql('students', conn, if_exists='append', index=False)
                conn.commit()
                conn.close()
                st.success("Imported!")

# --- MODULE 2: ENROLLMENT & COURSES ---
with tab_enroll:
    enroll_feature = st.selectbox("Action:", ["Class Rosters", "Assign Students to Class", "Manage Course List"])
    st.divider()

    if enroll_feature == "Manage Course List":
        st.subheader("Add/Edit Courses")
        with st.form("add_course"):
            c_name = st.text_input("Course Name (e.g., Math Advanced)")
            t_name = st.text_input("Teacher Name")
            sched = st.text_input("Schedule (e.g., Mon/Wed 4pm)")
            if st.form_submit_button("Create Course"):
                conn = get_connection()
                conn.execute("INSERT INTO courses (course_name, teacher, schedule) VALUES (?,?,?)", 
                             (c_name, t_name, sched))
                conn.commit()
                conn.close()
                st.success(f"Course '{c_name}' created!")

    elif enroll_feature == "Assign Students to Class":
        st.subheader("Enroll Student in a Course")
        conn = get_connection()
        # Get list of students and courses for dropdowns
        stu_df = pd.read_sql("SELECT sid, name FROM students WHERE status='Active'", conn)
        crs_df = pd.read_sql("SELECT course_id, course_name FROM courses", conn)
        conn.close()

        if not stu_df.empty and not crs_df.empty:
            with st.form("enroll_form"):
                selected_stu = st.selectbox("Select Student", 
                                            stu_df.apply(lambda x: f"{x['sid']} - {x['name']}", axis=1))
                selected_crs = st.selectbox("Select Course", 
                                            crs_df.apply(lambda x: f"{x['course_id']} - {x['course_name']}", axis=1))
                
                if st.form_submit_button("Confirm Enrollment"):
                    s_id = selected_stu.split(" - ")[0]
                    c_id = selected_crs.split(" - ")[0]
                    conn = get_connection()
                    conn.execute("INSERT INTO enrollments (sid, course_id) VALUES (?,?)", (s_id, c_id))
                    conn.commit()
                    conn.close()
                    st.success("Student successfully enrolled!")
        else:
            st.warning("Ensure you have created both Students and Courses first.")

    elif enroll_feature == "Class Rosters":
        st.subheader("View Students by Course")
        conn = get_connection()
        crs_df = pd.read_sql("SELECT * FROM courses", conn)
        
        if not crs_df.empty:
            target_crs = st.selectbox("Choose a Course to View Roster", 
                                      crs_df.apply(lambda x: f"{x['course_id']} - {x['course_name']}", axis=1))
            c_id = target_crs.split(" - ")[0]
            
            # Complex SQL Join to get student names for the specific course
            query = f'''
                SELECT s.sid, s.name, s.grade, s.p_contact 
                FROM students s
                JOIN enrollments e ON s.sid = e.sid
                WHERE e.course_id = {c_id}
            '''
            roster_df = pd.read_sql(query, conn)
            conn.close()
            
            if not roster_df.empty:
                st.write(f"**Total Students:** {len(roster_df)}")
                st.dataframe(roster_df, use_container_width=True)
            else:
                st.info("No students enrolled in this course yet.")
        else:
            conn.close()
            st.info("No courses created yet.")

# --- MODULE 3: TRACKING ---
with tab_tracking:
    st.subheader("Status Management")
    conn = get_connection()
    students_list = pd.read_sql("SELECT sid, name FROM students", conn)
    conn.close()

    with st.form("status_update"):
        target = st.selectbox("Select Student", students_list['sid'].tolist() if not students_list.empty else [])
        stat = st.selectbox("New Status", ["Active", "Leave", "Transferred", "Graduated"])
        if st.form_submit_button("Update Status"):
            conn = get_connection()
            conn.execute("UPDATE students SET status = ? WHERE sid = ?", (stat, target))
            conn.commit()
            conn.close()
            st.success("Status Updated.")

# --- MODULE 4: ATTENDANCE ---
with tab_attendance:
    st.subheader("Daily Attendance Sheet")
    date = st.date_input("Date", datetime.now())
    conn = get_connection()
    df_active = pd.read_sql("SELECT sid, name FROM students WHERE status='Active'", conn)
    conn.close()

    if not df_active.empty:
        att_df = df_active.copy()
        att_df['Status'] = "Present"
        edited = st.data_editor(att_df, use_container_width=True)
        if st.button("Submit Attendance"):
            conn = get_connection()
            for _, row in edited.iterrows():
                conn.execute("INSERT INTO attendance (date, sid, status) VALUES (?,?,?)",
                            (date.strftime("%Y-%m-%d"), row['sid'], row['Status']))
            conn.commit()
            conn.close()
            st.success("Attendance recorded.")

# --- MODULE 5: ANALYTICS ---
# --- MODULE 5: ANALYTICS ---
with tab_analytics:
    st.subheader("Performance Analytics")
    
    # Toggle between All Students vs Single Student
    view_mode = st.radio("Select View Mode:", ["Overview (All Students)", "Individual Progress (Trend)"], horizontal=True)
    st.divider()

    conn = get_connection()

    # --- VIEW 1: ALL STUDENTS (Separated Bar Charts) ---
    if view_mode == "Overview (All Students)":
        # We fetch the current/latest scores from the main students table
        df = pd.read_sql("SELECT name, math_score, chi_score FROM students", conn)
        
        if not df.empty:
            col_math, col_chi = st.columns(2)
            
            with col_math:
                st.markdown("### 🧮 Math Scores")
                # Create a clean dataframe for the chart
                df_math = df[['name', 'math_score']].set_index('name')
                st.bar_chart(df_math, color="#4A90E2") # Blue color
            
            with col_chi:
                st.markdown("### 📖 Chinese Scores")
                df_chi = df[['name', 'chi_score']].set_index('name')
                st.bar_chart(df_chi, color="#E24A4A") # Red color
        else:
            st.info("No student data available.")

    # --- VIEW 2: INDIVIDUAL PROGRESS (Trend Line) ---
    elif view_mode == "Individual Progress (Trend)":
        # 1. Select Student
        students = pd.read_sql("SELECT sid, name, math_score, chi_score FROM students", conn)
        
        if not students.empty:
            # Create a dropdown with names
            selected_option = st.selectbox("Select Student:", 
                                        students.apply(lambda x: f"{x['sid']} - {x['name']}", axis=1))
            sid = selected_option.split(" - ")[0]
            
            # Get the student's initial scores (Baseline)
            student_data = students[students['sid'] == sid].iloc[0]
            
            # 2. Fetch Exam History (Later Scores)
            history_df = pd.read_sql(f"SELECT date, subject, score FROM exam_records WHERE sid='{sid}' ORDER BY date", conn)
            
            # --- DATA MERGING LOGIC ---
            
            # Step A: Create the "Initial Score" rows
            # We assume a default start date (e.g., Sep 1st of current year) or "Day 0"
            current_year = datetime.now().year
            start_date = f"{current_year}-09-01"
            
            # If the first real exam is BEFORE Sep 1st, we shift the initial score to be earlier
            if not history_df.empty:
                first_exam_date = history_df['date'].min()
                if first_exam_date < start_date:
                    # Parse string to date, subtract 1 day, convert back to string
                    start_date = (pd.to_datetime(first_exam_date) - pd.Timedelta(days=1)).strftime('%Y-%m-%d')

            initial_data = [
                {"date": start_date, "subject": "Math", "score": student_data['math_score']},
                {"date": start_date, "subject": "Chinese", "score": student_data['chi_score']}
            ]
            
            # Step B: Combine Initial + History
            combined_df = pd.concat([pd.DataFrame(initial_data), history_df], ignore_index=True)
            
            # Step C: Convert 'date' to datetime objects for proper sorting/plotting
            combined_df['date'] = pd.to_datetime(combined_df['date'])
            combined_df = combined_df.sort_values(by='date')

            # --- PLOTTING ---
            st.write(f"### 📈 Score Trend: {student_data['name']}")
            
            # Pivot creates a format where Streamlit automatically draws different colored lines for subjects
            chart_data = combined_df.pivot_table(index='date', columns='subject', values='score', aggfunc='first')
            
            # Draw the chart
            st.line_chart(chart_data)
            
            # Show data table for verification
            with st.expander("View Data Source"):
                st.write("Combined Data (Initial + Exams):")
                st.dataframe(combined_df.style.format({"date": lambda t: t.strftime("%Y-%m-%d")}), use_container_width=True)

        else:
            st.info("No students found.")
            
    conn.close()

    # Quick Tool to Add Exam Data (For testing the Trend Line)
    with st.expander("➕ Admin: Add Historical Exam Record"):
        with st.form("add_exam_record"):
            s_list = pd.read_sql("SELECT sid, name FROM students", get_connection())
            stu_select = st.selectbox("Student", s_list['sid'].tolist())
            ex_date = st.date_input("Exam Date")
            ex_name = st.text_input("Exam Name (e.g. Midterm)")
            subj = st.selectbox("Subject", ["Math", "Chinese"])
            sc = st.number_input("Score", 0, 100)
            
            if st.form_submit_button("Save Record"):
                c = get_connection()
                c.execute("INSERT INTO exam_records (sid, exam_name, date, subject, score) VALUES (?,?,?,?,?)",
                          (stu_select, ex_name, ex_date, subj, sc))
                c.commit()
                c.close()
                st.success("Record Saved! Check the Trend view.")