"""
국가별 분석 컴포넌트
"""
import streamlit as st
import pandas as pd
import plotly.express as px

def render_country_bar_charts(df, col_mapping, top_n=10, is_patent=False):
    """국가별 바 차트"""
    # 국가 컬럼 찾기
    country_col = None
    for col in df.columns:
        if col.lower() in ['country', 'nation', '국가']:
            country_col = col
            break
    
    if not country_col:
        st.warning("국가 컬럼을 찾을 수 없습니다.")
        return
    
    # 총 논문/특허 수 컬럼 찾기
    papers_col = col_mapping.get('total_papers', 'total_papers')
    if papers_col not in df.columns:
        # 대체 컬럼 찾기
        for col in df.columns:
            if 'total' in col.lower() and 'paper' in col.lower():
                papers_col = col
                break
    
    if papers_col in df.columns:
        country_sum = df.groupby(country_col)[papers_col].sum().nlargest(top_n)
        
        title = "특허 출원 상위 국가" if is_patent else "논문 생산 상위 국가"
        fig = px.bar(
            x=country_sum.index, 
            y=country_sum.values,
            labels={'x': '국가', 'y': '수량'},
            title=title
        )
        st.plotly_chart(fig, use_container_width=True)

def render_country_comparison(df, col_mapping):
    """국가별 비교 분석"""
    country_col = None
    for col in df.columns:
        if col.lower() in ['country', 'nation', '국가']:
            country_col = col
            break
    
    if not country_col:
        return None, None
    
    # 국가별 메트릭 계산
    agg_dict = {}
    
    # 가능한 컬럼들 추가
    possible_cols = ['total_papers', 'h_index', 'top10_ratio', 'q1_ratio']
    for col in possible_cols:
        if col in col_mapping and col_mapping[col] in df.columns:
            agg_dict[col_mapping[col]] = 'sum' if 'total' in col else 'mean'
    
    if agg_dict:
        country_metrics = df.groupby(country_col).agg(agg_dict)
        top_countries = country_metrics.nlargest(5, country_metrics.columns[0])
        return top_countries.index.tolist(), country_metrics
    
    return None, None