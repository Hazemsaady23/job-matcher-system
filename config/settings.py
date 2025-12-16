"""
Configuration - Application Settings
All configurable parameters for the job matcher system
"""

# ==========================================
# MATCHING ALGORITHM SETTINGS
# ==========================================

# Scoring weights (must sum to 1.0)
SEMANTIC_SIMILARITY_WEIGHT = 0.40  # 40%
SKILLS_MATCH_WEIGHT = 0.30         # 30%
EXPERIENCE_MATCH_WEIGHT = 0.15     # 15%
EDUCATION_MATCH_WEIGHT = 0.15      # 15%

# Matching thresholds
MIN_MATCH_SCORE = 50.0             # Minimum score to consider (0-100)
GOOD_MATCH_THRESHOLD = 70.0        # Score above this = "Good Match"
EXCELLENT_MATCH_THRESHOLD = 85.0   # Score above this = "Excellent Match"

# Skills matching
MIN_SKILL_MATCHES = 3              # Minimum skills that must match
SKILL_MATCH_THRESHOLD = 0.6        # 60% of required skills should match

# ==========================================
# TEXT PROCESSING SETTINGS
# ==========================================

# Text cleaning
MIN_TEXT_LENGTH = 50               # Minimum characters for valid text
MAX_TEXT_LENGTH = 10000            # Maximum characters to process
REMOVE_STOPWORDS = True            # Remove common words (the, is, at, etc.)

# PDF extraction
MAX_PDF_PAGES = 10                 # Maximum pages to extract from PDF

# ==========================================
# MODEL SETTINGS
# ==========================================

# Sentence Transformer
SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_BATCH_SIZE = 32
MAX_SEQ_LENGTH = 512

# spaCy NER
SPACY_MODEL = "en_core_web_sm"
SPACY_BATCH_SIZE = 50

# GPT-2 Text Generation
GPT2_MODEL = "distilgpt2"
GPT2_MAX_LENGTH = 150
GPT2_TEMPERATURE = 0.8
GPT2_TOP_P = 0.92

# ==========================================
# ATS CHECKER SETTINGS
# ==========================================

ATS_MIN_KEYWORD_DENSITY = 0.02     # 2% keyword density minimum
ATS_REQUIRED_SECTIONS = ["experience", "education", "skills"]
ATS_MIN_WORD_COUNT = 200
ATS_MAX_WORD_COUNT = 1000
ATS_PENALTY_PER_MISSING_SECTION = 10

# ==========================================
# UI SETTINGS (Streamlit)
# ==========================================

# Display
RESULTS_PER_PAGE = 10
MAX_JOBS_BATCH_ANALYSIS = 50
SHOW_CONFIDENCE_SCORES = True

# Charts
CHART_HEIGHT = 400
CHART_THEME = "plotly_dark"

# ==========================================
# DATA LOADING SETTINGS
# ==========================================

USE_SAMPLE_DATA = True             # True = 1000 jobs, False = full dataset
CACHE_DATA = True                  # Cache loaded data in memory
MAX_RESUMES_TO_LOAD = 1000         # For batch processing

# ==========================================
# PERFORMANCE SETTINGS
# ==========================================

USE_GPU = False                    # Use GPU if available (set True if you have CUDA)
NUM_WORKERS = 4                    # Parallel processing workers
BATCH_PROCESSING = True            # Process multiple items at once

# ==========================================
# LOGGING
# ==========================================

LOG_LEVEL = "INFO"                 # DEBUG, INFO, WARNING, ERROR
VERBOSE = True                     # Print detailed progress

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_match_quality(score):
    """Get match quality label based on score"""
    if score >= EXCELLENT_MATCH_THRESHOLD:
        return "Excellent Match", "🟢"
    elif score >= GOOD_MATCH_THRESHOLD:
        return "Good Match", "🟡"
    elif score >= MIN_MATCH_SCORE:
        return "Fair Match", "🟠"
    else:
        return "Poor Match", "🔴"

def validate_settings():
    """Validate that settings are correct"""
    # Check weights sum to 1.0
    total_weight = (SEMANTIC_SIMILARITY_WEIGHT + 
                   SKILLS_MATCH_WEIGHT + 
                   EXPERIENCE_MATCH_WEIGHT + 
                   EDUCATION_MATCH_WEIGHT)
    
    if abs(total_weight - 1.0) > 0.01:
        raise ValueError(f"Weights must sum to 1.0, got {total_weight}")
    
    print("✅ All settings validated!")

if __name__ == "__main__":
    validate_settings()
    print("\n📊 Current Settings:")
    print(f"  Matching: {SEMANTIC_SIMILARITY_WEIGHT:.0%} semantic + "
          f"{SKILLS_MATCH_WEIGHT:.0%} skills + "
          f"{EXPERIENCE_MATCH_WEIGHT:.0%} experience + "
          f"{EDUCATION_MATCH_WEIGHT:.0%} education")
    print(f"  Sample Data: {USE_SAMPLE_DATA}")
    print(f"  GPU: {'Enabled' if USE_GPU else 'Disabled'}")