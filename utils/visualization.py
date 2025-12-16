"""
Visualization - Create charts and graphs for results
"""

import plotly.graph_objects as go
import plotly.express as px
import sys
sys.path.append('.')
from config.settings import CHART_HEIGHT, CHART_THEME

# ==========================================
# MATCH SCORE GAUGE
# ==========================================

def create_score_gauge(score: float, title: str = "Match Score") -> go.Figure:
    """
    Create gauge chart for match score
    
    Args:
        score: Score (0-100)
        title: Chart title
    
    Returns:
        Plotly figure
    """
    # Determine color
    if score >= 85:
        color = "#10b981"  # Green
    elif score >= 70:
        color = "#fbbf24"  # Yellow
    elif score >= 50:
        color = "#f97316"  # Orange
    else:
        color = "#ef4444"  # Red
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 24, 'color': 'white'}},
        number={'font': {'size': 48, 'color': 'white'}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color},
            'bgcolor': "rgba(30, 41, 59, 0.5)",
            'borderwidth': 2,
            'bordercolor': "white",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.3)'},
                {'range': [50, 70], 'color': 'rgba(249, 115, 22, 0.3)'},
                {'range': [70, 85], 'color': 'rgba(251, 191, 36, 0.3)'},
                {'range': [85, 100], 'color': 'rgba(16, 185, 129, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "white", 'family': "Arial"},
        height=300
    )
    
    return fig

# ==========================================
# SCORE BREAKDOWN BAR CHART
# ==========================================

def create_score_breakdown(semantic: float, skills: float, experience: float, education: float) -> go.Figure:
    """
    Create bar chart for score breakdown
    
    Args:
        semantic: Semantic score (0-100)
        skills: Skills score (0-100)
        experience: Experience score (0-100)
        education: Education score (0-100)
    
    Returns:
        Plotly figure
    """
    categories = ['Semantic\nSimilarity', 'Skills\nMatch', 'Experience\nMatch', 'Education\nMatch']
    scores = [semantic, skills, experience, education]
    colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=scores,
            text=[f'{s:.1f}%' for s in scores],
            textposition='outside',
            marker_color=colors,
            hovertemplate='%{x}<br>Score: %{y:.1f}%<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="Score Breakdown",
        yaxis_title="Score (%)",
        yaxis=dict(range=[0, 110]),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(30, 41, 59, 0.3)',
        font={'color': "white"},
        height=CHART_HEIGHT,
        showlegend=False
    )
    
    return fig

# ==========================================
# SKILLS COMPARISON
# ==========================================

def create_skills_comparison(matching_skills: list, missing_skills: list) -> go.Figure:
    """
    Create horizontal bar chart comparing skills
    
    Args:
        matching_skills: List of matching skills
        missing_skills: List of missing skills
    
    Returns:
        Plotly figure
    """
    # Limit to top 10 each
    matching = matching_skills[:10]
    missing = missing_skills[:10]
    
    fig = go.Figure()
    
    # Matching skills (positive)
    if matching:
        fig.add_trace(go.Bar(
            y=matching,
            x=[1] * len(matching),
            orientation='h',
            name='You Have',
            marker_color='#10b981',
            hovertemplate='%{y}<extra></extra>'
        ))
    
    # Missing skills (negative)
    if missing:
        fig.add_trace(go.Bar(
            y=missing,
            x=[-1] * len(missing),
            orientation='h',
            name='Missing',
            marker_color='#ef4444',
            hovertemplate='%{y}<extra></extra>'
        ))
    
    fig.update_layout(
        title=f"Skills Analysis ({len(matching_skills)} Matched / {len(missing_skills)} Missing)",
        xaxis=dict(
            showticklabels=False,
            range=[-1.5, 1.5]
        ),
        yaxis=dict(autorange="reversed"),
        barmode='relative',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(30, 41, 59, 0.3)',
        font={'color': "white"},
        height=max(300, (len(matching) + len(missing)) * 25),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

# ==========================================
# RADAR CHART
# ==========================================

def create_radar_chart(semantic: float, skills: float, experience: float, education: float) -> go.Figure:
    """
    Create radar chart for multi-dimensional view
    
    Args:
        semantic: Semantic score (0-100)
        skills: Skills score (0-100)
        experience: Experience score (0-100)
        education: Education score (0-100)
    
    Returns:
        Plotly figure
    """
    categories = ['Semantic<br>Match', 'Skills', 'Experience', 'Education']
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=[semantic, skills, experience, education],
        theta=categories,
        fill='toself',
        name='Your Match',
        line_color='#f59e0b',
        fillcolor='rgba(245, 158, 11, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color='white'),
                gridcolor='rgba(255, 255, 255, 0.2)'
            ),
            angularaxis=dict(
                tickfont=dict(color='white', size=12),
                gridcolor='rgba(255, 255, 255, 0.2)'
            ),
            bgcolor='rgba(30, 41, 59, 0.3)'
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "white"},
        height=400
    )
    
    return fig

