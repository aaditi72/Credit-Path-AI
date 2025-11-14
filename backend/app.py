from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from inference import predict_default_probability
from recommendation import recommend_action
from logger import log_request
from schemas import BorrowerInput
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from database import Base, engine

app = FastAPI(
    title="CreditPath AI - Loan Risk Prediction API",
    description="Predicts borrower default probability and provides risk recommendations. This API powers smarter credit decisions.",
    version="1.0.0"
)

# Auth router
app.include_router(auth_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://credit-path-ai-17fc.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Runs on API startup."""
    try:
        print("⏳ Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database OK!")
    except Exception as e:
        print(f"⚠ Database initialization error: {e}")


@app.get("/", summary="Health check endpoint")
def root():
    """Basic root endpoint."""
    return {"message": "✅ CreditPath AI Backend is running successfully! Visit /docs for API documentation."}


@app.post("/api/predict", summary="Predict default risk + recommendation")
def predict(data: BorrowerInput):
    """
    Receives borrower data → preprocess → predict probability → generate recommendation → log transaction → return response.
    """
    try:
        borrower_dict = data.model_dump()

        # 🔥 NEW MODEL PIPELINE (updated)
        result = predict_default_probability(borrower_dict)
        prob_value = result["probability"]                      # probability for detected default label
        class_prob_map = result["class_probability_map"]        # mapping label -> prob
        detected_default_label = result["default_label"]

        recommendation = recommend_action(prob_value, borrower_dict)

        response = {
            "timestamp": datetime.utcnow().isoformat(),
            "default_probability": round(prob_value, 4),
            "class_probability_map": class_prob_map,
            "detected_default_label": str(detected_default_label),
            "recommendation": recommendation,
            "model_version": "model_lgbm_tuned_v1",  # optional: set correct model name
            "status": "success"
            }

        # Log request & response
        log_request(borrower_dict, response)

        return JSONResponse(content=response, status_code=200)

    except HTTPException as e:
        error_msg = {"status": "error", "message": e.detail}
        log_request(data.model_dump(), error_msg)
        raise e

    except Exception as e:
        error_msg = {"status": "error", "message": f"Internal Server Error: {str(e)}"}
        log_request(data.model_dump(), error_msg)
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {str(e)}")


@app.get("/api/health", summary="Health endpoint")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "API is healthy"
    }


# Local or Render entry point
if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
