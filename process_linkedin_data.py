"""
LinkedIn Dataset Processor
Loads, cleans, and merges multiple CSV files into a unified dataset
"""

import pandas as pd
import os
from pathlib import Path

# Paths
BASE_DIR = Path(r"D:\job-matcher-system")
DATA_DIR = BASE_DIR / "data" / "linkedin_jobs"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

def load_linkedin_data():
    """
    Load all LinkedIn CSV files
    Returns: Dictionary of dataframes
    """
    print("📥 Loading LinkedIn dataset files...")
    
    files = {
        'postings': 'postings.csv',
        'companies': 'companies.csv',
        'job_skills': 'job_skills.csv',
        'skills': 'skills.csv',
        'salaries': 'salaries.csv',
        'benefits': 'benefits.csv',
        'job_industries': 'job_industries.csv',
        'industries': 'industries.csv',
        'company_industries': 'company_industries.csv',
        'company_specialities': 'company_specialities.csv',
        'employee_counts': 'employee_counts.csv'
    }
    
    data = {}
    
    for key, filename in files.items():
        file_path = DATA_DIR / filename
        if file_path.exists():
            try:
                df = pd.read_csv(file_path, low_memory=False)
                data[key] = df
                print(f"  ✅ Loaded {key}: {len(df):,} records")
            except Exception as e:
                print(f"  ⚠️  Error loading {key}: {e}")
        else:
            print(f"  ⏭️  File not found: {filename}")
    
    return data

def explore_dataset(data):
    """
    Display dataset statistics and column information
    """
    print("\n" + "="*60)
    print("📊 DATASET EXPLORATION")
    print("="*60)
    
    # Postings (main file)
    if 'postings' in data:
        df = data['postings']
        print(f"\n🎯 POSTINGS.CSV ({len(df):,} jobs)")
        print(f"Columns: {list(df.columns)}")
        print(f"\nSample columns:")
        for col in df.columns[:10]:
            print(f"  • {col}: {df[col].dtype}")
        print(f"\nMissing values:")
        missing = df.isnull().sum()
        print(missing[missing > 0].head(10))
    
    # Job Skills
    if 'job_skills' in data:
        df = data['job_skills']
        print(f"\n🔧 JOB_SKILLS.CSV ({len(df):,} skill mappings)")
        print(f"Columns: {list(df.columns)}")
    
    # Skills database
    if 'skills' in data:
        df = data['skills']
        print(f"\n💡 SKILLS.CSV ({len(df):,} unique skills)")
        print(f"Columns: {list(df.columns)}")
        print(f"Sample skills: {df['skill_name'].head(10).tolist() if 'skill_name' in df.columns else 'N/A'}")
    
    # Companies
    if 'companies' in data:
        df = data['companies']
        print(f"\n🏢 COMPANIES.CSV ({len(df):,} companies)")
        print(f"Columns: {list(df.columns)}")
    
    # Salaries
    if 'salaries' in data:
        df = data['salaries']
        print(f"\n💰 SALARIES.CSV ({len(df):,} salary records)")
        print(f"Columns: {list(df.columns)}")

