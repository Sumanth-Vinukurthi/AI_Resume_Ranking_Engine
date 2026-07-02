import json
from urllib import response
from Graph import state
from Graph import state
from Graph.state import RecruitmentState
import docx2txt
from langchain_google_genai import ChatGoogleGenerativeAI
from Graph.prompts import jd_prompt
from langchain_core.messages import HumanMessage, ToolMessage,AIMessage,SystemMessage
from langchain_community.vectorstores import FAISS
from parser import json_to_documents
from models import embeddings
# from sentence_transformers import CrossEncoder
# from FlagEmbedding import FlagReranker
from parser import json_to_documents,build_candidate_text
from models import reranker,CandidateResponse,JDModel
import time
import csv
import os

llm = ChatGoogleGenerativeAI(

        model="gemini-2.5-flash-lite",   # or gemini-1.5-pro
        temperature=0.1,
        google_api_key = ""
    )


def jd_extraction_node(state: RecruitmentState): 

    print("Entered jd_extraction_node")

    count = 0
    with open(state["candidates_file_path"],"r",encoding="utf-8") as f:
 
        for _ in f:
            count += 1
 
    state["total_candidates"] = count
    jd_text = docx2txt.process(state["jd_file_path"])
    structured_llm = (llm.with_structured_output(JDModel))
    jd = structured_llm.invoke([SystemMessage(content=jd_prompt),HumanMessage(content=jd_text)])
    # print("extracted jd : ",jd.model_dump())
    state["jd"] = jd.model_dump()

    return state

 
def experience_score_node(state: RecruitmentState):
    print("Entered experience_score_node")

    required_exp = state["jd"].get("ideal_candidate_profile", 0).get("total_experience_years",0).get("min",0)
        
    with open(state["candidates_file_path"],"r",encoding="utf-8") as source, open("outputs/experience_scores.jsonl","w",encoding="utf-8") as target:

        if required_exp == 0:
 
            for line in source:
    
                candidate = json.loads(line)
    
                # exp = candidate["profile"].get("years_of_experience",0)
    
                target.write(json.dumps({"candidate_id":candidate["candidate_id"],"score":100})+ "\n")

        else:

            for line in source:
    
                candidate = json.loads(line)
                exp = candidate["profile"].get("years_of_experience",0)
                score = (exp * 100)/required_exp #min(exp / max(required_exp, 1),1) * 100
                if score > 100:
                    score = 100

                target.write(json.dumps({"candidate_id":candidate["candidate_id"],"score":round(score, 2)})+ "\n")

    return {}
 
 
PROFICIENCY = {
 
    "beginner": 0.4,
 
    "intermediate": 0.7,
 
    "advanced": 1.0
}
 
 
def skill_score_node(state: RecruitmentState):
    print("Entered skill_score_node")
 
    required_skills = [skill.lower() for skill in state["jd"].get("required_skills",[])]
    required_skills.extend([skill.lower() for skill in state["jd"].get("preferred_skills",[])])
 
    with open(state["candidates_file_path"],"r",encoding="utf-8") as source, open("outputs/skill_scores.jsonl","w",encoding="utf-8") as target:
        for line in source:
            candidate = json.loads(line)
 
            score = 0
 
            for skill in candidate.get(
                "skills",
                []
            ): 
                name = (
                    skill["name"]
                    .lower()
                )
 
                if name not in required_skills:
                    continue
 
                prof = PROFICIENCY.get(
                    skill[
                        "proficiency"
                    ].lower(),
                    0.4
                )
 
                duration = min(
                    skill.get(
                        "duration_months",
                        0
                    ) / 24,
                    1
                )
 
                endorsements = min(
                    skill.get(
                        "endorsements",
                        0
                    ) / 50,
                    1
                )
 
                score += ( prof * 60 + duration * 20 + endorsements * 20)
 
            if required_skills:
 
                score = score / len(required_skills)
 
            score = min(score,100)
 
            target.write(json.dumps({"candidate_id":candidate["candidate_id"],"score":round(score, 2)})+ "\n")
 
    return {}
 

