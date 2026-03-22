from pydantic import BaseModel
from typing import List

class SearchQuery(BaseModel):
    query: str

class ReferenceModel(BaseModel):
    code_snippet: str
    relevance_score: int
    file_path: str
    start_line: int
    end_line: int
    type: str

class SearchResponseModel(BaseModel):
    agent_message: str
    references: List[ReferenceModel]
