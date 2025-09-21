"""
기술수준조사 서지분석 대시보드 - 4개 모듈 구조
main.py
"""

import streamlit as st
import sys
import os
import warnings
import pandas as pd
warnings.filterwarnings('ignore')

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 페이지 설정
st.set_page_config(
    page_title="기술수준조사 서지분석 대시보드",
    page_icon="📈",
    layout="wide"
)

# 컴포넌트 import
try:
    from utils.data_loader import load_data, filter_data
    from components.metrics import (
        render_summary_metrics, 
        render_yearly_metrics, 
        render_top_countries_metrics,
        render_comparison_gauge,
        render_data_quality_metrics
    )
    from components.trends import (
        render_basic_timeseries,
        render_combined_timeseries,
        render_cumulative_trends,
        render_growth_rate_analysis,
        render_trend_comparison,
        render_forecast_trend
    )
    from components.country import (
        render_country_trends,
        render_country_detail_analysis,
        render_country_comparison_matrix,
        render_country_ranking,
        render_country_growth_analysis,
        render_regional_analysis
    )
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    st.error(f"모듈 import 오류: {e}")
    st.info("다음 파일들이 올바른 위치에 있는지 확인하세요:")
    st.code("""
    utils/data_loader.py
    components/metrics.py
    components/trends.py
    components/country.py
    """)
    IMPORTS_SUCCESSFUL = False

def create_sample_data():
    """샘플 데이터 생성 (테스트용)"""
    import numpy as np
    
    # 샘플 논문 데이터
    countries = ['미국', '중국', '독일', '일본', '한국', '영국', '프랑스', '캐나다', '이탈리아', '호주']
    years = list(range(2018, 2025))
    
    paper_data = []
    for country in countries:
        for year in years:
            paper_data.append({
                'Year': year,
                'Country': country,
                'Total_Papers': np.random.randint(100, 1000),
                'H_Index': np.random.randint(10, 50),
                'Q1_Ratio(%)': np.random.uniform(20, 80),
                'Collaboration_Ratio(%)': np.random.uniform(30, 70),
                'Avg_Citations': np.random.uniform(5, 25),
                'Avg_mrnif': np.random.uniform(0.8, 2.5)
            })
    
    # 샘플 특허 데이터
    patent_data = []
    for country in countries:
        for year in years:
            patent_data.append({
                'Year': year,
                'Country': country,
                'patent_count': np.random.randint(50, 500),
                'triadic_ratio': np.random.uniform(0.1, 0.8),
                'claims_per_patent': np.random.uniform(10, 30),
                'foreign_filing_intensity': np.random.uniform(0.2, 0.9),
                'h_index': np.random.randint(5, 25)
            })
    
    papers_df = pd.DataFrame(paper_data)
    patents_df = pd.DataFrame(patent_data)
    
    return papers_df, patents_df

def get_summary_stats(papers_df, patents_df):
    """요약 통계 생성"""
    paper_count = len(papers_df) if papers_df is not None and not papers_df.empty else 0
    patent_count = len(patents_df) if patents_df is not None and not patents_df.empty else 0
    
    year_range = None
    country_count = 0
    
    # 연도 범위 계산
    all_years = []
    for df in [papers_df, patents_df]:
        if df is not None and not df.empty and 'Year' in df.columns:
            try:
                years = pd.to_numeric(df['Year'], errors='coerce').dropna()
                if not years.empty:
                    all_years.extend(years.tolist())
            except Exception:
                continue
    
    if all_years:
        try:
            year_range = (int(min(all_years)), int(max(all_years)))
        except (ValueError, TypeError):
            year_range = None
    
    # 국가 수 계산
    all_countries = set()
    for df in [papers_df, patents_df]:
        if df is not None and not df.empty and 'Country' in df.columns:
            try:
                countries = df['Country'].dropna().unique()
                all_countries.update(countries)
            except Exception:
                continue
    
    country_count = len(all_countries)
    
    return {
        'paper_count': paper_count,
        'patent_count': patent_count,
        'total_count': paper_count + patent_count,
        'year_range': year_range,
        'country_count': country_count
    }

