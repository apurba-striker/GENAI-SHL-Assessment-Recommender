import pandas as pd
import re
import os

def extract_assessment_name(url):
    """Extract clean assessment name from URL"""
    match = re.search(r'/view/([^/]+)/?$', url)
    if match:
        name = match.group(1)
        # Clean URL encoding
        name = name.replace('%28', '(').replace('%29', ')')
        name = name.replace('%2528', '(').replace('%2529', ')')
        return name.replace('-', ' ').title()
    return "Unknown Assessment"

def classify_assessment_type(name):
    """
    Classify assessment types:
    K = Knowledge & Skills (technical tests)
    P = Personality & Behavior
    A = Ability & Aptitude (cognitive)
    B = Biodata & SJT (situational judgment)
    """
    name_lower = name.lower()
    
    # Technical/Knowledge tests
    if any(w in name_lower for w in ['java', 'python', 'sql', 'javascript', 'js',
                                      'programming', 'coding', 'excel', 'technical',
                                      'development', 'ado.net', 'ssas', 'ssis',
                                      'drupal', 'automation', 'selenium']):
        return 'K'
    
    # Personality/Behavioral
    if any(w in name_lower for w in ['personality', 'opq', 'communication',
                                      'leadership', 'interpersonal', 'behavior',
                                      'emotional', 'motivation', 'culture']):
        return 'P'
    
    # Cognitive/Aptitude
    if any(w in name_lower for w in ['cognitive', 'numerical', 'verbal',
                                      'reasoning', 'aptitude', 'verify',
                                      'logical', 'abstract', 'general ability']):
        return 'A'
    
    # Sales/SJT
    if 'sales' in name_lower:
        return 'B'
    
    # Default to Knowledge
    return 'K'

def estimate_duration(name):
    """Estimate typical test duration in minutes"""
    name_lower = name.lower()
    
    if any(w in name_lower for w in ['entry', 'sift', 'screen', 'short']):
        return 20
    elif any(w in name_lower for w in ['advanced', 'comprehensive', 'long']):
        return 60
    elif any(w in name_lower for w in ['adaptive', 'intermediate']):
        return 40
    elif any(w in name_lower for w in ['java', 'python', 'sql', 'programming']):
        return 35
    elif any(w in name_lower for w in ['personality', 'opq', 'behavior']):
        return 35
    else:
        return 30

def extract_skills(name):
    """Extract relevant skills from assessment name"""
    name_lower = name.lower()
    skills = []
    
    # Programming languages
    skill_map = {
        'java': 'Java',
        'python': 'Python',
        'sql': 'SQL',
        'javascript': 'JavaScript',
        'js': 'JavaScript',
        'excel': 'Excel',
        'c++': 'C++',
        '.net': '.NET',
        'ado.net': 'ADO.NET',
        'drupal': 'Drupal',
        'selenium': 'Selenium'
    }
    
    for key, value in skill_map.items():
        if key in name_lower:
            if value not in skills:
                skills.append(value)
    
    # Soft skills
    if 'communication' in name_lower:
        skills.append('Communication')
    if 'leadership' in name_lower:
        skills.append('Leadership')
    if 'interpersonal' in name_lower:
        skills.append('Interpersonal Skills')
    if 'sales' in name_lower:
        skills.append('Sales')
    if 'account' in name_lower:
        skills.append('Accounting')
    if 'english' in name_lower:
        skills.append('English')
    if 'data' in name_lower and 'entry' in name_lower:
        skills.append('Data Entry')
    
    return ', '.join(skills) if skills else 'General Skills'

def generate_description(name, test_type):
    """Generate meaningful description"""
    type_descriptions = {
        'K': f"Technical skills assessment measuring knowledge and proficiency in {name}",
        'P': f"Personality and behavioral assessment evaluating traits for {name}",
        'A': f"Cognitive ability test measuring reasoning and problem-solving for {name}",
        'B': f"Situational judgment test assessing decision-making for {name}",
        'S': f"Simulation-based assessment with realistic scenarios for {name}"
    }
    return type_descriptions.get(test_type, f"Assessment for {name}")

def main():
    print("="*80)
    print("BUILDING SHL ASSESSMENT DATABASE")
    print("="*80)
    
    # Load training data
    train_df = pd.read_excel('./data/Gen_AI-Dataset.xlsx', sheet_name='Train-Set')
    test_df = pd.read_excel('./data/Gen_AI-Dataset.xlsx', sheet_name='Test-Set')
    
    print(f"\n✅ Loaded {len(train_df)} training samples")
    print(f"✅ Loaded {len(test_df)} test queries")
    
    # Extract unique assessment URLs
    assessment_urls = train_df['Assessment_url'].unique()
    print(f"\n📊 Found {len(assessment_urls)} unique assessments")
    
    # Build enriched database
    assessments = []
    for idx, url in enumerate(assessment_urls, 1):
        name = extract_assessment_name(url)
        test_type = classify_assessment_type(name)
        
        assessments.append({
            'id': idx,
            'name': name,
            'url': url,
            'test_type': test_type,
            'duration_mins': estimate_duration(name),
            'skills': extract_skills(name),
            'description': generate_description(name, test_type)
        })
    
    assessments_df = pd.DataFrame(assessments)
    
    # Display distribution
    print("\n📈 Test Type Distribution:")
    type_counts = assessments_df['test_type'].value_counts()
    type_names = {
        'K': 'Knowledge & Skills',
        'P': 'Personality & Behavior',
        'A': 'Ability & Aptitude',
        'B': 'Biodata & SJT'
    }
    for test_type, count in type_counts.items():
        print(f"   {test_type} ({type_names.get(test_type, 'Other')}): {count}")
    
    # Save to files
    os.makedirs('../data', exist_ok=True)
    assessments_df.to_csv('../data/assessments_enriched_db.csv', index=False)
    assessments_df.to_json('../data/assessments_enriched_db.json', orient='records', indent=2)
    
    print(f"\n✅ Saved {len(assessments_df)} assessments to:")
    print("   - ./data/assessments_enriched_db.csv")
    print("   - ./data/assessments_enriched_db.json")
    
    # Show sample assessments
    print("\n📋 Sample Assessments:")
    for idx in [0, 5, 10]:
        if idx < len(assessments_df):
            row = assessments_df.iloc[idx]
            print(f"\n{idx+1}. {row['name']}")
            print(f"   Type: {row['test_type']} | Duration: {row['duration_mins']}min")
            print(f"   Skills: {row['skills']}")
    
    print("\n" + "="*80)
    print("DATABASE BUILD COMPLETE ✅")
    print("="*80)

if __name__ == "__main__":
    main()