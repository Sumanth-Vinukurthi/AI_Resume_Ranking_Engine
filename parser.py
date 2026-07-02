from langchain_core.documents import Document
import json

# def json_to_documents(json_data: list):
#     documents = []
#     for data in json_data:
#         data_in_str=""
#         for k,v in data.items():
#             if isinstance(v, list):
#                 list_to_string= ', '.join(str(item) for item in v)
#                 data_in_str+= f"{k}: {list_to_string}\n"
#             else:
#                 data_in_str+=f"{k}: {v}\n"
        
#         documents.append(Document(page_content=data_in_str))

#     return documents


# def json_to_documents(json_data):

#     documents = []

#     for resume in json_data:

#         documents.append(
#             Document(
#                 page_content=json.dumps(resume, indent=2)
#             )
#         )

#     return documents


# from langchain_core.documents import Document

def json_to_documents(json_data):

    documents = []

    for r in json_data:

        candidate_id = r.get("candidate_id")

        profile = r.get("profile", {})
        skills = r.get("skills", [])
        career = r.get("career_history", [])

        skill_text = " ".join([s.get("name","") for s in skills])

        career_text = " ".join(
            c.get("title","") + " " + c.get("description","")
            for c in career
        )

        text = f"""
        TITLE: {profile.get("current_title","")}
        SUMMARY: {profile.get("summary","")}
        SKILLS: {skill_text}
        CURRENT COMPANY: {profile.get("current_company","")}
        CAREER: {career_text}
        LOCATION: {profile.get("location","")}
        """.strip()

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "candidate_id": candidate_id   
                }
            )
        )
    print("Parsing done")
    return documents


def build_candidate_text(documents):
    output = []

    for c in documents:
        candidate_id = c.get("candidate_id", "")

        profile = c.get("profile", {})
        signals = c.get("redrob_signals", {})
        skills = c.get("skills", [])
        career = c.get("career_history", [])

        skill_text = ", ".join([s.get("name", "") for s in skills])

        career_text = " | ".join([
            f"{j.get('title','')} at {j.get('company','')} ({j.get('industry','')})"
            for j in career
        ])

        signal_text = f"""
        response_rate: {signals.get("recruiter_response_rate", 0)}
        interview_rate: {signals.get("interview_completion_rate", 0)}
        github_activity: {signals.get("github_activity_score", 0)}
        notice_period_days: {signals.get("notice_period_days", 90)}
        open_to_work: {signals.get("open_to_work_flag", False)}
        """

        text = f"""
        TITLE: {profile.get("current_title", "")}
        SUMMARY: {profile.get("summary", "")}
        EXPERIENCE_YEARS: {profile.get("years_of_experience", "")}

        SKILLS: {skill_text}

        CAREER_HISTORY: {career_text}

        SIGNALS:
        {signal_text}
        """

        output.append({
            "candidate_id": candidate_id,
            "text": text.strip(),
            "raw": c
        })

    return output