def render_sidebar_controls(papers_df, patents_df):
    """사이드바 컨트롤 렌더링"""
    st.sidebar.title("⚙️ 대시보드 설정")
    
    # 1. 데이터 소스 선택
    st.sidebar.subheader("📊 데이터 소스")
    data_source = st.sidebar.selectbox(
        "데이터 소스 선택",
        ["엑셀 파일", "샘플 데이터"],
        index=1,
        help="분석할 데이터 소스를 선택하세요"
    )
    
    # 2. 연도 범위 설정
    year_min, year_max = 2020, 2024  # 기본값 설정
    
    try:
        all_years = []
        
        # 논문 데이터에서 연도 추출
        if papers_df is not None and not papers_df.empty and 'Year' in papers_df.columns:
            paper_years = pd.to_numeric(papers_df['Year'], errors='coerce').dropna()
            if not paper_years.empty:
                all_years.extend(paper_years.tolist())
        
        # 특허 데이터에서 연도 추출
        if patents_df is not None and not patents_df.empty and 'Year' in patents_df.columns:
            patent_years = pd.to_numeric(patents_df['Year'], errors='coerce').dropna()
            if not patent_years.empty:
                all_years.extend(patent_years.tolist())
        
        # 연도 범위 계산
        if all_years:
            year_min = int(min(all_years))
            year_max = int(max(all_years))
        
    except Exception as e:
        # 에러 발생 시 기본값 사용
        st.sidebar.warning(f"연도 범위 계산 중 오류: {e}")
        year_min, year_max = 2020, 2024
    
    st.sidebar.subheader("📅 연도 필터")
    year_range = st.sidebar.slider(
        "분석 연도 범위",
        min_value=year_min,
        max_value=year_max,
        value=(year_min, year_max),
        help="분석할 연도 범위를 선택하세요"
    )
    
    # 3. 국가 선택
    available_countries = []
    
    try:
        # 논문 데이터에서 국가 추출
        if papers_df is not None and not papers_df.empty and 'Country' in papers_df.columns:
            paper_countries = papers_df['Country'].dropna().unique().tolist()
            available_countries.extend(paper_countries)
        
        # 특허 데이터에서 국가 추출
        if patents_df is not None and not patents_df.empty and 'Country' in patents_df.columns:
            patent_countries = patents_df['Country'].dropna().unique().tolist()
            available_countries.extend(patent_countries)
        
        # 중복 제거 및 정렬
        available_countries = sorted(list(set(available_countries)))
        
    except Exception as e:
        st.sidebar.warning(f"국가 목록 생성 중 오류: {e}")
        available_countries = []
    
    if available_countries:
        st.sidebar.subheader("🌍 국가 필터")
        
        # 전체 선택/해제 버튼
        col1, col2 = st.sidebar.columns(2)
        with col1:
            select_all = st.button("전체 선택", key="select_all")
        with col2:
            select_none = st.button("전체 해제", key="select_none")
        
        # 기본 선택 국가 (상위 10개)
        default_countries = available_countries[:10] if len(available_countries) >= 10 else available_countries
        
        if select_all:
            selected_countries = available_countries
        elif select_none:
            selected_countries = []
        else:
            selected_countries = st.sidebar.multiselect(
                "분석 대상 국가",
                options=available_countries,
                default=default_countries,
                help="분석할 국가를 선택하세요 (최대 20개 권장)"
            )
    else:
        selected_countries = []
        st.sidebar.info("선택 가능한 국가가 없습니다.")
    
    # 4. 분석 모드 선택
    st.sidebar.subheader("🔍 분석 모드")
    analysis_mode = st.sidebar.selectbox(
        "분석 유형",
        ["📊 전체 대시보드", "📈 트렌드 분석", "🌍 국가별 분석", "📋 상세 분석"],
        index=0,
        help="원하는 분석 유형을 선택하세요"
    )
    
    return {
        'data_source': data_source,
        'year_range': year_range,
        'selected_countries': selected_countries,
        'analysis_mode': analysis_mode
    }

def filter_data_by_controls(papers_df, patents_df, controls):
    """컨트롤에 따라 데이터 필터링"""
    filtered_papers = None
    filtered_patents = None
    
    # 논문 데이터 필터링
    try:
        if papers_df is not None and not papers_df.empty:
            filtered_papers = papers_df.copy()
            
            # 연도 필터링
            if controls['year_range'] and 'Year' in filtered_papers.columns:
                years = pd.to_numeric(filtered_papers['Year'], errors='coerce')
                mask = (years >= controls['year_range'][0]) & (years <= controls['year_range'][1])
                mask = mask.fillna(False)  # NaN 값 처리
                filtered_papers = filtered_papers[mask]
            
            # 국가 필터링
            if controls['selected_countries'] and 'Country' in filtered_papers.columns:
                filtered_papers = filtered_papers[filtered_papers['Country'].isin(controls['selected_countries'])]
                
    except Exception as e:
        st.warning(f"논문 데이터 필터링 중 오류: {e}")
        filtered_papers = papers_df.copy() if papers_df is not None else None
    
    # 특허 데이터 필터링
    try:
        if patents_df is not None and not patents_df.empty:
            filtered_patents = patents_df.copy()
            
            # 연도 필터링
            if controls['year_range'] and 'Year' in filtered_patents.columns:
                years = pd.to_numeric(filtered_patents['Year'], errors='coerce')
                mask = (years >= controls['year_range'][0]) & (years <= controls['year_range'][1])
                mask = mask.fillna(False)  # NaN 값 처리
                filtered_patents = filtered_patents[mask]
            
            # 국가 필터링
            if controls['selected_countries'] and 'Country' in filtered_patents.columns:
                filtered_patents = filtered_patents[filtered_patents['Country'].isin(controls['selected_countries'])]
                
    except Exception as e:
        st.warning(f"특허 데이터 필터링 중 오류: {e}")
        filtered_patents = patents_df.copy() if patents_df is not None else None
    
    return filtered_papers, filtered_patents

