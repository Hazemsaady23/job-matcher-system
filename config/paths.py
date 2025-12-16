"""
Configuration - File Paths
Centralized path management for the job matcher system
"""

from pathlib import Path

# ==========================================
# BASE DIRECTORIES
# ==========================================
BASE_DIR = Path(r"D:\job-matcher-system")
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "pretrained_models"

# ==========================================
# DATA PATHS
# ==========================================

# Kaggle Resume Dataset
KAGGLE_RESUMES_DIR = DATA_DIR / "kaggle_resumes"
RESUME_CSV = KAGGLE_RESUMES_DIR / "UpdatedResumeDataSet.csv"
RESUME_PDFS_DIR = KAGGLE_RESUMES_DIR / "pdfs"

# LinkedIn Job Dataset
LINKEDIN_JOBS_DIR = DATA_DIR / "linkedin_jobs"
LINKEDIN_POSTINGS = LINKEDIN_JOBS_DIR / "postings.csv"
LINKEDIN_COMPANIES = LINKEDIN_JOBS_DIR / "companies.csv"
LINKEDIN_JOB_SKILLS = LINKEDIN_JOBS_DIR / "job_skills.csv"
LINKEDIN_SKILLS = LINKEDIN_JOBS_DIR / "skills.csv"
LINKEDIN_SALARIES = LINKEDIN_JOBS_DIR / "salaries.csv"
LINKEDIN_BENEFITS = LINKEDIN_JOBS_DIR / "benefits.csv"

# Processed Data
PROCESSED_DIR = DATA_DIR / "processed"
LINKEDIN_JOBS_FULL = PROCESSED_DIR / "linkedin_jobs_full.csv"
LINKEDIN_JOBS_SAMPLE = PROCESSED_DIR / "linkedin_jobs_sample.csv"
LINKEDIN_JOBS_LIGHT = PROCESSED_DIR / "linkedin_jobs_light.csv"

# Sample Data
SKILLS_DATABASE = DATA_DIR / "skills_database.json"
SAMPLE_RESUMES = DATA_DIR / "sample_resumes.txt"
SAMPLE_JOBS = DATA_DIR / "sample_job_descriptions.txt"

# ==========================================
# MODEL PATHS
# ==========================================

# Sentence Transformer (for semantic similarity)
SENTENCE_TRANSFORMER_DIR = MODELS_DIR / "sentence_transformer"
SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"  # Will be downloaded

# spaCy Model (for NER)
SPACY_MODEL_DIR = MODELS_DIR / "spacy_model"
SPACY_MODEL_NAME = "en_core_web_sm"

# GPT-2 Model (for suggestions)
GPT2_MODEL_DIR = MODELS_DIR / "gpt2_model"
GPT2_MODEL_NAME = "distilgpt2"

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def ensure_directories():
    """
    Create all necessary directories if they don't exist
    """
    directories = [
        DATA_DIR,
        KAGGLE_RESUMES_DIR,
        RESUME_PDFS_DIR,
        LINKEDIN_JOBS_DIR,
        PROCESSED_DIR,
        MODELS_DIR,
        SENTENCE_TRANSFORMER_DIR,
        SPACY_MODEL_DIR,
        GPT2_MODEL_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("✅ All directories ready!")

def check_data_files():
    """
    Check if required data files exist
    Returns: dict with file availability
    """
    files = {
        "Resume CSV": RESUME_CSV.exists(),
        "Resume PDFs": RESUME_PDFS_DIR.exists() and any(RESUME_PDFS_DIR.iterdir()),
        "LinkedIn Postings": LINKEDIN_POSTINGS.exists(),
        "LinkedIn Skills": LINKEDIN_JOB_SKILLS.exists(),
        "Skills Database": SKILLS_DATABASE.exists(),
        "Sample Resumes": SAMPLE_RESUMES.exists(),
        "Sample Jobs": SAMPLE_JOBS.exists()
    }
    
    return files

def print_data_status():
    """
    Print the status of all data files
    """
    print("\n" + "="*60)
    print("📊 DATA FILES STATUS")
    print("="*60)
    
    files = check_data_files()
    
    for name, exists in files.items():
        status = "✅" if exists else "❌"
        print(f"{status} {name}")
    
    print("="*60 + "\n")
    
    # Count missing files
    missing = sum(1 for exists in files.values() if not exists)
    
    if missing == 0:
        print("🎉 All data files are ready!")
    else:
        print(f"⚠️  {missing} data file(s) missing")
        print("💡 Run data processing scripts to prepare missing files")
    
    return missing == 0

def get_processed_job_file(sample=True):
    """
    Get the appropriate processed job file
    
    Args:
        sample (bool): If True, return sample file (1000 jobs)
                      If False, return full file (33K+ jobs)
    
    Returns:
        Path: Path to the job file
    """
    if sample:
        if LINKEDIN_JOBS_SAMPLE.exists():
            return LINKEDIN_JOBS_SAMPLE
        else:
            print("⚠️  Sample file not found, using light file")
            return LINKEDIN_JOBS_LIGHT
    else:
        if LINKEDIN_JOBS_FULL.exists():
            return LINKEDIN_JOBS_FULL
        else:
            print("⚠️  Full file not found, using sample file")
            return LINKEDIN_JOBS_SAMPLE

# ==========================================
# USAGE EXAMPLE
# ==========================================

if __name__ == "__main__":
    # Ensure all directories exist
    ensure_directories()
    
    # Check data file status
    all_ready = print_data_status()
    
    # Print some paths
    print("\n📁 Key Paths:")
    print(f"Base Directory: {BASE_DIR}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Models Directory: {MODELS_DIR}")
    print(f"\nResume CSV: {RESUME_CSV}")
    print(f"LinkedIn Jobs: {LINKEDIN_POSTINGS}")
    print(f"Skills Database: {SKILLS_DATABASE}")
    
    # Test processed file getter
    print(f"\n🎯 Using job file: {get_processed_job_file(sample=True)}")