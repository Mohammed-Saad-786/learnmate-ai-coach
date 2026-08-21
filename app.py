# ================================
# INSTALL
# ================================
# requirements.txt:
# groq
# gradio
# reportlab


# ================================
# IMPORTS
# ================================
import os
import re

import gradio as gr
from groq import Groq

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4


# ================================
# API CONFIGURATION
# ================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not configured. "
        "Add GROQ_API_KEY under Hugging Face Space Settings → Secrets."
    )

client = Groq(api_key=GROQ_API_KEY)

# Current Groq production model
MODEL = "openai/gpt-oss-20b"


# ================================
# GLOBAL RESPONSE
# ================================

latest_response = ""


# ================================
# PDF FUNCTION
# ================================

def create_pdf(text):

    if not text:
        text = "No roadmap generated."

    file_path = "/tmp/learnmate_roadmap.pdf"

    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle
    )

    from reportlab.lib.styles import (
        getSampleStyleSheet,
        ParagraphStyle
    )

    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from xml.sax.saxutils import escape


    # ==========================================
    # PDF DOCUMENT
    # ==========================================

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=45,
        bottomMargin=45,
        title="LearnMate AI Coach - Career Roadmap",
        author="LearnMate AI Coach",
        subject="Career Roadmap",
        creator="LearnMate AI Coach"
    )


    # ==========================================
    # STYLES
    # ==========================================

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "PDFTitle",
        parent=styles["Title"],
        fontSize=22,
        leading=26,
        alignment=TA_CENTER,
        spaceAfter=20
    )

    heading1 = ParagraphStyle(
        "Heading1Custom",
        parent=styles["Heading1"],
        fontSize=16,
        leading=20,
        spaceBefore=14,
        spaceAfter=8
    )

    heading2 = ParagraphStyle(
        "Heading2Custom",
        parent=styles["Heading2"],
        fontSize=13,
        leading=17,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["BodyText"],
        fontSize=10,
        leading=15,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "BulletCustom",
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-8,
        spaceAfter=4
    )


    # ==========================================
    # MARKDOWN → REPORTLAB
    # ==========================================

    def format_markdown(line):

        line = line.strip()

        if not line:
            return ""

        # Remove emojis / unsupported characters
        line = re.sub(
            r"[^\x00-\x7F]+",
            "",
            line
        )

        # Escape HTML special characters first
        line = escape(line)

        # ======================================
        # LINKS
        # [Google](https://google.com)
        # ======================================

        line = re.sub(
            r"\[([^\]]+)\]\((https?://[^\)]+)\)",
            r'<link href="\2" color="blue">\1</link>',
            line
        )

        # ======================================
        # BOLD
        # **text**
        # ======================================

        line = re.sub(
            r"\*\*(.*?)\*\*",
            r"<b>\1</b>",
            line
        )

        # ======================================
        # ITALIC
        # *text*
        # ======================================

        line = re.sub(
            r"(?<!\*)\*([^*]+)\*(?!\*)",
            r"<i>\1</i>",
            line
        )

        # ======================================
        # INLINE CODE
        # `code`
        # ======================================

        line = re.sub(
            r"`([^`]+)`",
            r"<font name='Courier'>\1</font>",
            line
        )

        return line


    # ==========================================
    # BUILD PDF
    # ==========================================

    story = []

    lines = text.split("\n")

    i = 0

    # Main title
    story.append(
        Paragraph(
            "LearnMate AI Coach",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Career Roadmap",
            ParagraphStyle(
                "Subtitle",
                parent=body_style,
                alignment=TA_CENTER,
                fontSize=11,
                spaceAfter=20
            )
        )
    )


    while i < len(lines):

        raw_line = lines[i].strip()

        # ======================================
        # EMPTY LINE
        # ======================================

        if not raw_line:

            story.append(
                Spacer(1, 5)
            )

            i += 1
            continue


        # ======================================
        # HORIZONTAL LINE
        # ---
        # ======================================

        if re.match(r"^[-*_]{3,}$", raw_line):

            story.append(
                Spacer(1, 5)
            )

            story.append(
                Table(
                    [[""]],
                    colWidths=[515],
                    rowHeights=[1],
                    style=TableStyle([
                        (
                            "LINEBELOW",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.grey
                        )
                    ])
                )
            )

            story.append(
                Spacer(1, 8)
            )

            i += 1
            continue


        # ======================================
        # HEADINGS
        # ## Heading
        # ### Heading
        # ======================================

        heading_match = re.match(
            r"^(#{1,6})\s+(.*)",
            raw_line
        )

        if heading_match:

            level = len(
                heading_match.group(1)
            )

            heading_text = format_markdown(
                heading_match.group(2)
            )

            if level <= 2:

                story.append(
                    Paragraph(
                        heading_text,
                        heading1
                    )
                )

            else:

                story.append(
                    Paragraph(
                        heading_text,
                        heading2
                    )
                )

            i += 1
            continue


        # ======================================
        # TABLE DETECTION
        # ======================================

        if (
            "|" in raw_line
            and i + 1 < len(lines)
            and "|" in lines[i + 1]
            and re.match(
                r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$",
                lines[i + 1]
            )
        ):

            table_data = []

            # Header
            header = [
                cell.strip()
                for cell in raw_line.strip("|").split("|")
            ]

            table_data.append([
                Paragraph(
                    "<b>" + format_markdown(cell) + "</b>",
                    body_style
                )
                for cell in header
            ])

            i += 2

            # Table rows
            while i < len(lines):

                row_line = lines[i].strip()

                if "|" not in row_line:
                    break

                row = [
                    cell.strip()
                    for cell in row_line.strip("|").split("|")
                ]

                table_data.append([
                    Paragraph(
                        format_markdown(cell),
                        body_style
                    )
                    for cell in row
                ])

                i += 1


            # Calculate columns
            column_count = len(
                table_data[0]
            )

            available_width = 515

            col_widths = [
                available_width / column_count
            ] * column_count


            table = Table(
                table_data,
                colWidths=col_widths,
                repeatRows=1
            )


            table.setStyle(
                TableStyle([
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),

                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey
                    ),

                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),

                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    ),

                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    ),

                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    )
                ])
            )

            story.append(table)

            story.append(
                Spacer(1, 10)
            )

            continue


        # ======================================
        # BULLET LIST
        # - item
        # * item
        # ======================================

        bullet_match = re.match(
            r"^[-*+]\s+(.*)",
            raw_line
        )

        if bullet_match:

            bullet_text = format_markdown(
                bullet_match.group(1)
            )

            story.append(
                Paragraph(
                    "• " + bullet_text,
                    bullet_style
                )
            )

            i += 1
            continue


        # ======================================
        # NUMBERED LIST
        # 1. item
        # ======================================

        number_match = re.match(
            r"^(\d+)\.\s+(.*)",
            raw_line
        )

        if number_match:

            number = number_match.group(1)

            number_text = format_markdown(
                number_match.group(2)
            )

            story.append(
                Paragraph(
                    f"{number}. {number_text}",
                    bullet_style
                )
            )

            i += 1
            continue


        # ======================================
        # NORMAL PARAGRAPH
        # ======================================

        formatted_line = format_markdown(
            raw_line
        )

        story.append(
            Paragraph(
                formatted_line,
                body_style
            )
        )

        i += 1


    # ==========================================
    # PDF METADATA
    # ==========================================

    def add_metadata(canvas, document):

        canvas.setTitle(
            "LearnMate AI Coach - Career Roadmap"
        )

        canvas.setAuthor(
            "LearnMate AI Coach"
        )

        canvas.setSubject(
            "Career Roadmap generated by LearnMate AI Coach"
        )

        canvas.setCreator(
            "LearnMate AI Coach"
        )


    # Rebuild with metadata callback
    doc.build(
        story,
        onFirstPage=add_metadata,
        onLaterPages=add_metadata
    )

    return file_path


