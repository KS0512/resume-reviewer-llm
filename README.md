AI Resume Reviewer

A web-based SaaS application that leverages **Google Gemini AI** to analyze and improve resumes.  
The app provides detailed feedback on **ATS compatibility, clarity, impact, and relevance**, and also generates a **polished resume** tailored to the target job role.

Features

- Upload resume as **text** or **PDF**
- Get **ATS, clarity, impact, and relevance scores** (out of 10)
- Receive a **section-wise analysis** with strengths, weaknesses, and suggestions
- **Highlights resume text** (strengths & gaps with hover explanations)
- Compare **resume vs job description**
- Generate a **polished professional resume** tailored to a specific role
- Clean and modern UI with hover tooltips for highlights

Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, JavaScript
- **AI Model:** Google Gemini (`gemini-1.5-flash`)
- **PDF Processing:** pdfplumber
- **Deployment:** Render (free tier)

Project Structure

resume-reviewer-llm/
│
├── app.py                # Flask backend
├── requirements.txt      # Python dependencies
├── Procfile              # For Render deployment (Gunicorn entrypoint)
├── templates/
│   └── index.html        # Main frontend
├── static/
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript
│   └── assets/           # Icons, images (optional)
└── README.md             # Documentation

Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/ks0512/resume-reviewer-llm.git
cd resume-reviewer-llm
```

### 2. Create & Activate Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # for Mac/Linux
venv\Scripts\activate      # for Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variable (Gemini API Key)
- Get your Gemini API key from: [Google AI Studio](https://aistudio.google.com)  
- Add it to your environment:

Mac/Linux:
bash
export GEMINI_API_KEY="your_api_key_here"

Windows (PowerShell):
powershell
setx GEMINI_API_KEY "your_api_key_here"


### 5. Run the Application Locally
bash
python app.py

Visit: [http://localhost:5000](http://localhost:5000)

Deployment (Render)

1. Push code to GitHub
2. Create a new Web Service on [Render](https://render.com)
3. Connect your GitHub repo
4. Add environment variable:
   - `GEMINI_API_KEY` = `your_api_key_here`
5. Add `Procfile`:
      web: gunicorn app:app
6. Render will build and deploy automatically
7. Get your live URL (e.g., `https://genai-resume-reviewer.onrender.com`)

API Endpoints

### POST /analyze
Analyze resume against job role & optional job description.

**Request:**
- Form-data:
  - `resume` (text) or `resumeFile` (PDF)
  - `job_role` (required)
  - `job_description` (optional)

**Response:**
```json
{
  "scores": {
    "ats_compatibility": 8,
    "clarity_readability": 7,
    "impact_achievements": 6,
    "relevance_to_jd": 7
  },
  "analysis": "...markdown content...",
  "highlighted_text": "...resume with <mark> tags..."
}
```
### `POST /generate`
Generate a polished resume for a given job role.

**Request:**
- Form-data:
  - `resume` (text) or `resumeFile` (PDF)
  - `job_role` (required)

**Response:**
```json
{
  "polishedResume": "...formatted resume text..."
}
```

Team Members

- [Khilna Shah](https://github.com/ks0512)  
- [Leema B Jacob](https://github.com/leemzz) 
- [Kavinithi Sera](https://github.com/kavinithi-sera) 
- Shweta Yadav

Notes

- Render apps may sleep after inactivity, UptimeRobot is used to keep it alive.  
- Ensure resumes are text-based PDFs (not scanned images).  
- API quota depends on Gemini API key limits.
- This project is for academic/demo purposes.  
- Do not use to misrepresent resumes or fabricate details.