def main():
    # 제목
    st.title("📈 기술수준조사 시계열 대시보드")
    st.caption("논문 및 특허 데이터의 시계열 분석 전문 대시보드")
    st.markdown("---")
    
    # 데이터 로드
    try:
        if IMPORTS_SUCCESSFUL:
            # 실제 데이터 로드 시도
            papers_df, patents_df = load_data()
        else:
            papers_df, patents_df = None, None
    except Exception as e:
        st.warning(f"데이터 로드 중 오류: {e}")
        papers_df, patents_df = None, None
    
    # 데이터가 없거나 비어있으면 샘플 데이터 사용
    if (papers_df is None or papers_df.empty) and (patents_df is None or patents_df.empty):
        st.info("📋 실제 데이터를 찾을 수 없어 샘플 데이터를 사용합니다.")
        papers_df, patents_df = create_sample_data()
    
    # 사이드바 컨트롤
    controls = render_sidebar_controls(papers_df, patents_df)
    
    # 데이터 필터링
    filtered_papers, filtered_patents = filter_data_by_controls(papers_df, patents_df, controls)
    
    # 필터링 후 요약 정보
    summary = get_summary_stats(filtered_papers, filtered_patents)
    
    # 메인 콘텐츠 렌더링
    analysis_mode = controls['analysis_mode']
    
    if analysis_mode == "📊 전체 대시보드":
        render_full_dashboard(filtered_papers, filtered_patents, summary, controls)
        
    elif analysis_mode == "📈 트렌드 분석":
        render_trend_dashboard(filtered_papers, filtered_patents)
        
    elif analysis_mode == "🌍 국가별 분석":
        render_country_dashboard(filtered_papers, filtered_patents, controls)
        
    else:  # 상세 분석
        render_detailed_dashboard(filtered_papers, filtered_patents, summary)
    
    # 사이드바 요약 정보
    render_sidebar_summary(summary, controls)

def render_full_dashboard(papers_df, patents_df, summary, controls):
    """전체 대시보드 렌더링"""
    if IMPORTS_SUCCESSFUL:
        # 1. 요약 메트릭
        render_summary_metrics(summary)
        st.markdown("---")
        
        # 2. 연도별 메트릭
        render_yearly_metrics(papers_df, patents_df)
        st.markdown("---")
        
        # 3. 기본 시계열
        render_basic_timeseries(papers_df, patents_df)
        st.markdown("---")
        
        # 4. 상위 국가 정보
        render_top_countries_metrics(papers_df, top_n=5)
        st.markdown("---")
        
        # 5. 비교 게이지
        render_comparison_gauge(papers_df, patents_df)
    else:
        st.error("컴포넌트를 로드할 수 없어 대시보드를 표시할 수 없습니다.")

def render_trend_dashboard(papers_df, patents_df):
    """트렌드 분석 대시보드"""
    st.header("📈 시계열 트렌드 분석")
    
    if IMPORTS_SUCCESSFUL:
        # 트렌드 분석 옵션
        trend_option = st.selectbox(
            "트렌드 분석 유형",
            ["기본 시계열", "통합 비교", "누적 추이", "성장률 분석", "상관관계", "예측 분석"],
            index=0
        )
        
        if trend_option == "기본 시계열":
            render_basic_timeseries(papers_df, patents_df)
        elif trend_option == "통합 비교":
            render_combined_timeseries(papers_df, patents_df)
        elif trend_option == "누적 추이":
            render_cumulative_trends(papers_df, patents_df)
        elif trend_option == "성장률 분석":
            render_growth_rate_analysis(papers_df, patents_df)
        elif trend_option == "상관관계":
            render_trend_comparison(papers_df, patents_df)
        else:  # 예측 분석
            render_forecast_trend(papers_df, patents_df)
    else:
        st.error("트렌드 분석 컴포넌트를 로드할 수 없습니다.")

