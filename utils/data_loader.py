"""
데이터 로더 및 전처리 유틸리티 (시트명 수정)
utils/data_loader.py
"""

import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data():
    """엑셀 파일에서 데이터 로드"""
    excel_file = '_통합평가자료.xlsx'
    
    papers_df = None
    patents_df = None
    
    if os.path.exists(excel_file):
        try:
            papers_df = pd.read_excel(excel_file, sheet_name='논문')
            patents_df = pd.read_excel(excel_file, sheet_name='특허')
        except Exception as e:
            st.sidebar.error(f"데이터 로드 실패: {e}")
    else:
        st.sidebar.warning(f"파일을 찾을 수 없습니다: {excel_file}")
    
    return papers_df, patents_df

def get_summary_stats(papers_df, patents_df):
    """요약 통계 생성"""
    paper_count = len(papers_df) if papers_df is not None and not papers_df.empty else 0
    patent_count = len(patents_df) if patents_df is not None and not patents_df.empty else 0
    
    year_range = None
    country_count = 0
    
    # 연도 범위 계산
    all_years = []
    if papers_df is not None and not papers_df.empty and 'Year' in papers_df.columns:
        years = pd.to_numeric(papers_df['Year'], errors='coerce').dropna()
        if not years.empty:
            all_years.extend(years.tolist())
    
    if patents_df is not None and not patents_df.empty and 'Year' in patents_df.columns:
        years = pd.to_numeric(patents_df['Year'], errors='coerce').dropna()
        if not years.empty:
            all_years.extend(years.tolist())
    
    if all_years:
        try:
            min_year = int(min(all_years))
            max_year = int(max(all_years))
            year_range = (min_year, max_year)
        except (ValueError, TypeError):
            year_range = None
    
    # 국가 수 계산
    all_countries = set()
    if papers_df is not None and not papers_df.empty and 'Country' in papers_df.columns:
        countries = papers_df['Country'].dropna().unique()
        all_countries.update(countries)
    
    if patents_df is not None and not patents_df.empty and 'Country' in patents_df.columns:
        countries = patents_df['Country'].dropna().unique()
        all_countries.update(countries)
    
    country_count = len(all_countries)
    
    # 논문/특허 총계 계산
    total_papers = 0
    if papers_df is not None and not papers_df.empty and 'Total_Papers' in papers_df.columns:
        total_papers = papers_df['Total_Papers'].sum()
    
    total_patents = 0
    if patents_df is not None and not patents_df.empty:
        # 특허 수 컬럼 찾기
        patent_cols = ['Total_Papers', 'total_papers', 'Patent_Count', 'count']
        for col in patent_cols:
            if col in patents_df.columns:
                total_patents = patents_df[col].sum()
                break
    
    return {
        'paper_count': total_papers,
        'patent_count': total_patents,
        'total_count': total_papers + total_patents,
        'year_range': year_range,
        'country_count': country_count
    }