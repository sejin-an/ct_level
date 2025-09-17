"""
영향력 분석 컴포넌트 - H-index, mRNIF
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def render_hindex_by_country(df, col_mapping):
    """국가별 H-index 분석"""
    # 컬럼 찾기
    h_col = None
    for col in df.columns:
        if 'h_index' in col.lower() or 'hindex' in col.lower():
            h_col = col
            break
    
    country_col = None
    for col in df.columns:
        if col.lower() in ['country', 'nation', '국가']:
            country_col = col
            break
    
    if h_col and country_col:
        country_h = df.groupby(country_col)[h_col].mean().nlargest(15)
        fig = px.bar(country_h, title="국가별 평균 H-index",
                     labels={'value': 'H-index', 'index': '국가'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("H-index 데이터가 없습니다.")

def render_hindex_timeline(df, col_mapping):
    """H-index 시계열 분석"""
    h_col = None
    for col in df.columns:
        if 'h_index' in col.lower() or 'hindex' in col.lower():
            h_col = col
            break
    
    year_col = None
    for col in df.columns:
        if col.lower() in ['year', '연도']:
            year_col = col
            break
    
    if h_col and year_col:
        yearly_h = df.groupby(year_col)[h_col].mean().reset_index()
        fig = px.line(yearly_h, x=year_col, y=h_col, 
                     title="연도별 평균 H-index 추이", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("시계열 H-index 데이터가 없습니다.")

def render_mrnif_distribution(df, col_mapping):
    """mRNIF 분포 분석"""
    mrnif_col = None
    for col in df.columns:
        if 'mrnif' in col.lower():
            mrnif_col = col
            break
    
    if mrnif_col:
        fig = px.histogram(df, x=mrnif_col, nbins=30,
                          title="mRNIF 분포",
                          labels={mrnif_col: 'mRNIF'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("mRNIF 데이터가 없습니다.")

def render_mrnif_by_country(df, col_mapping):
    """국가별 mRNIF 분석"""
    mrnif_col = None
    for col in df.columns:
        if 'mrnif' in col.lower():
            mrnif_col = col
            break
    
    country_col = None
    for col in df.columns:
        if col.lower() in ['country', 'nation', '국가']:
            country_col = col
            break
    
    if mrnif_col and country_col:
        country_mrnif = df.groupby(country_col)[mrnif_col].mean().nlargest(15)
        fig = px.bar(country_mrnif, title="국가별 평균 mRNIF",
                     labels={'value': 'mRNIF', 'index': '국가'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("국가별 mRNIF 데이터가 없습니다.")

# 기존 함수 유지 (호환성)
def render_impact_analysis(df, col_mapping):
    """통합 영향력 분석"""
    st.subheader("🎯 영향력 분석")
    
    col1, col2 = st.columns(2)
    with col1:
        render_hindex_by_country(df, col_mapping)
    with col2:
        render_mrnif_distribution(df, col_mapping)