def merge_job_data(data):
    """
    Merge postings with skills, companies, and salaries
    Returns: Unified DataFrame
    """
    print("\n" + "="*60)
    print("🔗 MERGING DATASETS")
    print("="*60)
    
    # Start with postings
    df_jobs = data['postings'].copy()
    print(f"\n1. Starting with {len(df_jobs):,} job postings")
    
    # Merge with companies (if available)
    if 'companies' in data:
        df_companies = data['companies'].copy()
        # Find common column (usually 'company_id')
        company_id_col = 'company_id' if 'company_id' in df_jobs.columns else None
        
        if company_id_col:
            df_jobs = df_jobs.merge(
                df_companies, 
                on=company_id_col, 
                how='left', 
                suffixes=('', '_company')
            )
            print(f"2. Merged with companies: {len(df_jobs):,} records")
    
    # Aggregate skills per job
    if 'job_skills' in data and 'skills' in data:
        df_job_skills = data['job_skills'].copy()
        df_skills = data['skills'].copy()
        
        # Merge job_skills with skills to get skill names
        skill_id_col = 'skill_abr' if 'skill_abr' in df_job_skills.columns else 'skill_id'
        skill_name_col = 'skill_name' if 'skill_name' in df_skills.columns else 'name'
        
        if skill_id_col in df_job_skills.columns:
            df_job_skills = df_job_skills.merge(
                df_skills[[skill_id_col, skill_name_col]], 
                on=skill_id_col, 
                how='left'
            )
            
            # Aggregate skills per job
            job_id_col = 'job_id' if 'job_id' in df_job_skills.columns else 'posting_id'
            skills_grouped = df_job_skills.groupby(job_id_col)[skill_name_col].apply(
                lambda x: ', '.join(x.dropna().astype(str))
            ).reset_index()
            skills_grouped.columns = [job_id_col, 'required_skills']
            
            # Merge with main dataframe
            df_jobs = df_jobs.merge(skills_grouped, on=job_id_col, how='left')
            print(f"3. Merged with skills: {len(df_jobs):,} records")
    
    # Merge with salaries (if available)
    if 'salaries' in data:
        df_salaries = data['salaries'].copy()
        salary_job_id = 'job_id' if 'job_id' in df_salaries.columns else 'posting_id'
        
        if salary_job_id in df_jobs.columns:
            df_jobs = df_jobs.merge(
                df_salaries, 
                on=salary_job_id, 
                how='left',
                suffixes=('', '_salary')
            )
            print(f"4. Merged with salaries: {len(df_jobs):,} records")
    
    return df_jobs

def clean_job_data(df):
    """
    Clean and prepare job data for matching
    """
    print("\n" + "="*60)
    print("🧹 CLEANING DATA")
    print("="*60)
    
    df_clean = df.copy()
    
    # Identify important columns
    important_cols = []
    
    # Job description column
    desc_cols = ['description', 'job_description', 'desc', 'text']
    for col in desc_cols:
        if col in df_clean.columns:
            important_cols.append(col)
            print(f"  ✅ Found description column: {col}")
            break
    
    # Job title column
    title_cols = ['title', 'job_title', 'position', 'role']
    for col in title_cols:
        if col in df_clean.columns:
            important_cols.append(col)
            print(f"  ✅ Found title column: {col}")
            break
    
    # Company column
    company_cols = ['company', 'company_name', 'employer']
    for col in company_cols:
        if col in df_clean.columns:
            important_cols.append(col)
            print(f"  ✅ Found company column: {col}")
            break
    
    # Skills column
    if 'required_skills' in df_clean.columns:
        important_cols.append('required_skills')
        print(f"  ✅ Found skills column: required_skills")
    
    # Location column
    location_cols = ['location', 'job_location', 'city', 'work_location']
    for col in location_cols:
        if col in df_clean.columns:
            important_cols.append(col)
            print(f"  ✅ Found location column: {col}")
            break
    
    # Experience column
    exp_cols = ['experience_level', 'experience', 'seniority', 'level']
    for col in exp_cols:
        if col in df_clean.columns:
            important_cols.append(col)
            print(f"  ✅ Found experience column: {col}")
            break
    
    # Salary columns
    salary_cols = ['salary', 'min_salary', 'max_salary', 'compensation']
    for col in salary_cols:
        if col in df_clean.columns:
            important_cols.append(col)
    
    # Drop rows with missing descriptions
    desc_col = [col for col in desc_cols if col in df_clean.columns]
    if desc_col:
        before = len(df_clean)
        df_clean = df_clean.dropna(subset=[desc_col[0]])
        after = len(df_clean)
        print(f"\n  🗑️  Removed {before - after:,} jobs with missing descriptions")
    
    # Remove duplicates
    before = len(df_clean)
    df_clean = df_clean.drop_duplicates()
    after = len(df_clean)
    if before > after:
        print(f"  🗑️  Removed {before - after:,} duplicate records")
    
    print(f"\n  ✅ Final dataset: {len(df_clean):,} clean job postings")
    
    return df_clean, important_cols

