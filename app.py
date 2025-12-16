"""
Job Matcher & Resume Analyzer - Main Streamlit Application
"""

import streamlit as st
import sys
sys.path.append('.')

from utils.pdf_extractor import extract_text_from_uploaded_file
from models.matcher import calculate_match_score, generate_match_insights, generate_recommendations
from models.ats_checker import check_ats_compatibility, generate_ats_improvements
from utils.visualization import *
from utils.data_loader import load_sample_resumes, load_sample_jobs
from config.settings import *

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Job Matcher & Resume Analyzer",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM CSS
# ==========================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617 0%, #0f172a 100%);
    }
    h1 {
        color: #f59e0b !important;
        text-align: center;
    }
    h2, h3 {
        color: #fbbf24 !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(245, 158, 11, 0.5);
    }
    .stTextArea textarea {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border: 2px solid #334155 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# MAIN APP
# ==========================================

def main():
    # Title
    st.markdown("# 💼 AI Job Matcher & Resume Analyzer")
    st.markdown("### Match your resume with job descriptions using AI")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎯 How It Works")
        st.markdown("""
        1. **Upload Resume** (PDF/DOCX/TXT)
        2. **Paste Job Description**
        3. **Get AI Analysis**
        
        **Features:**
        - 🤖 AI Matching Score
        - 📊 Skills Gap Analysis
        - ✅ ATS Compatibility Check
        - 💡 Improvement Suggestions
        """)
        
        st.markdown("---")
        st.markdown("### 🔧 Settings")
        
        show_details = st.checkbox("Show Detailed Analysis", value=True)
        show_charts = st.checkbox("Show Visualizations", value=True)
        
        st.markdown("---")
        st.markdown("### 📚 Quick Samples")
        if st.button("Load Sample Data"):
            st.session_state['use_sample'] = True
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Single Match", "📊 Batch Analysis", "ℹ️ About"])
    
    # ==========================================
    # TAB 1: SINGLE MATCH
    # ==========================================
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📄 Step 1: Upload Resume")
            
            # Resume input
            resume_file = st.file_uploader(
                "Upload your resume",
                type=['pdf', 'docx', 'txt'],
                help="Supported formats: PDF, DOCX, TXT"
            )
            
            resume_text = ""
            
            if resume_file:
                with st.spinner("📖 Extracting text from resume..."):
                    try:
                        resume_text = extract_text_from_uploaded_file(resume_file)
                        st.success(f"✅ Resume loaded ({len(resume_text)} characters)")
                        
                        with st.expander("👀 Preview Resume Text"):
                            st.text_area("", resume_text[:500] + "...", height=150, disabled=True)
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
            
            # Or use sample
            if st.session_state.get('use_sample'):
                samples = load_sample_resumes()
                if samples:
                    resume_text = samples[0]
                    st.info("📝 Using sample resume")
        
        with col2:
            st.markdown("### 💼 Step 2: Paste Job Description")
            
            job_text = st.text_area(
                "Paste the job description here",
                height=300,
                placeholder="Paste the complete job description including requirements, skills, qualifications..."
            )
            
            # Or use sample
            if st.session_state.get('use_sample'):
                samples = load_sample_jobs()
                if samples:
                    job_text = samples[0]
                    st.info("📝 Using sample job description")
        
        # Analyze button
        st.markdown("---")
        
        if st.button("🚀 Analyze Match", type="primary", use_container_width=True):
            if not resume_text:
                st.error("⚠️ Please upload a resume or load sample data")
            elif not job_text:
                st.error("⚠️ Please paste a job description or load sample data")
            else:
                # Main analysis
                with st.spinner("🤖 AI is analyzing... This may take 30-60 seconds..."):
                    try:
                        # Calculate match
                        result = calculate_match_score(resume_text, job_text)
                        
                        # Check ATS
                        ats_result = check_ats_compatibility(resume_text, job_text)
                        
                        st.success("✅ Analysis Complete!")
                        
                        # ==========================================
                        # RESULTS SECTION
                        # ==========================================
                        st.markdown("---")
                        st.markdown("## 📊 Match Results")
                        
                        # Main score
                        score_col1, score_col2, score_col3 = st.columns([2, 1, 1])
                        
                        with score_col1:
                            if show_charts:
                                st.plotly_chart(
                                    create_score_gauge(result['total_score']),
                                    use_container_width=True
                                )
                        
                        with score_col2:
                            st.metric(
                                "Overall Match",
                                f"{result['total_score']:.1f}%",
                                result['match_quality']
                            )
                            st.metric(
                                "ATS Score",
                                f"{ats_result['ats_score']}/100",
                                ats_result['status']
                            )
                        
                        with score_col3:
                            st.metric(
                                "Skills Match",
                                result['skills_match_count']
                            )
                            st.metric(
                                "Experience",
                                f"{result['resume']['years_of_experience']} years"
                            )
                        
                        # Score breakdown
                        if show_charts:
                            st.markdown("### 📈 Score Breakdown")
                            
                            breakdown_col1, breakdown_col2 = st.columns(2)
                            
                            with breakdown_col1:
                                st.plotly_chart(
                                    create_score_breakdown(
                                        result['semantic_score'],
                                        result['skills_score'],
                                        result['experience_score'],
                                        result['education_score']
                                    ),
                                    use_container_width=True
                                )
                            
                            with breakdown_col2:
                                st.plotly_chart(
                                    create_radar_chart(
                                        result['semantic_score'],
                                        result['skills_score'],
                                        result['experience_score'],
                                        result['education_score']
                                    ),
                                    use_container_width=True
                                )
                        
                        # Skills analysis
                        st.markdown("### 🎯 Skills Analysis")
                        
                        if show_charts and (result['matching_skills'] or result['missing_skills']):
                            st.plotly_chart(
                                create_skills_comparison(
                                    result['matching_skills'],
                                    result['missing_skills']
                                ),
                                use_container_width=True
                            )
                        
                        skill_col1, skill_col2 = st.columns(2)
                        
                        with skill_col1:
                            st.markdown("#### ✅ Skills You Have")
                            if result['matching_skills']:
                                for skill in result['matching_skills'][:10]:
                                    st.markdown(f"- {skill}")
                            else:
                                st.info("No matching skills found")
                        
                        with skill_col2:
                            st.markdown("#### ⚠️ Missing Skills")
                            if result['missing_skills']:
                                for skill in result['missing_skills'][:10]:
                                    st.markdown(f"- {skill}")
                            else:
                                st.success("You have all required skills!")
                        
                        # Insights
                        st.markdown("### 💡 AI Insights")
                        insights = generate_match_insights(result)
                        for insight in insights:
                            st.info(insight)
                        
                        # Recommendations
                        st.markdown("### 📋 Recommendations")
                        recommendations = generate_recommendations(result)
                        for rec in recommendations:
                            st.success(rec)
                        
                        # ATS Analysis
                        st.markdown("### 🤖 ATS Compatibility")
                        
                        if show_charts:
                            st.plotly_chart(
                                create_ats_chart(ats_result['ats_score']),
                                use_container_width=True
                            )
                        
                        if ats_result['issues']:
                            st.error("**Issues Found:**")
                            for issue in ats_result['issues']:
                                st.markdown(f"- {issue}")
                        
                        if ats_result['warnings']:
                            st.warning("**Warnings:**")
                            for warning in ats_result['warnings']:
                                st.markdown(f"- {warning}")
                        
                        # ATS Improvements
                        improvements = generate_ats_improvements(ats_result)
                        if improvements:
                            with st.expander("🔧 View ATS Improvements"):
                                for imp in improvements:
                                    st.markdown(imp)
                        
                        # Detailed analysis (optional)
                        if show_details:
                            with st.expander("📑 Detailed Analysis"):
                                st.json({
                                    'match_score': result['total_score'],
                                    'semantic_score': result['semantic_score'],
                                    'skills_score': result['skills_score'],
                                    'experience_score': result['experience_score'],
                                    'education_score': result['education_score'],
                                    'resume_word_count': result['resume']['word_count'],
                                    'job_word_count': result['job']['word_count']
                                })
                    
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {e}")
                        st.exception(e)
    
    # ==========================================
    # TAB 2: BATCH ANALYSIS
    # ==========================================
    with tab2:
        st.markdown("## 📊 Batch Job Analysis")
        st.info("🚧 Coming soon! Match your resume against multiple jobs at once.")
        
        st.markdown("""
        **Features (Coming Soon):**
        - Upload multiple job descriptions
        - Compare all matches side-by-side
        - Export results to CSV
        - Identify best opportunities
        """)
    
    # ==========================================
    # TAB 3: ABOUT
    # ==========================================
    with tab3:
        st.markdown("## ℹ️ About This App")
        
        st.markdown("""
        ### 🎯 What This App Does
        
        This AI-powered tool analyzes how well your resume matches a job description using:
        
        1. **Semantic Similarity (40%)** - AI understands meaning, not just keywords
        2. **Skills Matching (30%)** - Compares your skills with job requirements
        3. **Experience Match (15%)** - Evaluates years of experience
        4. **Education Match (15%)** - Checks degree requirements
        
        ### 🤖 Technology Stack
        
        - **Sentence-BERT** - For semantic text similarity
        - **spaCy** - For natural language processing
        - **Streamlit** - For the web interface
        - **Plotly** - For interactive visualizations
        
        ### 📊 How to Use
        
        1. Upload your resume (PDF, DOCX, or TXT)
        2. Paste the job description
        3. Click "Analyze Match"
        4. Review your match score and insights
        5. Follow recommendations to improve
        
        ### 💡 Tips for Best Results
        
        - Use a complete, well-formatted resume
        - Paste the full job description (not just a snippet)
        - Update your resume based on recommendations
        - Check ATS compatibility before applying
        
        ### 📝 Note
        
        This tool provides guidance only. Always review and customize your application
        for each job. Human judgment is essential!
        """)
        
        st.markdown("---")
        st.markdown("**Version:** 1.0.0 | **Built with:** Python, Streamlit, PyTorch")

# ==========================================
# RUN APP
# ==========================================

if __name__ == "__main__":
    # Initialize session state
    if 'use_sample' not in st.session_state:
        st.session_state['use_sample'] = False
    
    main()