def career_score_node(state: RecruitmentState):
    print("Entered career_score_node")


    with open(
        state["candidates_file_path"],
        "r",
        encoding="utf-8"
    ) as source, open(
        "outputs/career_scores.jsonl",
        "w",
        encoding="utf-8"
    ) as target:

        for line in source:

            candidate = json.loads(line)

            score = candidate.get("score", 0)

            career_score = 0

            history = candidate.get("career_history", [])

            # Company size score
            largest_company = 0

            for job in history:

                size = str(job.get("company_size", ""))

                if "10001" in size:
                    largest_company = max(largest_company, 25)

                elif "1001" in size:
                    largest_company = max(largest_company, 20)

                elif "201" in size:
                    largest_company = max(largest_company, 15)

            career_score += largest_company

            # Stability score
            if history:

                avg_months = (
                    sum(
                        h.get("duration_months", 0)
                        for h in history
                    )
                    / len(history)
                )

                if avg_months >= 24:
                    career_score += 25

                elif avg_months >= 12:
                    career_score += 15

                elif avg_months >= 6:
                    career_score += 5

            # Seniority score
            title = (
                candidate.get("profile", {})
                .get("current_title", "")
                .lower()
            )

            if any(
                x in title
                for x in [
                    "principal",
                    "staff",
                    "architect",
                    "lead",
                    "manager"
                ]
            ):
                career_score += 25

            elif "senior" in title:
                career_score += 15

            # Product company score
            industries = " ".join(
                h.get("industry", "").lower()
                for h in history
            )

            if any(
                x in industries
                for x in [
                    "software",
                    "internet",
                    "saas",
                    "artificial intelligence",
                    "fintech"
                ]
            ):
                career_score += 25

            target.write(
                json.dumps(
                    {
                        "candidate_id": candidate["candidate_id"],
                        "score": score + career_score
                    }
                )
                + "\n"
            )

    return {}

def behavior_score_node(state: RecruitmentState):

    print("Entered behavior_score_node")

    with open(state["candidates_file_path"],"r",encoding="utf-8") as source, open("outputs/behavior_scores.jsonl","w",encoding="utf-8") as target:

        for line in source:

            candidate = json.loads(line)

            signals = candidate["redrob_signals"]

            score = 0
 
            if signals.get("open_to_work_flag"):
                score += 20

            score += (signals.get("recruiter_response_rate",0) * 30)
            score += (signals.get("interview_completion_rate",0) * 30)
            score += (signals.get("offer_acceptance_rate",0) * 20)
            score = min(score,100)
            target.write(json.dumps({"candidate_id":candidate["candidate_id"],"score":round(score, 2)})+ "\n")

    return {}
 
def availability_score_node(state: RecruitmentState):
    print("Entered availability_score_node")
 
    with open(state["candidates_file_path"],"r",encoding="utf-8") as source, open("outputs/availability_scores.jsonl","w",encoding="utf-8") as target:
 
        for line in source:
 
            candidate = json.loads(line)
 
            signals = candidate["redrob_signals"]
 
            notice = signals.get("notice_period_days",90)
 
            score = 0
 
            if notice <= 30:
                score += 60
 
            elif notice <= 60:
                score += 40
 
            if signals.get("willing_to_relocate"):
                score += 40
 
            score = min(score,100)
 
            target.write(json.dumps({
                                        "candidate_id":candidate["candidate_id"],
                                        "score":score
                                            
                                    })+ "\n")
 
    return {}

