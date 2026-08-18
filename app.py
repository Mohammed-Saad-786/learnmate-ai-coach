# ================================
# INSTALL
# ================================
# !pip install groq gradio fpdf
import os
from groq import Groq
import gradio as gr
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import re



# ================================
# API KEY
# ================================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# ================================
# PDF FUNCTION
def create_pdf(text):

    if not text:
        text = "No roadmap generated."

     # Remove emojis/non-ASCII (optional if you use a Unicode font)
    text = re.sub(r"[^\x00-\x7F]+", "", text)

    file_path = "/tmp/learnmate_roadmap.pdf"

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    story = []

    for line in text.split("\n"):
        if line.strip():
            story.append(Paragraph(line.replace("&", "&amp;"), styles["BodyText"]))

    doc.build(story)

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
latest_response = ""
# ================================
# CAREER QUERY CLASSIFIER
# ================================
def is_career_query(message):
    prompt = f"""
You are a classifier.
Determine whether the user's query is asking about:
- becoming a profession
- career roadmap
- skills required
- salary
- job roles
- certifications
- education path
- career growth
Answer ONLY one word:
YES or NO
User: {message}
"""

    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content.strip().upper() == "YES"
    
def learnmate(message, history, level):
    global latest_response

    if not is_career_query(message):
        return (
            "🎓 I am LearnMate AI Coach.\n\n"
            "I specialize in career guidance and roadmaps.\n\n"
            "Please ask questions such as:\n"
            "• How to become an Artist?\n"
            "• Doctor career roadmap\n"
            "• Skills needed for a Pilot\n"
            "• Fashion Designer salary\n"
            "• Chef career path\n"
            "• AI Engineer roadmap"
        )

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

        latest_response = text
        return text

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

        latest_response = text
        return text


# ================================
# PDF DOWNLOAD
# ================================
def download_pdf():
    global latest_response

    try:
        if not latest_response:
            raise ValueError("No roadmap available.")

        return create_pdf(latest_response)

    except Exception as e:
        print("PDF Error:", e)
        return None

# ================================
# UI
# ================================
def prepare_download():
    path = download_pdf()

    if path is None:
        return gr.DownloadButton(
            visible=False
        )

    return gr.DownloadButton(
        label="📥 Download Roadmap PDF",
        value=path,
        visible=True
    )
with gr.Blocks() as demo:

    gr.Markdown("# 🎓 LearnMate AI Coach")
    gr.Markdown("Chat with your AI career mentor 🚀")

    level = gr.Radio(
        ["Beginner","Intermediate","Advanced"],
        value="Beginner",
        label="Select Level"
    )

    

    chatbot = gr.ChatInterface(
        fn=learnmate,
        additional_inputs=[level],
        textbox=gr.Textbox(
        placeholder="Example: I want to become a Full Stack Developer 🚀"
    )
    )

    gr.Markdown("### 📄 Download Roadmap")

    pdf_btn = gr.Button("Generate PDF")

    pdf_output = gr.DownloadButton(
    label="📥 Download Roadmap PDF",
    visible=False
    )

    pdf_btn.click(
    fn=prepare_download,
    outputs=pdf_output
    )

demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    
)
