"""
시계열 트렌드 분석 컴포넌트
components/trends.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def render_yearly_trends_comprehensive(papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """포괄적 연도별 트렌드 분석"""
    st.subheader("📈 연도별 종합 트렌드")
    
    if papers_df.empty and patents_df.empty:
        st.warning("표시할 데이터가 없습니다.")
        return
    
    # 4개 서브플롯 생성
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            '논문 출간 수 추이', 
            '특허 출원 수 추이', 
            '논문 품질 지표 (H-Index)', 
            '특허 품질 지표 (Triadic 비율)'
        ),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    
    # 1. 논문 출간 수 추이
    if not papers_df.empty and 'Total_Papers' in papers_df.columns:
        papers_yearly = papers_df.groupby(['Year', 'Country'])['Total_Papers'].sum().reset_index()
        for i, country in enumerate(papers_yearly['Country'].unique()):
            country_data = papers_yearly[papers_yearly['Country'] == country]
            fig.add_trace(
                go.Scatter(
                    x=country_data['Year'],
                    y=country_data['Total_Papers'],
                    mode='lines+markers',
                    name=f"{country}",
                    line=dict(color=colors[i % len(colors)], width=2),
                    marker=dict(size=6)
                ),
                row=1, col=1
            )
    
    # 2. 특허 출원 수 추이
    if not patents_df.empty:
        patent_col = 'patent_count' if 'patent_count' in patents_df.columns else 'Total_Papers'
        if patent_col in patents_df.columns:
            patents_yearly = patents_df.groupby(['Year', 'Country'])[patent_col].sum().reset_index()
            for i, country in enumerate(patents_yearly['Country'].unique()):
                country_data = patents_yearly[patents_yearly['Country'] == country]
                fig.add_trace(
                    go.Scatter(
                        x=country_data['Year'],
                        y=country_data[patent_col],
                        mode='lines+markers',
                        name=f"{country}",
                        line=dict(color=colors[i % len(colors)], width=2, dash='dash'),
                        marker=dict(size=6),
                        showlegend=False
                    ),
                    row=1, col=2
                )
    
    # 3. H-Index 추이
    if not papers_df.empty and 'H_Index' in papers_df.columns:
        h_index_yearly = papers_df.groupby(['Year', 'Country'])['H_Index'].mean().reset_index()
        for i, country in enumerate(h_index_yearly['Country'].unique()):
            country_data = h_index_yearly[h_index_yearly['Country'] == country]
            fig.add_trace(
                go.Scatter(
                    x=country_data['Year'],
                    y=country_data['H_Index'],
                    mode='lines+markers',
                    name=f"{country}",
                    line=dict(color=colors[i % len(colors)], width=2),
                    marker=dict(size=6),
                    showlegend=False
                ),
                row=2, col=1
            )
    
    # 4. Triadic 비율 추이
    if not patents_df.empty and 'triadic_ratio' in patents_df.columns:
        triadic_yearly = patents_df.groupby(['Year', 'Country'])['triadic_ratio'].mean().reset_index()
        triadic_yearly['triadic_ratio'] = triadic_yearly['triadic_ratio'] * 100  # 백분율 변환
        for i, country in enumerate(triadic_yearly['Country'].unique()):
            country_data = triadic_yearly[triadic_yearly['Country'] == country]
            fig.add_trace(
                go.Scatter(
                    x=country_data['Year'],
                    y=country_data['triadic_ratio'],
                    mode='lines+markers',
                    name=f"{country}",
                    line=dict(color=colors[i % len(colors)], width=2, dash='dash'),
                    marker=dict(size=6),
                    showlegend=False
                ),
                row=2, col=2
            )
    
    # 레이아웃 업데이트
    fig.update_layout(
        height=600,
        title_text="연도별 주요 지표 종합 트렌드",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # 축 라벨 설정
    fig.update_xaxes(title_text="연도", row=2, col=1)
    fig.update_xaxes(title_text="연도", row=2, col=2)
    fig.update_yaxes(title_text="논문 수", row=1, col=1)
    fig.update_yaxes(title_text="특허 수", row=1, col=2)
    fig.update_yaxes(title_text="H-Index", row=2, col=1)
    fig.update_yaxes(title_text="Triadic 비율 (%)", row=2, col=2)
    
    st.plotly_chart(fig, use_container_width=True)

def render_growth_rate_analysis(papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """성장률 분석"""
    st.subheader("📊 연간 성장률 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not papers_df.empty and len(papers_df['Year'].unique()) > 1:
            # 논문 성장률
            papers_growth = calculate_growth_rates(papers_df, 'Total_Papers', '논문')
            if not papers_growth.empty:
                fig = px.bar(
                    papers_growth,
                    x='Country',
                    y='Growth_Rate',
                    color='Growth_Rate',
                    title='논문 수 연간 성장률',
                    color_continuous_scale='RdYlBu_r',
                    text='Growth_Rate'
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(xaxis_tickangle=-45, yaxis_title='성장률 (%)')
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not patents_df.empty and len(patents_df['Year'].unique()) > 1:
            # 특허 성장률
            patent_col = 'patent_count' if 'patent_count' in patents_df.columns else 'Total_Papers'
            patents_growth = calculate_growth_rates(patents_df, patent_col, '특허')
            if not patents_growth.empty:
                fig = px.bar(
                    patents_growth,
                    x='Country',
                    y='Growth_Rate',
                    color='Growth_Rate',
                    title='특허 수 연간 성장률',
                    color_continuous_scale='RdYlBu_r',
                    text='Growth_Rate'
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(xaxis_tickangle=-45, yaxis_title='성장률 (%)')
                st.plotly_chart(fig, use_container_width=True)

def calculate_growth_rates(df: pd.DataFrame, value_col: str, data_type: str) -> pd.DataFrame:
    """성장률 계산"""
    growth_data = []
    
    for country in df['Country'].unique():
        country_data = df[df['Country'] == country].sort_values('Year')
        if len(country_data) > 1 and value_col in country_data.columns:
            yearly_data = country_data.groupby('Year')[value_col].sum()
            growth_rate = yearly_data.pct_change().mean() * 100
            
            growth_data.append({
                'Country': country,
                'Growth_Rate': growth_rate,
                'Type': data_type
            })
    
    return pd.DataFrame(growth_data)

def render_correlation_analysis(papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """상관관계 분석"""
    st.subheader("🔗 지표간 상관관계")
    
    # 논문-특허 통합 데이터 생성
    if papers_df.empty or patents_df.empty:
        st.warning("논문과 특허 데이터가 모두 필요합니다.")
        return
    
    # 국가별 통합 데이터
    correlation_data = []
    
    for country in set(papers_df['Country'].unique()) & set(patents_df['Country'].unique()):
        papers_country = papers_df[papers_df['Country'] == country]
        patents_country = patents_df[patents_df['Country'] == country]
        
        if not papers_country.empty and not patents_country.empty:
            patent_col = 'patent_count' if 'patent_count' in patents_country.columns else 'Total_Papers'
            
            correlation_data.append({
                'Country': country,
                'Papers': papers_country['Total_Papers'].sum() if 'Total_Papers' in papers_country.columns else 0,
                'Patents': patents_country[patent_col].sum() if patent_col in patents_country.columns else 0,
                'H_Index': papers_country['H_Index'].mean() if 'H_Index' in papers_country.columns else 0,
                'Triadic_Ratio': patents_country['triadic_ratio'].mean() * 100 if 'triadic_ratio' in patents_country.columns else 0,
                'Q1_Ratio': papers_country['Q1_Ratio(%)'].mean() if 'Q1_Ratio(%)' in papers_country.columns else 0
            })
    
    if correlation_data:
        corr_df = pd.DataFrame(correlation_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 논문 수 vs H-Index
            fig = px.scatter(
                corr_df,
                x='Papers',
                y='H_Index',
                color='Country',
                size='Q1_Ratio',
                title='논문 수 vs H-Index',
                hover_data=['Q1_Ratio']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 특허 수 vs Triadic 비율
            fig = px.scatter(
                corr_df,
                x='Patents',
                y='Triadic_Ratio',
                color='Country',
                title='특허 수 vs Triadic 비율',
                hover_data=['Country']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

def render_seasonal_analysis(papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """계절성 분석 (월별 데이터가 있는 경우)"""
    st.subheader("📅 시계열 패턴 분석")
    
    # 연도별 데이터 패턴 분석
    if not papers_df.empty:
        papers_pattern = analyze_yearly_patterns(papers_df, 'Total_Papers', '논문')
        if papers_pattern:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    label="논문 발행 패턴",
                    value=papers_pattern['trend'],
                    delta=f"변동계수: {papers_pattern['cv']:.2f}"
                )
            
            with col2:
                if not patents_df.empty:
                    patent_col = 'patent_count' if 'patent_count' in patents_df.columns else 'Total_Papers'
                    patents_pattern = analyze_yearly_patterns(patents_df, patent_col, '특허')
                    if patents_pattern:
                        st.metric(
                            label="특허 출원 패턴",
                            value=patents_pattern['trend'],
                            delta=f"변동계수: {patents_pattern['cv']:.2f}"
                        )

def analyze_yearly_patterns(df: pd.DataFrame, value_col: str, data_type: str) -> dict:
    """연도별 패턴 분석"""
    if df.empty or value_col not in df.columns:
        return None
    
    yearly_totals = df.groupby('Year')[value_col].sum()
    
    if len(yearly_totals) < 2:
        return None
    
    # 트렌드 분석
    years = yearly_totals.index.values
    values = yearly_totals.values
    
    # 선형 회귀로 트렌드 계산
    slope = np.polyfit(years, values, 1)[0]
    cv = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
    
    if slope > 0:
        trend = "증가 추세"
    elif slope < 0:
        trend = "감소 추세"
    else:
        trend = "안정적"
    
    return {
        'trend': trend,
        'cv': cv,
        'slope': slope
    }

def render_forecasting(papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """간단한 예측 분석"""
    st.subheader("🔮 트렌드 예측")
    
    if papers_df.empty and patents_df.empty:
        st.warning("예측을 위한 데이터가 부족합니다.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not papers_df.empty and len(papers_df['Year'].unique()) > 1:
            forecast_papers = create_simple_forecast(papers_df, 'Total_Papers', '논문')
            if forecast_papers:
                st.plotly_chart(forecast_papers, use_container_width=True)
    
    with col2:
        if not patents_df.empty and len(patents_df['Year'].unique()) > 1:
            patent_col = 'patent_count' if 'patent_count' in patents_df.columns else 'Total_Papers'
            forecast_patents = create_simple_forecast(patents_df, patent_col, '특허')
            if forecast_patents:
                st.plotly_chart(forecast_patents, use_container_width=True)

def create_simple_forecast(df: pd.DataFrame, value_col: str, data_type: str):
    """단순 선형 예측"""
    if value_col not in df.columns:
        return None
    
    # 연도별 총합 계산
    yearly_data = df.groupby('Year')[value_col].sum().reset_index()
    
    if len(yearly_data) < 2:
        return None
    
    # 선형 회귀
    x = yearly_data['Year'].values
    y = yearly_data[value_col].values
    
    # 다음 2년 예측
    future_years = np.arange(x.max() + 1, x.max() + 3)
    coeffs = np.polyfit(x, y, 1)
    trend_line = np.poly1d(coeffs)
    
    # 과거 트렌드
    extended_years = np.arange(x.min(), x.max() + 3)
    trend_values = trend_line(extended_years)
    
    # 그래프 생성
    fig = go.Figure()
    
    # 실제 데이터
    fig.add_trace(go.Scatter(
        x=yearly_data['Year'],
        y=yearly_data[value_col],
        mode='markers+lines',
        name=f'실제 {data_type} 수',
        line=dict(color='blue', width=3),
        marker=dict(size=8)
    ))
    
    # 트렌드 라인
    fig.add_trace(go.Scatter(
        x=extended_years,
        y=trend_values,
        mode='lines',
        name='트렌드 예측',
        line=dict(color='red', width=2, dash='dash')
    ))
    
    # 예측 구간 표시
    fig.add_vrect(
        x0=x.max() + 0.5, x1=future_years.max() + 0.5,
        fillcolor="rgba(255,0,0,0.1)",
        layer="below",
        line_width=0,
    )
    
    fig.update_layout(
        title=f'{data_type} 수 트렌드 및 예측',
        xaxis_title='연도',
        yaxis_title=f'{data_type} 수',
        height=400,
        showlegend=True
    )
    
    return fig