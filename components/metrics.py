"""
KPI 메트릭 컴포넌트
components/metrics.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def render_kpi_cards(df: pd.DataFrame, papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """주요 지표 카드 렌더링"""
    st.subheader("📊 주요 지표")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_papers = papers_df['Total_Papers'].sum() if not papers_df.empty and 'Total_Papers' in papers_df.columns else 0
        unique_countries_papers = papers_df['Country'].nunique() if not papers_df.empty else 0
        st.metric(
            label="📄 총 논문 수",
            value=f"{total_papers:,}",
            delta=f"{unique_countries_papers} 국가"
        )
    
    with col2:
        # 특허 수 계산
        patent_col = 'patent_count' if 'patent_count' in patents_df.columns else 'Total_Papers'
        total_patents = 0
        if not patents_df.empty and patent_col in patents_df.columns:
            total_patents = patents_df[patent_col].sum()
        
        unique_countries_patents = patents_df['Country'].nunique() if not patents_df.empty else 0
        st.metric(
            label="⚖️ 총 특허 수",
            value=f"{total_patents:,}",
            delta=f"{unique_countries_patents} 국가"
        )
    
    with col3:
        avg_h_index = 0
        if not papers_df.empty and 'H_Index' in papers_df.columns:
            avg_h_index = papers_df['H_Index'].mean()
        
        st.metric(
            label="📈 평균 H-Index",
            value=f"{avg_h_index:.1f}",
            delta="논문 기준"
        )
    
    with col4:
        years = df['Year'].nunique() if not df.empty else 0
        countries = df['Country'].nunique() if not df.empty else 0
        st.metric(
            label="🌍 분석 범위",
            value=f"{years}년간",
            delta=f"{countries} 국가"
        )

def render_growth_metrics(papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """성장률 지표"""
    if papers_df.empty and patents_df.empty:
        return
    
    st.subheader("📈 성장률 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not papers_df.empty and len(papers_df['Year'].unique()) > 1:
            # 논문 성장률 계산
            papers_yearly = papers_df.groupby('Year')['Total_Papers'].sum().reset_index()
            if len(papers_yearly) > 1:
                papers_yearly['Growth_Rate'] = papers_yearly['Total_Papers'].pct_change() * 100
                latest_growth = papers_yearly['Growth_Rate'].iloc[-1]
                
                st.metric(
                    label="📄 논문 성장률",
                    value=f"{latest_growth:.1f}%",
                    delta=f"전년 대비"
                )
    
    with col2:
        if not patents_df.empty and len(patents_df['Year'].unique()) > 1:
            # 특허 성장률 계산
            patent_col = 'patent_count' if 'patent_count' in patents_df.columns else 'Total_Papers'
            if patent_col in patents_df.columns:
                patents_yearly = patents_df.groupby('Year')[patent_col].sum().reset_index()
                if len(patents_yearly) > 1:
                    patents_yearly['Growth_Rate'] = patents_yearly[patent_col].pct_change() * 100
                    latest_growth = patents_yearly['Growth_Rate'].iloc[-1]
                    
                    st.metric(
                        label="⚖️ 특허 성장률",
                        value=f"{latest_growth:.1f}%",
                        delta=f"전년 대비"
                    )

def render_quality_metrics(papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """품질 지표"""
    st.subheader("🏆 품질 지표")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not papers_df.empty and 'Q1_Ratio(%)' in papers_df.columns:
            avg_q1_ratio = papers_df['Q1_Ratio(%)'].mean()
            st.metric(
                label="📊 평균 Q1 비율",
                value=f"{avg_q1_ratio:.1f}%",
                delta="논문 품질"
            )
    
    with col2:
        if not papers_df.empty and 'Collaboration_Ratio(%)' in papers_df.columns:
            avg_collab = papers_df['Collaboration_Ratio(%)'].mean()
            st.metric(
                label="🤝 국제협력 비율",
                value=f"{avg_collab:.1f}%",
                delta="협력 수준"
            )
    
    with col3:
        if not patents_df.empty and 'triadic_ratio' in patents_df.columns:
            avg_triadic = patents_df['triadic_ratio'].mean() * 100
            st.metric(
                label="🌐 Triadic 비율",
                value=f"{avg_triadic:.1f}%",
                delta="특허 품질"
            )
    
    with col4:
        if not patents_df.empty and 'claims_per_patent' in patents_df.columns:
            avg_claims = patents_df['claims_per_patent'].mean()
            st.metric(
                label="📋 평균 청구항",
                value=f"{avg_claims:.1f}",
                delta="특허당"
            )

def render_comparison_gauge(papers_df: pd.DataFrame, patents_df: pd.DataFrame, 
                           selected_country: str = None):
    """게이지 차트로 국가별 비교"""
    if selected_country is None and not papers_df.empty:
        selected_country = papers_df['Total_Papers'].idxmax() if 'Total_Papers' in papers_df.columns else papers_df.iloc[0]['Country']
    
    if selected_country is None:
        return
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "indicator"}, {"type": "indicator"}]],
        subplot_titles=('논문 H-Index', '특허 Triadic 비율')
    )
    
    # 논문 H-Index 게이지
    if not papers_df.empty:
        country_papers = papers_df[papers_df['Country'] == selected_country]
        if not country_papers.empty and 'H_Index' in country_papers.columns:
            h_index = country_papers['H_Index'].iloc[0]
            max_h_index = papers_df['H_Index'].max()
            
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=h_index,
                domain={'x': [0, 0.5], 'y': [0, 1]},
                title={'text': f"{selected_country} H-Index"},
                gauge={
                    'axis': {'range': [None, max_h_index]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, max_h_index*0.5], 'color': "lightgray"},
                        {'range': [max_h_index*0.5, max_h_index*0.8], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': max_h_index*0.9
                    }
                }
            ), row=1, col=1)
    
    # 특허 Triadic 비율 게이지
    if not patents_df.empty:
        country_patents = patents_df[patents_df['Country'] == selected_country]
        if not country_patents.empty and 'triadic_ratio' in country_patents.columns:
            triadic_ratio = country_patents['triadic_ratio'].iloc[0] * 100
            
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=triadic_ratio,
                domain={'x': [0.5, 1], 'y': [0, 1]},
                title={'text': f"{selected_country} Triadic %"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkred"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ), row=1, col=2)
    
    fig.update_layout(height=300, title_text=f"{selected_country} 주요 지표")
    st.plotly_chart(fig, use_container_width=True)

def render_top_performers(papers_df: pd.DataFrame, patents_df: pd.DataFrame, top_n: int = 5):
    """상위 성과자 표시"""
    st.subheader(f"🏆 상위 {top_n}개국")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not papers_df.empty and 'Total_Papers' in papers_df.columns:
            top_papers = papers_df.nlargest(top_n, 'Total_Papers')[['Country', 'Total_Papers', 'H_Index']]
            top_papers = top_papers.rename(columns={
                'Country': '국가',
                'Total_Papers': '논문 수',
                'H_Index': 'H-Index'
            })
            st.write("**논문 수 기준**")
            st.dataframe(top_papers, use_container_width=True, hide_index=True)
    
    with col2:
        if not patents_df.empty:
            patent_col = 'patent_count' if 'patent_count' in patents_df.columns else 'Total_Papers'
            if patent_col in patents_df.columns:
                display_cols = ['Country', patent_col]
                if 'triadic_ratio' in patents_df.columns:
                    display_cols.append('triadic_ratio')
                
                top_patents = patents_df.nlargest(top_n, patent_col)[display_cols]
                
                # 컬럼명 변경
                rename_dict = {'Country': '국가'}
                if patent_col == 'patent_count':
                    rename_dict['patent_count'] = '특허 수'
                else:
                    rename_dict[patent_col] = '특허 수'
                
                if 'triadic_ratio' in top_patents.columns:
                    rename_dict['triadic_ratio'] = 'Triadic 비율'
                    top_patents['triadic_ratio'] = top_patents['triadic_ratio'].apply(lambda x: f"{x*100:.1f}%")
                
                top_patents = top_patents.rename(columns=rename_dict)
                st.write("**특허 수 기준**")
                st.dataframe(top_patents, use_container_width=True, hide_index=True)