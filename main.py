"""
기술수준조사 서지분석 대시보드 - 컴포넌트 구조
main.py
"""

import streamlit as st
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 컴포넌트 import
from utils.data_loader import load_and_preprocess_data, get_available_filters
from components.metrics import (
    render_kpi_cards, 
    render_growth_metrics, 
    render_quality_metrics,
    render_top_performers
)
from components.trends import (
    render_yearly_trends_comprehensive,
    render_growth_rate_analysis,
    render_correlation_analysis,
    render_forecasting
)
from components.country import (
    render_country_comparison_dashboard,
    render_country_rankings,
    render_radar_comparison,
    render_competitive_positioning
)

import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="기술수준조사 서지분석 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def render_sidebar_filters(df, papers_df, patents_df):
    """사이드바 필터 렌더링"""
    st.sidebar.title("🔍 분석 설정")
    st.sidebar.markdown("---")
    
    if df.empty:
        st.sidebar.error("데이터가 없습니다.")
        return {}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    # 연도 범위 선택
    year_min, year_max = int(df['Year'].min()), int(df['Year'].max())
    year_range = st.sidebar.slider(
        "📅 분석 연도 범위",
        min_value=year_min,
        max_value=year_max,
        value=(year_min, year_max),
        help="분석할 연도 범위를 선택하세요"
    )
    
    # 국가 선택
    countries = sorted(df['Country'].unique())
    selected_countries = st.sidebar.multiselect(
        "🌍 분석 대상 국가",
        options=countries,
        default=countries,
        help="분석할 국가를 선택하세요"
    )
    
    # 분석 유형 선택
    analysis_options = [
        "📊 종합 대시보드",
        "📈 트렌드 분석", 
        "🌍 국가별 비교",
        "🎯 상세 분석"
    ]
    
    selected_analysis = st.sidebar.selectbox(
        "📋 분석 유형",
        options=analysis_options,
        index=0,
        help="원하는 분석 유형을 선택하세요"
    )
    
    # 데이터 필터링
    filtered_df = df[
        (df['Year'] >= year_range[0]) & 
        (df['Year'] <= year_range[1]) & 
        (df['Country'].isin(selected_countries))
    ]
    
    filtered_papers = papers_df[
        (papers_df['Year'] >= year_range[0]) & 
        (papers_df['Year'] <= year_range[1]) & 
        (papers_df['Country'].isin(selected_countries))
    ]
    
    filtered_patents = patents_df[
        (patents_df['Year'] >= year_range[0]) & 
        (patents_df['Year'] <= year_range[1]) & 
        (patents_df['Country'].isin(selected_countries))
    ]
    
    # 필터 정보 표시
    st.sidebar.markdown("---")
    st.sidebar.info(f"""
    **📊 필터링된 데이터**
    - 총 레코드: {len(filtered_df):,}개
    - 논문 데이터: {len(filtered_papers):,}개  
    - 특허 데이터: {len(filtered_patents):,}개
    - 분석 국가: {len(selected_countries)}개
    - 분석 기간: {year_range[0]}-{year_range[1]}년
    """)
    
    return {
        'analysis_type': selected_analysis,
        'year_range': year_range,
        'countries': selected_countries
    }, filtered_df, filtered_papers, filtered_patents

def render_comprehensive_dashboard(filtered_df, filtered_papers, filtered_patents):
    """종합 대시보드 렌더링"""
    st.title("📊 서지분석 종합 대시보드")
    st.caption("논문 및 특허 데이터 통합 분석")
    st.markdown("---")
    
    # 1. KPI 메트릭
    render_kpi_cards(filtered_df, filtered_papers, filtered_patents)
    st.markdown("---")
    
    # 2. 성장률 및 품질 지표
    col1, col2 = st.columns(2)
    with col1:
        render_growth_metrics(filtered_papers, filtered_patents)
    with col2:
        render_quality_metrics(filtered_papers, filtered_patents)
    
    st.markdown("---")
    
    # 3. 상위 성과자
    render_top_performers(filtered_papers, filtered_patents)
    st.markdown("---")
    
    # 4. 국가별 경쟁력 포지셔닝
    from utils.data_loader import DataLoader
    loader = DataLoader()
    country_summary = loader.get_yearly_summary(filtered_papers, filtered_patents)
    
    if not country_summary.empty:
        # 최신 연도 데이터로 포지셔닝 분석
        latest_year = country_summary['Year'].max()
        latest_data = country_summary[country_summary['Year'] == latest_year]
        
        # 논문/특허 통합 데이터 생성 (간단한 버전)
        if not latest_data.empty:
            from components.country import create_country_summary
            positioning_data = create_country_summary(
                filtered_papers[filtered_papers['Year'] == latest_year],
                filtered_patents[filtered_patents['Year'] == latest_year]
            )
            if not positioning_data.empty:
                render_competitive_positioning(positioning_data)

def render_trend_analysis(filtered_df, filtered_papers, filtered_patents):
    """트렌드 분석 페이지"""
    st.title("📈 트렌드 분석")
    st.caption("연도별 변화 추이 및 성장 패턴 분석")
    st.markdown("---")
    
    # 1. 종합 트렌드
    render_yearly_trends_comprehensive(filtered_papers, filtered_patents)
    st.markdown("---")
    
    # 2. 성장률 분석
    render_growth_rate_analysis(filtered_papers, filtered_patents)
    st.markdown("---")
    
    # 3. 상관관계 분석
    render_correlation_analysis(filtered_papers, filtered_patents)
    st.markdown("---")
    
    # 4. 예측 분석
    render_forecasting(filtered_papers, filtered_patents)