# ==========================================
# ATS SCORE CHART
# ==========================================

def create_ats_chart(ats_score: float) -> go.Figure:
    """
    Create progress bar for ATS score
    
    Args:
        ats_score: ATS compatibility score (0-100)
    
    Returns:
        Plotly figure
    """
    # Determine color
    if ats_score >= 80:
        color = "#10b981"
    elif ats_score >= 60:
        color = "#fbbf24"
    else:
        color = "#ef4444"
    
    fig = go.Figure(go.Indicator(
        mode="number+gauge",
        value=ats_score,
        title={'text': "ATS Compatibility", 'font': {'size': 20, 'color': 'white'}},
        number={'font': {'size': 36, 'color': 'white'}, 'suffix': '/100'},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color},
            'bgcolor': "rgba(30, 41, 59, 0.5)",
            'steps': [
                {'range': [0, 60], 'color': 'rgba(239, 68, 68, 0.3)'},
                {'range': [60, 80], 'color': 'rgba(251, 191, 36, 0.3)'},
                {'range': [80, 100], 'color': 'rgba(16, 185, 129, 0.3)'}
            ]
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "white"},
        height=250
    )
    
    return fig

# ==========================================
# BATCH RESULTS TABLE
# ==========================================

def create_batch_results_chart(results: list) -> go.Figure:
    """
    Create horizontal bar chart for batch matching results
    
    Args:
        results: List of match results (top 10)
    
    Returns:
        Plotly figure
    """
    # Limit to top 10
    top_results = results[:10]
    
    job_titles = [r['job'].get('title', f"Job {r['job_index']}") for r in top_results]
    scores = [r['total_score'] for r in top_results]
    
    # Color based on score
    colors = ['#10b981' if s >= 70 else '#fbbf24' if s >= 50 else '#ef4444' for s in scores]
    
    fig = go.Figure(data=[
        go.Bar(
            y=job_titles,
            x=scores,
            orientation='h',
            text=[f'{s:.1f}%' for s in scores],
            textposition='outside',
            marker_color=colors,
            hovertemplate='%{y}<br>Match: %{x:.1f}%<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="Top Matching Jobs",
        xaxis_title="Match Score (%)",
        xaxis=dict(range=[0, 110]),
        yaxis=dict(autorange="reversed"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(30, 41, 59, 0.3)',
        font={'color': "white"},
        height=max(400, len(top_results) * 40),
        showlegend=False
    )
    
    return fig

# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":
    print("✅ Visualization module ready!")
    print("\nAvailable charts:")
    print("  - create_score_gauge()")
    print("  - create_score_breakdown()")
    print("  - create_skills_comparison()")
    print("  - create_radar_chart()")
    print("  - create_ats_chart()")
    print("  - create_batch_results_chart()")