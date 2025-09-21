"""
기술수준조사 서지분석 대시보드 - 4개 모듈 구조
main.py
"""

import streamlit as st
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정을 가장 먼저
st.set_page_config(
    page_title="기술수준조사 시계열 대시보드",
    page_icon="📈",
    layout="wide"
)

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 컴포넌트 import
try:
    from utils.data_loader import DataLoader, get_available_countries, get_available_years
    from components.metrics import (
        render_summary_metrics, 
        render_yearly_metrics, 
        render_top_countries_metrics,
        render_comparison_gauge,
        render_data_quality_metrics
    )
    from components.trends import (
        render_yearly_trends_comprehensive,
        render_growth_rate_analysis,
        render_correlation_analysis,
        render_seasonal_analysis,
        render_forecasting
    )
    from components.country import (
        render_country_trends,
        render_country_detail_analysis,
        render_country_comparison_matrix,
        render_country_ranking,
        render_country_growth_analysis,
        render_regional_analysis
    )
except ImportError as e:
    st.error(f"모듈 import 오류: {e}")
    st.info("다음 파일들이 올바른 위치에 있는지 확인하세요:")
    st.code("""
    utils/data_loader.py
    components/metrics.py
    components/trends.py
    components/country.py
    """)
    st.stop()

def render_sidebar_controls(papers_df, patents_df):
    """사이드바 컨트롤 렌더링"""
    st.sidebar.title("⚙️ 대시보드 설정")
    
    # 1. 샘플 크기 설정
    st.sidebar.subheader("📊 데이터 설정")
    sample_size = st.sidebar.selectbox(
        "데이터 샘플 크기",
        [1000, 5000, 10000, "전체"],
        index=1,
        help="분석할 데이터 크기를 선택하세요"
    )
    
    # 2. 연도 범위 설정
    if not papers_df.empty or not patents_df.empty:
        year_min, year_max = get_available_years(papers_df, patents_df)
        
        st.sidebar.subheader("📅 연도 필터")
        year_range = st.sidebar.slider(
            "분석 연도 범위",
            min_value=year_min,
            max_value=year_max,
            value=(year_min, year_max),
            help="분석할 연도 범위를 선택하세요"
        )
    else:
        year_range = (2020, 2024)
    
    # 3. 국가 선택
    available_countries = get_available_countries(papers_df, patents_df)
    
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
    
    # 4. 분석 모드 선택
    st.sidebar.subheader("🔍 분석 모드")
    analysis_mode = st.sidebar.selectbox(
        "분석 유형",
        ["📊 전체 대시보드", "📈 트렌드 분석", "🌍 국가별 분석", "📋 상세 분석"],
        index=0,
        help="원하는 분석 유형을 선택하세요"
    )
    
    return {
        'sample_size': sample_size,
        'year_range': year_range,
        'selected_countries': selected_countries,
        'analysis_mode': analysis_mode
    }

def render_full_dashboard(papers_df, patents_df, summary, controls):
    """전체 대시보드 렌더링"""
    # 1. 요약 메트릭
    render_summary_metrics(summary)
    st.markdown("---")
    
    # 2. 연도별 메트릭
    render_yearly_metrics(papers_df, patents_df)
    st.markdown("---")
    
    # 3. 종합 시계열 트렌드
    render_yearly_trends_comprehensive(papers_df, patents_df)
    st.markdown("---")
    
    # 4. 상위 국가 정보
    render_top_countries_metrics(papers_df, top_n=5)
    st.markdown("---")
    
    # 5. 비교 게이지
    render_comparison_gauge(papers_df, patents_df)

def render_trend_dashboard(papers_df, patents_df):
    """트렌드 분석 대시보드"""
    st.header("📈 시계열 트렌드 분석")
    
    # 트렌드 분석 옵션
    trend_option = st.selectbox(
        "트렌드 분석 유형",
        ["종합 트렌드", "성장률 분석", "상관관계 분석", "패턴 분석", "예측 분석"],
        index=0
    )
    
    if trend_option == "종합 트렌드":
        render_yearly_trends_comprehensive(papers_df, patents_df)
    elif trend_option == "성장률 분석":
        render_growth_rate_analysis(papers_df, patents_df)
    elif trend_option == "상관관계 분석":
        render_correlation_analysis(papers_df, patents_df)
    elif trend_option == "패턴 분석":
        render_seasonal_analysis(papers_df, patents_df)
    else:  # 예측 분석
        render_forecasting(papers_df, patents_df)

