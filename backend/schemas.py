from pydantic import BaseModel, Field
from typing import Optional

class BorrowerInput(BaseModel):
    loan_amnt: float
    int_rate: float
    installment: float
    sub_grade: str
    annual_inc: float
    dti: float
    open_acc: int
    revol_util: float
    total_acc: int
    mort_acc: int
    pub_rec: int = 0
    revol_bal: float = 0.0
    pub_rec_bankruptcies: int = 0
