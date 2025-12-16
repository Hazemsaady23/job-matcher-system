"""
Text Processor - Clean and preprocess text data
"""

import re
import string
from typing import List
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

# ==========================================
# TEXT CLEANING
# ==========================================

def clean_text(text: str, remove_stops: bool = False) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Input text
        remove_stops: Remove stopwords
    
    Returns:
        Cleaned text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    
    # Remove emails
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove phone numbers
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove stopwords if requested
    if remove_stops:
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(text)
        text = ' '.join([w for w in words if w not in stop_words])
    
    return text.strip()

def remove_special_characters(text: str, keep_spaces: bool = True) -> str:
    """Remove special characters from text"""
    if keep_spaces:
        pattern = r'[^a-zA-Z0-9\s]'
    else:
        pattern = r'[^a-zA-Z0-9]'
    
    return re.sub(pattern, '', text)

def normalize_whitespace(text: str) -> str:
    """Normalize whitespace to single spaces"""
    return ' '.join(text.split())

# ==========================================
# TEXT EXTRACTION
# ==========================================

def extract_keywords(text: str, top_n: int = 20) -> List[str]:
    """Extract top keywords from text (simple frequency-based)"""
    # Clean text
    text = clean_text(text, remove_stops=True)
    
    # Tokenize
    words = word_tokenize(text.lower())
    
    # Filter words (length > 3, alphanumeric)
    words = [w for w in words if len(w) > 3 and w.isalnum()]
    
    # Count frequency
    from collections import Counter
    word_freq = Counter(words)
    
    # Get top N
    return [word for word, _ in word_freq.most_common(top_n)]

def extract_sentences(text: str, max_sentences: int = None) -> List[str]:
    """Extract sentences from text"""
    # Simple sentence splitting
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if max_sentences:
        return sentences[:max_sentences]
    return sentences

# ==========================================
# TEXT METRICS
# ==========================================

def get_word_count(text: str) -> int:
    """Count words in text"""
    return len(text.split())

def get_char_count(text: str) -> int:
    """Count characters in text"""
    return len(text)

def get_sentence_count(text: str) -> int:
    """Count sentences in text"""
    return len(extract_sentences(text))

# ==========================================
# RESUME/JOB SPECIFIC
# ==========================================

def extract_email(text: str) -> str:
    """Extract email address from text"""
    match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    return match.group(0) if match else ""

def extract_phone(text: str) -> str:
    """Extract phone number from text"""
    match = re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
    return match.group(0) if match else ""

def extract_urls(text: str) -> List[str]:
    """Extract URLs from text"""
    return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)

def extract_years_of_experience(text: str) -> int:
    """
    Extract years of experience from text
    Looks for patterns like "5 years", "5+ years", "5-7 years"
    """
    # Common patterns
    patterns = [
        r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
        r'(\d+)\+?\s*yrs?\s+(?:of\s+)?experience',
        r'experience[:\s]+(\d+)\+?\s*years?',
        r'(\d+)-\d+\s*years?\s+(?:of\s+)?experience'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return int(match.group(1))
    
    return 0

# ==========================================
# SECTION DETECTION
# ==========================================

def detect_sections(text: str) -> dict:
    """
    Detect common resume/job sections
    Returns dict with section presence
    """
    text_lower = text.lower()
    
    sections = {
        'summary': any(keyword in text_lower for keyword in ['summary', 'objective', 'profile']),
        'experience': any(keyword in text_lower for keyword in ['experience', 'work history', 'employment']),
        'education': any(keyword in text_lower for keyword in ['education', 'academic', 'degree']),
        'skills': any(keyword in text_lower for keyword in ['skills', 'technical skills', 'competencies']),
        'projects': any(keyword in text_lower for keyword in ['projects', 'portfolio']),
        'certifications': any(keyword in text_lower for keyword in ['certifications', 'certificates', 'licensed'])
    }
    
    return sections

# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":
    # Test text
    sample = """
    John Doe - Senior Data Scientist
    Email: john.doe@email.com | Phone: 555-123-4567
    
    SUMMARY
    Experienced data scientist with 5+ years of experience in machine learning.
    
    SKILLS
    Python, Machine Learning, SQL, AWS
    
    Check my portfolio at https://johndoe.com
    """
    
    print("🔄 Testing Text Processor...\n")
    
    print("Original:", sample[:100], "...")
    print("\nCleaned:", clean_text(sample)[:100], "...")
    print("\nEmail:", extract_email(sample))
    print("Phone:", extract_phone(sample))
    print("Years:", extract_years_of_experience(sample))
    print("\nKeywords:", extract_keywords(sample)[:10])
    print("\nSections:", detect_sections(sample))
    print("\n✅ Text processor working!")