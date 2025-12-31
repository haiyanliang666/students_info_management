import streamlit as st
import pandas as pd
import io
import sqlite3
from datetime import datetime
import streamlit as st
import pandas as pd
import io
import sqlite3
from datetime import datetime

# --- 1. PAGE CONFIG (MUST BE FIRST) ---
st.set_page_config(page_title="School System", layout="wide")

# Custom CSS for cleaner tabs
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; font-weight: bold; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE SETUP ---
def get_connection():
    return sqlite3.connect('school.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Core Tables
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT, linked_id TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS students (sid TEXT PRIMARY KEY, name TEXT, school TEXT, grade TEXT, p_contact TEXT, s_contact TEXT, math_score REAL, chi_score REAL, status TEXT DEFAULT 'Active')''')
    c.execute('''CREATE TABLE IF NOT EXISTS courses (course_id INTEGER PRIMARY KEY AUTOINCREMENT, course_name TEXT, teacher TEXT, schedule TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY AUTOINCREMENT, sid TEXT, course_id INTEGER, FOREIGN KEY (sid) REFERENCES students (sid), FOREIGN KEY (course_id) REFERENCES courses (course_id))''')
    
    # Activity Tables
    c.execute('''CREATE TABLE IF NOT EXISTS schedule (id INTEGER PRIMARY KEY AUTOINCREMENT, course_id INTEGER, day TEXT, start_time TEXT, end_time TEXT, FOREIGN KEY (course_id) REFERENCES courses (course_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (task_id INTEGER PRIMARY KEY AUTOINCREMENT, course_id INTEGER, description TEXT, assigned_date TEXT, due_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS task_completions (id INTEGER PRIMARY KEY AUTOINCREMENT, task_id INTEGER, sid TEXT, completed_date TEXT, stars_earned INTEGER DEFAULT 0, FOREIGN KEY (task_id) REFERENCES tasks (task_id))''')
    
    # Records Tables
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, sid TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, sid TEXT, change_type TEXT, notes TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS exam_records (id INTEGER PRIMARY KEY AUTOINCREMENT, sid TEXT, exam_name TEXT, date TEXT, subject TEXT, score REAL, FOREIGN KEY (sid) REFERENCES students (sid))''')

    # Create Admin if not exists
    try:
        c.execute("INSERT INTO users VALUES ('admin', '123456', 'admin', 'Admin')")
    except:
        pass
    
    conn.commit()
    conn.close()

init_db()

# --- 3. LOGIN LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_id = None

def login_page():
    st.header("🔐 Login to School System")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        conn = get_connection()
        user = pd.read_sql(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'", conn)
        conn.close()
        if not user.empty:
            st.session_state.logged_in = True
            st.session_state.user_role = user.iloc[0]['role']
            st.session_state.user_id = user.iloc[0]['linked_id']
            st.success("Login Successful!")
            st.rerun()
        else:
            st.error("Invalid Username or Password")

if not st.session_state.logged_in:
    login_page()
    st.stop() 

if st.sidebar.button("Log Out"):
    st.session_state.logged_in = False
    st.rerun()

# --- 4. MAIN APP LOGIC ---

# >>>>>>>>> ADMIN / TEACHER VIEW <<<<<<<<<
if st.session_state.user_role in ['admin', 'teacher']:
    st.title("🏫 Afterschool Management System")
    st.sidebar.title(f"👨‍🏫 Welcome, {st.session_state.user_id}")

    # Unified Tabs List
    tabs_labels = [
        "👤 Student Info", "📚 Enrollment", "📅 Schedule", "📝 Homework", 
        "🔄 Tracking", "✅ Attendance", "📊 Analytics"
    ]
    
    # Add Admin Tab only if Admin
    if st.session_state.user_role == 'admin':
        tabs_labels.append("🔐 User Accounts")

    # Create the Tabs
    tabs = st.tabs(tabs_labels)

    # --- TAB 1: STUDENT INFO ---
    with tabs[0]:
        sub_feature = st.selectbox("Select Action:", ["View List", "Add Student", "Manage (Edit/Delete)", "Import/Export"], key="info_box")
        st.divider()
        
        conn = get_connection()
        if sub_feature == "View List":
            df = pd.read_sql("SELECT * FROM students", conn)
            if not df.empty:
                search = st.text_input("Search Name/ID")
                if search:
                    df = df[df['name'].str.contains(search, case=False) | df['sid'].str.contains(search)]
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No data.")
        
        elif sub_feature == "Add Student":
            with st.form("add_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                sid = c1.text_input("Student ID")
                name = c1.text_input("Name")
                school = c1.text_input("School")
                grade = c1.selectbox("Grade", ["G1", "G2", "G3", "G4", "G5", "G6"])
                p_con = c2.text_input("Parent Contact")
                s_con = c2.text_input("School Contact")
                math = c2.number_input("Math", 0, 100)
                chi = c2.number_input("Chinese", 0, 100)
                if st.form_submit_button("Save"):
                    try:
                        conn.execute("INSERT INTO students VALUES (?,?,?,?,?,?,?,?,?)", (sid, name, school, grade, p_con, s_con, math, chi, 'Active'))
                        conn.commit()
                        st.success("Saved!")
                    except Exception as e:
                        st.error(f"Error: {e}")

        elif sub_feature == "Manage (Edit/Delete)":
            students = pd.read_sql("SELECT sid, name FROM students", conn)
            if not students.empty:
                sel = st.selectbox("Select Student", students.apply(lambda x: f"{x['sid']} - {x['name']}", axis=1))
                tid = sel.split(" - ")[0]
                curr = pd.read_sql(f"SELECT * FROM students WHERE sid='{tid}'", conn).iloc[0]
                
                t1, t2 = st.tabs(["Edit", "Delete"])
                with t1:
                    with st.form("edit_f"):
                        n_name = st.text_input("Name", curr['name'])
                        if st.form_submit_button("Update"):
                            conn.execute("UPDATE students SET name=? WHERE sid=?", (n_name, tid))
                            conn.commit()
                            st.success("Updated!")
                with t2:
                    st.error("Danger Zone")
                    if st.button("Delete Permanently"):
                        conn.execute("DELETE FROM students WHERE sid=?", (tid,))
                        conn.execute("DELETE FROM enrollments WHERE sid=?", (tid,))
                        conn.commit()
                        st.success("Deleted")
                        st.rerun()

        elif sub_feature == "Import/Export":
            # Simple Export
            df = pd.read_sql("SELECT * FROM students", conn)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            st.download_button("Download Excel", output.getvalue(), "students.xlsx")
        
        conn.close()

    # --- TAB 2: ENROLLMENT ---
    with tabs[1]:
        act = st.selectbox("Action:", ["Manage Courses", "Enroll Student", "View Rosters"])
        conn = get_connection()
        
        if act == "Manage Courses":
            with st.form("add_c"):
                cn = st.text_input("Course Name")
                tn = st.text_input("Teacher")
                if st.form_submit_button("Add Course"):
                    conn.execute("INSERT INTO courses (course_name, teacher) VALUES (?,?)", (cn, tn))
                    conn.commit()
                    st.success("Course Added")
        
        elif act == "Enroll Student":
            stu = pd.read_sql("SELECT sid, name FROM students", conn)
            crs = pd.read_sql("SELECT course_id, course_name FROM courses", conn)
            if not stu.empty and not crs.empty:
                s_sel = st.selectbox("Student", stu.apply(lambda x: f"{x['sid']} - {x['name']}", axis=1), key="enroll_student")
                c_sel = st.selectbox("Course", crs.apply(lambda x: f"{x['course_id']} - {x['course_name']}", axis=1), key="enroll_course")
                if st.button("Enroll"):
                    conn.execute("INSERT INTO enrollments (sid, course_id) VALUES (?,?)", (s_sel.split(" - ")[0], c_sel.split(" - ")[0]))
                    conn.commit()
                    st.success("Enrolled")

        elif act == "View Rosters":
            crs = pd.read_sql("SELECT * FROM courses", conn)
            if not crs.empty:
                c_sel = st.selectbox("Course", crs.apply(lambda x: f"{x['course_id']} - {x['course_name']}", axis=1), key="enroll_course")
                cid = c_sel.split(" - ")[0]
                roster = pd.read_sql(f"SELECT s.name, s.grade FROM students s JOIN enrollments e ON s.sid=e.sid WHERE e.course_id={cid}", conn)
                st.dataframe(roster)
        conn.close()

    # --- TAB 3: SCHEDULE ---
    with tabs[2]:
        st.subheader("Manage Weekly Schedule")
        conn = get_connection()
        courses = pd.read_sql("SELECT course_id, course_name FROM courses", conn)
        
        c1, c2, c3, c4 = st.columns(4)
        crs_select = c1.selectbox("Course", courses.apply(lambda x: f"{x['course_id']} - {x['course_name']}", axis=1), key="sched_course")
        day_select = c2.selectbox("Day", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        t_start = c3.time_input("Start")
        t_end = c4.time_input("End")
            
        if st.button("Add Schedule Slot"):
            cid = crs_select.split(" - ")[0]
            conn.execute("INSERT INTO schedule (course_id, day, start_time, end_time) VALUES (?,?,?,?)",
                        (cid, day_select, str(t_start), str(t_end)))
            conn.commit()
            st.success("Added!")
        
        sched_df = pd.read_sql("SELECT c.course_name, s.day, s.start_time FROM schedule s JOIN courses c ON s.course_id=c.course_id", conn)
        st.dataframe(sched_df, use_container_width=True)
        conn.close()

    # --- TAB 4: HOMEWORK ---
    with tabs[3]:
        st.subheader("Assign Homework")
        conn = get_connection()
        courses = pd.read_sql("SELECT course_id, course_name FROM courses", conn)
        
        with st.form("hw_form"):
            tc = st.selectbox("Class", courses.apply(lambda x: f"{x['course_id']} - {x['course_name']}", axis=1))
            desc = st.text_area("Description")
            dd = st.date_input("Due Date")
            if st.form_submit_button("Assign"):
                conn.execute("INSERT INTO tasks (course_id, description, assigned_date, due_date) VALUES (?,?,?,?)",
                            (tc.split(" - ")[0], desc, str(datetime.now().date()), str(dd)))
                conn.commit()
                st.success("Assigned!")
        
        st.divider()
        st.write("Completion Tracker")
        track_df = pd.read_sql("SELECT s.name, t.description, tc.stars_earned FROM task_completions tc JOIN tasks t ON tc.task_id=t.task_id JOIN students s ON tc.sid=s.sid", conn)
        st.dataframe(track_df)
        conn.close()

    # --- TAB 5: TRACKING ---
    with tabs[4]:
        st.subheader("Student Status Tracking")
        conn = get_connection()
        s_list = pd.read_sql("SELECT sid, name, status FROM students", conn)
        
        c1, c2 = st.columns(2)
        target = c1.selectbox("Student", s_list.apply(lambda x: f"{x['sid']} - {x['name']}", axis=1), key="track_student")
        stat = c2.selectbox("New Status", ["Active", "Leave", "Graduated"])
        
        if st.button("Update Status"):
            conn.execute("UPDATE students SET status=? WHERE sid=?", (stat, target.split(" - ")[0]))
            conn.commit()
            st.success("Status Updated")
        conn.close()

    # --- TAB 6: ATTENDANCE ---
    with tabs[5]:
        st.subheader("Daily Attendance")
        date = st.date_input("Date")
        conn = get_connection()
        df = pd.read_sql("SELECT sid, name FROM students WHERE status='Active'", conn)
        
        if not df.empty:
            df['Status'] = "Present"
            edited = st.data_editor(df, use_container_width=True)
            if st.button("Save Attendance"):
                for _, row in edited.iterrows():
                    conn.execute("INSERT INTO attendance (date, sid, status) VALUES (?,?,?)", (str(date), row['sid'], row['Status']))
                conn.commit()
                st.success("Saved")
        conn.close()

    # --- TAB 7: ANALYTICS ---
    with tabs[6]:
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


    # --- TAB 8: ACCOUNTS (ADMIN ONLY) ---
    if st.session_state.user_role == 'admin':
        with tabs[7]:
            st.subheader("Manage Users")
            with st.form("new_user"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                r = st.selectbox("Role", ["Student", "Teacher", "Admin"])
                l = st.text_input("Link ID (SID for Student, Name for Teacher)")
                if st.form_submit_button("Create"):
                    conn = get_connection()
                    try:
                        conn.execute("INSERT INTO users VALUES (?,?,?,?)", (u, p, r.lower(), l))
                        conn.commit()
                        st.success("Created")
                    except:
                        st.error("Username exists")
                    conn.close()
            
            conn = get_connection()
            st.dataframe(pd.read_sql("SELECT username, role, linked_id FROM users", conn))
            conn.close()

# >>>>>>>>> STUDENT VIEW <<<<<<<<<
elif st.session_state.user_role == 'student':
    student_id = st.session_state.user_id
    st.title(f"👋 Hi, Student {student_id}")
    
    t1, t2 = st.tabs(["📅 My Schedule", "⭐ My Homework"])
    conn = get_connection()

    with t1:
        sch = pd.read_sql(f'''
            SELECT c.course_name, s.day, s.start_time 
            FROM enrollments e 
            JOIN schedule s ON e.course_id=s.course_id 
            JOIN courses c ON c.course_id=e.course_id 
            WHERE e.sid='{student_id}'
        ''', conn)
        st.table(sch)

    with t2:
        tasks = pd.read_sql(f'''
            SELECT t.task_id, c.course_name, t.description, t.due_date 
            FROM tasks t 
            JOIN enrollments e ON t.course_id=e.course_id 
            JOIN courses c ON c.course_id=e.course_id 
            WHERE e.sid='{student_id}' 
            AND t.task_id NOT IN (SELECT task_id FROM task_completions WHERE sid='{student_id}')
        ''', conn)
        
        if not tasks.empty:
            for _, row in tasks.iterrows():
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{row['course_name']}**: {row['description']} (Due: {row['due_date']})")
                if c2.button("Done", key=row['task_id']):
                    conn.execute("INSERT INTO task_completions (task_id, sid, completed_date, stars_earned) VALUES (?,?,?,1)", (row['task_id'], student_id, str(datetime.now().date())))
                    conn.commit()
                    st.balloons()
                    st.rerun()
        else:
            st.success("No homework!")
            
        stars = pd.read_sql(f"SELECT SUM(stars_earned) as s FROM task_completions WHERE sid='{student_id}'", conn).iloc[0]['s']
        st.metric("Total Stars", int(stars) if stars else 0)
    
    conn.close()