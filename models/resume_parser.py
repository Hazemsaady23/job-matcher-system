"""
Resume Parser - Extract structured info from resumes
"""

import sys
sys.path.append('.')
from utils.text_processor import *
from models.skill_extractor import extract_skills_fuzzy
from utils.data_loader import load_skills_database
import re

# ==========================================
# RESUME PARSING
# ==========================================

def parse_resume(resume_text: str) -> dict:
    """
    Parse resume and extract structured information
    
    Args:
        resume_text: Raw resume text
    
    Returns:
        Dictionary with parsed information
    """
    # Load skills database
    skills_db = load_skills_database()
    
    # Extract information
    parsed = {
        'raw_text': resume_text,
        'cleaned_text': clean_text(resume_text),
        'email': extract_email(resume_text),
        'phone': extract_phone(resume_text),
        'urls': extract_urls(resume_text),
        'skills': extract_skills_fuzzy(resume_text, skills_db),
        'years_of_experience': extract_years_of_experience(resume_text),
        'sections': detect_sections(resume_text),
        'keywords': extract_keywords(resume_text, top_n=20),
        'word_count': get_word_count(resume_text),
        'education_level': extract_education_level(resume_text)
    }
    
    return parsed

# ==========================================
# EDUCATION EXTRACTION
# ==========================================

def extract_education_level(text: str) -> str:
    """
    Extract highest education level from resume
    
    Returns: 'PhD', 'Masters', 'Bachelors', 'Associates', 'High School', or 'Unknown'
    """
    text_lower = text.lower()
    
    # PhD patterns
    phd_patterns = ['ph.d', 'phd', 'doctorate', 'doctoral']
    if any(pattern in text_lower for pattern in phd_patterns):
        return 'PhD'
    
    # Masters patterns
    masters_patterns = ['master', 'msc', 'm.sc', 'ma', 'm.a', 'mba', 'ms', 'm.s']
    if any(pattern in text_lower for pattern in masters_patterns):
        return 'Masters'
    
    # Bachelors patterns
    bachelors_patterns = ['bachelor', 'bsc', 'b.sc', 'ba', 'b.a', 'bs', 'b.s', 'be', 'b.e', 'btech', 'b.tech']
    if any(pattern in text_lower for pattern in bachelors_patterns):
        return 'Bachelors'
    
    # Associates patterns
    associates_patterns = ['associate', 'as', 'a.s', 'aa', 'a.a']
    if any(pattern in text_lower for pattern in associates_patterns):
        return 'Associates'
    
    # High school
    hs_patterns = ['high school', 'secondary school', 'diploma']
    if any(pattern in text_lower for pattern in hs_patterns):
        return 'High School'
    
    return 'Unknown'

def compare_education_levels(resume_edu: str, required_edu: str) -> float:
    """
    Compare education levels
    
    Returns: Score 0-1 (1 = meets or exceeds requirement)
    """
    education_hierarchy = {
        'High School': 1,
        'Associates': 2,
        'Bachelors': 3,
        'Masters': 4,
        'PhD': 5,
        'Unknown': 0
    }
    
    resume_level = education_hierarchy.get(resume_edu, 0)
    required_level = education_hierarchy.get(required_edu, 0)
    
    if required_level == 0:  # No requirement
        return 1.0
    
    if resume_level >= required_level:
        return 1.0
    elif resume_level == required_level - 1:
        return 0.7  # One level below
    elif resume_level > 0:
        return 0.3  # Has some education
    else:
        return 0.0  # Unknown education

# ==========================================
# EXPERIENCE EXTRACTION
# ==========================================

def extract_company_names(text: str) -> list:
    """Extract potential company names (simple heuristic)"""
    # Look for lines with capitalized words after "at" or before job titles
    companies = []
    
    patterns = [
        r'(?:at|@)\s+([A-Z][A-Za-z\s&,\.]+(?:Inc|LLC|Corp|Co|Ltd)?)',
        r'([A-Z][A-Za-z\s&]+(?:Inc|LLC|Corp|Co|Ltd))'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        companies.extend(matches)
    
    # Clean and deduplicate
    companies = [c.strip() for c in companies if len(c.strip()) > 3]
    return list(set(companies))[:5]  # Top 5

def extract_job_titles(text: str) -> list:
    """Extract potential job titles"""
    common_titles = [
        'engineer', 'developer', 'scientist', 'analyst', 'manager',
        'architect', 'consultant', 'designer', 'specialist', 'lead',
        'director', 'coordinator', 'administrator', 'technician'
    ]
    
    titles = []
    text_lower = text.lower()
    
    for title in common_titles:
        if title in text_lower:
            # Find context around the title
            pattern = r'([A-Za-z\s]{0,20}' + title + r'[A-Za-z\s]{0,20})'
            matches = re.findall(pattern, text, re.IGNORECASE)
            titles.extend([m.strip() for m in matches if len(m.strip()) > 5])
    
    return list(set(titles))[:5]  # Top 5

# ==========================================
# RESUME QUALITY METRICS
# ==========================================

def assess_resume_quality(parsed_resume: dict) -> dict:
    """
    Assess resume quality based on completeness
    
    Returns: Quality metrics
    """
    quality = {
        'completeness_score': 0,
        'has_contact': False,
        'has_skills': False,
        'has_experience': False,
        'has_education': False,
        'word_count_ok': False,
        'issues': []
    }
    
    # Check contact info
    if parsed_resume.get('email') or parsed_resume.get('phone'):
        quality['has_contact'] = True
        quality['completeness_score'] += 20
    else:
        quality['issues'].append("Missing contact information")
    
    # Check skills
    if len(parsed_resume.get('skills', [])) >= 3:
        quality['has_skills'] = True
        quality['completeness_score'] += 30
    else:
        quality['issues'].append("Few or no skills listed")
    
    # Check experience section
    if parsed_resume['sections'].get('experience'):
        quality['has_experience'] = True
        quality['completeness_score'] += 30
    else:
        quality['issues'].append("Missing experience section")
    
    # Check education section
    if parsed_resume['sections'].get('education'):
        quality['has_education'] = True
        quality['completeness_score'] += 10
    else:
        quality['issues'].append("Missing education section")
    
    # Check word count
    word_count = parsed_resume['word_count']
    if 200 <= word_count <= 1000:
        quality['word_count_ok'] = True
        quality['completeness_score'] += 10
    else:
        if word_count < 200:
            quality['issues'].append(f"Resume too short ({word_count} words)")
        else:
            quality['issues'].append(f"Resume too long ({word_count} words)")
    
    return quality

# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":
    sample = """
    JOHN DOE
    Email: john@email.com | Phone: 555-1234
    
    SUMMARY
    Senior Data Scientist with 5 years of experience
    
    SKILLS
    Python, Machine Learning, SQL, AWS, TensorFlow
    
    EXPERIENCE
    Data Scientist at TechCorp Inc.
    Developed ML models
    
    EDUCATION
    Master of Science in Computer Science
    """
    
    print("🔄 Testing Resume Parser...\n")
    
    parsed = parse_resume(sample)
    
    print("Contact:", parsed['email'], parsed['phone'])
    print("Skills:", parsed['skills'][:5])
    print("Experience:", parsed['years_of_experience'], "years")
    print("Education:", parsed['education_level'])
    print("Sections:", parsed['sections'])
    
    quality = assess_resume_quality(parsed)
    print(f"\nQuality Score: {quality['completeness_score']}/100")
    print("Issues:", quality['issues'])
    
    print("\n✅ Resume parser working!")