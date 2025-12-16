"""
Data Loader - Load and cache datasets
"""

import pandas as pd
import json
from pathlib import Path
import streamlit as st
from config.paths import *
from config.settings import USE_SAMPLE_DATA, CACHE_DATA

# ==========================================
# LOAD RESUMES
# ==========================================

@st.cache_data
def load_resume_dataset():
    """Load Kaggle resume dataset"""
    if not RESUME_CSV.exists():
        st.error(f"❌ Resume dataset not found: {RESUME_CSV}")
        return None
    
    df = pd.read_csv(RESUME_CSV)
    print(f"✅ Loaded {len(df)} resumes")
    return df

# ==========================================
# LOAD JOBS
# ==========================================

@st.cache_data
def load_job_dataset(sample=USE_SAMPLE_DATA):
    """Load LinkedIn job dataset"""
    job_file = get_processed_job_file(sample=sample)
    
    if not job_file.exists():
        st.error(f"❌ Job dataset not found: {job_file}")
        st.info("💡 Run: python process_linkedin_data.py")
        return None
    
    df = pd.read_csv(job_file)
    print(f"✅ Loaded {len(df)} jobs")
    return df

# ==========================================
# LOAD SKILLS DATABASE
# ==========================================

@st.cache_data
def load_skills_database():
    """Load skills JSON database"""
    if not SKILLS_DATABASE.exists():
        st.warning(f"⚠️  Skills database not found: {SKILLS_DATABASE}")
        return {}
    
    with open(SKILLS_DATABASE, 'r') as f:
        skills = json.load(f)
    
    # Flatten to a single list
    all_skills = []
    for category, skill_list in skills.items():
        all_skills.extend(skill_list)
    
    print(f"✅ Loaded {len(all_skills)} skills")
    return all_skills

# ==========================================
# LOAD SAMPLE DATA
# ==========================================

def load_sample_resumes():
    """Load sample resume text file"""
    if not SAMPLE_RESUMES.exists():
        return []
    
    with open(SAMPLE_RESUMES, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by separator
    resumes = content.split('---')
    return [r.strip() for r in resumes if r.strip()]

def load_sample_jobs():
    """Load sample job descriptions"""
    if not SAMPLE_JOBS.exists():
        return []
    
    with open(SAMPLE_JOBS, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by separator
    jobs = content.split('---')
    return [j.strip() for j in jobs if j.strip()]

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_random_resume(n=1):
    """Get random resume(s) from dataset"""
    df = load_resume_dataset()
    if df is None:
        return None
    return df.sample(n=n)

def get_random_job(n=1):
    """Get random job(s) from dataset"""
    df = load_job_dataset()
    if df is None:
        return None
    return df.sample(n=n)

# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":
    print("\n🔄 Testing Data Loader...\n")
    
    # Test resume loading
    resumes = load_resume_dataset()
    if resumes is not None:
        print(f"Resume columns: {list(resumes.columns)}")
    
    # Test job loading
    jobs = load_job_dataset(sample=True)
    if jobs is not None:
        print(f"Job columns: {list(jobs.columns)}")
    
    # Test skills
    skills = load_skills_database()
    print(f"Sample skills: {skills[:10]}")
    
    # Test samples
    sample_resumes = load_sample_resumes()
    print(f"\n✅ Loaded {len(sample_resumes)} sample resumes")
    
    sample_jobs = load_sample_jobs()
    print(f"✅ Loaded {len(sample_jobs)} sample jobs")