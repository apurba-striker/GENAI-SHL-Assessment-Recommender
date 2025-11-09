import pandas as pd
from recommender import AssessmentRecommender
import os

def calculate_recall_at_k(train_df, recommender, k=10):
    """Calculate Mean Recall@K on training set"""
    recalls = []
    
    print(f"\n{'='*80}")
    print(f"CALCULATING MEAN RECALL@{k} ON TRAINING SET")
    print('='*80)
    
    for idx, query in enumerate(train_df['Query'].unique(), 1):
        true_urls = set(train_df[train_df['Query'] == query]['Assessment_url'])
        
        predictions = recommender.recommend(query, top_k=k)
        pred_urls = set([p['url'] for p in predictions])
        
        intersection = true_urls.intersection(pred_urls)
        recall = len(intersection) / len(true_urls) if true_urls else 0
        recalls.append(recall)
        
        print(f"\nQuery {idx}: {query[:80]}...")
        print(f"  Ground truth: {len(true_urls)} assessments")
        print(f"  Predicted: {len(pred_urls)} assessments")
        print(f"  Matches: {len(intersection)}")
        print(f"  Recall@{k}: {recall:.4f}")
    
    mean_recall = sum(recalls) / len(recalls) if recalls else 0
    
    print(f"\n{'='*80}")
    print(f"MEAN RECALL@{k}: {mean_recall:.4f} ({mean_recall*100:.2f}%)")
    print('='*80)
    
    return mean_recall

def generate_test_predictions(test_df, recommender, output_path='../data/test_predictions.csv'):
    """
    Generate predictions for test set
    
    CRITICAL: Must return 5-10 unique recommendations per query (assignment requirement)
    """
    
    print(f"\n{'='*80}")
    print(" GENERATING TEST SET PREDICTIONS")
    print('='*80)
    
    predictions = []
    
    for idx, query in enumerate(test_df['Query'], 1):
        print(f"\n🔍 Query {idx}/{len(test_df)}:")
        print(f"   {query[:100]}...")
        
        recs = recommender.recommend(query, top_k=10)
        
        unique_recs = []
        seen_urls = set()
        
        for rec in recs:
            if rec['url'] not in seen_urls:
                unique_recs.append(rec)
                seen_urls.add(rec['url'])
        if len(unique_recs) < 5:
            print(f"     Only {len(unique_recs)} unique recommendations, getting more...")
            
            from sklearn.metrics.pairwise import cosine_similarity
            query_vector = recommender.model.encode([query], normalize_embeddings=True)[0].reshape(1, -1)
            similarities = cosine_similarity(query_vector, recommender.assessment_vectors).flatten()
            
            all_results = recommender.assessments_df.copy()
            all_results['similarity'] = similarities
            all_results = all_results.sort_values('similarity', ascending=False)
            
            for _, row in all_results.iterrows():
                if row['url'] not in seen_urls:
                    unique_recs.append(row.to_dict())
                    seen_urls.add(row['url'])
                    if len(unique_recs) >= 10:
                        break
        
        num_recs = min(10, max(5, len(unique_recs)))
        final_recs = unique_recs[:num_recs]
        
        print(f"   Generated {num_recs} unique recommendations")

        for rec in final_recs:
            predictions.append({
                'Query': query,
                'Assessment_url': rec['url']
            })
    
    predictions_df = pd.DataFrame(predictions)
    
    print(f"\n{'='*80}")
    print(" VALIDATION")
    print('='*80)
    
    for query in test_df['Query']:
        count = len(predictions_df[predictions_df['Query'] == query])
        status = "Yes" if 5 <= count <= 10 else "No"
        print(f"{status} {count} recommendations for: {query[:60]}...")
    
    has_duplicates = False
    for query in test_df['Query']:
        query_df = predictions_df[predictions_df['Query'] == query]
        if query_df['Assessment_url'].duplicated().any():
            dup_count = query_df['Assessment_url'].duplicated().sum()
            print(f" {dup_count} duplicates found in: {query[:50]}...")
            has_duplicates = True
    
    if not has_duplicates:
        print("No duplicate URLs per query")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    predictions_df.to_csv(output_path, index=False)
    
    print(f"\n{'='*80}")
    print(f" SAVED {len(predictions_df)} PREDICTIONS")
    print('='*80)
    print(f"File: {output_path}")
    print(f" Total rows: {len(predictions_df)}")
    print(f" Queries: {test_df['Query'].nunique()}")
    print(f" Average: {len(predictions_df)/test_df['Query'].nunique():.1f} per query")
    
 
    print(f"\n{'='*80}")
    print("SAMPLE OUTPUT (First Query)")
    print('='*80)
    first_query = test_df['Query'].iloc[0]
    sample = predictions_df[predictions_df['Query'] == first_query]
    print(f"\nQuery: {first_query[:80]}...")
    print(f"\nRecommendations ({len(sample)}):")
    for i, row in sample.iterrows():
        assessment_name = row['Assessment_url'].split('/')[-2].replace('-', ' ').title()
        print(f"   {i+1}. {assessment_name}")
    
    return predictions_df

def main():
    print("="*80)
    print("🎯 SHL ASSESSMENT RECOMMENDER - EVALUATION & PREDICTION")
    print("="*80)
    
    # Load data
    train_df = pd.read_excel('./data/Gen_AI-Dataset.xlsx', sheet_name='Train-Set')
    test_df = pd.read_excel('./data/Gen_AI-Dataset.xlsx', sheet_name='Test-Set')
    
    print(f"\nData Loaded:")
    print(f"   Training: {len(train_df)} rows ({train_df['Query'].nunique()} unique queries)")
    print(f"   Test: {len(test_df)} queries")
    
    print(f"\n{'='*80}")
    print(" INITIALIZING RECOMMENDER")
    print('='*80)
    recommender = AssessmentRecommender()
    
    mean_recall = calculate_recall_at_k(train_df, recommender, k=10)
    
    predictions_df = generate_test_predictions(test_df, recommender)
    
    print(f"\n{'='*80}")
    print("EVALUATION COMPLETE")
    print('='*80)
    print(f" Mean Recall@10: {mean_recall:.4f} ({mean_recall*100:.1f}%)")
    print(f" Test Predictions: ./data/test_predictions.csv")
    print(f" Total Predictions: {len(predictions_df)}")
    print(f" Ready for submission!")
    print('='*80)

if __name__ == "__main__":
    main()
