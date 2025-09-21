"""
간단한 디버깅 버전 - 기본 기능만 구현
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="기술수준조사 대시보드 (Simple)",
    page_icon="📈",
    layout="wide"
)

def create_sample_data():
    """샘플 데이터 생성"""
    countries = ['미국', '중국', '독일', '일본', '한국', '영국', '프랑스', '캐나다', '이탈리아', '호주']
    years = list(range(2018, 2025))
    
    # 논문 데이터
    paper_data = []
    for country in countries:
        for year in years:
            paper_data.append({
                'Year': year,
                'Country': country,
                'Total_Papers': np.random.randint(100, 1000),
                'H_Index': np.random.randint(10, 50),
                'Q1_Ratio': np.random.uniform(20, 80),
                'Citations': np.random.uniform(5, 25)
            })
    
    # 특허 데이터
    patent_data = []
    for country in countries:
        for year in years:
            patent_data.append({
                'Year': year,
                'Country': country,
                'Patent_Count': np.random.randint(50, 500),
                'Triadic_Ratio': np.random.uniform(0.1, 0.8),
                'Claims_Per_Patent': np.random.uniform(10, 30)
            })
    
    return pd.DataFrame(paper_data), pd.DataFrame(patent_data)

def safe_get_summary(papers_df, patents_df):
    """안전한 요약 통계"""
    try:
        paper_count = len(papers_df) if papers_df is not None else 0
        patent_count = len(patents_df) if patents_df is not None else 0
        
        # 연도 범위
        years = []
        if papers_df is not None and 'Year' in papers_df.columns:
            years.extend(papers_df['Year'].tolist())
        if patents_df is not None and 'Year' in patents_df.columns:
            years.extend(patents_df['Year'].tolist())
        
        year_range = (min(years), max(years)) if years else (2020, 2024)
        
        # 국가 수
        countries = set()
        if papers_df is not None and 'Country' in papers_df.columns:
            countries.update(papers_df['Country'].unique())
        if patents_df is not None and 'Country' in patents_df.columns:
            countries.update(patents_df['Country'].unique())
        
        return {
            'paper_count': paper_count,
            'patent_count': patent_count,
            'total_count': paper_count + patent_count,
            'year_range': year_range,
            'country_count': len(countries)
        }
    except Exception as e:
        st.error(f"요약 통계 생성 중 오류: {e}")
        return {
            'paper_count': 0,
            'patent_count': 0,
            'total_count': 0,
            'year_range': (2020, 2024),
            'country_count': 0
        }

def render_basic_metrics(summary):
    """기본 메트릭 표시"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 논문 수", f"{summary['paper_count']:,}")
    with col2:
        st.metric("⚖️ 특허 수", f"{summary['patent_count']:,}")
    with col3:
        st.metric("📅 분석 기간", f"{summary['year_range'][0]}-{summary['year_range'][1]}")
    with col4:
        st.metric("🌍 국가 수", f"{summary['country_count']}")

def render_basic_charts(papers_df, patents_df):
    """기본 차트 표시"""
    col1, col2 = st.columns(2)
    
    with col1:
        if papers_df is not None and not papers_df.empty:
            # 연도별 논문 수
            yearly_papers = papers_df.groupby('Year')['Total_Papers'].sum().reset_index()
            fig = px.line(yearly_papers, x='Year', y='Total_Papers', 
                         title='연도별 논문 수 추이', markers=True)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if patents_df is not None and not patents_df.empty:
            # 연도별 특허 수
            yearly_patents = patents_df.groupby('Year')['Patent_Count'].sum().reset_index()
            fig = px.line(yearly_patents, x='Year', y='Patent_Count', 
                         title='연도별 특허 수 추이', markers=True)
            st.plotly_chart(fig, use_container_width=True)

def render_country_analysis(papers_df, patents_df):
    """국가별 분석"""
    col1, col2 = st.columns(2)
    
    with col1:
        if papers_df is not None and not papers_df.empty:
            # 국가별 논문 수
            country_papers = papers_df.groupby('Country')['Total_Papers'].sum().nlargest(10)
            fig = px.bar(x=country_papers.index, y=country_papers.values,
                        title='상위 10개국 논문 수')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if patents_df is not None and not patents_df.empty:
            # 국가별 특허 수
            country_patents = patents_df.groupby('Country')['Patent_Count'].sum().nlargest(10)
            fig = px.bar(x=country_patents.index, y=country_patents.values,
                        title='상위 10개국 특허 수')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

def main():
    # 제목
    st.title("📈 기술수준조사 대시보드 (Simple Version)")
    st.caption("기본 기능 테스트용 간단 버전")
    st.markdown("---")
    
    # 데이터 생성
    with st.spinner("샘플 데이터 생성 중..."):
        papers_df, patents_df = create_sample_data()
    
    st.success("✅ 데이터 로드 완료!")
    
    # 사이드바 필터
    st.sidebar.title("🔧 필터 설정")
    
    # 연도 필터
    year_range = st.sidebar.slider(
        "연도 범위",
        min_value=2018,
        max_value=2024,
        value=(2020, 2024)
    )
    
    # 국가 필터
    available_countries = papers_df['Country'].unique().tolist()
    selected_countries = st.sidebar.multiselect(
        "국가 선택",
        options=available_countries,
        default=available_countries[:5]
    )
    
    # 데이터 필터링
    if selected_countries:
        papers_filtered = papers_df[
            (papers_df['Country'].isin(selected_countries)) &
            (papers_df['Year'] >= year_range[0]) &
            (papers_df['Year'] <= year_range[1])
        ]
        patents_filtered = patents_df[
            (patents_df['Country'].isin(selected_countries)) &
            (patents_df['Year'] >= year_range[0]) &
            (patents_df['Year'] <= year_range[1])
        ]
    else:
        papers_filtered = papers_df[
            (papers_df['Year'] >= year_range[0]) &
            (papers_df['Year'] <= year_range[1])
        ]
        patents_filtered = patents_df[
            (patents_df['Year'] >= year_range[0]) &
            (patents_df['Year'] <= year_range[1])
        ]
    
    # 요약 통계
    summary = safe_get_summary(papers_filtered, patents_filtered)
    
    # 메트릭 표시
    render_basic_metrics(summary)
    st.markdown("---")
    
    # 기본 차트
    st.subheader("📈 시계열 분석")
    render_basic_charts(papers_filtered, patents_filtered)
    st.markdown("---")
    
    # 국가별 분석
    st.subheader("🌍 국가별 분석")
    render_country_analysis(papers_filtered, patents_filtered)
    st.markdown("---")
    
    # 데이터 테이블
    tab1, tab2 = st.tabs(["📄 논문 데이터", "⚖️ 특허 데이터"])
    
    with tab1:
        st.subheader("논문 데이터 (상위 100행)")
        st.dataframe(papers_filtered.head(100), use_container_width=True)
    
    with tab2:
        st.subheader("특허 데이터 (상위 100행)")
        st.dataframe(patents_filtered.head(100), use_container_width=True)
    
    # 사이드바 정보
    st.sidebar.markdown("---")
    st.sidebar.success(f"""
    **현재 데이터:**
    - 논문: {len(papers_filtered):,}건
    - 특허: {len(patents_filtered):,}건
    - 선택 국가: {len(selected_countries)}개
    """)

if __name__ == "__main__":
    main()