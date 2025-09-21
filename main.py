"""
Ultra Simple 버전 - 에러 방지 극대화
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="기술수준조사 대시보드",
    page_icon="📈",
    layout="wide"
)

def create_safe_sample_data():
    """완전히 안전한 샘플 데이터 생성"""
    try:
        countries = ['미국', '중국', '독일', '일본', '한국', '영국', '프랑스', '캐나다', '이탈리아', '호주']
        years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
        
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
                    'Claims': np.random.uniform(10, 30)
                })
        
        papers_df = pd.DataFrame(paper_data)
        patents_df = pd.DataFrame(patent_data)
        
        return papers_df, patents_df
        
    except Exception as e:
        st.error(f"샘플 데이터 생성 오류: {e}")
        # 최소한의 데이터라도 반환
        return pd.DataFrame({'Year': [2024], 'Country': ['한국'], 'Total_Papers': [100]}), pd.DataFrame({'Year': [2024], 'Country': ['한국'], 'Patent_Count': [50]})

def safe_render_metrics(papers_df, patents_df):
    """안전한 메트릭 렌더링"""
    try:
        st.subheader("📊 기본 통계")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            paper_count = len(papers_df) if papers_df is not None else 0
            st.metric("📄 논문 수", f"{paper_count:,}")
        
        with col2:
            patent_count = len(patents_df) if patents_df is not None else 0
            st.metric("⚖️ 특허 수", f"{patent_count:,}")
        
        with col3:
            if papers_df is not None and 'Year' in papers_df.columns:
                years = papers_df['Year'].dropna()
                if not years.empty:
                    year_range = f"{int(years.min())}-{int(years.max())}"
                    st.metric("📅 연도 범위", year_range)
                else:
                    st.metric("📅 연도 범위", "N/A")
            else:
                st.metric("📅 연도 범위", "N/A")
        
        with col4:
            if papers_df is not None and 'Country' in papers_df.columns:
                countries = papers_df['Country'].dropna().nunique()
                st.metric("🌍 국가 수", f"{countries}")
            else:
                st.metric("🌍 국가 수", "0")
    
    except Exception as e:
        st.error(f"메트릭 렌더링 오류: {e}")

def safe_render_basic_charts(papers_df, patents_df):
    """안전한 기본 차트 렌더링"""
    try:
        st.subheader("📈 기본 차트")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if papers_df is not None and 'Year' in papers_df.columns:
                try:
                    # 연도별 논문 수
                    if 'Total_Papers' in papers_df.columns:
                        yearly_papers = papers_df.groupby('Year')['Total_Papers'].sum().reset_index()
                    else:
                        yearly_papers = papers_df.groupby('Year').size().reset_index(name='Count')
                        yearly_papers.columns = ['Year', 'Total_Papers']
                    
                    fig = px.line(yearly_papers, x='Year', y='Total_Papers', 
                                 title='연도별 논문 수', markers=True)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"논문 차트 오류: {e}")
        
        with col2:
            if patents_df is not None and 'Year' in patents_df.columns:
                try:
                    # 연도별 특허 수
                    if 'Patent_Count' in patents_df.columns:
                        yearly_patents = patents_df.groupby('Year')['Patent_Count'].sum().reset_index()
                    else:
                        yearly_patents = patents_df.groupby('Year').size().reset_index(name='Count')
                        yearly_patents.columns = ['Year', 'Patent_Count']
                    
                    fig = px.line(yearly_patents, x='Year', y='Patent_Count', 
                                 title='연도별 특허 수', markers=True,
                                 color_discrete_sequence=['#FF6B6B'])
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"특허 차트 오류: {e}")
    
    except Exception as e:
        st.error(f"차트 렌더링 오류: {e}")

def safe_render_country_analysis(papers_df, patents_df):
    """안전한 국가별 분석"""
    try:
        st.subheader("🌍 국가별 분석")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if papers_df is not None and 'Country' in papers_df.columns:
                try:
                    # 국가별 논문 수
                    if 'Total_Papers' in papers_df.columns:
                        country_papers = papers_df.groupby('Country')['Total_Papers'].sum().nlargest(10)
                    else:
                        country_papers = papers_df['Country'].value_counts().head(10)
                    
                    fig = px.bar(x=country_papers.index, y=country_papers.values,
                                title='상위 10개국 논문 수')
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"국가별 논문 차트 오류: {e}")
        
        with col2:
            if patents_df is not None and 'Country' in patents_df.columns:
                try:
                    # 국가별 특허 수
                    if 'Patent_Count' in patents_df.columns:
                        country_patents = patents_df.groupby('Country')['Patent_Count'].sum().nlargest(10)
                    else:
                        country_patents = patents_df['Country'].value_counts().head(10)
                    
                    fig = px.bar(x=country_patents.index, y=country_patents.values,
                                title='상위 10개국 특허 수',
                                color_discrete_sequence=['#FF6B6B'])
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"국가별 특허 차트 오류: {e}")
    
    except Exception as e:
        st.error(f"국가별 분석 오류: {e}")

def safe_render_sidebar(papers_df, patents_df):
    """완전히 안전한 사이드바"""
    try:
        st.sidebar.title("🔧 설정")
        
        # 연도 범위 - 안전한 기본값 사용
        year_min, year_max = 2018, 2024
        
        try:
            if papers_df is not None and 'Year' in papers_df.columns:
                years = pd.to_numeric(papers_df['Year'], errors='coerce').dropna()
                if not years.empty:
                    year_min = max(int(years.min()), 2010)  # 최소값 제한
                    year_max = min(int(years.max()), 2030)  # 최대값 제한
        except:
            pass  # 기본값 유지
        
        year_range = st.sidebar.slider(
            "연도 범위",
            min_value=year_min,
            max_value=year_max,
            value=(year_min, year_max)
        )
        
        # 국가 선택 - 안전한 방식
        countries = []
        try:
            if papers_df is not None and 'Country' in papers_df.columns:
                countries.extend(papers_df['Country'].dropna().unique().tolist())
            if patents_df is not None and 'Country' in patents_df.columns:
                countries.extend(patents_df['Country'].dropna().unique().tolist())
            countries = sorted(list(set(countries)))
        except:
            countries = ['한국', '미국', '중국', '일본', '독일']  # 기본 국가
        
        selected_countries = st.sidebar.multiselect(
            "국가 선택",
            options=countries,
            default=countries[:5] if len(countries) >= 5 else countries
        )
        
        return year_range, selected_countries
        
    except Exception as e:
        st.sidebar.error(f"사이드바 오류: {e}")
        return (2018, 2024), ['한국', '미국', '중국']

def safe_filter_data(papers_df, patents_df, year_range, selected_countries):
    """완전히 안전한 데이터 필터링"""
    filtered_papers = papers_df
    filtered_patents = patents_df
    
    try:
        # 논문 데이터 필터링
        if papers_df is not None and not papers_df.empty:
            filtered_papers = papers_df.copy()
            
            # 연도 필터
            if 'Year' in filtered_papers.columns:
                years = pd.to_numeric(filtered_papers['Year'], errors='coerce')
                mask = (years >= year_range[0]) & (years <= year_range[1])
                mask = mask.fillna(False)
                filtered_papers = filtered_papers[mask]
            
            # 국가 필터
            if selected_countries and 'Country' in filtered_papers.columns:
                filtered_papers = filtered_papers[filtered_papers['Country'].isin(selected_countries)]
    except Exception as e:
        st.warning(f"논문 데이터 필터링 오류: {e}")
    
    try:
        # 특허 데이터 필터링
        if patents_df is not None and not patents_df.empty:
            filtered_patents = patents_df.copy()
            
            # 연도 필터
            if 'Year' in filtered_patents.columns:
                years = pd.to_numeric(filtered_patents['Year'], errors='coerce')
                mask = (years >= year_range[0]) & (years <= year_range[1])
                mask = mask.fillna(False)
                filtered_patents = filtered_patents[mask]
            
            # 국가 필터
            if selected_countries and 'Country' in filtered_patents.columns:
                filtered_patents = filtered_patents[filtered_patents['Country'].isin(selected_countries)]
    except Exception as e:
        st.warning(f"특허 데이터 필터링 오류: {e}")
    
    return filtered_papers, filtered_patents

def main():
    # 제목
    st.title("📈 기술수준조사 대시보드")
    st.caption("Ultra Simple 버전 - 최대 안정성")
    st.markdown("---")
    
    # 데이터 생성
    try:
        with st.spinner("데이터 생성 중..."):
            papers_df, patents_df = create_safe_sample_data()
        
        st.success("✅ 데이터 로드 완료!")
        
        # 사이드바 설정
        year_range, selected_countries = safe_render_sidebar(papers_df, patents_df)
        
        # 데이터 필터링
        filtered_papers, filtered_patents = safe_filter_data(
            papers_df, patents_df, year_range, selected_countries
        )
        
        # 메트릭 표시
        safe_render_metrics(filtered_papers, filtered_patents)
        st.markdown("---")
        
        # 기본 차트
        safe_render_basic_charts(filtered_papers, filtered_patents)
        st.markdown("---")
        
        # 국가별 분석
        safe_render_country_analysis(filtered_papers, filtered_patents)
        st.markdown("---")
        
        # 데이터 테이블
        tab1, tab2 = st.tabs(["📄 논문 데이터", "⚖️ 특허 데이터"])
        
        with tab1:
            try:
                st.subheader("논문 데이터 (상위 100행)")
                if filtered_papers is not None and not filtered_papers.empty:
                    st.dataframe(filtered_papers.head(100), use_container_width=True)
                else:
                    st.info("표시할 논문 데이터가 없습니다.")
            except Exception as e:
                st.error(f"논문 테이블 오류: {e}")
        
        with tab2:
            try:
                st.subheader("특허 데이터 (상위 100행)")
                if filtered_patents is not None and not filtered_patents.empty:
                    st.dataframe(filtered_patents.head(100), use_container_width=True)
                else:
                    st.info("표시할 특허 데이터가 없습니다.")
            except Exception as e:
                st.error(f"특허 테이블 오류: {e}")
        
        # 사이드바 정보
        try:
            st.sidebar.markdown("---")
            st.sidebar.success(f"""
            **현재 데이터:**
            - 논문: {len(filtered_papers) if filtered_papers is not None else 0:,}건
            - 특허: {len(filtered_patents) if filtered_patents is not None else 0:,}건
            - 국가: {len(selected_countries)}개 선택
            """)
        except Exception as e:
            st.sidebar.error(f"정보 표시 오류: {e}")
        
    except Exception as e:
        st.error(f"애플리케이션 실행 중 치명적 오류: {e}")
        st.info("페이지를 새로고침해주세요.")

if __name__ == "__main__":
    main()