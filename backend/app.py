from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from recommender import AssessmentRecommender
import uvicorn

app = FastAPI(
    title="SHL Assessment Recommender API",
    description="AI-powered assessment recommendation system using transformer embeddings",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("🚀 Initializing Assessment Recommender...")
recommender = AssessmentRecommender(db_path='./data/assessments_enriched_db.csv')
print(" Recommender ready!")

class QueryRequest(BaseModel):
    query: str

class AssessmentResponse(BaseModel):
    name: str
    url: str
    test_type: str
    duration_mins: int
    skills: str
    description: str
    relevance_score: float

class RecommendationResponse(BaseModel):
    query: str
    count: int
    recommendations: List[AssessmentResponse]

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "SHL Assessment Recommender API",
        "status": "active",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "recommend": "/recommend (POST)",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    """
    Health check endpoint (REQUIRED by assignment)
    """
    return {
        "status": "healthy",
        "service": "SHL Assessment Recommender",
        "assessments_loaded": len(recommender.assessments_df),
        "model": "sentence-transformers/all-MiniLM-L6-v2",
        "embedding_dimension": 384
    }

@app.post("/recommend", response_model=RecommendationResponse)
@app.post("/recommend")
def get_recommendations(request: QueryRequest):
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        recommendations = recommender.recommend(request.query, top_k=10)
        
        type_map = {
            'K': ["Knowledge & Skills"],
            'P': ["Personality & Behaviour"],
            'A': ["Ability & Aptitude"],
            'B': ["Biodata & SJT"]
        }
        
        result = []
        for rec in recommendations:
            result.append({
                "url": rec['url'],
                "name": rec['name'],
                "adaptive_support": rec.get('adaptive_support', 'No'),
                "description": rec['description'],
                "duration": int(rec['duration_mins']),
                "remote_support": rec.get('remote_support', 'Yes'),
                "test_type": type_map.get(rec['test_type'], ["Other"])
            })
        
        return {"recommended_assessments": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



if __name__ == "__main__":
    print("\n" + "="*80)
    print(" STARTING SHL ASSESSMENT RECOMMENDER API")
    print("="*80)
    print(" API will be available at: http://localhost:8000")
    print(" Docs available at: http://localhost:8000/docs")
    print("="*80 + "\n")
    
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)