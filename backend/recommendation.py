# --- START OF FILE recommendation.py ---

from datetime import datetime
import logging

print(f"datetime imported: {datetime}")

# Configure basic logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def recommend_action(probability, borrower_data):
    # Initialize reasoning_list at the beginning of the function
    reasoning_list = []

    # Define your risk thresholds
    # Reverting LOW_RISK_THRESHOLD to a more standard/conservative value
    LOW_RISK_THRESHOLD = 0.20   # <= 15% probability -> APPROVE
    MODERATE_RISK_THRESHOLD = 0.40 # > 15% and <= 40% probability -> APPROVE WITH CONDITIONS
    HIGH_RISK_THRESHOLD = 0.60  # > 40% and <= 60% probability -> DECLINE
                                # > 60% probability -> DECLINE (VERY HIGH RISK)

    decision = ""
    risk_category = ""

    # Extract relevant data points from borrower_data for richer reasoning
    # Use .get() with a default value to prevent KeyError if a field is missing in the input
    loan_amnt = borrower_data.get('loan_amnt', 0.0)
    annual_inc = borrower_data.get('annual_inc', 0.0)
    dti = borrower_data.get('dti', 0.0)
    credit_utilization_ratio = borrower_data.get('credit_utilization_ratio', 0.0)
    sub_grade = borrower_data.get('sub_grade', 0.0)
    open_acc = borrower_data.get('open_acc', 0)
    mort_acc = borrower_data.get('mort_acc', 0)
    pub_rec_bankruptcies = borrower_data.get('pub_rec_bankruptcies', 0)
    total_acc = borrower_data.get('total_acc', 0)
    revol_util = borrower_data.get('revol_util', 0.0) # Original Revolving line utilization
    int_rate = borrower_data.get('int_rate', 0.0)
    loan_to_income_ratio = borrower_data.get('loan_to_income_ratio', 0.0)


    # --- Decision Logic and Reasoning Population ---
    if probability <= LOW_RISK_THRESHOLD:
        decision = "APPROVE LOAN"
        risk_category = "LOW RISK"
        reasoning_list.append("The applicant exhibits a very low probability of default.")
        reasoning_list.append(f"Strong financial indicators, including an annual income of ${annual_inc:,.2f} and a favorable debt-to-income ratio ({dti:.2f}%).")
        if credit_utilization_ratio < 0.3:
            reasoning_list.append(f"Excellent credit utilization ({credit_utilization_ratio:.2%}) indicates responsible credit management.")
        elif credit_utilization_ratio <= 0.4:
             reasoning_list.append(f"Good credit utilization ({credit_utilization_ratio:.2%}) reflects healthy credit habits.")
        if sub_grade > 0 and sub_grade <= 3: # Assuming lower sub_grade is better (e.g., A1, A2, A3)
            reasoning_list.append(f"High credit sub-grade ({sub_grade:.1f}) reflects strong creditworthiness.")
        if mort_acc >= 1:
            reasoning_list.append(f"Presence of {mort_acc} mortgage account(s) suggests established financial responsibility.")
        reasoning_list.append("Recommended for approval with favorable terms.")

    elif probability <= MODERATE_RISK_THRESHOLD: # probability > 0.15 and <= 0.40
        decision = "APPROVE LOAN WITH CONDITIONS"
        risk_category = "MODERATE RISK"
        reasoning_list.append("The applicant has a moderate probability of default.")
        reasoning_list.append(f"Annual income of ${annual_inc:,.2f} provides reasonable repayment capacity, but other factors suggest caution.")
        if 25 < dti <= 40: # Specific DTI range for moderate risk
            reasoning_list.append(f"Debt-to-income ratio ({dti:.2f}%) is elevated, requiring careful consideration for new debt.")
        if 40 < revol_util <= 60: # Specific Revolving utilization range
            reasoning_list.append(f"Revolving credit utilization ({revol_util:.2f}%) is moderate, indicating reliance on available credit.")
        if sub_grade > 3 and sub_grade <= 7: # Moderate sub_grade range
            reasoning_list.append(f"Credit sub-grade ({sub_grade:.1f}) is fair, indicating some areas for credit improvement.")
        if open_acc < 8:
            reasoning_list.append(f"Fewer open credit lines ({open_acc}) might limit the depth of the applicant's credit history.")
        reasoning_list.append("Approval is recommended, potentially with a slightly higher interest rate, a reduced loan amount, or stricter repayment terms.")

    elif probability <= HIGH_RISK_THRESHOLD: # probability > 0.40 and <= 0.60
        decision = "DECLINE LOAN"
        risk_category = "HIGH RISK"
        reasoning_list.append("The applicant presents a high probability of default.")
        if dti > 40: # High DTI
            reasoning_list.append(f"High debt-to-income ratio ({dti:.2f}%) indicates significant financial strain and limited capacity for new debt.")
        if revol_util > 60: # High Revolving utilization
            reasoning_list.append(f"Very high revolving credit utilization ({revol_util:.2f}%) suggests potential financial distress or over-reliance on credit.")
        if sub_grade > 7: # Low sub_grade (indicating higher risk)
            reasoning_list.append(f"Low credit sub-grade ({sub_grade:.1f}) reflects significant credit risk.")
        if pub_rec_bankruptcies > 0:
            reasoning_list.append(f"Presence of {pub_rec_bankruptcies} public record bankruptcies indicates prior financial instability.")
        if loan_to_income_ratio > 0.4 and annual_inc < 50000:
            reasoning_list.append(f"The requested loan amount (${loan_amnt:,.2f}) is high relative to the annual income (${annual_inc:,.2f}), posing a high burden.")
        reasoning_list.append("Loan is declined due to a combination of elevated risk factors, making it unsuitable at this time.")

    else: # probability > 0.60 (VERY HIGH RISK)
        decision = "DECLINE LOAN"
        risk_category = "VERY HIGH RISK"
        reasoning_list.append("The applicant exhibits a very high probability of default.")
        reasoning_list.append("Multiple critical and adverse risk factors have been identified, pointing to extreme financial vulnerability.")
        if pub_rec_bankruptcies > 1:
            reasoning_list.append(f"Multiple public record bankruptcies ({pub_rec_bankruptcies}) indicate a severe history of financial difficulty.")
        if dti > 50 and revol_util > 80:
            reasoning_list.append("Extremely high debt-to-income ratio and credit utilization strongly suggest an inability to manage further debt.")
        reasoning_list.append("Declining this loan is strongly advised to prevent potential losses and protect the applicant from further financial strain.")


    # Construct and return the full recommendation dictionary
    return {
        "timestamp": datetime.now().isoformat(),
        "decision": decision,
        "risk_category": risk_category,
        "probability": probability,
        "reasoning": reasoning_list
    }
# --- END OF FILE recommendation.py ---