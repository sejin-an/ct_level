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
import warnings
warnings.filterwarnings('ignore')

def safe_get_column(df, keywords):
    """안전하게 컬럼 찾기"""
    if df is None or df.empty:
        return None
    
    for col in df.columns:
        for keyword in keywords:
            if keyword.lower() in col.lower():
                return col
    return None

def safe_get_numeric_column(df, keywords):
    """안전하게 숫자형 컬럼 찾기"""
    if df is None or df.empty:
        return None
    
    for col in df.columns:
        for keyword in keywords:
            if keyword.lower() in col.lower():
                try:
                    pd.to_numeric(df[col], errors='coerce')
                    return col
                except:
                    continue
    return None

def render_basic_timeseries(papers_df, patents_df):
    """기본 시계열 분석"""
    st.subheader("📈 기본 시계열 분석")
    
    if papers_df is None and patents_df is None:
        st.warning("표시할 데이터가 없습니다.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        if papers_df is not None and not papers_df.empty:
            render_paper_timeseries(papers_df)
    
    with col2:
        if patents_df is not None and not patents_df.empty:
            render_patent_timeseries(patents_df)

def render_paper_timeseries(papers_df):
    """논문 시계열 분석"""
    try:
        year_col = safe_get_column(papers_df, ['Year', '연도'])
        papers_col = safe_get_numeric_column(papers_df, ['total', 'paper', '논문'])
        
        if not year_col:
            st.info("연도 컬럼을 찾을 수 없습니다.")
            return
            
        if not papers_col:
            # 단순 개수 집계
            yearly_data = papers_df.groupby(year_col).size().reset_index(name='Count')
            papers_col = 'Count'
        else:
            # 합계 집계
            yearly_data = papers_df.groupby(year_col)[papers_col].sum().reset_index()
        
        yearly_data = yearly_data.sort_values(year_col)
        
        fig = px.line(
            yearly_data, 
            x=year_col, 
            y=papers_col,
            title='📄 연도별 논문 수 추이',
            markers=True
        )
        fig.update_traces(line_width=3, marker_size=8)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # 성장률 계산
        if len(yearly_data) > 1:
            growth_rate = yearly_data[papers_col].pct_change().mean() * 100
            if not pd.isna(growth_rate):
                st.metric("📈 평균 성장률", f"{growth_rate:.1f}%")
            
    except Exception as e:
        st.error(f"논문 시계열 분석 오류: {e}")

def render_patent_timeseries(patents_df):
    """특허 시계열 분석"""
    try:
        year_col = safe_get_column(patents_df, ['Year', '연도'])
        patent_col = safe_get_numeric_column(patents_df, ['patent', 'count', '특허'])
        
        if not year_col:
            st.info("연도 컬럼을 찾을 수 없습니다.")
            return
            
        if not patent_col:
            # 단순 개수 집계
            yearly_data = patents_df.groupby(year_col).size().reset_index(name='Count')
            patent_col = 'Count'
        else:
            # 합계 집계
            yearly_data = patents_df.groupby(year_col)[patent_col].sum().reset_index()
        
        yearly_data = yearly_data.sort_values(year_col)
        
        fig = px.line(
            yearly_data, 
            x=year_col, 
            y=patent_col,
            title='⚖️ 연도별 특허 수 추이',
            markers=True,
            color_discrete_sequence=['#FF6B6B']
        )
        fig.update_traces(line_width=3, marker_size=8)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # 성장률 계산
        if len(yearly_data) > 1:
            growth_rate = yearly_data[patent_col].pct_change().mean() * 100
            if not pd.isna(growth_rate):
                st.metric("📈 평균 성장률", f"{growth_rate:.1f}%")
            
    except Exception as e:
        st.error(f"특허 시계열 분석 오류: {e}")

def render_combined_timeseries(papers_df, patents_df):
    """통합 시계열 비교"""
    st.subheader("🔄 논문 vs 특허 통합 비교")
    
    if papers_df is None or patents_df is None:
        st.warning("논문과 특허 데이터가 모두 필요합니다.")
        return
    
    try:
        # 논문 데이터 처리
        paper_year_col = safe_get_column(papers_df, ['Year', '연도'])
        paper_count_col = safe_get_numeric_column(papers_df, ['total', 'paper', '논문'])
        
        # 특허 데이터 처리
        patent_year_col = safe_get_column(patents_df, ['Year', '연도'])
        patent_count_col = safe_get_numeric_column(patents_df, ['patent', 'count', '특허'])
        
        if not paper_year_col or not patent_year_col:
            st.warning("연도 컬럼을 찾을 수 없습니다.")
            return
        
        # 논문 연도별 집계
        if paper_count_col:
            paper_yearly = papers_df.groupby(paper_year_col)[paper_count_col].sum().reset_index()
        else:
            paper_yearly = papers_df.groupby(paper_year_col).size().reset_index(name='Count')
            paper_count_col = 'Count'
        
        # 특허 연도별 집계
        if patent_count_col:
            patent_yearly = patents_df.groupby(patent_year_col)[patent_count_col].sum().reset_index()
        else:
            patent_yearly = patents_df.groupby(patent_year_col).size().reset_index(name='Count')
            patent_count_col = 'Count'
        
        # 이중 축 차트 생성
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # 논문 데이터
        fig.add_trace(
            go.Scatter(
                x=paper_yearly[paper_year_col],
                y=paper_yearly[paper_count_col],
                mode='lines+markers',
                name='논문 수',
                line=dict(color='#4ECDC4', width=3),
                marker=dict(size=8)
            ),
            secondary_y=False,
        )
        
        # 특허 데이터
        fig.add_trace(
            go.Scatter(
                x=patent_yearly[patent_year_col],
                y=patent_yearly[patent_count_col],
                mode='lines+markers',
                name='특허 수',
                line=dict(color='#FF6B6B', width=3),
                marker=dict(size=8)
            ),
            secondary_y=True,
        )
        
        # 축 라벨 설정
        fig.update_xaxes(title_text="연도")
        fig.update_yaxes(title_text="논문 수", secondary_y=False)
        fig.update_yaxes(title_text="특허 수", secondary_y=True)
        
        fig.update_layout(
            title="논문 vs 특허 이중축 비교",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 상관관계 분석
        render_correlation_metrics(paper_yearly, patent_yearly, paper_year_col, patent_year_col, paper_count_col, patent_count_col)
        
    except Exception as e:
        st.error(f"통합 시계열 분석 오류: {e}")

def render_correlation_metrics(paper_data, patent_data, year_col1, year_col2, count_col1, count_col2):
    """상관관계 메트릭"""
    try:
        # 공통 연도 찾기
        common_years = set(paper_data[year_col1]) & set(patent_data[year_col2])
        
        if len(common_years) < 3:
            st.info("상관관계 분석을 위한 충분한 데이터가 없습니다.")
            return
        
        # 공통 연도 데이터 추출
        paper_common = paper_data[paper_data[year_col1].isin(common_years)].sort_values(year_col1)
        patent_common = patent_data[patent_data[year_col2].isin(common_years)].sort_values(year_col2)
        
        if len(paper_common) == len(patent_common):
            # 상관계수 계산
            correlation = np.corrcoef(paper_common[count_col1], patent_common[count_col2])[0, 1]
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📊 상관계수", f"{correlation:.3f}")
            with col2:
                if abs(correlation) > 0.7:
                    st.success("🔗 강한 상관관계")
                elif abs(correlation) > 0.4:
                    st.warning("🔗 중간 상관관계")
                else:
                    st.info("🔗 약한 상관관계")
                    
    except Exception as e:
        st.warning(f"상관관계 분석 중 오류: {e}")

def render_cumulative_trends(papers_df, patents_df):
    """누적 추이 분석"""
    st.subheader("📈 누적 추이 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if papers_df is not None and not papers_df.empty:
            render_cumulative_chart(papers_df, "논문", ['total', 'paper', '논문'])
    
    with col2:
        if patents_df is not None and not patents_df.empty:
            render_cumulative_chart(patents_df, "특허", ['patent', 'count', '특허'])

def render_cumulative_chart(df, data_type, keywords):
    """누적 차트 렌더링"""
    try:
        year_col = safe_get_column(df, ['Year', '연도'])
        count_col = safe_get_numeric_column(df, keywords)
        
        if not year_col:
            st.info(f"{data_type} 연도 컬럼을 찾을 수 없습니다.")
            return
        
        # 연도별 집계 및 누적합 계산
        if count_col:
            yearly_data = df.groupby(year_col)[count_col].sum().reset_index()
        else:
            yearly_data = df.groupby(year_col).size().reset_index(name='Count')
            count_col = 'Count'
        
        yearly_data = yearly_data.sort_values(year_col)
        yearly_data['cumulative'] = yearly_data[count_col].cumsum()
        
        fig = px.area(
            yearly_data,
            x=year_col,
            y='cumulative',
            title=f"{data_type} 누적 추이",
            color_discrete_sequence=['#45B7D1']
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # 총 누적량 표시
        total_cumulative = yearly_data['cumulative'].iloc[-1]
        st.metric(f"📊 총 누적 {data_type} 수", f"{total_cumulative:,.0f}")
        
    except Exception as e:
        st.error(f"{data_type} 누적 분석 오류: {e}")

def render_growth_rate_analysis(papers_df, patents_df):
    """성장률 분석"""
    st.subheader("📊 성장률 세부 분석")
    
    tab1, tab2, tab3 = st.tabs(["📄 논문 성장률", "⚖️ 특허 성장률", "📈 비교 분석"])
    
    with tab1:
        if papers_df is not None and not papers_df.empty:
            render_detailed_growth_analysis(papers_df, "논문", ['total', 'paper', '논문'])
    
    with tab2:
        if patents_df is not None and not patents_df.empty:
            render_detailed_growth_analysis(patents_df, "특허", ['patent', 'count', '특허'])
    
    with tab3:
        render_growth_comparison(papers_df, patents_df)

def render_detailed_growth_analysis(df, data_type, keywords):
    """상세 성장률 분석"""
    try:
        year_col = safe_get_column(df, ['Year', '연도'])
        count_col = safe_get_numeric_column(df, keywords)
        
        if not year_col:
            st.info(f"{data_type} 연도 컬럼을 찾을 수 없습니다.")
            return
        
        # 전체 성장률
        if count_col:
            yearly_total = df.groupby(year_col)[count_col].sum().reset_index()
        else:
            yearly_total = df.groupby(year_col).size().reset_index(name='Count')
            count_col = 'Count'
        
        yearly_total = yearly_total.sort_values(year_col)
        yearly_total['growth_rate'] = yearly_total[count_col].pct_change() * 100
        
        # 성장률 차트
        growth_data = yearly_total.dropna()
        if not growth_data.empty:
            fig = px.bar(
                growth_data,
                x=year_col,
                y='growth_rate',
                title=f"{data_type} 연간 성장률 (%)",
                color='growth_rate',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # 통계 요약
            avg_growth = growth_data['growth_rate'].mean()
            std_growth = growth_data['growth_rate'].std()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("평균 성장률", f"{avg_growth:.1f}%")
            with col2:
                st.metric("성장률 표준편차", f"{std_growth:.1f}%")
            with col3:
                volatility = "높음" if std_growth > 20 else "중간" if std_growth > 10 else "낮음"
                st.metric("변동성", volatility)
        
    except Exception as e:
        st.error(f"{data_type} 성장률 분석 오류: {e}")

def render_growth_comparison(papers_df, patents_df):
    """성장률 비교 분석"""
    try:
        if papers_df is None or patents_df is None:
            st.warning("논문과 특허 데이터가 모두 필요합니다.")
            return
        
        # 논문 성장률 계산
        paper_year_col = safe_get_column(papers_df, ['Year', '연도'])
        paper_count_col = safe_get_numeric_column(papers_df, ['total', 'paper', '논문'])
        
        # 특허 성장률 계산
        patent_year_col = safe_get_column(patents_df, ['Year', '연도'])
        patent_count_col = safe_get_numeric_column(patents_df, ['patent', 'count', '특허'])
        
        if not paper_year_col or not patent_year_col:
            st.warning("성장률 비교를 위한 연도 컬럼을 찾을 수 없습니다.")
            return
        
        # 연도별 성장률 계산
        if paper_count_col:
            paper_yearly = papers_df.groupby(paper_year_col)[paper_count_col].sum()
        else:
            paper_yearly = papers_df.groupby(paper_year_col).size()
        
        if patent_count_col:
            patent_yearly = patents_df.groupby(patent_year_col)[patent_count_col].sum()
        else:
            patent_yearly = patents_df.groupby(patent_year_col).size()
        
        paper_growth = paper_yearly.pct_change() * 100
        patent_growth = patent_yearly.pct_change() * 100
        
        # 공통 연도 찾기
        common_years = set(paper_growth.index) & set(patent_growth.index)
        
        if len(common_years) > 1:
            comparison_data = []
            for Year in sorted(common_years):
                if not (pd.isna(paper_growth[Year]) or pd.isna(patent_growth[Year])):
                    comparison_data.append({
                        'Year': Year,
                        'Paper_Growth': paper_growth[Year],
                        'Patent_Growth': patent_growth[Year]
                    })
            
            if comparison_data:
                comp_df = pd.DataFrame(comparison_data)
                
                fig = px.line(
                    comp_df,
                    x='Year',
                    y=['Paper_Growth', 'Patent_Growth'],
                    title="논문 vs 특허 성장률 비교",
                    markers=True
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # 평균 성장률 비교
                col1, col2 = st.columns(2)
                with col1:
                    avg_paper_growth = comp_df['Paper_Growth'].mean()
                    st.metric("논문 평균 성장률", f"{avg_paper_growth:.1f}%")
                with col2:
                    avg_patent_growth = comp_df['Patent_Growth'].mean()
                    st.metric("특허 평균 성장률", f"{avg_patent_growth:.1f}%")
        
    except Exception as e:
        st.error(f"성장률 비교 분석 오류: {e}")

def render_trend_comparison(papers_df, patents_df):
    """트렌드 상관관계 분석"""
    st.subheader("🔗 트렌드 상관관계 분석")
    render_combined_timeseries(papers_df, patents_df)

def render_forecast_trend(papers_df, patents_df):
    """간단한 트렌드 예측"""
    st.subheader("🔮 트렌드 예측 (단순 선형)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if papers_df is not None and not papers_df.empty:
            render_simple_forecast(papers_df, "논문", ['total', 'paper', '논문'])
    
    with col2:
        if patents_df is not None and not patents_df.empty:
            render_simple_forecast(patents_df, "특허", ['patent', 'count', '특허'])

def render_simple_forecast(df, data_type, keywords):
    """단순 선형 예측"""
    try:
        year_col = safe_get_column(df, ['Year', '연도'])
        count_col = safe_get_numeric_column(df, keywords)
        
        if not year_col:
            st.info(f"{data_type} 연도 컬럼을 찾을 수 없습니다.")
            return
        
        # 연도별 집계
        if count_col:
            yearly_data = df.groupby(year_col)[count_col].sum().reset_index()
        else:
            yearly_data = df.groupby(year_col).size().reset_index(name='Count')
            count_col = 'Count'
        
        yearly_data = yearly_data.sort_values(year_col)
        
        if len(yearly_data) < 3:
            st.info(f"{data_type} 예측을 위한 충분한 데이터가 없습니다.")
            return
        
        # 선형 회귀
        x = yearly_data[year_col].values
        y = yearly_data[count_col].values
        
        # numpy polyfit을 사용한 1차 다항식 피팅
        coeffs = np.polyfit(x, y, 1)
        slope, intercept = coeffs[0], coeffs[1]
        
        # R² 계산
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # 미래 연도 예측 (2년)
        future_years = np.arange(x.max() + 1, x.max() + 3)
        future_values = slope * future_years + intercept
        
        # 전체 트렌드 라인
        all_years = np.arange(x.min(), x.max() + 3)
        trend_line = slope * all_years + intercept
        
        # 그래프 생성
        fig = go.Figure()
        
        # 실제 데이터
        fig.add_trace(go.Scatter(
            x=yearly_data[year_col],
            y=yearly_data[count_col],
            mode='markers+lines',
            name=f'실제 {data_type} 수',
            line=dict(color='blue', width=3),
            marker=dict(size=8)
        ))
        
        # 트렌드 라인
        fig.add_trace(go.Scatter(
            x=all_years,
            y=trend_line,
            mode='lines',
            name='예측 트렌드',
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
            title=f'{data_type} 수 예측 (R² = {r_squared:.3f})',
            xaxis_title='연도',
            yaxis_title=f'{data_type} 수',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 예측 결과 표시
        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"{int(future_years[0])}년 예측", f"{future_values[0]:,.0f}")
        with col2:
            st.metric(f"{int(future_years[1])}년 예측", f"{future_values[1]:,.0f}")
        
        # 신뢰도 표시
        confidence = "높음" if r_squared > 0.8 else "중간" if r_squared > 0.5 else "낮음"
        st.info(f"📊 예측 신뢰도: {confidence} (R² = {r_squared:.3f})")
        
    except Exception as e:
        st.error(f"{data_type} 예측 분석 오류: {e}")