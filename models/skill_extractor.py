"""
Skill Extractor - Extract skills from resume/job text
"""

import spacy
from typing import List, Set
import sys
sys.path.append('.')
from utils.data_loader import load_skills_database

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    print("⚠️  spaCy model not found. Run: python -m spacy download en_core_web_sm")
    nlp = None

# ==========================================
# SKILL EXTRACTION
# ==========================================

def extract_skills(text: str, skills_db: List[str] = None) -> List[str]:
    """
    Extract skills from text using keyword matching
    
    Args:
        text: Resume or job description text
        skills_db: List of known skills
    
    Returns:
        List of found skills
    """
    if skills_db is None:
        skills_db = load_skills_database()
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in skills_db:
        # Match whole words
        if f" {skill.lower()} " in f" {text_lower} ":
            found_skills.append(skill)
    
    return list(set(found_skills))

def extract_skills_fuzzy(text: str, skills_db: List[str] = None) -> List[str]:
    """
    Extract skills with fuzzy matching (handles variations)
    
    Args:
        text: Resume or job description text
        skills_db: List of known skills
    
    Returns:
        List of found skills
    """
    if skills_db is None:
        skills_db = load_skills_database()
    
    text_lower = text.lower()
    found_skills = set()
    
    # Direct matching
    for skill in skills_db:
        skill_lower = skill.lower()
        
        # Exact match
        if skill_lower in text_lower:
            found_skills.add(skill)
            continue
        
        # Handle common variations
        variations = [
            skill_lower.replace('.', ''),  # Remove dots (e.g., "Node.js" → "Nodejs")
            skill_lower.replace('-', ' '),  # Replace hyphens
            skill_lower.replace(' ', ''),   # Remove spaces
        ]
        
        for var in variations:
            if var in text_lower:
                found_skills.add(skill)
                break
    
    return list(found_skills)

def extract_skills_with_spacy(text: str) -> List[str]:
    """
    Extract skills using spaCy NER
    
    Args:
        text: Resume or job description text
    
    Returns:
        List of extracted entities
    """
    if nlp is None:
        return []
    
    doc = nlp(text)
    skills = []
    
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "GPE"]:
            skills.append(ent.text)
    
    return list(set(skills))

# ==========================================
# SKILL COMPARISON
# ==========================================

def calculate_skill_match(resume_skills: List[str], job_skills: List[str]) -> float:
    """
    Calculate skill match percentage
    
    Args:
        resume_skills: Skills from resume
        job_skills: Required skills from job
    
    Returns:
        Match percentage (0-100)
    """
    if not job_skills:
        return 100.0
    
    resume_set = set(s.lower() for s in resume_skills)
    job_set = set(s.lower() for s in job_skills)
    
    matched = resume_set & job_set
    match_percentage = (len(matched) / len(job_set)) * 100
    
    return round(match_percentage, 2)

def find_missing_skills(resume_skills: List[str], job_skills: List[str]) -> List[str]:
    """
    Find skills present in job but missing from resume
    
    Args:
        resume_skills: Skills from resume
        job_skills: Required skills from job
    
    Returns:
        List of missing skills
    """
    resume_set = set(s.lower() for s in resume_skills)
    job_set = set(s.lower() for s in job_skills)
    
    missing = job_set - resume_set
    
    # Return with original casing from job_skills
    return [s for s in job_skills if s.lower() in missing]

def find_matching_skills(resume_skills: List[str], job_skills: List[str]) -> List[str]:
    """
    Find skills present in both resume and job
    
    Args:
        resume_skills: Skills from resume
        job_skills: Required skills from job
    
    Returns:
        List of matching skills
    """
    resume_set = set(s.lower() for s in resume_skills)
    job_set = set(s.lower() for s in job_skills)
    
    matched = resume_set & job_set
    
    return [s for s in job_skills if s.lower() in matched]

# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":
    # Test text
    sample_resume = """
    SKILLS
    Python, Machine Learning, TensorFlow, SQL, AWS, Docker, Git
    Experience with React, Node.js, and MongoDB
    """
    
    sample_job = """
    REQUIRED SKILLS
    Python, Machine Learning, PyTorch, SQL, AWS, Kubernetes
    """
    
    print("🔄 Testing Skill Extractor...\n")
    
    # Load skills database
    skills_db = load_skills_database()
    print(f"✅ Loaded {len(skills_db)} skills\n")
    
    # Extract skills
    resume_skills = extract_skills_fuzzy(sample_resume, skills_db)
    job_skills = extract_skills_fuzzy(sample_job, skills_db)
    
    print(f"Resume Skills: {resume_skills}")
    print(f"Job Skills: {job_skills}\n")
    
    # Calculate match
    match_pct = calculate_skill_match(resume_skills, job_skills)
    print(f"Match: {match_pct}%")
    
    # Find missing
    missing = find_missing_skills(resume_skills, job_skills)
    print(f"Missing: {missing}")
    
    # Find matching
    matching = find_matching_skills(resume_skills, job_skills)
    print(f"Matching: {matching}")
    
    print("\n✅ Skill extractor working!")