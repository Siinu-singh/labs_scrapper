from fastapi import HTTPException, status

class ScraperException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class InvalidLabException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid lab name. Supported: 1mg, orange, redcliffe, lalpathlabs"
        )
