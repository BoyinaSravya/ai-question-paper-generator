import streamlit as st
import pandas as pd
import PyPDF2
import random
from fpdf import FPDF

st.set_page_config(page_title="AI Question Paper Generator", layout="wide")

st.title("AI Question Paper Generator")

# ---------- INPUT ----------
college = st.text_input("College Name", "RAMACHANDRA COLLEGE OF ENGINEERING")
course_no = st.text_input("Course Number")

regulation = st.selectbox(
    "Regulation",
    ["R20","R21","R22","R23","R24","R25","R26","R27","R28","R29","R30"]
)

set_no = st.selectbox("Set Number", ["SET-1","SET-2","SET-3"])

exam_title = st.text_input(
    "Exam Title",
    "I B.TECH I SEMESTER REGULAR EXAMINATIONS, JAN-2024"
)

subject = st.text_input("Subject", "AI")
semester = st.selectbox("Semester", ["1","2","3","4","5","6","7","8"])
branch = st.text_input("Branch", "AIML")
time = st.text_input("Exam Duration", "3 hours")

exam_type = st.selectbox("Exam Type", ["MID-1","MID-2","SEMESTER"])
difficulty = st.selectbox("Difficulty Level", ["Easy","Medium","Hard"])

uploaded_file = st.file_uploader("Upload Syllabus (PDF or Excel)", type=["pdf","xlsx"])

# ---------- MARKS ----------
if exam_type == "SEMESTER":
    max_marks = 70
    partA_q = 10
else:
    max_marks = 40
    partA_q = 5

# ---------- READ SYLLABUS ----------
topics = []

if uploaded_file:

    if uploaded_file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
        topics = text.split()

    else:
        df = pd.read_excel(uploaded_file)
        topics = df.astype(str).values.flatten().tolist()

topics = list(set([t.strip() for t in topics if str(t).strip() != ""]))

# ---------- SAFETY CLEAN ----------
def clean_text(text):
    return str(text).encode("ascii", "ignore").decode()

# ---------- DIFFICULTY ----------
difficulty_map = {"Easy":0, "Medium":1, "Hard":2}
difficulty_level = difficulty_map[difficulty]

# ---------- QUESTION SYSTEM ----------
used_questions = set()

def generate_question(topic, mode="VSAQ"):

    if mode == "VSAQ":
        base = [
            f"Define {topic} with suitable example.",
            f"Explain the concept of {topic}.",
            f"Write short notes on {topic}.",
            f"Describe the characteristics of {topic}.",
            f"Explain the importance of {topic} in AI."
        ]
    else:
        base = [
            f"Explain {topic} in detail with examples.",
            f"Discuss architecture and working of {topic}.",
            f"Explain advantages and applications of {topic}.",
            f"Describe working mechanism of {topic}.",
            f"Explain theoretical concepts of {topic} in AI."
        ]

    # difficulty boost
    if difficulty_level == 1:
        base.append(f"Analyze {topic} with real-world applications.")
    elif difficulty_level == 2:
        base.append(f"Critically evaluate {topic} with limitations and advanced use cases.")

    q = random.choice(base)

    while q in used_questions:
        q = random.choice(base)

    used_questions.add(q)
    return q

# ---------- GENERATE ----------
if st.button("Generate Question Paper"):

    if not uploaded_file:
        st.warning("Please upload syllabus file")
        st.stop()

    used_questions.clear()

    # ---------- HEADER ----------
    st.markdown(f"""
    <div style="text-align:center">
        <h2><b>{college}</b></h2>
        <h4><b>{course_no} {regulation} {set_no}</b></h4>
        <h4><b>{exam_title}</b></h4>
        <h3><b>{subject}</b></h3>
        <h4><b>Semester {semester}</b></h4>
        <h4><b>{branch}</b></h4>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("_"*120)

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;font-weight:bold">
        <span>Time: {time}</span>
        <span>Max Marks: {max_marks}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("_"*120)

    # ---------- PART A ----------
    st.subheader("PART-A")

    selected = random.sample(topics, min(len(topics), partA_q))

    partA = ""

    for i, t in enumerate(selected):
        q = f"{i+1}. {generate_question(t, 'VSAQ')}"
        st.write(q)
        partA += q + "\n"

    st.markdown("_"*120)

    # ---------- PART B ----------
    st.subheader("PART-B")

    units = (
        ["UNIT-I","UNIT-II","UNIT-III","UNIT-IV","UNIT-V"]
        if exam_type == "SEMESTER"
        else ["UNIT-I","UNIT-II","UNIT-III"]
    )

    partB = ""

    for i, u in enumerate(units):

        st.markdown(f"### {u}")

        topic = random.choice(topics)

        q1 = f"{i+1}A) {generate_question(topic, 'LAQ')}"
        q2 = f"{i+1}B) {generate_question(topic, 'LAQ')}"

        st.write(q1)
        st.write("OR")
        st.write(q2)

        partB += f"{u}\n{q1}\nOR\n{q2}\n"

    # ---------- PDF ----------
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, clean_text(college), ln=True, align="C")

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, clean_text(f"{course_no} {regulation} {set_no}"), ln=True, align="C")
    pdf.cell(0, 8, clean_text(exam_title), ln=True, align="C")

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, clean_text(subject), ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, clean_text(f"Semester {semester} | {branch}"), ln=True, align="C")

    pdf.ln(5)
    pdf.cell(0, 8, "_"*120, ln=True)

    pdf.cell(95, 8, clean_text(f"Time: {time}"))
    pdf.cell(0, 8, clean_text(f"Max Marks: {max_marks}"), ln=True, align="R")

    pdf.cell(0, 8, "_"*120, ln=True)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "PART-A", ln=True)

    pdf.set_font("Arial", "", 12)
    for line in partA.split("\n"):
        pdf.multi_cell(0, 8, clean_text(line))

    pdf.cell(0, 8, "_"*120, ln=True)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "PART-B", ln=True)

    pdf.set_font("Arial", "", 12)
    for line in partB.split("\n"):
        pdf.multi_cell(0, 8, clean_text(line))

    pdf.output("question_paper.pdf")

    # ---------- DOWNLOAD ----------
    with open("question_paper.pdf", "rb") as f:
        st.download_button(
            "Download Question Paper PDF",
            f,
            file_name="question_paper.pdf"
        )