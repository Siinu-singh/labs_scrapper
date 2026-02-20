from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

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


# Batch Scraper Schemas
class StartBatchScrapingRequest(BaseModel):
    """Request to start batch scraping"""
    total_batches: Optional[int] = Field(None, description="Number of batches to scrape. If null, scrapes all tests")
    batch_size: int = Field(10, ge=1, le=50, description="Number of tests per batch")

class BatchScrapingResponse(BaseModel):
    """Response from batch scraping start"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    total_batches: Optional[int] = None
    total_tests: Optional[int] = None

class BatchStatusResponse(BaseModel):
    """Batch scraping status"""
    status: str
    message: Optional[str] = None
    current_batch: Optional[int] = None
    total_batches: Optional[int] = None
    completed_batches: Optional[int] = None
    progress_percent: Optional[float] = None
    batch_size: Optional[int] = None
    started_at: Optional[str] = None
    batches: Optional[Dict[str, Any]] = None

class ResetBatchStateRequest(BaseModel):
    """Request to reset batch state"""
    force: bool = Field(False, description="Force reset even if scraping is in progress")
