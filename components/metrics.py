"""
KPI 메트릭 컴포넌트
components/metrics.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def render_summary_metrics(summary: dict):
    """요약 메트릭 카드 렌더링"""
    st.subheader("📊 요약 통계")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📄 총 논문 수",
            value=f"{summary['paper_count']:,}",
            help="전체 논문 레코드 수"
        )
    
    with col2:
        st.metric(
            label="⚖️ 총 특허 수", 
            value=f"{summary['patent_count']:,}",
            help="전체 특허 레코드 수"
        )
    
    with col3:
        if summary['year_range']:
            year_range = f"{summary['year_range'][0]}-{summary['year_range'][1]}"
            st.metric(
                label="📅 분석 기간",
                value=year_range,
                help="데이터 연도 범위"
            )
        else:
            st.metric(label="📅 분석 기간", value="N/A")
    
    with col4:
        st.metric(
            label="🌍 국가 수",
            value=f"{summary['country_count']}",
            help="분석 대상 국가 수"
        )

def render_yearly_metrics(papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """연도별 메트릭"""
    st.subheader("📈 연도별 성장 지표")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not papers_df.empty and 'Year' in papers_df.columns:
            yearly_papers = papers_df.groupby('Year').size()
            
            if len(yearly_papers) > 1:
                # 최근 증가율 계산
                recent_growth = yearly_papers.pct_change().iloc[-1] * 100
                latest_count = yearly_papers.iloc[-1]
                
                st.metric(
                    label="📄 최근 논문 수",
                    value=f"{latest_count:,}",
                    delta=f"{recent_growth:+.1f}%" if not np.isnan(recent_growth) else None,
                    help=f"{yearly_papers.index[-1]}년 기준"
                )
            else:
                st.metric(label="📄 최근 논문 수", value=f"{yearly_papers.iloc[0]:,}")
    
    with col2:
        if not patents_df.empty and 'Year' in patents_df.columns:
            yearly_patents = patents_df.groupby('Year').size()
            
            if len(yearly_patents) > 1:
                # 최근 증가율 계산
                recent_growth = yearly_patents.pct_change().iloc[-1] * 100
                latest_count = yearly_patents.iloc[-1]
                
                st.metric(
                    label="⚖️ 최근 특허 수",
                    value=f"{latest_count:,}",
                    delta=f"{recent_growth:+.1f}%" if not np.isnan(recent_growth) else None,
                    help=f"{yearly_patents.index[-1]}년 기준"
                )
            else:
                st.metric(label="⚖️ 최근 특허 수", value=f"{yearly_patents.iloc[0]:,}")

def render_top_countries_metrics(papers_df: pd.DataFrame, top_n: int = 5):
    """상위 국가 메트릭"""
    if papers_df.empty or 'Country' not in papers_df.columns:
        return
    
    st.subheader(f"🏆 상위 {top_n}개국")
    
    # 국가별 집계
    country_counts = papers_df['Country'].value_counts().head(top_n)
    
    # 컬럼으로 표시
    cols = st.columns(min(top_n, 5))
    
    for i, (country, count) in enumerate(country_counts.items()):
        if i < len(cols):
            with cols[i]:
                # 전체 대비 비율 계산
                total_count = len(papers_df)
                percentage = (count / total_count) * 100 if total_count > 0 else 0
                
                st.metric(
                    label=f"🌍 {country}",
                    value=f"{count:,}",
                    delta=f"{percentage:.1f}%",
                    help="전체 대비 비율"
                )

def render_distribution_metrics(papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """분포 메트릭"""
    st.subheader("📊 데이터 분포")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 연도별 분포
        if not papers_df.empty and 'Year' in papers_df.columns:
            year_counts = papers_df['Year'].value_counts()
            most_active_year = year_counts.index[0]
            max_count = year_counts.iloc[0]
            
            st.metric(
                label="📅 최다 발행 연도",
                value=str(most_active_year),
                delta=f"{max_count:,}건",
                help="논문 발행이 가장 많은 연도"
            )
    
    with col2:
        # 국가별 분포
        if not papers_df.empty and 'Country' in papers_df.columns:
            unique_countries = papers_df['Country'].nunique()
            avg_per_country = len(papers_df) / unique_countries if unique_countries > 0 else 0
            
            st.metric(
                label="🌍 평균 국가당 논문",
                value=f"{avg_per_country:.1f}",
                help="국가당 평균 논문 수"
            )
    
    with col3:
        # 데이터 완성도
        if not papers_df.empty:
            # 주요 컬럼의 결측값 비율
            key_cols = ['Year', 'Country']
            available_cols = [col for col in key_cols if col in papers_df.columns]
            
            if available_cols:
                completeness = papers_df[available_cols].notna().all(axis=1).mean() * 100
                st.metric(
                    label="✅ 데이터 완성도",
                    value=f"{completeness:.1f}%",
                    help="주요 컬럼 완성도"
                )

def render_comparison_gauge(papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """논문 vs 특허 비교 게이지"""
    if papers_df.empty and patents_df.empty:
        return
    
    st.subheader("⚖️ 논문 vs 특허 비율")
    
    paper_count = len(papers_df)
    patent_count = len(patents_df)
    total_count = paper_count + patent_count
    
    if total_count > 0:
        paper_ratio = (paper_count / total_count) * 100
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = paper_ratio,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "논문 비율 (%)"},
            delta = {'reference': 50, 'suffix': "%"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 25], 'color': "lightgray"},
                    {'range': [25, 50], 'color': "gray"},
                    {'range': [50, 75], 'color': "lightblue"},
                    {'range': [75, 100], 'color': "blue"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
        # 수치 정보
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📄 논문: {paper_count:,}건 ({paper_ratio:.1f}%)")
        with col2:
            st.info(f"⚖️ 특허: {patent_count:,}건 ({100-paper_ratio:.1f}%)")

def render_data_quality_metrics(papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """데이터 품질 메트릭"""
    st.subheader("🔍 데이터 품질 지표")
    
    col1, col2, col3 = st.columns(3)
    
    # 논문 데이터 품질
    with col1:
        if not papers_df.empty:
            # 중복 확인 (Year + Country 기준)
            if all(col in papers_df.columns for col in ['Year', 'Country']):
                total_rows = len(papers_df)
                unique_combinations = papers_df[['Year', 'Country']].drop_duplicates().shape[0]
                duplicate_ratio = ((total_rows - unique_combinations) / total_rows) * 100 if total_rows > 0 else 0
                
                st.metric(
                    label="📄 논문 중복률",
                    value=f"{duplicate_ratio:.1f}%",
                    help="연도-국가 조합 기준 중복 비율"
                )
    
    # 특허 데이터 품질  
    with col2:
        if not patents_df.empty:
            if all(col in patents_df.columns for col in ['Year', 'Country']):
                total_rows = len(patents_df)
                unique_combinations = patents_df[['Year', 'Country']].drop_duplicates().shape[0]
                duplicate_ratio = ((total_rows - unique_combinations) / total_rows) * 100 if total_rows > 0 else 0
                
                st.metric(
                    label="⚖️ 특허 중복률",
                    value=f"{duplicate_ratio:.1f}%",
                    help="연도-국가 조합 기준 중복 비율"
                )
    
    # 전체 데이터 범위
    with col3:
        all_years = []
        if not papers_df.empty and 'Year' in papers_df.columns:
            all_years.extend(papers_df['Year'].tolist())
        if not patents_df.empty and 'Year' in patents_df.columns:
            all_years.extend(patents_df['Year'].tolist())
        
        if all_years:
            year_span = max(all_years) - min(all_years) + 1
            st.metric(
                label="📅 데이터 기간 폭",
                value=f"{year_span}년",
                help="최소-최대 연도 차이"
            )