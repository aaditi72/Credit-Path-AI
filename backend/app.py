from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from inference import predict_default_probability
from recommendation import recommend_action
from logger import log_request
from schemas import BorrowerInput
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from database import Base, engine # Ensure database is imported for potential use if needed

app = FastAPI(
    title="CreditPath AI - Loan Risk Prediction API",
    description="Predicts borrower default probability and provides risk recommendations. This API powers smarter credit decisions.",
    version="1.0.0"
)

app.include_router(auth_router)

# IMPORTANT: Restrict allow_origins in production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://credit-path-ai-17fc.onrender.com"], # Add your frontend's actual origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Ensures database tables are created on startup."""
    print("Attempting to create database tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    print("Database tables check complete.")


@app.get("/", summary="Health check endpoint")
def root():
    """Root endpoint for health check."""
    return {"message": "✅ CreditPath AI Backend is running successfully! Visit /docs for API documentation."}


@app.post("/api/predict", response_model=dict, summary="Get loan default risk prediction and recommendation")
def predict(data: BorrowerInput):
    """
    Receives borrower data, validates it, predicts default probability using the ML model,
    generates a risk-based recommendation with reasoning, logs the transaction, and returns the response.
    """

    try:
        borrower_dict = data.dict()

        prob = predict_default_probability(borrower_dict)
        recommendation = recommend_action(prob, borrower_dict) # Pass borrower_dict for richer reasoning

        response = {
            "timestamp": datetime.now().isoformat(),
            "default_probability": round(prob, 4),
            "recommendation": recommendation,
            "model_version": "xgb_hypertuned_all_features_v1",
            "status": "success"
        }

        log_request(borrower_dict, response)

        return JSONResponse(content=response, status_code=200)

    except HTTPException as e:
        # Re-raise explicit HTTPExceptions (e.g., from Pydantic validation)
        error_msg = {"status": "error", "message": e.detail}
        log_request(data.dict(), error_msg)
        raise e
    except Exception as e:
        # Handles other runtime or model-related errors gracefully
        error_msg = {"status": "error", "message": f"Internal Server Error: {str(e)}"}
        log_request(data.dict(), error_msg)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.get("/api/health", summary="Basic health check endpoint")
def health_check():
    """Basic health check endpoint."""
    return {"status": "ok", "timestamp": datetime.now().isoformat(), "message": "API is healthy"}


# Only runs when started directly (for Render/Local testing)
if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)

# Add a simple /api/batch_predict endpoint if you want to implement it in FastAPI later
# @app.post("/api/batch_predict")
# async def batch_predict(file: UploadFile = File(...)):
#     """
#     Accepts a CSV file, processes each row for prediction, and returns aggregated results.
#     """
#     # Implement CSV parsing and calling predict_default_probability for each row
#     # This would be a more complex endpoint.
#     # For now, frontend simulates it by calling single_predict repeatedly.
#     return {"message": "Batch prediction not yet implemented on backend, frontend simulates."}