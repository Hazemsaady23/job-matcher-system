"""
Matcher - Core matching algorithm between resume and job
"""

import sys
sys.path.append('.')
from sentence_transformers import SentenceTransformer
from models.resume_parser import parse_resume, compare_education_levels
from models.job_analyzer import parse_job_description
from models.skill_extractor import calculate_skill_match, find_missing_skills, find_matching_skills
from config.settings import *
import streamlit as st

# Load Sentence-BERT model
@st.cache_resource
def load_sentence_transformer():
    """Load Sentence-BERT model for semantic similarity"""
    print("📥 Loading Sentence-BERT model...")
    model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
    print("✅ Model loaded!")
    return model

# ==========================================
# CORE MATCHING ALGORITHM
# ==========================================

def calculate_match_score(resume_text: str, job_text: str) -> dict:
    """
    Calculate comprehensive match score between resume and job
    
    Args:
        resume_text: Resume text
        job_text: Job description text
    
    Returns:
        Dictionary with scores and details
    """
    # Parse resume and job
    resume = parse_resume(resume_text)
    job = parse_job_description(job_text)
    
    # Load model
    model = load_sentence_transformer()
    
    # 1. SEMANTIC SIMILARITY (40%)
    semantic_score = calculate_semantic_similarity(
        resume['cleaned_text'], 
        job['cleaned_text'], 
        model
    )
    
    # 2. SKILLS MATCH (30%)
    skills_score = calculate_skill_match(
        resume['skills'], 
        job['required_skills']
    ) / 100  # Normalize to 0-1
    
    # 3. EXPERIENCE MATCH (15%)
    experience_score = calculate_experience_match(
        resume['years_of_experience'],
        job['years_of_experience']
    )
    
    # 4. EDUCATION MATCH (15%)
    education_score = compare_education_levels(
        resume['education_level'],
        job['education_required']
    )
    
    # Calculate weighted total
    total_score = (
        semantic_score * SEMANTIC_SIMILARITY_WEIGHT +
        skills_score * SKILLS_MATCH_WEIGHT +
        experience_score * EXPERIENCE_MATCH_WEIGHT +
        education_score * EDUCATION_MATCH_WEIGHT
    ) * 100  # Convert to 0-100 scale
    
    # Find skill gaps
    missing_skills = find_missing_skills(resume['skills'], job['required_skills'])
    matching_skills = find_matching_skills(resume['skills'], job['required_skills'])
    
    # Compile results
    results = {
        'total_score': round(total_score, 2),
        'match_quality': get_match_quality(total_score)[0],
        'match_emoji': get_match_quality(total_score)[1],
        
        # Component scores (0-100)
        'semantic_score': round(semantic_score * 100, 2),
        'skills_score': round(skills_score * 100, 2),
        'experience_score': round(experience_score * 100, 2),
        'education_score': round(education_score * 100, 2),
        
        # Details
        'resume': resume,
        'job': job,
        'matching_skills': matching_skills,
        'missing_skills': missing_skills,
        'skills_match_count': f"{len(matching_skills)}/{len(job['required_skills'])}"
    }
    
    return results

# ==========================================
# COMPONENT CALCULATIONS
# ==========================================

def calculate_semantic_similarity(text1: str, text2: str, model) -> float:
    """
    Calculate semantic similarity using Sentence-BERT
    
    Args:
        text1: First text
        text2: Second text
        model: Sentence-BERT model
    
    Returns:
        Similarity score (0-1)
    """
    # Generate embeddings
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)
    
    # Calculate cosine similarity
    from torch.nn.functional import cosine_similarity
    similarity = cosine_similarity(embedding1.unsqueeze(0), embedding2.unsqueeze(0))
    
    return similarity.item()

def calculate_experience_match(resume_years: int, required_years: int) -> float:
    """
    Calculate experience match score
    
    Args:
        resume_years: Years of experience in resume
        required_years: Required years in job
    
    Returns:
        Score (0-1)
    """
    if required_years == 0:
        return 1.0  # No requirement
    
    if resume_years >= required_years:
        return 1.0  # Meets or exceeds
    elif resume_years >= required_years * 0.8:
        return 0.9  # Close enough
    elif resume_years >= required_years * 0.6:
        return 0.7  # Somewhat close
    elif resume_years > 0:
        return 0.4  # Has some experience
    else:
        return 0.0  # No experience

# ==========================================
# BATCH MATCHING
# ==========================================

def match_resume_to_multiple_jobs(resume_text: str, job_list: list) -> list:
    """
    Match one resume against multiple jobs
    
    Args:
        resume_text: Resume text
        job_list: List of job description texts
    
    Returns:
        List of match results sorted by score
    """
    results = []
    
    for i, job_text in enumerate(job_list):
        try:
            match = calculate_match_score(resume_text, job_text)
            match['job_index'] = i
            results.append(match)
        except Exception as e:
            print(f"⚠️  Error matching job {i}: {e}")
    
    # Sort by total score (descending)
    results.sort(key=lambda x: x['total_score'], reverse=True)
    
    return results

