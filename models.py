from FlagEmbedding import FlagReranker
from langchain_huggingface import HuggingFaceEmbeddings
from pydantic import BaseModel,Field
from typing import TypedDict,List,Optional

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    encode_kwargs={
        "batch_size": 256,  
        "normalize_embeddings": True
    }
)


reranker = FlagReranker(
    "BAAI/bge-reranker-v2-m3",
    # use_fp16=True
)


class Candidate(BaseModel):
    candidate_id: str
    reasoning: str

class CandidateResponse(BaseModel):
    candidate_1: Optional[Candidate] = Field(default=None)
    candidate_2: Optional[Candidate] = Field(default=None)
    candidate_3: Optional[Candidate] = Field(default=None)
    candidate_4: Optional[Candidate] = Field(default=None)
    candidate_5: Optional[Candidate] = Field(default=None)


class Location(BaseModel):
    preferred: List[str]
    acceptable: List[str]
    relocation_allowed: bool
 
 
class ExperienceRange(BaseModel):
    min: float
    max: float
 
 
class Experience(BaseModel):
    preferred_range_years: ExperienceRange
    minimum_judgment_level: Optional[str] = None
 
 
class MandatoryRequirements(BaseModel):
    production_ml_experience: bool = False
    production_embedding_retrieval_experience: bool = False
    vector_database_experience: bool = False
    python: bool = False
    ranking_evaluation_experience: bool = False
 
 
class BehavioralSignals(BaseModel):
    startup_mindset: bool = False
    product_thinking: bool = False
    ship_fast: bool = False
    async_communication: bool = False
    comfortable_with_ambiguity: bool = False
 
 
class IdealCandidateProfile(BaseModel):
 
    total_experience_years: ExperienceRange
 
    applied_ai_experience_years: ExperienceRange
 
    has_production_ranking_system: bool = False
 
    has_production_search_system: bool = False
 
    has_production_recommendation_system: bool = False
 
    product_company_background: bool = False
 
 
class RankingWeights(BaseModel):
 
    production_retrieval_experience: float
 
    ranking_system_experience: float
 
    evaluation_experience: float
 
    vector_database_experience: float
 
    python_strength: float
 
    startup_product_fit: float
 
    behavioral_signals: float
 
 
class JDModel(BaseModel):
 
    job_title: str
 
    company: Optional[str] = None
 
    employment_type: Optional[str] = None
 
    location: Location
 
    experience: Experience
 
    mandatory_requirements: MandatoryRequirements
 
    required_skills: List[str]
 
    required_tools: List[str]
 
    required_concepts: List[str]
 
    preferred_skills: List[str]
 
    responsibilities: List[str]
 
    behavioral_signals: BehavioralSignals
 
    disqualifiers: List[str]
 
    ideal_candidate_profile: IdealCandidateProfile
 
    ranking_weights: RankingWeights