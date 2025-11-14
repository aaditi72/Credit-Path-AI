from pydantic import BaseModel, Field
from typing import Optional

class BorrowerInput(BaseModel):
    loan_amnt: float = Field(..., gt=0)
    int_rate: float = Field(..., ge=0, le=50)
    installment: float = Field(..., gt=0)

    # Subgrade must be string like "A3", "B1", etc.
    sub_grade: str = Field(..., description="Borrower subgrade label (example: 'B3')")

    annual_inc: float = Field(..., gt=0)
    dti: float = Field(..., ge=0, le=100)

    open_acc: int = Field(..., ge=0)
    revol_util: float = Field(..., ge=0, le=100)
    total_acc: int = Field(..., ge=0)
    mort_acc: int = Field(..., ge=0)

    # Optional fields
    pub_rec: Optional[int] = 0
    revol_bal: Optional[float] = 0.0
    pub_rec_bankruptcies: Optional[int] = 0

    class Config:
        schema_extra = {
            "example": {
                "loan_amnt": 15000,
                "int_rate": 12.5,
                "installment": 450,
                "sub_grade": "B3",
                "annual_inc": 60000,
                "dti": 20.5,
                "open_acc": 8,
                "revol_util": 45.2,
                "total_acc": 15,
                "mort_acc": 2,
                "pub_rec": 0,
                "revol_bal": 12000,
                "pub_rec_bankruptcies": 0
            }
        }