# ==========================================
# MATCH INSIGHTS
# ==========================================

def generate_match_insights(match_result: dict) -> list:
    """
    Generate actionable insights from match results
    
    Args:
        match_result: Result from calculate_match_score
    
    Returns:
        List of insight strings
    """
    insights = []
    
    total = match_result['total_score']
    semantic = match_result['semantic_score']
    skills = match_result['skills_score']
    experience = match_result['experience_score']
    education = match_result['education_score']
    
    # Overall assessment
    if total >= EXCELLENT_MATCH_THRESHOLD:
        insights.append("🎉 Excellent match! This is a great opportunity for you.")
    elif total >= GOOD_MATCH_THRESHOLD:
        insights.append("👍 Good match! You have strong qualifications for this role.")
    elif total >= MIN_MATCH_SCORE:
        insights.append("🤔 Fair match. Consider highlighting relevant experience.")
    else:
        insights.append("⚠️  Low match. This may not be the best fit.")
    
    # Semantic similarity
    if semantic >= 80:
        insights.append("✅ Your resume content aligns well with the job description.")
    elif semantic < 60:
        insights.append("💡 Consider using more keywords from the job description.")
    
    # Skills
    if skills >= 80:
        insights.append("✅ You have most of the required skills!")
    elif skills >= 50:
        insights.append(f"📚 Good skill match. Missing: {', '.join(match_result['missing_skills'][:3])}")
    else:
        insights.append(f"⚠️  Skill gap detected. Focus on: {', '.join(match_result['missing_skills'][:5])}")
    
    # Experience
    if experience >= 90:
        insights.append("✅ Your experience level matches perfectly.")
    elif experience < 70:
        resume_years = match_result['resume']['years_of_experience']
        job_years = match_result['job']['years_of_experience']
        if resume_years < job_years:
            insights.append(f"⚠️  Job requires {job_years}+ years, you have {resume_years} years.")
    
    # Education
    if education >= 90:
        insights.append("✅ Your education meets the requirements.")
    elif education < 70:
        insights.append(f"⚠️  Job requires: {match_result['job']['education_required']}")
    
    return insights

# ==========================================
# RECOMMENDATIONS
# ==========================================

def generate_recommendations(match_result: dict) -> list:
    """
    Generate actionable recommendations to improve match
    
    Args:
        match_result: Result from calculate_match_score
    
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    skills = match_result['skills_score']
    semantic = match_result['semantic_score']
    
    # Skill recommendations
    if skills < 70 and match_result['missing_skills']:
        missing = match_result['missing_skills'][:5]
        recommendations.append(f"📚 **Learn these skills:** {', '.join(missing)}")
    
    # Resume optimization
    if semantic < 70:
        recommendations.append("📝 **Update resume:** Use more keywords from the job description")
        recommendations.append("💡 **Tailor content:** Highlight relevant experience for this role")
    
    # Quantify achievements
    recommendations.append("📊 **Add numbers:** Quantify your achievements (e.g., 'Improved efficiency by 30%')")
    
    # ATS optimization
    recommendations.append("🤖 **ATS-friendly:** Use standard section headers (Experience, Education, Skills)")
    
    return recommendations

# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":
    sample_resume = """
    JOHN DOE
    Senior Data Scientist
    Email: john@email.com
    
    SUMMARY
    5 years of experience in machine learning and data science
    
    SKILLS
    Python, Machine Learning, TensorFlow, SQL, AWS, Pandas, NumPy
    
    EXPERIENCE
    Senior Data Scientist at TechCorp (3 years)
    - Built ML models with 95% accuracy
    - Led team of 4 data scientists
    
    EDUCATION
    Master of Science in Computer Science
    """
    
    sample_job = """
    Position: Senior Data Scientist
    Company: AI Innovations
    
    We seek a Senior Data Scientist with 4+ years experience.
    
    REQUIRED SKILLS:
    Python, Machine Learning, PyTorch, SQL, AWS, Docker
    
    REQUIREMENTS:
    - Master's degree preferred
    - 4+ years of experience
    - Strong ML background
    """
    
    print("🔄 Testing Matcher...\n")
    
    # Calculate match
    result = calculate_match_score(sample_resume, sample_job)
    
    print(f"Total Score: {result['total_score']}/100 {result['match_emoji']}")
    print(f"Quality: {result['match_quality']}")
    print(f"\nBreakdown:")
    print(f"  Semantic: {result['semantic_score']}/100")
    print(f"  Skills: {result['skills_score']}/100")
    print(f"  Experience: {result['experience_score']}/100")
    print(f"  Education: {result['education_score']}/100")
    
    print(f"\nMatching Skills ({len(result['matching_skills'])}):", result['matching_skills'])
    print(f"Missing Skills ({len(result['missing_skills'])}):", result['missing_skills'])
    
    print("\n💡 Insights:")
    for insight in generate_match_insights(result):
        print(f"  {insight}")
    
    print("\n📋 Recommendations:")
    for rec in generate_recommendations(result):
        print(f"  {rec}")
    
    print("\n✅ Matcher working!")