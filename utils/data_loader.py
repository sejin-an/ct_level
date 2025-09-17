"""
PKL 데이터 로드 및 필터링 유틸리티
"""
import streamlit as st
import pandas as pd
import pickle
import os

@st.cache_data
def load_data():
    """PKL 파일에서 논문/특허 데이터 로드"""
    paper_path = 'data/pap_detail.pkl'
    patent_path = 'data/pat_detail.pkl'
    
    paper_df = None
    patent_df = None
    
    # 논문 데이터 로드
    if os.path.exists(paper_path):
        with open(paper_path, 'rb') as f:
            paper_df = pickle.load(f)
        paper_df['datatype'] = 'paper'
    
    # 특허 데이터 로드  
    if os.path.exists(patent_path):
        with open(patent_path, 'rb') as f:
            patent_df = pickle.load(f)
        patent_df['datatype'] = 'patent'
    
    return paper_df, patent_df

def filter_data(paper_df, patent_df, sidebar):
    """사이드바 필터 적용"""
    
    # 연도 필터
    min_year = 2011
    max_year = 2024
    
    year_range = sidebar.slider(
        "연도 범위",
        min_year, max_year,
        (2015, 2024)
    )
    
    # 기술 분야 필터
    tech_col_paper = None
    tech_col_patent = None
    
    if paper_df is not None:
        for col in paper_df.columns:
            if any(keyword in col.lower() for keyword in ['label', 'tech', '기술', '분야']):
                tech_col_paper = col
                break
    
    if patent_df is not None:
        for col in patent_df.columns:
            if any(keyword in col.lower() for keyword in ['label', 'tech', '기술', '분야']):
                tech_col_patent = col
                break
    
    # 기술 분야 목록 수집
    tech_labels = []
    if tech_col_paper and paper_df is not None:
        tech_labels.extend(paper_df[tech_col_paper].unique().tolist())
    if tech_col_patent and patent_df is not None:
        tech_labels.extend(patent_df[tech_col_patent].unique().tolist())
    tech_labels = list(set(tech_labels))
    tech_labels.sort()
    
    # 기술 분야 선택
    selected_tech = sidebar.multiselect(
        "기술 분야 선택",
        options=['전체'] + tech_labels,
        default=['전체']
    )
    
    # 국가 컬럼명 찾기
    paper_country_col = None
    patent_country_col = None
    
    if paper_df is not None:
        for col in paper_df.columns:
            if col.lower() in ['country', 'nation', '국가']:
                paper_country_col = col
                break
    
    if patent_df is not None:
        for col in patent_df.columns:
            if col.lower() in ['country', 'nation', '국가']:
                patent_country_col = col
                break
    
    # 국가 필터 준비
    paper_countries = [] if paper_country_col is None else paper_df[paper_country_col].unique().tolist()
    patent_countries = [] if patent_country_col is None else patent_df[patent_country_col].unique().tolist()
    all_countries = list(set(paper_countries + patent_countries))
    
    # 주요 국가 매핑
    country_mapping = {
        '중국': ['CN', 'China', '중국'],
        '미국': ['US', 'United States', '미국'],
        'EU': ['EU', 'European Union'],
        '한국': ['KR', 'Korea', '한국', '대한민국'],
        '일본': ['JP', 'Japan', '일본'],
        '독일': ['DE', 'Germany', '독일'],
        '영국': ['GB', 'UK', 'United Kingdom', '영국'],
        '인도': ['IN', 'India', '인도']
    }
    
    selected_countries = sidebar.multiselect(
        "국가 선택",
        options=['전체'] + list(country_mapping.keys()),
        default=['전체']
    )
    
    # 필터링 적용
    filtered_paper = None
    filtered_patent = None
    
    if paper_df is not None:
        filtered_paper = paper_df.copy()
        
        # Year 컬럼 찾기
        year_col = None
        for col in filtered_paper.columns:
            if col.lower() in ['year', '연도']:
                year_col = col
                break
        
        if year_col:
            filtered_paper = filtered_paper[
                (filtered_paper[year_col] >= year_range[0]) & 
                (filtered_paper[year_col] <= year_range[1])
            ]
        
        # 기술 분야 필터
        if '전체' not in selected_tech and tech_col_paper:
            filtered_paper = filtered_paper[filtered_paper[tech_col_paper].isin(selected_tech)]
        
        # 국가 필터
        if '전체' not in selected_countries and paper_country_col:
            country_filter = []
            for country in selected_countries:
                country_filter.extend(country_mapping.get(country, [country]))
            filtered_paper = filtered_paper[filtered_paper[paper_country_col].isin(country_filter)]
    
    if patent_df is not None:
        filtered_patent = patent_df.copy()
        
        # Year 컬럼 찾기
        year_col = None
        for col in filtered_patent.columns:
            if col.lower() in ['year', '연도']:
                year_col = col
                break
        
        if year_col:
            filtered_patent = filtered_patent[
                (filtered_patent[year_col] >= year_range[0]) & 
                (filtered_patent[year_col] <= year_range[1])
            ]
        
        # 기술 분야 필터
        if '전체' not in selected_tech and tech_col_patent:
            filtered_patent = filtered_patent[filtered_patent[tech_col_patent].isin(selected_tech)]
        
        # 국가 필터
        if '전체' not in selected_countries and patent_country_col:
            country_filter = []
            for country in selected_countries:
                country_filter.extend(country_mapping.get(country, [country]))
            filtered_patent = filtered_patent[filtered_patent[patent_country_col].isin(country_filter)]
    
    return filtered_paper, filtered_patent

def get_column_names(df):
    """데이터프레임의 컬럼명을 표준화된 이름으로 매핑"""
    column_mapping = {
        # Paper columns
        'totalpapers': 'total_papers',
        'totalpaperscount': 'total_papers',
        'totalcitations': 'total_citations',
        'avgcitations': 'avg_citations',
        'hindex': 'h_index',
        'top10paperscitations': 'top10_citations',
        'top10papersmrnif': 'top10_mrnif',
        'top10ratio(%)': 'top10_ratio',
        'q1ratio(%)': 'q1_ratio',
        'collaborationratio(%)': 'collaboration_ratio',
        'avgmrnif': 'avg_mrnif',
        'productivityscore': 'productivity_score',
        'impactscore': 'impact_score',
        
        # Patent columns
        'totalpapers': 'total_papers',  # patent에서도 동일 사용
        'totalcitations': 'total_citations',
        'avgcitations': 'avg_citations',
        'hindex': 'h_index',
        'gindex': 'g_index',
        'triadicratio': 'triadic_ratio',
        'triadiccount': 'triadic_count',
        'totalclaims': 'total_claims',
        'avgclaims': 'avg_claims',
        'avgfamilycountries': 'avg_family_countries',
        'citationsperclaim': 'citations_per_claim'
    }
    
    if df is None:
        return {}
    
    result = {}
    for col in df.columns:
        clean_col = col.lower().replace('_', '').replace(' ', '').replace('-', '')
        if clean_col in column_mapping:
            result[column_mapping[clean_col]] = col
    
    return result