def render_country_dashboard(papers_df, patents_df, controls):
    """국가별 분석 대시보드"""
    st.header("🌍 국가별 비교 분석")
    
    if IMPORTS_SUCCESSFUL:
        # 국가별 분석 옵션
        country_option = st.selectbox(
            "국가별 분석 유형",
            ["국가별 트렌드", "상세 분석", "포지셔닝 매트릭스", "순위 분석", "성장률 분석", "지역별 분석"],
            index=0
        )
        
        if country_option == "국가별 트렌드":
            render_country_trends(papers_df, patents_df, top_n=10)
            
        elif country_option == "상세 분석":
            if controls['selected_countries']:
                render_country_detail_analysis(papers_df, controls['selected_countries'])
            else:
                st.warning("사이드바에서 분석할 국가를 선택해주세요.")
                
        elif country_option == "포지셔닝 매트릭스":
            render_country_comparison_matrix(papers_df, patents_df)
            
        elif country_option == "순위 분석":
            render_country_ranking(papers_df, patents_df)
            
        elif country_option == "성장률 분석":
            render_country_growth_analysis(papers_df)
            
        else:  # 지역별 분석
            render_regional_analysis(papers_df)
    else:
        st.error("국가별 분석 컴포넌트를 로드할 수 없습니다.")

def render_detailed_dashboard(papers_df, patents_df, summary):
    """상세 분석 대시보드"""
    st.header("📋 상세 분석")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 데이터 품질", "📄 논문 상세", "⚖️ 특허 상세", "📈 종합 분석"])
    
    with tab1:
        if IMPORTS_SUCCESSFUL:
            render_data_quality_metrics(papers_df, patents_df)
        else:
            st.info("데이터 품질 메트릭 컴포넌트를 사용할 수 없습니다.")
    
    with tab2:
        if papers_df is not None and not papers_df.empty:
            st.subheader("논문 데이터 상세")
            st.dataframe(papers_df.head(100), use_container_width=True)
            
            # 기본 통계
            st.subheader("기본 통계")
            numeric_cols = papers_df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                st.dataframe(papers_df[numeric_cols].describe(), use_container_width=True)
        else:
            st.info("논문 데이터가 없습니다.")
    
    with tab3:
        if patents_df is not None and not patents_df.empty:
            st.subheader("특허 데이터 상세")
            st.dataframe(patents_df.head(100), use_container_width=True)
            
            # 기본 통계
            st.subheader("기본 통계")
            numeric_cols = patents_df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                st.dataframe(patents_df[numeric_cols].describe(), use_container_width=True)
        else:
            st.info("특허 데이터가 없습니다.")
    
    with tab4:
        st.subheader("종합 분석 요약")
        
        # 요약 정보 표시
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**데이터 현황:**")
            st.write(f"- 논문 레코드: {summary['paper_count']:,}개")
            st.write(f"- 특허 레코드: {summary['patent_count']:,}개")
            if summary['year_range']:
                st.write(f"- 분석 기간: {summary['year_range'][0]}-{summary['year_range'][1]}년")
            st.write(f"- 분석 국가: {summary['country_count']}개")
        
        with col2:
            st.write("**주요 인사이트:**")
            
            # 간단한 인사이트 생성
            if summary['paper_count'] > summary['patent_count']:
                st.write("📄 논문 데이터가 특허 데이터보다 많습니다.")
            elif summary['patent_count'] > summary['paper_count']:
                st.write("⚖️ 특허 데이터가 논문 데이터보다 많습니다.")
            else:
                st.write("📊 논문과 특허 데이터가 균형적입니다.")
            
            if summary['year_range'] and summary['year_range'][1] - summary['year_range'][0] >= 5:
                st.write("📈 장기간 트렌드 분석이 가능합니다.")
            
            if summary['country_count'] >= 10:
                st.write("🌍 다양한 국가 간 비교 분석이 가능합니다.")

def render_sidebar_summary(summary, controls):
    """사이드바 요약 정보"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 현재 분석 데이터")
    
    st.sidebar.info(f"""
    **필터링된 데이터:**
    - 논문: {summary['paper_count']:,}건
    - 특허: {summary['patent_count']:,}건
    - 총계: {summary['total_count']:,}건
    - 선택 국가: {len(controls['selected_countries'])}개
    """)
    
    if summary['year_range']:
        st.sidebar.success(f"📅 분석 기간: {summary['year_range'][0]}-{summary['year_range'][1]}년")

if __name__ == "__main__":
    main()