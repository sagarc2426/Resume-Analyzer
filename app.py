import os
from flask import Flask, render_template, request
from resume_parser import extract_text_from_pdf, clean_text, semantic_match, extract_skills, SKILL_SET

app = Flask(__name__)
UPLOAD_FOLDER = 'resumes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_job_roles():
    roles = {}
    for filename in os.listdir("job_roles"):
        if filename.endswith(".txt"):
            role_name = filename.replace("_", " ").replace(".txt", "").title()
            roles[role_name] = os.path.join("job_roles", filename)
    return roles

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    matched_skills = []
    missing_skills = []
    selected_role = ""
    selected_exp = ""
    selected_type = ""

    job_roles = get_job_roles()

    if request.method == "POST":
        role = request.form.get("role")
        experience = request.form.get("experience")
        job_type = request.form.get("job_type")
        resume_file = request.files.get("resume")

        selected_role = role
        selected_exp = experience
        selected_type = job_type

        if not role or role not in job_roles or resume_file.filename == '' or not experience or not job_type:
            result = "⚠️ Please fill out all fields and upload a resume."
        else:
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_file.filename)
            resume_file.save(resume_path)

            resume_text = clean_text(extract_text_from_pdf(resume_path))
            with open(job_roles[role], "r") as f:
                jd_text = clean_text(f.read())

            score = semantic_match(resume_text, jd_text)

            print("📝 Resume Text:", resume_text[:500])
            print("📋 JD Text:", jd_text[:500])
            print("📊 Match Score:", score)

            threshold = {
                "Fresher": 60,
                "Intermediate": 70,
                "Senior": 80
            }.get(experience, 70)

            if score >= threshold:
                result = (
                    f"✅ Yes, your resume matches for the {experience} {job_type} {role} role! (Score: {score}%)"
                )
            else:
                result = (
                    f"❌ No, your resume does not match well for the {experience} {job_type} {role} role. (Score: {score}%)"
                )

            role_skills = SKILL_SET.get(role, [])
            matched_skills = extract_skills(resume_text, role_skills)
            missing_skills = list(set(role_skills) - set(matched_skills))

    return render_template("index.html", roles=job_roles.keys(), result=result,
                           matched_skills=matched_skills, missing_skills=missing_skills,
                           selected_role=selected_role, selected_exp=selected_exp, selected_type=selected_type)

if __name__ == "__main__":
    if not os.path.exists("resumes"):
        os.makedirs("resumes")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
