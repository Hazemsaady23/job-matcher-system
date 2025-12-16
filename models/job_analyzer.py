"""
Job Analyzer - Extract structured info from job descriptions
"""

import sys
sys.path.append('.')
from utils.text_processor import *
from models.skill_extractor import extract_skills_fuzzy
from utils.data_loader import load_skills_database
import re

# ==========================================
# JOB PARSING
# ==========================================

def parse_job_description(job_text: str) -> dict:
    """
    Parse job description and extract structured information
    
    Args:
        job_text: Raw job description text
    
    Returns:
        Dictionary with parsed information
    """
    # Load skills database
    skills_db = load_skills_database()
    
    # Extract information
    parsed = {
        'raw_text': job_text,
        'cleaned_text': clean_text(job_text),
        'title': extract_job_title(job_text),
        'company': extract_company_name(job_text),
        'location': extract_location(job_text),
        'required_skills': extract_skills_fuzzy(job_text, skills_db),
        'years_of_experience': extract_years_of_experience(job_text),
        'education_required': extract_years_of_experience(job_text),
        'salary_range': extract_salary(job_text),
        'job_type': extract_job_type(job_text),
        'keywords': extract_keywords(job_text, top_n=20),
        'word_count': get_word_count(job_text)
    }
    
    return parsed

# ==========================================
# JOB TITLE EXTRACTION
# ==========================================

def extract_job_title(text: str) -> str:
    """Extract job title from job description"""
    lines = text.split('\n')
    
    # Check first few lines for title-like patterns
    for line in lines[:5]:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Common patterns
        if any(keyword in line.lower() for keyword in ['position:', 'title:', 'role:']):
            title = re.sub(r'(position|title|role):\s*', '', line, flags=re.IGNORECASE)
            return title.strip()
        
        # If line is short and capitalized, likely a title
        if len(line) < 50 and len(line.split()) <= 6:
            if line[0].isupper():
                return line
    
    return "Unknown Position"

# ==========================================
# COMPANY EXTRACTION
# ==========================================

def extract_company_name(text: str) -> str:
    """Extract company name from job description"""
    # Look for common patterns
    patterns = [
        r'Company:\s*([A-Z][A-Za-z\s&,\.]+)',
        r'([A-Z][A-Za-z\s&]+(?:Inc|LLC|Corp|Co|Ltd))',
        r'Join\s+([A-Z][A-Za-z\s&]+)',
        r'About\s+([A-Z][A-Za-z\s&]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    
    return "Unknown Company"

# ==========================================
# LOCATION EXTRACTION
# ==========================================

def extract_location(text: str) -> str:
    """Extract job location"""
    # Common location patterns
    patterns = [
        r'Location:\s*([A-Za-z\s,]+)',
        r'([A-Za-z\s]+,\s*[A-Z]{2})',  # City, State
        r'(Remote|Hybrid|On-site)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return "Not specified"

# ==========================================
# SALARY EXTRACTION
# ==========================================

def extract_salary(text: str) -> dict:
    """
    Extract salary information
    
    Returns: Dict with min, max, currency
    """
    salary_info = {
        'min': None,
        'max': None,
        'currency': 'USD',
        'period': 'yearly'
    }
    
    # Patterns for salary ranges
    patterns = [
        r'\$?([\d,]+)k?\s*-\s*\$?([\d,]+)k?',  # $100k - $150k
        r'([\d,]+)\s*-\s*([\d,]+)',  # 100,000 - 150,000
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            min_sal = match.group(1).replace(',', '')
            max_sal = match.group(2).replace(',', '')
            
            # Handle 'k' notation
            if 'k' in text[match.start():match.end()].lower():
                salary_info['min'] = int(min_sal) * 1000
                salary_info['max'] = int(max_sal) * 1000
            else:
                salary_info['min'] = int(min_sal)
                salary_info['max'] = int(max_sal)
            
            return salary_info
    
    return salary_info

# ==========================================
# JOB TYPE EXTRACTION
# ==========================================

def extract_job_type(text: str) -> str:
    """
    Extract job type (Full-time, Part-time, Contract, etc.)
    """
    text_lower = text.lower()
    
    job_types = {
        'Full-time': ['full-time', 'full time', 'fulltime'],
        'Part-time': ['part-time', 'part time', 'parttime'],
        'Contract': ['contract', 'contractor', 'freelance'],
        'Internship': ['intern', 'internship'],
        'Temporary': ['temporary', 'temp']
    }
    
    for job_type, keywords in job_types.items():
        if any(keyword in text_lower for keyword in keywords):
            return job_type
    
    return 'Full-time'  # Default

# ==========================================
# SENIORITY LEVEL
# ==========================================

def extract_seniority_level(text: str) -> str:
    """
    Determine seniority level from job description
    """
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['senior', 'sr.', 'lead', 'principal', 'staff']):
        return 'Senior'
    elif any(word in text_lower for word in ['junior', 'jr.', 'entry', 'associate']):
        return 'Junior'
    elif any(word in text_lower for word in ['mid-level', 'intermediate']):
        return 'Mid-level'
    else:
        # Guess based on years of experience
        years = extract_years_of_experience(text)
        if years >= 5:
            return 'Senior'
        elif years >= 2:
            return 'Mid-level'
        elif years > 0:
            return 'Junior'
        else:
            return 'Entry-level'

# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":
    sample = """
    Position: Senior Data Scientist
    Company: TechCorp Inc.
    Location: San Francisco, CA
    Salary: $140,000 - $180,000
    
    We're seeking a Senior Data Scientist with 5+ years of experience.
    
    REQUIRED SKILLS:
    - Python
    - Machine Learning
    - TensorFlow
    - SQL
    - AWS
    
    REQUIREMENTS:
    - Master's degree in Computer Science or related field
    - 5+ years of experience in data science
    - Strong communication skills
    
    Full-time position with excellent benefits.
    """
    
    print("🔄 Testing Job Analyzer...\n")
    
    parsed = parse_job_description(sample)
    
    print("Title:", parsed['title'])
    print("Company:", parsed['company'])
    print("Location:", parsed['location'])
    print("Required Skills:", parsed['required_skills'][:5])
    print("Experience:", parsed['years_of_experience'], "years")
    print("Education:", parsed['education_required'])
    print("Salary:", parsed['salary_range'])
    print("Job Type:", parsed['job_type'])
    print("Seniority:", extract_seniority_level(sample))
    
    print("\n✅ Job analyzer working!")