def create_sample_dataset(df, n_samples=1000):
    """
    Create a smaller sample dataset for quick testing
    """
    print("\n" + "="*60)
    print("📦 CREATING SAMPLE DATASET")
    print("="*60)
    
    if len(df) > n_samples:
        df_sample = df.sample(n=n_samples, random_state=42)
        print(f"  ✅ Created sample with {n_samples:,} jobs")
    else:
        df_sample = df.copy()
        print(f"  ⚠️  Dataset has only {len(df):,} jobs (kept all)")
    
    return df_sample

def save_processed_data(df_full, df_sample, important_cols):
    """
    Save processed datasets
    """
    print("\n" + "="*60)
    print("💾 SAVING PROCESSED DATA")
    print("="*60)
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save full dataset
    full_path = OUTPUT_DIR / "linkedin_jobs_full.csv"
    df_full.to_csv(full_path, index=False)
    print(f"  ✅ Saved full dataset: {full_path}")
    print(f"     Records: {len(df_full):,}")
    print(f"     Columns: {len(df_full.columns)}")
    
    # Save sample dataset
    sample_path = OUTPUT_DIR / "linkedin_jobs_sample.csv"
    df_sample.to_csv(sample_path, index=False)
    print(f"  ✅ Saved sample dataset: {sample_path}")
    print(f"     Records: {len(df_sample):,}")
    
    # Save important columns only (lightweight version)
    if important_cols:
        df_light = df_full[important_cols].copy()
        light_path = OUTPUT_DIR / "linkedin_jobs_light.csv"
        df_light.to_csv(light_path, index=False)
        print(f"  ✅ Saved lightweight dataset: {light_path}")
        print(f"     Records: {len(df_light):,}")
        print(f"     Columns: {important_cols}")
    
    # Save column mapping info
    info_path = OUTPUT_DIR / "dataset_info.txt"
    with open(info_path, 'w', encoding='utf-8') as f:
        f.write("LinkedIn Dataset Information\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total Records: {len(df_full):,}\n")
        f.write(f"Total Columns: {len(df_full.columns)}\n\n")
        f.write("Important Columns:\n")
        for col in important_cols:
            f.write(f"  • {col}\n")
        f.write(f"\nAll Columns:\n")
        for col in df_full.columns:
            f.write(f"  • {col}: {df_full[col].dtype}\n")
    print(f"  ✅ Saved dataset info: {info_path}")

def main():
    """
    Main processing pipeline
    """
    print("="*60)
    print("🚀 LINKEDIN DATASET PROCESSOR")
    print("="*60)
    
    # Load data
    data = load_linkedin_data()
    
    if not data:
        print("\n❌ No data files found! Check your data directory.")
        return
    
    # Explore dataset
    explore_dataset(data)
    
    # Merge datasets
    df_merged = merge_job_data(data)
    
    # Clean data
    df_clean, important_cols = clean_job_data(df_merged)
    
    # Create sample
    df_sample = create_sample_dataset(df_clean, n_samples=1000)
    
    # Save processed data
    save_processed_data(df_clean, df_sample, important_cols)
    
    print("\n" + "="*60)
    print("✅ PROCESSING COMPLETE!")
    print("="*60)
    print("\n📁 Output files created in: data/processed/")
    print("  • linkedin_jobs_full.csv - Complete dataset")
    print("  • linkedin_jobs_sample.csv - 1000 job sample")
    print("  • linkedin_jobs_light.csv - Important columns only")
    print("  • dataset_info.txt - Dataset documentation")
    print("\n💡 Use the sample dataset for quick testing!")
    print("💡 Use the light dataset for faster loading!")
    print("💡 Use the full dataset for production!")

if __name__ == "__main__":
    main()
