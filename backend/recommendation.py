# recommendation.py
from datetime import datetime

def recommend_action(probability: float, borrower: dict):
    """
    Generates a fully detailed loan recommendation based on predicted default probability
    and borrower financial attributes.
    """

    p = probability
    reasoning = []

    # Extract borrower attributes safely
    loan_amnt = borrower.get("loan_amnt", 0)
    annual_inc = borrower.get("annual_inc", 0)
    dti = borrower.get("dti", 0)
    revol_util = borrower.get("revol_util", 0)
    sub_grade = borrower.get("sub_grade", "")
    open_acc = borrower.get("open_acc", 0)
    total_acc = borrower.get("total_acc", 0)
    mort_acc = borrower.get("mort_acc", 0)
    revol_bal = borrower.get("revol_bal", 0)
    pub_rec_bankruptcies = borrower.get("pub_rec_bankruptcies", 0)
    loan_to_income_ratio = borrower.get("loan_to_income_ratio", 0)

    # Thresholds
    VERY_LOW = 0.15
    LOW = 0.30
    MODERATE = 0.45
    HIGH = 0.60

    # -----------------------------
    # VERY LOW RISK
    # -----------------------------
    if p <= VERY_LOW:
        decision = "APPROVE LOAN"
        risk = "VERY LOW RISK"

        reasoning.append("The borrower demonstrates excellent repayment capacity with minimal risk indicators.")
        reasoning.append(f"Strong annual income (${annual_inc:,.2f}) relative to loan amount (${loan_amnt:,.2f}).")
        reasoning.append(f"Low debt-to-income ratio ({dti:.2f}%), indicating room for additional financial obligations.")
        
        if revol_util < 30:
            reasoning.append(f"Very healthy revolving utilization ({revol_util:.2f}%).")
        if loan_to_income_ratio < 0.2:
            reasoning.append("Loan amount is very small relative to income, reducing exposure.")
        if mort_acc >= 1:
            reasoning.append(f"Borrower has {mort_acc} mortgage account(s), indicating financial maturity.")
        if sub_grade in ["A1", "A2", "A3", "B1"]:
            reasoning.append(f"Excellent credit sub-grade ({sub_grade}), consistent with strong creditworthiness.")

        reasoning.append("Loan is considered safe and can be approved confidently with favorable terms.")

    # -----------------------------
    # LOW RISK
    # -----------------------------
    elif p <= LOW:
        decision = "APPROVE LOAN"
        risk = "LOW RISK"

        reasoning.append("Borrower's financial profile shows generally stable and low-risk behavior.")
        reasoning.append(f"Income of ${annual_inc:,.2f} supports repayment confidence.")
        
        if 20 <= dti <= 35:
            reasoning.append(f"Moderate debt-to-income ratio ({dti:.2f}%).")
        if 30 <= revol_util <= 50:
            reasoning.append(f"Reasonable revolving utilization ({revol_util:.2f}%), still within healthy bounds.")
        if loan_to_income_ratio <= 0.3:
            reasoning.append("Loan-to-income ratio is acceptable and manageable.")

        reasoning.append("Loan can be approved, possibly with standard terms.")

    # -----------------------------
    # MODERATE RISK
    # -----------------------------
    elif p <= MODERATE:
        decision = "APPROVE WITH CONDITIONS"
        risk = "MODERATE RISK"

        reasoning.append("The borrower shows moderate risk of default. Caution is advised.")
        reasoning.append("Approval possible but additional controls are recommended.")

        if dti > 35:
            reasoning.append(f"Elevated debt-to-income ratio ({dti:.2f}%) may strain repayment ability.")
        if revol_util > 50:
            reasoning.append(f"Credit utilization is moderately high ({revol_util:.2f}%), indicating dependency on revolving credit.")
        if pub_rec_bankruptcies > 0:
            reasoning.append("Past bankruptcy record increases risk profile.")
        if loan_to_income_ratio > 0.35:
            reasoning.append(f"Loan request (${loan_amnt:,.2f}) is high relative to income (${annual_inc:,.2f}).")

        reasoning.append("Recommend approval with conditions such as reduced loan amount, collateral, or slightly higher interest rate.")

    # -----------------------------
    # HIGH RISK
    # -----------------------------
    elif p <= HIGH:
        decision = "DECLINE LOAN"
        risk = "HIGH RISK"

        reasoning.append("Borrower presents multiple high-risk indicators that increase chances of default.")
        reasoning.append(f"Predicted default probability of {p:.2%} exceeds safe lending thresholds.")

        if dti > 40:
            reasoning.append(f"High DTI ({dti:.2f}%) shows borrower may already be financially stretched.")
        if revol_util > 70:
            reasoning.append(f"Very high revolving utilization ({revol_util:.2f}%), indicating credit stress.")
        if pub_rec_bankruptcies > 0:
            reasoning.append(f"{pub_rec_bankruptcies} recorded bankruptcies significantly worsen the risk profile.")
        if loan_to_income_ratio > 0.4:
            reasoning.append("Loan amount is too large compared to income, increasing repayment failure risk.")

        reasoning.append("Loan is not advisable based on the borrower’s current financial stability.")

    # -----------------------------
    # VERY HIGH RISK
    # -----------------------------
    else:
        decision = "DECLINE LOAN"
        risk = "VERY HIGH RISK"

        reasoning.append("Extremely high probability of default indicates severe risk.")
        reasoning.append("Borrower exhibits financial distress patterns that could lead to non-payment.")

        if dti > 50:
            reasoning.append(f"Very high DTI ({dti:.2f}%) signals inability to take on additional credit.")
        if revol_util > 80:
            reasoning.append(f"Critical revolving utilization ({revol_util:.2f}%) indicates urgent financial strain.")
        if pub_rec_bankruptcies > 1:
            reasoning.append("Multiple bankruptcies strongly indicate future repayment challenges.")
        if loan_to_income_ratio > 0.5:
            reasoning.append("Loan amount is disproportionately large relative to income.")

        reasoning.append("Loan must be declined to avoid high loss risk and borrower over-extension.")

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "decision": decision,
        "risk_category": risk,
        "probability": probability,
        "reasoning": reasoning
    }
