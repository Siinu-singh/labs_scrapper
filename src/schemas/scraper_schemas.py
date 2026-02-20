from enum import Enum
from pydantic import BaseModel, Field

class LabName(str, Enum):
    ONEMG = "1mg"
    ORANGE = "orange"
    REDCLIFFE = "redcliffe"
    LALPATHLABS = "lalpathlabs"

class ScrapeRequest(BaseModel):
    test_name: str = Field(min_length=1, max_length=200)
    lab_name: LabName

class TestResult(BaseModel):
    test_name: str
    price: str

class ScrapeResponse(BaseModel):
    lab: str
    test_searched: str
    results: list[TestResult]
    count: int
    
class ComparisonRequest(BaseModel):
    test_name: str = Field(min_length=1, max_length=200)
    
class LabComparison(BaseModel):
    lab: str
    test_name: str
    price: str
    
class ComparisonResponse(BaseModel):
    test_searched: str
    comparison: list[LabComparison]
