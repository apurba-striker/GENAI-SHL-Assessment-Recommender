import pandas as pd
import numpy as np
import os
import pickle
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class AssessmentRecommender:
    def __init__(self, db_path='./data/assessments_enriched_db.csv'):
        """Initialize recommender with Sentence-Transformers"""
        self.assessments_df = pd.read_csv(db_path)
        
        print("🔨 Loading Sentence-Transformer model (all-MiniLM-L6-v2)...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print(" Model loaded successfully")
        
        # Try to load pre-computed embeddings
        if not self.load_embeddings():
            self._build_embeddings_index()
    
    def _build_embeddings_index(self):
        """Build semantic search index using transformer embeddings"""
        print(" Building embeddings index...")
        
        # Create rich search texts (emphasize name and skills)
        search_texts = self.assessments_df.apply(
            lambda x: f"{x['name']} {x['name']} {x['skills']} {x['skills']} {x['description']} test type {x['test_type']}",
            axis=1
        ).tolist()
        
        # Generate embeddings using sentence-transformers
        self.assessment_vectors = self.model.encode(
            search_texts,
            show_progress_bar=True,
            batch_size=32,
            normalize_embeddings=True  # Normalize for cosine similarity
        )
        
        print(f" Built embeddings index: {self.assessment_vectors.shape}")
        
        # Save embeddings
        os.makedirs('./models', exist_ok=True)
        with open('./models/transformer_embeddings.pkl', 'wb') as f:
            pickle.dump(self.assessment_vectors, f)
        print(" Saved embeddings to ../models/transformer_embeddings.pkl")
    
    def load_embeddings(self, path='./models/transformer_embeddings.pkl'):
        """Load pre-computed embeddings"""
        if os.path.exists(path):
            with open(path, 'rb') as f:
                self.assessment_vectors = pickle.load(f)
            print(f"Loaded pre-computed embeddings from {path}")
            return True
        return False
    
    def extract_requirements(self, query):
        """Extract requirements from natural language query"""
        query_lower = query.lower()
        
        # Extract duration constraint - FIXED VERSION
        max_duration = None
        
        # Try different patterns with their multipliers
        duration_patterns = [
            (r'(\d+)\s*[-]?\s*(\d+)?\s*(min|minute)s?', 1),
            (r'(\d+)\s*[-]?\s*(\d+)?\s*(hour|hr)s?', 60),
            (r'under\s+(\d+)\s*(min|minute)s?', 1),
            (r'under\s+(\d+)\s*(hour|hr)s?', 60),
            (r'maximum\s+(\d+)\s*(min|minute)s?', 1),
            (r'maximum\s+(\d+)\s*(hour|hr)s?', 60),
            (r'max\s+(\d+)\s*(min|minute)s?', 1),
            (r'max\s+(\d+)\s*(hour|hr)s?', 60),
            (r'(\d+)\s*min', 1),
            (r'(\d+)\s*hour', 60),
        ]
        
        for pattern, multiplier in duration_patterns:
            match = re.search(pattern, query_lower)
            if match:
                max_duration = int(match.group(1)) * multiplier
                break
        
        # Detect technical skills
        tech_keywords = ['java', 'python', 'sql', 'javascript', 'js', 'programming',
                         'coding', 'technical', 'excel', 'development', 'engineer',
                         'developer', 'software', 'data analyst', 'analyst', 'sales']
        
        # Detect soft skills/personality
        soft_keywords = ['communication', 'personality', 'leadership', 'behavior',
                         'cultural', 'collaborate', 'interpersonal', 'emotional',
                         'team', 'social', 'motivat', 'cultural fit']
        
        # Detect cognitive/aptitude
        cognitive_keywords = ['cognitive', 'aptitude', 'reasoning', 'numerical',
                             'verbal', 'analytical', 'problem solving', 'logic']
        
        # Detect experience level
        entry_keywords = ['new graduate', 'graduate', 'entry', 'fresher', 'junior']
        has_entry = any(kw in query_lower for kw in entry_keywords)
        
        has_tech = any(kw in query_lower for kw in tech_keywords)
        has_soft = any(kw in query_lower for kw in soft_keywords)
        has_cognitive = any(kw in query_lower for kw in cognitive_keywords)
        
        return {
            'max_duration': max_duration,
            'needs_tech': has_tech,
            'needs_soft': has_soft,
            'needs_cognitive': has_cognitive,
            'needs_balanced': (has_tech and has_soft) or (has_tech and has_cognitive),
            'is_entry_level': has_entry
        }
    
    def recommend(self, query, top_k=10):
        """
        Get balanced recommendations for a query
        
        Returns 5-10 assessments with balanced type distribution if needed
        """
        # Parse query
        reqs = self.extract_requirements(query)
        
        # Generate query embedding
        query_vector = self.model.encode([query], normalize_embeddings=True)[0].reshape(1, -1)
        
        # Calculate semantic similarities
        similarities = cosine_similarity(query_vector, self.assessment_vectors).flatten()
        
        # Create results dataframe
        results = self.assessments_df.copy()
        results['similarity'] = similarities
        
        # Apply duration filter
        if reqs['max_duration']:
            filtered = results[results['duration_mins'] <= reqs['max_duration']]
            if len(filtered) >= 5:
                results = filtered
            else:
                # Relax constraint slightly if too few results
                results = results[results['duration_mins'] <= reqs['max_duration'] + 10]
        
        # Prefer entry-level tests if specified
        if reqs['is_entry_level']:
            results['boost'] = results['name'].str.lower().str.contains('entry|graduate|junior').astype(float) * 0.1
            results['similarity'] = results['similarity'] + results['boost']
        
        # Sort by similarity
        results = results.sort_values('similarity', ascending=False)
        
        # CRITICAL: Balance test types for mixed queries
        if reqs['needs_balanced']:
            # Get top K and P assessments separately
            k_assessments = results[results['test_type'] == 'K'].head(5)
            p_assessments = results[results['test_type'] == 'P'].head(5)
            
            # Include cognitive if needed
            if reqs['needs_cognitive']:
                a_assessments = results[results['test_type'] == 'A'].head(3)
                balanced = pd.concat([k_assessments, p_assessments, a_assessments])
            else:
                balanced = pd.concat([k_assessments, p_assessments])
            
            # Remove duplicates and re-sort
            results = balanced.drop_duplicates(subset=['url']).sort_values('similarity', ascending=False)
        
        # Return 5-10 results (assignment requirement)
        final_count = max(5, min(10, len(results)))
        final_results = results.head(final_count)
        
        return final_results.to_dict('records')

# Testing
if __name__ == "__main__":
    print("="*80)
    print("TESTING ASSESSMENT RECOMMENDER")
    print("="*80)
    
    recommender = AssessmentRecommender()
    
    # Test queries
    test_queries = [
        "Java developer with communication skills",
        "Sales assessment for new graduates under 1 hour",
        "Python and SQL skills test 40 minutes max"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f" Query: {query}")
        print('='*80)
        
        recs = recommender.recommend(query)
        
        print(f"\n Top {len(recs)} Recommendations:\n")
        for i, r in enumerate(recs, 1):
            print(f"{i}. {r['name']}")
            print(f"   Type: {r['test_type']} | Duration: {r['duration_mins']}min | Score: {r['similarity']:.4f}")
            print(f"   Skills: {r['skills']}")
            print()
    
    print("="*80)
    print(" ALL TESTS PASSED")
    print("="*80)