def avg_score_node(state: RecruitmentState):
    print("Entered avg_score_node")

    score_files = [
        open("outputs/skill_scores.jsonl"),
        open("outputs/experience_scores.jsonl"),
        open("outputs/career_scores.jsonl"),
        open("outputs/behavior_scores.jsonl"),
        open("outputs/availability_scores.jsonl")
    ]
    
    with open(state["candidates_file_path"],"r",encoding="utf-8") as candidates, open("outputs/updated_candidates.jsonl", "w") as out:
        
        for candidate_line, score_lines in zip(candidates, zip(*score_files)):
    
            # Load candidate record
            candidate = json.loads(candidate_line)
    
            # Load all score records
            records = [json.loads(line) for line in score_lines]
    
            # Compute average score
            avg_score = sum(r["score"] for r in records) / len(records)
    
            # Add to candidate record
            candidate["average_score"] = round(avg_score, 2)
    
            # Write updated record
            out.write(json.dumps(candidate) + "\n")
        
    for f in score_files:
        f.close()
            
    return state

import json
 
 
def percentile_filter_node(state):

    print("Entered percentile_filter_node")
 
    total_candidates = state["total_candidates"]
 
    # -----------------------
    # Dynamic Filtering
    # -----------------------
 
    if total_candidates >= 100000:
 
        keep_pct = 0.02
 
    elif total_candidates >= 50000:
 
        keep_pct = 0.03
 
    elif total_candidates >= 10000:
 
        keep_pct = 0.05
 
    elif total_candidates >= 5000:
 
        keep_pct = 0.10
 
    else:
 
        keep_pct = 0.20
 
    # -----------------------
    # Load Scores
    # -----------------------
 
    candidates = []
 
    with open("outputs/updated_candidates.jsonl","r",encoding="utf-8") as f:
 
        for line in f:
 
            candidates.append(json.loads(line))
 
    # -----------------------
    # Sort Descending
    # -----------------------
 
    candidates.sort(key=lambda x: x["average_score"],reverse=True)
 
    # -----------------------
    # Keep Top %
    # -----------------------
 
    keep_count = max(1,int(len(candidates)* keep_pct))
 
    shortlisted = (candidates[:keep_count])
 
    # -----------------------
    # Save
    # -----------------------
 
    with open("outputs/filtered_candidates.jsonl","w",encoding="utf-8") as f:
 
        for candidate in shortlisted[:keep_count]:
 
            f.write(json.dumps(candidate)+ "\n")
 
    print(f"\nTotal Candidates : {len(candidates)}")
 
    print(f"Keeping Top {keep_pct * 100:.0f}%")
 
    print(f"Candidates After Filter : "f"{len(shortlisted)}")
    state["total_candidates"] = len(shortlisted)
 
    return state

def ingest_documents(state:RecruitmentState):
    vectorstore_path="data/resume_vectorstore"
    print("Entered ingestion node.")
    resumes=[]
    with open("outputs/filtered_candidates.jsonl","r") as f:
        for line in f:
            if line.strip():
                resumes.append(json.loads(line))
    print("resumes done")
    resume_documents=json_to_documents(resumes)
    print("len of resume documents:")
    vectorstore = FAISS.from_documents(resume_documents, embeddings)
    texts = [doc.page_content for doc in resume_documents]

    vectors = embeddings.embed_documents(texts)

    vectorstore = FAISS.from_embeddings(
        list(zip(texts, vectors)),
        embedding=embeddings
    )
    print("vector store created")
    vectorstore.save_local(vectorstore_path)
    return state

