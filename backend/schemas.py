from pydantic import BaseModel, Field
from typing import Optional

class BorrowerInput(BaseModel):
    """
    Defines borrower data input schema for validation via FastAPI.
    """

    loan_amnt: float = Field(..., gt=0, description="Loan amount requested by the borrower.", title="Loan Amount", examples=[15000.0])
    int_rate: float = Field(..., ge=0, le=30, description="Interest rate on the loan (%).", title="Interest Rate", examples=[12.5])
    installment: float = Field(..., gt=0, description="Monthly installment payment.", title="Installment", examples=[450.0])
    sub_grade: float = Field(..., ge=1, le=10, description="Sub-grade of the borrower (1-10).", title="Sub-grade", examples=[5.0])
    annual_inc: float = Field(..., gt=0, description="Borrower's annual income.", title="Annual Income", examples=[60000.0])
    dti: float = Field(..., ge=0, le=100, description="Debt-to-income ratio (%).", title="DTI Ratio", examples=[20.5])
    open_acc: int = Field(..., ge=0, description="Number of open credit lines.", title="Open Accounts", examples=[8])
    revol_util: float = Field(..., ge=0, le=100, description="Revolving line utilization rate (%).", title="Revolving Utilization", examples=[45.2])
    total_acc: int = Field(..., ge=0, description="Total credit accounts.", title="Total Accounts", examples=[15])
    mort_acc: int = Field(..., ge=0, description="Number of mortgage accounts.", title="Mortgage Accounts", examples=[2])
    loan_to_income_ratio: float = Field(..., ge=0, le=1, description="Loan amount divided by annual income.", title="Loan-to-Income Ratio", examples=[0.25])
    credit_utilization_ratio: float = Field(..., ge=0, le=1, description="Ratio of revolving balance to credit limit (revol_util / 100).", title="Credit Utilization Ratio", examples=[0.45])
    pub_rec: Optional[int] = Field(0, ge=0, description="Number of derogatory public records.", title="Public Records", examples=[0])
    revol_bal: Optional[float] = Field(0.0, ge=0, description="Total revolving balance.", title="Revolving Balance", examples=[12000.0])
    pub_rec_bankruptcies: Optional[int] = Field(0, ge=0, description="Number of prior bankruptcies.", title="Public Record Bankruptcies", examples=[0])

    class Config:
        schema_extra = {
            "example": {
                "loan_amnt": 15000.0,
                "int_rate": 12.5,
                "installment": 450.0,
                "sub_grade": 5.0,
                "annual_inc": 60000.0,
                "dti": 20.5,
                "open_acc": 8,
                "revol_util": 45.2,
                "total_acc": 15,
                "mort_acc": 2,
                "loan_to_income_ratio": 0.25,
                "credit_utilization_ratio": 0.452,
                "pub_rec": 0,
                "revol_bal": 12000.0,
                "pub_rec_bankruptcies": 0
            }
        }