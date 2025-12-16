"""
ATS Checker - Check Applicant Tracking System compatibility
"""

import sys
sys.path.append('.')
from utils.text_processor import get_word_count, detect_sections, extract_keywords
from config.settings import *

# ==========================================
# ATS COMPATIBILITY CHECK
# ==========================================

def check_ats_compatibility(resume_text: str, job_text: str = None) -> dict:
    """
    Check if resume is ATS-friendly
    
    Args:
        resume_text: Resume text
        job_text: Optional job description for keyword matching
    
    Returns:
        ATS compatibility report
    """
    report = {
        'ats_score': 100,
        'issues': [],
        'warnings': [],
        'suggestions': [],
        'checks': {}
    }
    
    # 1. Word Count Check
    word_count = get_word_count(resume_text)
    if word_count < ATS_MIN_WORD_COUNT:
        report['ats_score'] -= 15
        report['issues'].append(f"Resume too short ({word_count} words, minimum {ATS_MIN_WORD_COUNT})")
    elif word_count > ATS_MAX_WORD_COUNT:
        report['ats_score'] -= 10
        report['warnings'].append(f"Resume too long ({word_count} words, maximum {ATS_MAX_WORD_COUNT})")
    else:
        report['checks']['word_count'] = '✅ Good length'
    
    # 2. Section Headers Check
    sections = detect_sections(resume_text)
    missing_sections = []
    
    for required_section in ATS_REQUIRED_SECTIONS:
        if not sections.get(required_section):
            missing_sections.append(required_section.title())
            report['ats_score'] -= ATS_PENALTY_PER_MISSING_SECTION
    
    if missing_sections:
        report['issues'].append(f"Missing sections: {', '.join(missing_sections)}")
    else:
        report['checks']['sections'] = '✅ All sections present'
    
    # 3. Keyword Density (if job provided)
    if job_text:
        keyword_score = check_keyword_density(resume_text, job_text)
        report['keyword_density'] = keyword_score
        
        if keyword_score < ATS_MIN_KEYWORD_DENSITY:
            report['ats_score'] -= 20
            report['issues'].append(f"Low keyword density ({keyword_score:.1%}, minimum {ATS_MIN_KEYWORD_DENSITY:.1%})")
        else:
            report['checks']['keywords'] = f"✅ Good keyword match ({keyword_score:.1%})"
    
    # 4. Formatting Check
    formatting_issues = check_formatting(resume_text)
    if formatting_issues:
        report['warnings'].extend(formatting_issues)
        report['ats_score'] -= 5 * len(formatting_issues)
    else:
        report['checks']['formatting'] = '✅ Clean formatting'
    
    # 5. File Format Suggestion
    report['suggestions'].append("💾 Save as .docx or .pdf (avoid .jpg or .png)")
    report['suggestions'].append("📝 Use standard fonts (Arial, Calibri, Times New Roman)")
    report['suggestions'].append("🔤 Use standard section headers")
    
    # Ensure score doesn't go below 0
    report['ats_score'] = max(0, report['ats_score'])
    
    # Overall assessment
    if report['ats_score'] >= 80:
        report['status'] = '✅ ATS-Friendly'
        report['status_color'] = 'green'
    elif report['ats_score'] >= 60:
        report['status'] = '⚠️ Needs Improvement'
        report['status_color'] = 'yellow'
    else:
        report['status'] = '❌ ATS Issues Detected'
        report['status_color'] = 'red'
    
    return report

# ==========================================
# KEYWORD DENSITY
# ==========================================

def check_keyword_density(resume_text: str, job_text: str) -> float:
    """
    Check keyword overlap between resume and job
    
    Returns:
        Keyword density score (0-1)
    """
    # Extract keywords from both
    resume_keywords = set(extract_keywords(resume_text, top_n=30))
    job_keywords = set(extract_keywords(job_text, top_n=30))
    
    if not job_keywords:
        return 1.0
    
    # Calculate overlap
    matched = resume_keywords & job_keywords
    density = len(matched) / len(job_keywords)
    
    return density

