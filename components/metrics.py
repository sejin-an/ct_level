"""
KPI 메트릭 컴포넌트
components/metrics.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def safe_get_numeric_value(value):
    """안전하게 숫자 값 추출"""
    try:
        if pd.isna(value):
            return 0
        return float(value)
    except:
        return 0

def safe_calculate_percentage(numerator, denominator):
    """안전하게 백분율 계산"""
    try:
        if denominator == 0:
            return 0
        return (numerator / denominator) * 100
    except:
        return 0

def render_summary_metrics(summary: dict):
    """요약 메트릭 카드 렌더링"""
    st.subheader("📊 요약 통계")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        paper_count = safe_get_numeric_value(summary.get('paper_count', 0))
        st.metric(
            label="📄 총 논문 수",
            value=f"{paper_count:,}",
            help="전체 논문 레코드 수"
        )
    
    with col2:
        patent_count = safe_get_numeric_value(summary.get('patent_count', 0))
        st.metric(
            label="⚖️ 총 특허 수", 
            value=f"{patent_count:,}",
            help="전체 특허 레코드 수"
        )
    
    with col3:
        year_range = summary.get('year_range')
        if year_range and len(year_range) == 2:
            year_display = f"{year_range[0]}-{year_range[1]}"
            st.metric(
                label="📅 분석 기간",
                value=year_display,
                help="데이터 연도 범위"
            )
        else:
            st.metric(label="📅 분석 기간", value="N/A")
    
    with col4:
        country_count = safe_get_numeric_value(summary.get('country_count', 0))
        st.metric(
            label="🌍 국가 수",
            value=f"{country_count}",
            help="분석 대상 국가 수"
        )

def render_yearly_metrics(papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """연도별 메트릭"""
    st.subheader("📈 연도별 성장 지표")
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_paper_yearly_metrics(papers_df)
    
    with col2:
        render_patent_yearly_metrics(patents_df)

def render_paper_yearly_metrics(papers_df):
    """논문 연도별 메트릭"""
    if papers_df is None or papers_df.empty:
        st.info("논문 데이터가 없습니다.")
        return
    
    try:
        from utils.data_loader import detect_data_structure
        structure = detect_data_structure(papers_df)
        
        if not structure['has_timeseries']:
            st.warning("논문 데이터에 연도 정보가 없습니다.")
            return
        
        year_col = structure['time_columns'][0]
        
        # 논문 수 컬럼 찾기
        paper_col = None
        if structure['numeric_columns']:
            paper_col = structure['numeric_columns'][0]
        
        if paper_col:
            yearly_papers = papers_df.groupby(year_col)[paper_col].sum()
        else:
            yearly_papers = papers_df.groupby(year_col).size()
        
        if len(yearly_papers) > 1:
            yearly_papers = yearly_papers.sort_index()
            latest_year = yearly_papers.index[-1]
            latest_count = yearly_papers.iloc[-1]
            
            # 전년 대비 증가율
            previous_count = yearly_papers.iloc[-2]
            growth_rate = safe_calculate_percentage(
                latest_count - previous_count, previous_count
            )
            delta_value = f"{growth_rate:+.1f}%"
            
            st.metric(
                label="📄 최근 논문 수",
                value=f"{latest_count:,}",
                delta=delta_value,
                help=f"{latest_year}년 기준"
            )
            
            # 연평균 증가율 (CAGR)
            if len(yearly_papers) > 2:
                first_count = yearly_papers.iloc[0]
                years_span = len(yearly_papers) - 1
                if first_count > 0:
                    cagr = ((latest_count / first_count) ** (1/years_span) - 1) * 100
                    st.metric(
                        label="📈 연평균 증가율",
                        value=f"{cagr:.1f}%",
                        help="CAGR (Compound Annual Growth Rate)"
                    )
        else:
            st.metric(
                label="📄 논문 수",
                value=f"{yearly_papers.iloc[0]:,}"
            )
            
    except Exception as e:
        st.error(f"논문 연도별 메트릭 오류: {e}")

def render_patent_yearly_metrics(patents_df):
    """특허 연도별 메트릭"""
    if patents_df is None or patents_df.empty:
        st.info("특허 데이터가 없습니다.")
        return
    
    try:
        from utils.data_loader import detect_data_structure
        structure = detect_data_structure(patents_df)
        
        if not structure['has_timeseries']:
            st.warning("특허 데이터에 연도 정보가 없습니다.")
            return
        
        year_col = structure['time_columns'][0]
        
        # 특허 수 컬럼 찾기
        patent_col = None
        if structure['numeric_columns']:
            patent_col = structure['numeric_columns'][0]
        
        if patent_col:
            yearly_patents = patents_df.groupby(year_col)[patent_col].sum()
        else:
            yearly_patents = patents_df.groupby(year_col).size()
        
        if len(yearly_patents) > 1:
            yearly_patents = yearly_patents.sort_index()
            latest_year = yearly_patents.index[-1]
            latest_count = yearly_patents.iloc[-1]
            
            # 전년 대비 증가율
            previous_count = yearly_patents.iloc[-2]
            growth_rate = safe_calculate_percentage(
                latest_count - previous_count, previous_count
            )
            delta_value = f"{growth_rate:+.1f}%"
            
            st.metric(
                label="⚖️ 최근 특허 수",
                value=f"{latest_count:,}",
                delta=delta_value,
                help=f"{latest_year}년 기준"
            )
            
            # 연평균 증가율 (CAGR)
            if len(yearly_patents) > 2:
                first_count = yearly_patents.iloc[0]
                years_span = len(yearly_patents) - 1
                if first_count > 0:
                    cagr = ((latest_count / first_count) ** (1/years_span) - 1) * 100
                    st.metric(
                        label="📈 연평균 증가율",
                        value=f"{cagr:.1f}%",
                        help="CAGR (Compound Annual Growth Rate)"
                    )
        else:
            st.metric(
                label="⚖️ 특허 수",
                value=f"{yearly_patents.iloc[0]:,}"
            )
            
    except Exception as e:
        st.error(f"특허 연도별 메트릭 오류: {e}")

def render_top_countries_metrics(papers_df: pd.DataFrame, top_n: int = 5):
    """상위 국가 메트릭"""
    if papers_df is None or papers_df.empty:
        return
    
    st.subheader(f"🏆 상위 {top_n}개국")
    
    try:
        from utils.data_loader import detect_data_structure
        structure = detect_data_structure(papers_df)
        
        if not structure['has_country']:
            st.warning("국가 정보가 없습니다.")
            return
        
        country_col = structure['country_columns'][0]
        
        # 주요 수치 컬럼 찾기
        main_col = None
        if structure['numeric_columns']:
            main_col = structure['numeric_columns'][0]
        
        if main_col:
            # 국가별 집계
            country_counts = papers_df.groupby(country_col)[main_col].sum().nlargest(top_n)
        else:
            # 컬럼이 없으면 단순 개수로 집계
            country_counts = papers_df[country_col].value_counts().head(top_n)
        
        # 컬럼으로 표시
        cols = st.columns(min(top_n, 5))
        
        total_count = country_counts.sum()
        
        for i, (country, count) in enumerate(country_counts.items()):
            if i < len(cols):
                with cols[i]:
                    # 전체 대비 비율 계산
                    percentage = safe_calculate_percentage(count, total_count)
                    
                    st.metric(
                        label=f"🌍 {country}",
                        value=f"{count:,}",
                        delta=f"{percentage:.1f}%",
                        help="상위 국가 대비 비율"
                    )
        
    except Exception as e:
        st.error(f"상위 국가 메트릭 오류: {e}")

def render_comparison_gauge(papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """논문 vs 특허 비교 게이지"""
    st.subheader("⚖️ 논문 vs 특허 비율")
    
    try:
        paper_count = len(papers_df) if papers_df is not None and not papers_df.empty else 0
        patent_count = len(patents_df) if patents_df is not None and not patents_df.empty else 0
        total_count = paper_count + patent_count
        
        if total_count > 0:
            paper_ratio = (paper_count / total_count) * 100
            
            # 게이지 차트
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
                        'value': 50
                    }
                }
            ))
            
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
            # 수치 정보
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"📄 논문: {paper_count:,}건 ({paper_ratio:.1f}%)")
            with col2:
                st.info(f"⚖️ 특허: {patent_count:,}건 ({100-paper_ratio:.1f}%)")
            with col3:
                # 균형도 평가
                balance = abs(paper_ratio - 50)
                if balance < 10:
                    balance_text = "🔄 균형적"
                elif balance < 25:
                    balance_text = "📊 편향적"
                else:
                    balance_text = "⚠️ 매우편향적"
                st.info(f"균형도: {balance_text}")
        else:
            st.warning("비교할 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"비교 게이지 오류: {e}")

def render_data_quality_metrics(papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """데이터 품질 메트릭"""
    st.subheader("🔍 데이터 품질 지표")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_data_completeness(papers_df, "논문")
    
    with col2:
        render_data_completeness(patents_df, "특허")
    
    with col3:
        render_data_consistency(papers_df, patents_df)

def render_data_completeness(df, data_type):
    """데이터 완성도 분석"""
    try:
        if df is None or df.empty:
            st.metric(f"{data_type} 완성도", "N/A")
            return
        
        from utils.data_loader import detect_data_structure
        structure = detect_data_structure(df)
        
        # 주요 컬럼들의 완성도 확인
        key_columns = []
        if structure['has_timeseries']:
            key_columns.extend(structure['time_columns'])
        if structure['has_country']:
            key_columns.extend(structure['country_columns'])
        
        if key_columns:
            # 모든 키 컬럼이 완성된 행의 비율
            complete_rows = df[key_columns].notna().all(axis=1).sum()
            total_rows = len(df)
            completeness = safe_calculate_percentage(complete_rows, total_rows)
            
            # 중복 확인
            if len(key_columns) >= 2:
                unique_combinations = df[key_columns].drop_duplicates().shape[0]
                duplicate_ratio = safe_calculate_percentage(
                    total_rows - unique_combinations, total_rows
                )
            else:
                duplicate_ratio = 0
            
            st.metric(
                label=f"{data_type} 완성도",
                value=f"{completeness:.1f}%",
                delta=f"중복: {duplicate_ratio:.1f}%",
                help="주요 컬럼 완성도 및 중복률"
            )
        else:
            st.metric(f"{data_type} 완성도", "측정불가")
            
    except Exception as e:
        st.warning(f"{data_type} 데이터 품질 분석 오류: {e}")

def render_data_consistency(papers_df, patents_df):
    """데이터 일관성 분석"""
    try:
        consistency_score = 0
        total_checks = 0
        
        from utils.data_loader import detect_data_structure
        
        # 연도 범위 일관성 확인
        if papers_df is not None and patents_df is not None:
            paper_structure = detect_data_structure(papers_df)
            patent_structure = detect_data_structure(patents_df)
            
            paper_years = set()
            patent_years = set()
            
            # 논문 연도 추출
            if paper_structure['has_timeseries']:
                year_col = paper_structure['time_columns'][0]
                paper_years = set(papers_df[year_col].dropna().unique())
            
            # 특허 연도 추출
            if patent_structure['has_timeseries']:
                year_col = patent_structure['time_columns'][0]
                patent_years = set(patents_df[year_col].dropna().unique())
            
            if paper_years and patent_years:
                # 공통 연도 비율
                common_years = paper_years & patent_years
                all_years = paper_years | patent_years
                if all_years:
                    year_consistency = len(common_years) / len(all_years) * 100
                    consistency_score += year_consistency
                    total_checks += 1
            
            # 국가 일관성 확인
            paper_countries = set()
            patent_countries = set()
            
            # 논문 국가 추출
            if paper_structure['has_country']:
                country_col = paper_structure['country_columns'][0]
                paper_countries = set(papers_df[country_col].dropna().unique())
            
            # 특허 국가 추출
            if patent_structure['has_country']:
                country_col = patent_structure['country_columns'][0]
                patent_countries = set(patents_df[country_col].dropna().unique())
            
            if paper_countries and patent_countries:
                # 공통 국가 비율
                common_countries = paper_countries & patent_countries
                all_countries = paper_countries | patent_countries
                if all_countries:
                    country_consistency = len(common_countries) / len(all_countries) * 100
                    consistency_score += country_consistency
                    total_checks += 1
        
        # 평균 일관성 점수
        if total_checks > 0:
            avg_consistency = consistency_score / total_checks
            
            if avg_consistency >= 80:
                consistency_level = "높음"
            elif avg_consistency >= 60:
                consistency_level = "중간"
            else:
                consistency_level = "낮음"
            
            st.metric(
                label="🔗 데이터 일관성",
                value=f"{avg_consistency:.0f}%",
                delta=consistency_level,
                help="논문-특허 간 연도/국가 일관성"
            )
        else:
            st.metric("🔗 데이터 일관성", "측정불가")
            
    except Exception as e:
        st.warning(f"데이터 일관성 분석 오류: {e}")