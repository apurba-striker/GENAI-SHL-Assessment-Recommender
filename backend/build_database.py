import pandas as pd
import re
import os
import requests
from bs4 import BeautifulSoup

def extract_assessment_name(url):
    match = re.search(r'/view/([^/]+)/?$', url)
    if match:
        name = match.group(1)
        name = name.replace('%28', '(').replace('%29', ')')
        name = name.replace('%2528', '(').replace('%2529', ')')
        return name.replace('-', ' ').title()
    return "Unknown Assessment"

def classify_assessment_type(name):
    name_lower = name.lower()
    if any(w in name_lower for w in ['java', 'python', 'sql', 'javascript', 'js',
                                     'programming', 'coding', 'excel', 'technical',
                                     'development', 'ado.net', 'ssas', 'ssis',
                                     'drupal', 'automation', 'selenium']):
        return 'K'
    if any(w in name_lower for w in ['personality', 'opq', 'communication',
                                     'leadership', 'interpersonal', 'behavior',
                                     'emotional', 'motivation', 'culture']):
        return 'P'
    if any(w in name_lower for w in ['cognitive', 'numerical', 'verbal',
                                     'reasoning', 'aptitude', 'verify',
                                     'logical', 'abstract', 'general ability']):
        return 'A'
    if 'sales' in name_lower:
        return 'B'
    return 'K'

def estimate_duration(name):
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
    name_lower = name.lower()
    skills = []
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


def scrape_adaptive_and_remote_support(url):
    """
    Scrapes SHL product catalog page to extract adaptive_support and remote_support flags.
    Return ('Yes' or 'No') strings for both fields.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Example heuristic selectors - these need to be adjusted per actual SHL catalog page structure
        text = soup.get_text(separator=' ').lower()
        
        adaptive_support = "Yes" if any(keyword in text for keyword in ["adaptive", "cat", "computer adaptive test"]) else "No"
        remote_support = "Yes" if any(keyword in text for keyword in ["remote", "online", "internet", "proctored"]) else "No"
        
        return adaptive_support, remote_support
    except Exception as e:
        print(f"⚠️ Failed to scrape {url}: {e}")
        return "No", "No"


def generate_description(name, test_type):
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
    
    train_df = pd.read_excel('./data/Gen_AI-Dataset.xlsx', sheet_name='Train-Set')
    test_df = pd.read_excel('./data/Gen_AI-Dataset.xlsx', sheet_name='Test-Set')
    
    print(f"\n Loaded {len(train_df)} training samples")
    print(f"Loaded {len(test_df)} test queries")
    
    assessment_urls = train_df['Assessment_url'].unique()
    print(f"\nFound {len(assessment_urls)} unique assessments")
    
    assessments = []
    for idx, url in enumerate(assessment_urls, 1):
        name = extract_assessment_name(url)
        test_type = classify_assessment_type(name)
        adaptive_support, remote_support = scrape_adaptive_and_remote_support(url)
        assessments.append({
            'id': idx,
            'name': name,
            'url': url,
            'test_type': test_type,
            'duration_mins': estimate_duration(name),
            'skills': extract_skills(name),
            'description': generate_description(name, test_type),
            'adaptive_support': adaptive_support,
            'remote_support': remote_support
        })
    
    assessments_df = pd.DataFrame(assessments)
    
    print("\n Test Type Distribution:")
    type_counts = assessments_df['test_type'].value_counts()
    type_names = {
        'K': 'Knowledge & Skills',
        'P': 'Personality & Behavior',
        'A': 'Ability & Aptitude',
        'B': 'Biodata & SJT'
    }
    for test_type, count in type_counts.items():
        print(f"   {test_type} ({type_names.get(test_type, 'Other')}): {count}")
    
    os.makedirs('./data', exist_ok=True)
    assessments_df.to_csv('./data/assessments_enriched_db.csv', index=False)
    assessments_df.to_json('./data/assessments_enriched_db.json', orient='records', indent=2)
    
    print(f"\n Saved {len(assessments_df)} assessments to:")
    print("   - ./data/assessments_enriched_db.csv")
    print("   - ./data/assessments_enriched_db.json")
    
    print("\n Sample Assessments:")
    for idx in [0, 5, 10]:
        if idx < len(assessments_df):
            row = assessments_df.iloc[idx]
            print(f"\n{idx+1}. {row['name']}")
            print(f"   Type: {row['test_type']} | Duration: {row['duration_mins']}min")
            print(f"   Skills: {row['skills']}")
            print(f"   Adaptive Support: {row['adaptive_support']}")
            print(f"   Remote Support: {row['remote_support']}")
    
    print("\n" + "="*80)
    print("DATABASE BUILD COMPLETE ")
    print("="*80)


if __name__ == "__main__":
    main()
