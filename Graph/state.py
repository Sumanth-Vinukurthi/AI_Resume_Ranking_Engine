from typing import TypedDict,List,Optional
from pydantic import BaseModel


class RecruitmentState(TypedDict):

    jd_file_path : str
    candidates_file_path : str

    jd : dict | None
    total_candidates : list | None

