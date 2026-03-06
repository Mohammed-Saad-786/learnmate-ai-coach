# ================================
# INSTALL
# ================================
# !pip install groq gradio fpdf

from groq import Groq
import gradio as gr
from fpdf import FPDF

# ================================
# API KEY
# ================================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# ================================
# PDF FUNCTION
def create_pdf(text):

    if not text:
        text = "No roadmap generated."

    # Convert unicode to safe latin characters
    text = text.encode("latin-1", "replace").decode("latin-1")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    for line in text.split("\n"):
        pdf.multi_cell(0, 8, line)

    file_path = "/tmp/learnmate_roadmap.pdf"
    pdf.output(file_path)

    return file_path


# ================================
# DOMAIN DATA
# ================================
KNOWN_DOMAINS = {

"frontend":{
"courses":[
("Meta Frontend Developer","https://coursera.org/professional-certificates/meta-front-end-developer"),
("freeCodeCamp","https://freecodecamp.org"),
("Odin Project","https://theodinproject.com")
],

"roles":[
"Frontend Developer",
"React Developer"
],

"salary":"₹3–10 LPA",

"steps":[
"Learn HTML CSS JavaScript",
"Build React Projects",
"Deploy Applications"
]
}

}


# ================================
# AI STEP GENERATION
# ================================
def generate_steps(domain, step, level):

    prompt=f"""
Domain: {domain}
Step: {step}
Level: {level}

Write 3 bullet points using *
"""

    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":prompt}]
    )

    return res.choices[0].message.content


# ================================
# CHAT FUNCTION
# ================================
def learnmate(message, history, level):

    msg=message.lower()

    if "frontend" in msg:

        text="🎯 Frontend Roadmap\n\n"

        text+="📚 Courses\n"
        for name,link in KNOWN_DOMAINS["frontend"]["courses"]:
            text+=f"{name}: {link}\n"

        text+="\n💼 Roles\nFrontend Developer\nReact Developer\n"

        text+="\n💰 Salary\n₹3–10 LPA\n\n"

        text+="🚀 Roadmap\n\n"

        for step in KNOWN_DOMAINS["frontend"]["steps"]:
            ai=generate_steps("frontend",step,level)
            text+=f"{step}\n{ai}\n\n"

        return text, text

    else:

        prompt=f"""
User wants roadmap for {message}
Level: {level}

Provide roadmap, roles, salary India, tools and courses
"""

        res=client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":prompt}]
        )

        text=res.choices[0].message.content

        return text, text


# ================================
# PDF DOWNLOAD
# ================================
def download_pdf(text):

    if not text:
        return None

    path=create_pdf(text)

    return path


# ================================
# UI
# ================================
with gr.Blocks(theme=gr.themes.Soft()) as demo:

    gr.Markdown("# 🎓 LearnMate AI Coach")
    gr.Markdown("Chat with your AI career mentor 🚀")

    level = gr.Radio(
        ["Beginner","Intermediate","Advanced"],
        value="Beginner",
        label="Select Level"
    )

    state = gr.State()

    chatbot = gr.ChatInterface(
        fn=learnmate,
        additional_inputs=[level],
        additional_outputs=[state]
    )

    gr.Markdown("### 📄 Download Roadmap")

    pdf_btn = gr.Button("Generate PDF")

    pdf_output = gr.File()

    pdf_btn.click(
        fn=download_pdf,
        inputs=state,
        outputs=pdf_output
    )

demo.launch()