def render_country_analysis(filtered_df, filtered_papers, filtered_patents):
    """국가별 비교 분석 페이지"""
    st.title("🌍 국가별 비교 분석")
    st.caption("국가간 성과 비교 및 경쟁력 분석")
    st.markdown("---")
    
    # 1. 국가별 비교 대시보드
    render_country_comparison_dashboard(filtered_papers, filtered_patents)
    st.markdown("---")
    
    # 2. 국가별 순위
    from components.country import create_country_summary
    
    # 모든 연도 통합 데이터 생성
    all_country_data = create_country_summary(filtered_papers, filtered_patents)
    
    if not all_country_data.empty:
        render_country_rankings(all_country_data, top_n=10)
        st.markdown("---")
        
        # 3. 레이더 차트 비교
        render_radar_comparison(all_country_data, max_countries=5)

def render_detailed_analysis(filtered_df, filtered_papers, filtered_patents):
    """상세 분석 페이지"""
    st.title("🎯 상세 분석")
    st.caption("심화 분석 및 상세 데이터")
    st.markdown("---")
    
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 논문 상세", 
        "⚖️ 특허 상세", 
        "📊 통계 분석", 
        "📋 원본 데이터"
    ])
    
    with tab1:
        if not filtered_papers.empty:
            st.subheader("논문 데이터 상세 분석")
            
            # 주요 컬럼 선택하여 표시
            paper_cols = ['Year', 'Country', 'Total_Papers', 'H_Index', 'Q1_Ratio(%)', 
                         'Collaboration_Ratio(%)', 'Avg_Citations', 'Avg_mrnif']
            available_paper_cols = [col for col in paper_cols if col in filtered_papers.columns]
            
            if available_paper_cols:
                st.dataframe(filtered_papers[available_paper_cols], use_container_width=True)
                
                # 다운로드
                csv = filtered_papers[available_paper_cols].to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 논문 데이터 다운로드",
                    data=csv,
                    file_name='papers_detailed.csv',
                    mime='text/csv'
                )
        else:
            st.info("논문 데이터가 없습니다.")
    
    with tab2:
        if not filtered_patents.empty:
            st.subheader("특허 데이터 상세 분석")
            
            # 특허 관련 주요 컬럼
            patent_cols = ['Year', 'Country', 'patent_count', 'triadic_ratio', 
                          'claims_per_patent', 'foreign_filing_intensity', 'h_index']
            available_patent_cols = [col for col in patent_cols if col in filtered_patents.columns]
            
            if available_patent_cols:
                st.dataframe(filtered_patents[available_patent_cols], use_container_width=True)
                
                # 다운로드
                csv = filtered_patents[available_patent_cols].to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 특허 데이터 다운로드",
                    data=csv,
                    file_name='patents_detailed.csv',
                    mime='text/csv'
                )
            else:
                st.dataframe(filtered_patents, use_container_width=True)
        else:
            st.info("특허 데이터가 없습니다.")
    
    with tab3:
        st.subheader("📊 기술통계")
        
        # 기본 통계
        col1, col2 = st.columns(2)
        
        with col1:
            if not filtered_papers.empty:
                st.write("**논문 데이터 기술통계**")
                numeric_cols = filtered_papers.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    st.dataframe(filtered_papers[numeric_cols].describe())
        
        with col2:
            if not filtered_patents.empty:
                st.write("**특허 데이터 기술통계**")
                numeric_cols = filtered_patents.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    st.dataframe(filtered_patents[numeric_cols].describe())
    
    with tab4:
        st.subheader("📋 원본 데이터")
        st.dataframe(filtered_df, use_container_width=True)
        
        # 전체 데이터 다운로드
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 전체 데이터 다운로드",
            data=csv,
            file_name='complete_data.csv',
            mime='text/csv'
        )

def main():
    """메인 애플리케이션"""
    # 데이터 로드
    try:
        df, papers_df, patents_df = load_and_preprocess_data()
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")
        st.info("엑셀 파일 '_통합평가자료.xlsx'가 현재 디렉토리에 있는지 확인해주세요.")
        return
    
    if df.empty:
        st.error("데이터를 로드할 수 없습니다. 엑셀 파일을 확인해주세요.")
        return
    
    # 사이드바 필터
    filters, filtered_df, filtered_papers, filtered_patents = render_sidebar_filters(
        df, papers_df, patents_df
    )
    
    if not filters:
        return
    
    # 분석 유형에 따른 페이지 렌더링
    analysis_type = filters['analysis_type']
    
    if analysis_type == "📊 종합 대시보드":
        render_comprehensive_dashboard(filtered_df, filtered_papers, filtered_patents)
        
    elif analysis_type == "📈 트렌드 분석":
        render_trend_analysis(filtered_df, filtered_papers, filtered_patents)
        
    elif analysis_type == "🌍 국가별 비교":
        render_country_analysis(filtered_df, filtered_papers, filtered_patents)
        
    elif analysis_type == "🎯 상세 분석":
        render_detailed_analysis(filtered_df, filtered_papers, filtered_patents)
    
    # 푸터 정보
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px;'>
        📊 기술수준조사 서지분석 대시보드 | 
        데이터 기간: {year_range[0]}-{year_range[1]}년 | 
        분석 국가: {country_count}개 | 
        최종 업데이트: {update_time}
    </div>
    """.format(
        year_range=filters['year_range'],
        country_count=len(filters['countries']),
        update_time="2024-09-21"
    ), unsafe_allow_html=True)

if __name__ == "__main__":
    main()