# ==========================================
# FORMATTING CHECKS
# ==========================================

def check_formatting(text: str) -> list:
    """
    Check for formatting issues that ATS might struggle with
    
    Returns:
        List of issues
    """
    issues = []
    
    # Check for tables (hard to detect in plain text, but look for patterns)
    if '|' in text or '\t' in text:
        issues.append("⚠️ Possible tables detected (ATS may not parse correctly)")
    
    # Check for special characters
    special_chars = ['★', '●', '◆', '▪', '✓', '→']
    if any(char in text for char in special_chars):
        issues.append("⚠️ Special characters detected (use standard bullets)")
    
    # Check for headers/footers patterns
    if text.count('Page') > 2 or text.count('Confidential') > 1:
        issues.append("⚠️ Possible headers/footers (remove before submitting)")
    
    # Check line length (extremely long lines might indicate formatting issues)
    lines = text.split('\n')
    very_long_lines = [l for l in lines if len(l) > 200]
    if len(very_long_lines) > 5:
        issues.append("⚠️ Very long lines detected (check formatting)")
    
    return issues

# ==========================================
# IMPROVEMENT SUGGESTIONS
# ==========================================

def generate_ats_improvements(ats_report: dict) -> list:
    """
    Generate specific improvement suggestions based on ATS report
    
    Args:
        ats_report: Result from check_ats_compatibility
    
    Returns:
        List of actionable suggestions
    """
    suggestions = []
    
    score = ats_report['ats_score']
    
    if score < 80:
        suggestions.append("🔧 **Priority Fixes:**")
        
        # Address issues first
        for issue in ats_report['issues']:
            if 'section' in issue.lower():
                suggestions.append("  • Add missing sections with clear headers")
            elif 'word' in issue.lower():
                suggestions.append("  • Adjust resume length to 400-800 words")
            elif 'keyword' in issue.lower():
                suggestions.append("  • Add more relevant keywords from job description")
        
        suggestions.append("\n💡 **Quick Wins:**")
        suggestions.append("  • Use standard section headers (EXPERIENCE, EDUCATION, SKILLS)")
        suggestions.append("  • Remove graphics, images, and special formatting")
        suggestions.append("  • Use simple bullet points (•) instead of fancy symbols")
        suggestions.append("  • List skills clearly (avoid tables)")
        suggestions.append("  • Save as .docx or PDF (not .jpg or .png)")
    
    return suggestions

# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":
    sample_resume = """
    JOHN DOE
    Senior Data Scientist
    
    SUMMARY
    5 years of experience in machine learning
    
    SKILLS
    Python, Machine Learning, SQL, AWS
    
    EXPERIENCE
    Data Scientist at TechCorp
    Built ML models and deployed to production
    
    EDUCATION
    Master of Science in Computer Science
    """
    
    sample_job = """
    Position: Senior Data Scientist
    
    Required: Python, Machine Learning, Deep Learning, SQL, AWS, Docker
    """
    
    print("🔄 Testing ATS Checker...\n")
    
    # Check ATS compatibility
    report = check_ats_compatibility(sample_resume, sample_job)
    
    print(f"ATS Score: {report['ats_score']}/100")
    print(f"Status: {report['status']}\n")
    
    if report['checks']:
        print("✅ Passed Checks:")
        for check, result in report['checks'].items():
            print(f"  {result}")
    
    if report['issues']:
        print("\n❌ Issues:")
        for issue in report['issues']:
            print(f"  {issue}")
    
    if report['warnings']:
        print("\n⚠️ Warnings:")
        for warning in report['warnings']:
            print(f"  {warning}")
    
    print("\n💡 Suggestions:")
    for suggestion in report['suggestions'][:3]:
        print(f"  {suggestion}")
    
    # Generate improvements
    improvements = generate_ats_improvements(report)
    if improvements:
        print("\n🔧 Improvements:")
        for imp in improvements:
            print(imp)
    
    print("\n✅ ATS checker working!")