# ================================
# DOMAIN DATA
# ================================

KNOWN_DOMAINS = {

    "frontend": {

        "courses": [
            (
                "Meta Frontend Developer",
                "https://coursera.org/professional-certificates/meta-front-end-developer"
            ),

            (
                "freeCodeCamp",
                "https://freecodecamp.org"
            ),

            (
                "Odin Project",
                "https://theodinproject.com"
            )
        ],

        "roles": [
            "Frontend Developer",
            "React Developer"
        ],

        "salary": "₹3–10 LPA",

        "steps": [
            "Learn HTML CSS JavaScript",
            "Build React Projects",
            "Deploy Applications"
        ]
    }
}


# ================================
# LOCAL CAREER QUERY DETECTION
# ================================

def is_career_query(message):

    if not message:
        return False

    msg = message.lower().strip()

    career_keywords = [

        # Career / roadmap
        "career",
        "career path",
        "career roadmap",
        "roadmap",
        "career growth",

        # Become
        "how to become",
        "how can i become",
        "want to become",
        "become a",
        "become an",

        # Skills
        "skills needed",
        "skills required",
        "what skills",
        "learn for",
        "what should i learn",

        # Jobs
        "job role",
        "job roles",
        "jobs",
        "job opportunities",
        "employment",

        # Salary
        "salary",
        "pay",
        "earning",
        "earn",

        # Education
        "course",
        "courses",
        "certification",
        "certifications",
        "degree",

        # Technologies
        "technologies needed",
        "technology needed",
        "tools needed",

        # Specific career words
        "developer",
        "engineer",
        "designer",
        "analyst",
        "scientist",
        "architect",
        "programmer",
        "pilot",
        "doctor",
        "lawyer",
        "teacher",
        "chef",
        "accountant",
        "marketer",
        "cybersecurity",
        "cyber security",
        "data science",
        "data analyst",
        "machine learning",
        "artificial intelligence",
        "ai engineer",
        "web developer",
        "software engineer",
        "frontend",
        "front end",
        "backend",
        "back end",
        "full stack",
        "cloud engineer",
        "devops",
        "ui ux",
        "digital marketing"
    ]

    return any(
        keyword in msg
        for keyword in career_keywords
    )