def render_country_dashboard(papers_df, patents_df, controls):
    """국가별 분석 대시보드"""
    st.header("🌍 국가별 비교 분석")
    
    # 국가별 분석 옵션
    country_option = st.selectbox(
        "국가별 분석 유형",
        ["국가별 트렌드", "상세 분석", "포지셔닝 매트릭스", "순위 분석", "성장률 분석", "지역별 분석"],
        index=0
    )
    
    if country_option == "국가별 트렌드":
        top_countries = render_country_trends(papers_df, patents_df, top_n=10)
        
        # 특정 국가 선택 분석
        if controls['selected_countries']:
            render_country_detail_analysis(papers_df, controls['selected_countries'])
            
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

def render_detailed_dashboard(papers_df, patents_df, summary):
    """상세 분석 대시보드"""
    st.header("📋 상세 분석")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 데이터 품질", "📄 논문 상세", "⚖️ 특허 상세", "📈 종합 분석"])
    
    with tab1:
        render_data_quality_metrics(papers_df, patents_df)
    
    with tab2:
        if not papers_df.empty:
            st.subheader("논문 데이터 상세")
            
            # 주요 컬럼 선택
            display_cols = ['Year', 'Country']
            optional_cols = ['Total_Papers', 'H_Index', 'Q1_Ratio(%)', 'Collaboration_Ratio(%)']
            
            for col in optional_cols:
                if col in papers_df.columns:
                    display_cols.append(col)
            
            # 데이터 표시 (최대 1000행)
            display_df = papers_df[display_cols].head(1000)
            st.dataframe(display_df, use_container_width=True)
            
            # 기본 통계
            st.subheader("기본 통계")
            numeric_cols = display_df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                st.dataframe(display_df[numeric_cols].describe(), use_container_width=True)
        else:
            st.info("논문 데이터가 없습니다.")
    
    with tab3:
        if not patents_df.empty:
            st.subheader("특허 데이터 상세")
            
            # 주요 컬럼 선택
            display_cols = ['Year', 'Country']
            optional_cols = ['patent_count', 'triadic_ratio', 'claims_per_patent']
            
            for col in optional_cols:
                if col in patents_df.columns:
                    display_cols.append(col)
            
            # 사용 가능한 컬럼만 선택
            available_cols = [col for col in display_cols if col in patents_df.columns]
            
            if available_cols:
                display_df = patents_df[available_cols].head(1000)
                st.dataframe(display_df, use_container_width=True)
                
                # 기본 통계
                st.subheader("기본 통계")
                numeric_cols = display_df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    st.dataframe(display_df[numeric_cols].describe(), use_container_width=True)
            else:
                st.dataframe(patents_df.head(1000), use_container_width=True)
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

def main():
    # 제목
    st.title("📈 기술수준조사 시계열 대시보드")
    st.caption("논문 및 특허 데이터의 시계열 분석 전문 대시보드")
    st.markdown("---")
    
    # 데이터 로더 초기화
    loader = DataLoader()
    
    # 초기 설정을 위한 임시 사이드바
    st.sidebar.title("🔧 로딩 설정")
    temp_sample_size = st.sidebar.selectbox(
        "초기 로딩 크기",
        [1000, 5000, 10000, "전체"],
        index=1,
        help="처음 로딩할 데이터 크기"
    )
    
    # 데이터 로드
    with st.spinner("데이터 로딩 중..."):
        df = loader.load_data(temp_sample_size)
    
    if df.empty:
        st.error("❌ 데이터를 로드할 수 없습니다.")
        st.info("💡 '_통합평가자료.xlsx' 파일이 올바른 위치에 있는지 확인하세요.")
        return
    
    # 데이터 전처리
    papers_df, patents_df = loader.preprocess_data(df)
    summary = loader.get_summary_stats(papers_df, patents_df)
    
    # 사이드바 컨트롤
    controls = render_sidebar_controls(papers_df, patents_df)
    
    # 데이터 필터링
    if controls['year_range']:
        papers_df, patents_df = loader.filter_data_by_years(
            papers_df, patents_df, controls['year_range']
        )
    
    if controls['selected_countries']:
        papers_df, patents_df = loader.filter_data_by_countries(
            papers_df, patents_df, controls['selected_countries']
        )
    
    # 필터링 후 요약 정보 업데이트
    filtered_summary = loader.get_summary_stats(papers_df, patents_df)
    
    # 메인 콘텐츠 렌더링
    analysis_mode = controls['analysis_mode']
    
    if analysis_mode == "📊 전체 대시보드":
        render_full_dashboard(papers_df, patents_df, filtered_summary, controls)
        
    elif analysis_mode == "📈 트렌드 분석":
        render_trend_dashboard(papers_df, patents_df)
        
    elif analysis_mode == "🌍 국가별 분석":
        render_country_dashboard(papers_df, patents_df, controls)
        
    else:  # 상세 분석
        render_detailed_dashboard(papers_df, patents_df, filtered_summary)
    
    # 사이드바 요약 정보
    render_sidebar_summary(filtered_summary, controls)

if __name__ == "__main__":
    main()