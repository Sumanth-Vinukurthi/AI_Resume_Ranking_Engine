from Graph.state import RecruitmentState
from langgraph.graph import StateGraph, START, END 
# from Graph.response_nodes import jd_extraction_node,advance_ranking_node,rag_node,skill_match_node,shortlist_node,qualification_filter_node,experience_score_node
from Graph.response_node import jd_extraction_node,experience_score_node,skill_score_node,career_score_node,behavior_score_node,availability_score_node,avg_score_node,percentile_filter_node,ingest_documents,retrieval_and_ranking_node,llm_evaluation_node,convert_to_csv

agent = StateGraph(RecruitmentState)

agent.add_node("jd_extraction_node",jd_extraction_node)
agent.add_node("experience_score_node",experience_score_node)
agent.add_node("skill_score_node",skill_score_node)
agent.add_node("career_score_node",career_score_node)
agent.add_node("behavior_score_node",behavior_score_node)
agent.add_node("availability_score_node",availability_score_node)
agent.add_node("avg_score_node",avg_score_node)
agent.add_node("percentile_filter_node",percentile_filter_node)
agent.add_node("ingest_documents",ingest_documents)
agent.add_node("retrieval_and_ranking_node",retrieval_and_ranking_node)
agent.add_node("llm_evaluation_node",llm_evaluation_node)
agent.add_node("convert_to_csv",convert_to_csv)

agent.add_edge(
    START,
    "jd_extraction_node"
)
 
agent.add_edge(
    "jd_extraction_node",
    "experience_score_node"
)

agent.add_edge(
    "jd_extraction_node",
    "skill_score_node"
)

agent.add_edge(    
    "jd_extraction_node",
    "career_score_node"
)

agent.add_edge(
    "jd_extraction_node",
    "behavior_score_node"
)

agent.add_edge(
    "jd_extraction_node",
    "availability_score_node"
)

####################################

agent.add_edge(
    "experience_score_node",
    "avg_score_node"
)

agent.add_edge(
    "skill_score_node",
    "avg_score_node"
)

agent.add_edge(
    "career_score_node",
    "avg_score_node"
)

agent.add_edge(
    "behavior_score_node",
    "avg_score_node"
)

agent.add_edge(
    "availability_score_node",
    "avg_score_node"
)
 
agent.add_edge(
    "avg_score_node",
    "percentile_filter_node"
)
 
agent.add_edge(
    "percentile_filter_node",
    "ingest_documents")

agent.add_edge("ingest_documents",
    "retrieval_and_ranking_node")

agent.add_edge(
    "retrieval_and_ranking_node",
    "llm_evaluation_node"
)

agent.add_edge(
    "llm_evaluation_node",
    "convert_to_csv"
)

agent.add_edge(
    "convert_to_csv",
    END 
    )
graph = agent.compile()