# ================================
# AI STEP GENERATION
# ================================

def generate_steps(domain, step, level):

    prompt = f"""
You are LearnMate AI Coach, a career mentor.
Domain: {domain}
Roadmap Step:
{step}
User Level:
{level}
Give exactly 3 short and practical bullet points.
Start every bullet point with "*".
Do not add unnecessary introduction or conclusion.
"""

    try:

        response = client.chat.completions.create(

            model=MODEL,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.5,

            max_tokens=250
        )

        return response.choices[0].message.content.strip()

    except Exception as e:

        print("Groq Step Generation Error:", e)

        return (
            "* Learn the fundamentals.\n"
            "* Practice with hands-on projects.\n"
            "* Build and deploy a real-world project."
        )


# ================================
# GENERAL CAREER ROADMAP
# ================================

def generate_general_roadmap(message, level):

    prompt = f"""
You are LearnMate AI Coach, a professional career guidance assistant.
User's career question:
{message}
User's current level:
{level}
Create a practical and beginner-friendly career roadmap.
Include these sections:
🎯 Career Overview
📚 Skills to Learn
🛠️ Tools and Technologies
🗺️ Step-by-Step Roadmap
💼 Job Roles
💰 Approximate Salary Range in India
🎓 Recommended Courses
🚀 Projects to Build
📈 Career Growth
Important instructions:
- Give practical advice.
- Keep the roadmap structured.
- Explain what to learn first and what to learn later.
- Mention relevant technologies.
- Suggest realistic projects.
- Give an approximate Indian salary range.
- Do not claim that a particular salary is guaranteed.
- Keep the response easy to understand.
"""

    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.5,

        max_tokens=2000
    )

    return response.choices[0].message.content.strip()


# ================================
# CHAT FUNCTION
# ================================

def learnmate(message, history, level):

    global latest_response

    try:

        # ----------------------------
        # Empty message
        # ----------------------------

        if not message or not message.strip():

            return (
                "Please enter a career-related question. "
                "For example: How do I become a Data Analyst?"
            )


        # ----------------------------
        # Career query check
        # ----------------------------

        if not is_career_query(message):

            response = (
                "🎓 **I am LearnMate AI Coach.**\n\n"

                "I specialize in career guidance and roadmaps.\n\n"

                "Please ask questions such as:\n\n"

                "• How to become an Artist?\n"
                "• Doctor career roadmap\n"
                "• Skills needed for a Pilot\n"
                "• Fashion Designer salary\n"
                "• Chef career path\n"
                "• AI Engineer roadmap\n"
                "• How to become a Data Analyst?\n"
                "• Full Stack Developer roadmap"
            )

            latest_response = response

            return response


        msg = message.lower()


        # ============================
        # FRONTEND SPECIAL CASE
        # ============================

        if (
            "frontend" in msg
            or "front end" in msg
        ):

            text = (
                "🎯 **Frontend Developer Roadmap**\n\n"
            )


            # ------------------------
            # Courses
            # ------------------------

            text += "📚 **Recommended Courses**\n\n"

            for name, link in KNOWN_DOMAINS["frontend"]["courses"]:

                text += f"• {name}\n"
                text += f"  {link}\n\n"


            # ------------------------
            # Roles
            # ------------------------

            text += "💼 **Job Roles**\n\n"

            for role in KNOWN_DOMAINS["frontend"]["roles"]:

                text += f"• {role}\n"

            text += "\n"


            # ------------------------
            # Salary
            # ------------------------

            text += "💰 **Approximate Salary in India**\n\n"

            text += (
                f"{KNOWN_DOMAINS['frontend']['salary']}\n\n"
            )


            # ------------------------
            # Roadmap
            # ------------------------

            text += "🚀 **Roadmap**\n\n"

            for step in KNOWN_DOMAINS["frontend"]["steps"]:

                text += f"### {step}\n\n"

                ai = generate_steps(
                    "frontend",
                    step,
                    level
                )

                text += f"{ai}\n\n"


            latest_response = text

            return text


        # ============================
        # GENERAL CAREER
        # ============================

        text = generate_general_roadmap(
            message,
            level
        )

        latest_response = text

        return text


    except Exception as e:

        print("LearnMate Error:", e)

        error_message = str(e)

        # ----------------------------
        # Friendly Groq error
        # ----------------------------

        if "model_not_found" in error_message:

            return (
                "⚠️ **AI model error**\n\n"
                "The configured Groq model is currently "
                "unavailable or your API key does not have "
                "access to it.\n\n"
                f"Configured model: `{MODEL}`"
            )


        if "401" in error_message:

            return (
                "⚠️ **Groq API key error**\n\n"
                "Please check your `GROQ_API_KEY` in the "
                "Hugging Face Space Secrets."
            )


        if "429" in error_message:

            return (
                "⚠️ **API rate limit reached.**\n\n"
                "Please wait a moment and try again."
            )


        return (
            "⚠️ **Something went wrong.**\n\n"
            "Please try your question again."
        )


