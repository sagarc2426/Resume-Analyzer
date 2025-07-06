from flask import Flask, render_template, request
import os
from resume_parser import extract_text_from_pdf, clean_text, match_resume_to_jd

app = Flask(__name__)
UPLOAD_FOLDER = 'resumes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Available roles
JOB_ROLES = {
    "Software Engineer": "job_roles/software_engineer.txt",
    "Data Analyst": "job_roles/data_analyst.txt"
}

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        role = request.form["role"]
        resume_file = request.files["resume"]

        if role not in JOB_ROLES or resume_file.filename == '':
            result = "Please select a valid role and upload a resume."
        else:
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_file.filename)
            resume_file.save(resume_path)

            resume_text = clean_text(extract_text_from_pdf(resume_path))

            with open(JOB_ROLES[role], "r") as f:
                jd_text = clean_text(f.read())

            score = match_resume_to_jd(resume_text, jd_text)

            if score >= 70:
                result = f"✅ Yes, your resume matches for the {role} job perfectly! (Score: {score}%)"
            else:
                result = f"❌ No, your resume does not match well for the {role} role. (Score: {score}%)"

    return render_template("index.html", roles=JOB_ROLES.keys(), result=result)

if __name__ == "__main__":
    if not os.path.exists("resumes"):
        os.makedirs("resumes")
    app.run(debug=True)
