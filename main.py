from fastapi import FastAPI, UploadFile, File
from pathlib import Path
import shutil
from Graph.builder import graph
from fastapi.middleware.cors import CORSMiddleware
from Graph.response_node import jd_extraction_node
import pandas as pd

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
UPLOAD_DIR = Path("uploads")
 
UPLOAD_DIR.mkdir(
    exist_ok=True
)
 
@app.post("/upload")
async def upload_files( candidates: UploadFile = File(...), job_description: UploadFile = File(...) ):
 
    candidates_path = UPLOAD_DIR / "candidates.jsonl"
 
    jd_path = UPLOAD_DIR/ job_description.filename
 
    with open(candidates_path,"wb") as buffer:
 
        shutil.copyfileobj(candidates.file, buffer)
 
    with open(jd_path,"wb") as buffer:
 
        shutil.copyfileobj(job_description.file,buffer)

    response = graph.invoke({
        "jd_file_path":jd_path,
        "candidates_file_path":candidates_path,
        "jd" : None,
        "total_candidates" : None
    })
    df = pd.read_csv("final_outputs/final_candidates.csv")
    return df.to_dict(orient="records")
    





 
