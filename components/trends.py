"""
트렌드 분석 컴포넌트
"""
import streamlit as st
import plotly.express as px

def render_yearly_trend(df, col_mapping):
    """연도별 추이 차트"""
    # Year 컬럼 찾기
    year_col = None
    for col in df.columns:
        if col.lower() in ['year', '연도']:
            year_col = col
            break
    
    if not year_col:
        return None
    
    # Papers 컬럼 찾기
    papers_col = col_mapping.get('total_papers', 'total_papers')
    if papers_col not in df.columns:
        for col in df.columns:
            if 'total' in col.lower() and 'paper' in col.lower():
                papers_col = col
                break
    
    if papers_col in df.columns:
        yearly = df.groupby(year_col)[papers_col].sum().reset_index()
        fig = px.line(yearly, x=year_col, y=papers_col, 
                      title="연도별 추이", markers=True)
        return fig
    return None

def render_tech_trend(df, col_mapping):
    """기술 분야별 트렌드"""
    # 기술 분야 컬럼 찾기
    tech_col = None
    for col in df.columns:
        if any(keyword in col.lower() for keyword in ['tech', 'label', '기술', '분야']):
            tech_col = col
            break
    
    if tech_col and tech_col in df.columns:
        tech_sum = df.groupby(tech_col).size().nlargest(10)
        fig = px.bar(tech_sum, title="기술 분야별 분포")
        return fig
    return None