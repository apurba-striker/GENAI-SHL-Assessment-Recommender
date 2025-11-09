# SHL Assessment Recommender

An AI-powered assessment recommendation system that helps recruiters and HR professionals find the perfect SHL assessments for their hiring needs using natural language queries and transformer-based semantic search.

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/apurba-striker/GENAI-SHL-Assessment-Recommender)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-19.1+-blue)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-green)](https://fastapi.tiangolo.com/)

## 🎯 Overview

This project provides an intelligent recommendation system for SHL assessments. It uses state-of-the-art transformer embeddings to understand natural language queries and recommend the most relevant assessments based on:

- **Skills and competencies** (e.g., Java, Python, SQL, Communication)
- **Test types** (Knowledge & Skills, Personality & Behavior, Ability & Aptitude, Biodata & SJT)
- **Duration constraints** (e.g., "under 40 minutes")
- **Job level** (e.g., entry-level, graduate positions)
- **Assessment features** (adaptive support, remote support)

## ✨ Features

- 🔍 **Semantic Search**: Uses Sentence-Transformers (`all-MiniLM-L6-v2`) for intelligent query understanding
- 📊 **Smart Filtering**: Automatically extracts requirements from natural language (duration, skills, test types)
- 🎯 **Balanced Recommendations**: Provides 5-10 diverse recommendations with balanced test type distribution
- 🌐 **RESTful API**: FastAPI-based backend with automatic OpenAPI documentation
- 💻 **Modern Frontend**: React-based user interface with real-time recommendations
- 🐳 **Docker Support**: Containerized deployment for easy setup
- 📈 **Evaluation Metrics**: Built-in Recall@K calculation for model evaluation

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │────────▶│   FastAPI    │────────▶│ Recommender │
│   (React)   │  HTTP   │   Backend    │         │   Engine    │
└─────────────┘         └──────────────┘         └─────────────┘
                              │                          │
                              │                          │
                        ┌─────▼──────┐          ┌───────▼────────┐
                        │  Database   │          │  Transformer   │
                        │   (CSV)     │          │   Embeddings   │
                        └─────────────┘          └────────────────┘
```

## 🛠️ Tech Stack

### Backend

- **Python 3.11+**
- **FastAPI** - Modern, fast web framework
- **Sentence-Transformers** - Semantic embeddings (`all-MiniLM-L6-v2`)
- **scikit-learn** - Cosine similarity calculations
- **pandas** - Data manipulation
- **uvicorn** - ASGI server

### Frontend

- **React 19.1+** - UI library
- **Vite** - Build tool and dev server
- **Axios** - HTTP client
- **CSS3** - Modern styling

### ML/AI

- **Sentence-Transformers** - Transformer-based embeddings (384 dimensions)
- **Cosine Similarity** - Semantic matching algorithm

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- Node.js 18+ and npm
- (Optional) Docker and Docker Compose

### Backend Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/apurba-striker/GENAI-SHL-Assessment-Recommender.git
   cd GENAI-SHL-Assessment-Recommender
   ```

2. **Navigate to backend directory**

   ```bash
   cd backend
   ```

3. **Create virtual environment** (recommended)

   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Build the assessment database** (if not already present)

   ```bash
   python build_database.py
   ```

6. **Run the backend server**

   ```bash
   python app.py
   ```

   The API will be available at `http://localhost:8000`

   - API Documentation: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`

### Frontend Setup

1. **Navigate to frontend directory**

   ```bash
   cd frontend
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Update API URL** (if needed)

   Edit `src/App.jsx` and update the `API_URL` constant:

   ```javascript
   const API_URL = "http://localhost:8000"; // For local development
   ```

4. **Start development server**

   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

### Docker Setup

1. **Build and run backend container**
   ```bash
   cd backend
   docker build -t shl-recommender-backend .
   docker run -p 8000:8000 shl-recommender-backend
   ```

## 🚀 Usage

### Web Interface

1. Open the frontend application in your browser
2. Enter a natural language query, for example:
   - "Java developer with communication skills"
   - "Sales assessment for new graduates under 1 hour"
   - "Python and SQL skills test, max 40 minutes"
   - "Entry-level cognitive ability test"
3. Click "Get Recommendations"
4. Review the top 5-10 recommended assessments with details

### API Usage

#### Health Check

```bash
curl http://localhost:8000/health
```

#### Get Recommendations

```bash
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{"query": "Java developer with communication skills"}'
```

#### Response Format

```json
{
  "recommended_assessments": [
    {
            "url": "https://www.shl.com/solutions/products/product-catalog/view/core-java-advanced-level-new/",
            "name": "Core Java Advanced Level New",
            "adaptive_support": "Yes",
            "description": "Technical skills assessment measuring knowledge and proficiency in Core Java Advanced Level New",
            "duration": 60,
            "remote_support": "Yes",
            "test_type": [
                "Knowledge & Skills"
            ]
    },
    .....
  ]
}
```

### Python Script Usage

#### Generate Predictions for Test Set

```bash
cd backend
python generate_predictions.py
```

This will:

- Calculate Mean Recall@10 on the training set
- Generate predictions for the test set
- Save results to `data/test_predictions.csv`

#### Test the Recommender

```bash
cd backend
python recommender.py
```

## 📁 Project Structure

```
GENAI-SHL-Assessment-Recommender/
├── backend/
│   ├── app.py                    # FastAPI application
│   ├── recommender.py            # Core recommendation engine
│   ├── build_database.py         # Database builder from Excel data
│   ├── generate_predictions.py   # Evaluation and prediction script
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Docker configuration
│   ├── data/
│   │   ├── assessments_enriched_db.csv
│   │   ├── assessments_enriched_db.json
│   │   ├── Gen_AI-Dataset.xlsx
│   │   └── test_predictions.csv
│   └── models/
│       └── transformer_embeddings.pkl
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Main React component
│   │   ├── App.css               # Styles
│   │   ├── main.jsx              # Entry point
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── data/                         # Shared data directory
├── models/                       # Shared models directory
└── README.md                     # This file
```

## 🔧 API Endpoints

### `GET /`

Root endpoint with API information.

### `GET /health`

Health check endpoint. Returns:

- Service status
- Number of assessments loaded
- Model information

### `POST /recommend`

Get assessment recommendations based on a query.

**Request Body:**

```json
{
  "query": "string"
}
```

**Response:**

```json
{
  "recommended_assessments": [
    {
      "name": "string",
      "url": "string",
      "test_type": ["string"],
      "duration": 0,
      "adaptive_support": "Yes|No",
      "remote_support": "Yes|No",
      "description": "string"
    }
  ]
}
```

## 🧪 Evaluation

The system uses **Recall@K** as the primary evaluation metric:

- **Recall@10**: Measures how many relevant assessments are found in the top 10 recommendations
- Calculated on the training set to validate model performance
- Test predictions are generated with 5-10 unique recommendations per query

Run evaluation:

```bash
cd backend
python generate_predictions.py
```

## 🎨 Features in Detail

### Natural Language Understanding

The system extracts:

- **Duration constraints**: "under 40 minutes", "max 1 hour"
- **Technical skills**: Java, Python, SQL, JavaScript, etc.
- **Soft skills**: Communication, Leadership, Personality
- **Cognitive abilities**: Reasoning, Aptitude, Numerical
- **Job level**: Entry-level, Graduate, Junior

### Recommendation Strategy

1. **Semantic Matching**: Uses transformer embeddings to find semantically similar assessments
2. **Filtering**: Applies duration and other constraints
3. **Balancing**: Ensures diverse test type distribution when needed
4. **Boosting**: Gives preference to entry-level assessments for graduate queries
5. **Deduplication**: Ensures unique recommendations per query

## 🚢 Deployment

### RenderDeployment

1. Update `API_URL` in `frontend/src/App.jsx` to your backend URL
2. Deploy backend using Docker or directly with Python
3. Deploy frontend as a static site

### Docker Compose (Coming Soon)

```yaml
version: "3.8"
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
```

## License

This project is open source and available under the [MIT License](LICENSE).

## Author

**Apurba Patra**

- GitHub: [@apurba-striker](https://github.com/apurba-striker)
- Repository: [GENAI-SHL-Assessment-Recommender](https://github.com/apurba-striker/GENAI-SHL-Assessment-Recommender)

## Acknowledgments

- SHL for providing assessment data
- Sentence-Transformers team for the excellent embedding models
- FastAPI and React communities for amazing frameworks

## Performance

- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Embedding Dimension**: 384
- **Recommendation Speed**: < 100ms per query
- **Model Size**: ~90MB (transformer model)

## Future Enhancements

- [ ] User feedback loop for improving recommendations
- [ ] Multi-language support
- [ ] Advanced filtering options (industry, role level)
- [ ] Recommendation explanation/justification
- [ ] Batch recommendation API
- [ ] Caching for frequently asked queries
- [ ] A/B testing framework

---

⭐ If you find this project helpful, please consider giving it a star!