# ================================
# PDF DOWNLOAD
# ================================

def download_pdf():

    global latest_response

    try:

        if not latest_response:

            raise ValueError(
                "No roadmap available."
            )

        return create_pdf(
            latest_response
        )

    except Exception as e:

        print(
            "PDF Error:",
            e
        )

        return None


# ================================
# PREPARE DOWNLOAD
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


# ================================
# GRADIO UI
# ================================

with gr.Blocks(
    css="""
    /* Keep the existing appearance */
    
    @media (max-width: 768px) {
        /* Make the entire app fit the phone width */
        .gradio-container {
            width: 100% !important;
            max-width: 100% !important;
            padding-left: 8px !important;
            padding-right: 8px !important;
            box-sizing: border-box !important;
        }
        /* Prevent components from becoming wider than screen */
        .gradio-container > * {
            max-width: 100% !important;
            box-sizing: border-box !important;
        }
        /* Chat component */
        .chatbot {
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }
        .message {
            max-width: 100% !important;
            box-sizing: border-box !important;
}
        
        p, pre, code {
            max-width: 100% !important;
}
        /* Mobile table fix */
.chatbot table,
.message table {
    display: block !important;
    overflow-x: auto !important;
    width: 100% !important;
    min-width: 650px !important;
}
/* Keep table words intact */
.chatbot table th,
.chatbot table td,
.message table th,
.message table td {
    word-break: normal !important;
    overflow-wrap: normal !important;
}
        /* Input */
        textarea {
            max-width: 100% !important;
            box-sizing: border-box !important;
        }
        /* Buttons */
        button {
            max-width: 100% !important;
            box-sizing: border-box !important;
        }
    }
   @media (max-width: 480px) {
    .gradio-container {
        padding-left: 5px !important;
        padding-right: 5px !important;
    }
    .chatbot {
        width: 100% !important;
    }
    .message {
        max-width: 100% !important;
    }
}
    """
) as demo:

    gr.Markdown(
        "# 🎓 LearnMate AI Coach"
    )

    gr.Markdown(
        "Chat with your AI career mentor 🚀"
    )


    # ============================
    # LEVEL
    # ============================

    level = gr.Radio(

        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ],

        value="Beginner",

        label="Select Level"
    )


    # ============================
    # CHATBOT
    # ============================

    chatbot = gr.ChatInterface(

        fn=learnmate,

        additional_inputs=[
            level
        ],

        textbox=gr.Textbox(

            placeholder=(
                "Example: I want to become "
                "a Full Stack Developer 🚀"
            )
        )
    )


    # ============================
    # PDF SECTION
    # ============================

    gr.Markdown(
        "### 📄 Download Roadmap"
    )


    pdf_btn = gr.Button(
        "Generate PDF"
    )


    pdf_output = gr.DownloadButton(

        label="📥 Download Roadmap PDF",

        visible=False
    )


    pdf_btn.click(

        fn=prepare_download,

        outputs=pdf_output
    )


# ================================
# LAUNCH
# ================================

demo.launch(

    server_name="0.0.0.0",

    server_port=7860
)
