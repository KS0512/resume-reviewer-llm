import os
import io
import textwrap
import google.generativeai as genai
import pdfplumber
from flask import Flask, request, jsonify, render_template
import json

# Configure the Gemini API with the key stored as a secret in the environment.
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    print("Gemini API key successfully loaded.")
except KeyError:
    print("Error: GEMINI_API_KEY environment variable not found. Please set it in your environment.")
    exit()

app = Flask(__name__)

# --- Global Error Handler (unchanged) ---
@app.errorhandler(Exception)
def handle_error(e):
    print(f"An unexpected server error occurred: {e}")
    response = {
        "error": f"An internal server error occurred: {str(e)}. Please check the server logs for more details."
    }
    return jsonify(response), 500

# --- Updated System Instructions ---
system_instruction_analysis = textwrap.dedent("""
    You are a world-class resume reviewer and career coach. Your task is to provide a comprehensive, structured analysis of a resume based on a target job role and an optional job description.

    Output must be a single, valid JSON object with EXACTLY THREE keys:

    1. "scores": An object with ratings out of 10 for:
       - "ats_compatibility"
       - "clarity_readability"
       - "impact_achievements"
       - "relevance_to_jd"

    2. "analysis": Markdown with clear SECTIONS. For each section (Education, Experience, Skills, etc.), give:
       - Strengths
       - Weaknesses
       - Suggestions

       Then add an **Overall Evaluation** at the end including:
       - Missing Skills / Keywords (specific, role-relevant)
       - Redundant or Vague Language (list phrases and suggest better alternatives)

       Resume vs Job Description Comparison should also be here, with matches vs gaps.
       Keep the bullets concise and professional. If the resume is not in English, write the analysis in that language.

    3. "highlighted_text": The ORIGINAL resume text, cleaned and formatted (remove weird symbols, fix spacing), with only targeted phrases wrapped in HTML <mark> tags:
       - <mark class="strength" title="WHY this is strong"> for quantified results, impact, aligned skills
       - <mark class="weakness" title="WHY this is weak"> for vague / redundant phrases
       - Keep highlighting selective (≤ 10% of text). Do not over-highlight.
""")

system_instruction_generation = textwrap.dedent("""
    You are a professional resume writer. Take the user's raw resume text and rewrite it into a polished, professional, and well-structured resume tailored for the given job role.

    The output must be ONLY the polished resume text in markdown format.

    Focus on:
    - Clarity and Conciseness (no fluff).
    - Strong action verbs and quantified achievements.
    - Tailoring to the target role.
    - Accurate, ethical enhancement of phrasing (no fabrication).
    - Use headings, bolding, and bullet points for readability.

    If the input resume is not in English, produce the resume in the SAME language with appropriate regional conventions.
""")

def extract_resume_text(request_form, request_files):
    """
    Extracts resume text from either a text area or a PDF file upload.
    Returns the text content or an error message.
    """
    if 'resumeFile' in request_files:
        resume_file = request_files['resumeFile']
        if resume_file.filename != '':
            try:
                # Read the file into an in-memory buffer
                pdf_stream = io.BytesIO(resume_file.read())
                with pdfplumber.open(pdf_stream) as pdf:
                    resume_text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            resume_text += page_text + "\n"
                # If nothing extracted:
                if not resume_text.strip():
                    return None, "Could not extract text from the PDF. It might be an image-based file (like a scan). Please use a text-based PDF or paste the text directly."
                # Clean up formatting
                resume_text = " ".join(resume_text.split())
                return resume_text, None
            except Exception as e:
                return None, f"Failed to process PDF: {str(e)}. The file may be corrupted."
    # Fallback to text area input
    resume_text = request_form.get('resume', '')
    if not resume_text.strip():
        return None, "Resume text is required. Please paste text or upload a file."
    return resume_text, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    resume_text, error = extract_resume_text(request.form, request.files)
    if error:
        return jsonify({"error": error}), 400

    job_role = request.form.get('job_role', '')
    job_description = request.form.get('job_description', '')
    if not job_role:
        return jsonify({"error": "A target job role is required."}), 400

    user_prompt = f"Resume:\n---\n{resume_text}\n---\n\nJob Role:\n---\n{job_role}\n---\n\nJob Description (Optional):\n---\n{job_description}\n---"

    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction_analysis
        )
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json"
        )
        response = model.generate_content(user_prompt, generation_config=generation_config)
        response_json = json.loads(response.text)
        return jsonify(response_json)
    except Exception as e:
        print(f"API Error in /analyze: {e}")
        return jsonify({"error": f"Failed to get analysis. An API error occurred. Details: {str(e)}"}), 500

@app.route('/generate', methods=['POST'])
def generate_resume():
    resume_text, error = extract_resume_text(request.form, request.files)
    if error:
        return jsonify({"error": error}), 400

    job_role = request.form.get('job_role', '')
    if not job_role:
        return jsonify({"error": "A target job role is required to generate the resume."}), 400

    user_prompt = f"Resume:\n---\n{resume_text}\n---\n\nJob Role:\n---\n{job_role}\n---"

    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction_generation
        )
        response = model.generate_content(user_prompt)
        return jsonify({"polishedResume": response.text})
    except Exception as e:
        print(f"API Error in /generate: {e}")
        return jsonify({"error": f"Failed to generate resume. An API error occurred. Details: {str(e)}"}), 500

if __name__ == '__main__':
    # Keep original behavior
    app.run(host='0.0.0.0', port=5000, debug=True)