def retrieval_and_ranking_node(state:RecruitmentState):
    jd_text = state["jd"].get("job_title", "") + " " + \
              " ".join(state["jd"].get("required_skills", [])) + " " + \
              " ".join(state["jd"].get("required_concepts", [])) + " " + \
              " ".join(state["jd"].get("required_tools", []))
    
    vectorstore = FAISS.load_local(
        "data/resume_vectorstore",
        embeddings,
        allow_dangerous_deserialization=True
    )
    print("total top k:", state["total_candidates"]*0.1)
    retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k":int(state["total_candidates"]*0.1)
    }
)

    results = retriever.invoke(
        jd_text
    )

    print("retreived results:",results)
    pairs = [
        [jd_text, doc.page_content]
        for doc in results
    ]

    scores = reranker.compute_score(pairs,normalize= True)

    docs_with_scores={}
    for i in range(len(scores)):
        docs_with_scores[results[i]]=scores[i]

    docs_with_sorted_scores= sorted(
            docs_with_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
    
    with open("outputs/top_ranked_candidates.jsonl","w",encoding="utf-8") as f:
        for doc, score in docs_with_sorted_scores[:101]:
            f.write(json.dumps({"candidate_id":doc.metadata.get("candidate_id", ""), "score": score,"candidate": doc}) + "\n")

    return state


def llm_evaluation_node(state:RecruitmentState):
    print("Entered llm_evaluation_node")
    input_jsons=[]
    with open("outputs/top_ranked_candidates.jsonl","r",encoding="utf-8") as f:
        count=0
        l=""
        for line in f:
            candidate = json.loads(line)
            candidate_text = candidate
            l += str(candidate_text) + "\n"
            count+=1
            if count>5:
                input_jsons.append(l)
                count=0
                l=""
        if l:   
            input_jsons.append(l)

    jd_text = state["jd"].get("job_title", "") + " " + \
            " ".join(state["jd"].get("required_skills", [])) + " " + \
            " ".join(state["jd"].get("required_concepts", [])) + " " + \
            " ".join(state["jd"].get("required_tools", []))
    
    for batch in input_jsons:
        prompt = f"""
        You are an expert recruiter. Evaluate the following  5 or less candidates against the job description and provide reasoning on how they match the requirements. 
        Job Description: {jd_text}
        Candidates: {batch}
        """
        structured_llm = llm.with_structured_output(CandidateResponse)
        response = structured_llm.invoke([HumanMessage(content=prompt)])
        response= response.model_dump()
        with open("outputs/llm_evaluation.jsonl","a",encoding="utf-8") as out:
            for i in response:
                out.write(json.dumps(response[i])+ "\n")
        print("llm response:",response)
        time.sleep(5)

        with open("outputs/llm_evaluation.jsonl","r",encoding="utf-8") as out, open("outputs/top_ranked_candidates.jsonl","r",encoding="utf-8") as f, open("outputs/final_candidates.jsonl","w",encoding="utf-8") as final:
            llm_evaluations = {}
            c=1
            for line in out:
                eval = json.loads(line)
                llm_evaluations[eval["candidate_id"]] = eval["reasoning"]
            for line in f:
                new_candidate={}
                candidate = json.loads(line)
                candidate_id = candidate["candidate_id"]
                reasoning = llm_evaluations.get(candidate_id, "")
                new_candidate["candidate_id"] = candidate_id
                new_candidate["rank"]=c
                new_candidate["score"] = candidate["score"]
                new_candidate["reasoning"] = reasoning
                final.write(json.dumps(new_candidate)+ "\n")
                c+=1
    
            
    return state

def convert_to_csv(state:RecruitmentState):
    print("Entered convert_to_csv node")
    input_file = "outputs/final_candidates.jsonl"
    output_file = "final_outputs/final_candidates.csv"

    rows = []

    # read jsonl
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))

    # get headers from first row
    headers = rows[0].keys() if rows else []

    # write csv
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    print("Conversion done:", output_file)
    files_to_delete = [
    "outputs/availability_scores.jsonl",
    "outputs/behavior_scores.jsonl",
    "outputs/career_scores.jsonl",
    "outputs/experience_scores.jsonl",
    "outputs/filtered_candidates.jsonl",
    "outputs/skill_scores.jsonl",
    "outputs/top_ranked_candidates.jsonl",
    "outputs/llm_evaluation.jsonl",
    "outputs/updated_candidates.jsonl",
    ]

    for file in files_to_delete:
        if os.path.exists(file):
            os.remove(file)