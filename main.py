"""
향상된 기술수준조사 전문가용 대시보드 - 메인
enhanced_main.py
"""

import streamlit as st
import sys
import os
import warnings
import pandas as pd
import numpy as np
warnings.filterwarnings('ignore')

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 페이지 설정
st.set_page_config(
    page_title="🎯 기술수준조사 전문가 평가 대시보드",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 컴포넌트 import
try:
    from utils.data_loader import load_data, get_summary_stats
    
    # 기존 컴포넌트 (함수명 수정)
    from components.metrics import render_kpi_cards as render_summary_metrics
    from components.trends import render_basic_timeseries
    from components.country import render_country_trends
    
    # 향상된 컴포넌트
    from components.enhanced_metrics import (
        render_expert_summary_dashboard,
        render_quality_indicators_analysis,
        render_patent_innovation_analysis,
        render_comparative_benchmarking
    )
    from components.enhanced_trends import (
        render_technology_evolution_timeline,
        render_predictive_trends_analysis,
        render_innovation_lifecycle_analysis,
        render_cross_technology_impact_analysis,
        render_emerging_technology_detection,
        render_technology_convergence_analysis
    )
    from components.enhanced_country import (
        render_global_competitiveness_dashboard,
        render_collaborative_network_analysis,
        render_emerging_countries_analysis,
        render_regional_technology_leadership
    )
    
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    st.error(f"모듈 import 오류: {e}")
    st.info("enhanced_metrics.py, enhanced_trends.py, enhanced_country.py 파일을 확인하세요.")
    IMPORTS_SUCCESSFUL = False

# 스타일링
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .analysis-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

def load_and_process_data():
    """데이터 로드 및 전처리"""
    try:
        if IMPORTS_SUCCESSFUL:
            papers_df, patents_df = load_data()
            
            # 데이터 품질 검증
            if papers_df is not None and not papers_df.empty:
                st.sidebar.success(f"✅ 논문 데이터: {len(papers_df):,} 건")
                
                # 주요 컬럼 확인
                required_cols = ['Label_m', 'label_m_title', 'Year', 'Country', 'Total_Papers']
                missing_cols = [col for col in required_cols if col not in papers_df.columns]
                if missing_cols:
                    st.sidebar.warning(f"⚠️ 누락된 컬럼: {missing_cols}")
                
            if patents_df is not None and not patents_df.empty:
                st.sidebar.success(f"✅ 특허 데이터: {len(patents_df):,} 건")
            
            return papers_df, patents_df
        else:
            return None, None
    except Exception as e:
        st.sidebar.error(f"❌ 데이터 로드 실패: {e}")
        return None, None

def render_enhanced_sidebar_controls(papers_df, patents_df):
    """향상된 사이드바 컨트롤"""
    st.sidebar.markdown("""
    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; color: white; margin-bottom: 1rem;'>
        <h2>🎯 전문가 분석 설정</h2>
        <p>기술수준조사 평가자료</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 1. 분석 모드 선택
    st.sidebar.subheader("📊 분석 모드")
    analysis_mode = st.sidebar.selectbox(
        "분석 유형 선택",
        [
            "🎯 종합 평가 대시보드",
            "📈 기술 트렌드 분석", 
            "🌍 글로벌 경쟁력 분석",
            "🔬 연구 품질 분석",
            "💡 혁신 패턴 분석",
            "🤝 협력 네트워크 분석",
            "📋 상세 데이터 분석"
        ],
        help="원하는 분석 관점을 선택하세요"
    )
    
    # 2. 기술 분야 필터
    tech_filter = None
    if papers_df is not None and 'label_m_title' in papers_df.columns:
        st.sidebar.subheader("🔬 기술 분야 필터")
        
        tech_options = ['전체'] + sorted(papers_df['label_m_title'].unique())
        selected_techs = st.sidebar.multiselect(
            "분석 대상 기술 분야",
            options=tech_options,
            default=['전체'],
            help="특정 기술 분야로 분석을 제한할 수 있습니다"
        )
        
        if '전체' not in selected_techs and selected_techs:
            tech_filter = selected_techs
            st.sidebar.success(f"✅ 선택된 기술 분야: {len(selected_techs)}개")
    
    # 3. 국가 그룹 선택
    country_filter = None
    if papers_df is not None and 'Country' in papers_df.columns:
        st.sidebar.subheader("🌍 국가 그룹")
        
        # 주요국 자동 식별
        top_countries = papers_df.groupby('Country')['Total_Papers'].sum().nlargest(20).index.tolist()
        
        country_group = st.sidebar.selectbox(
            "분석 대상 국가군",
            ["전체 국가", "상위 10개국", "상위 20개국", "직접 선택"],
            help="분석할 국가 범위를 설정하세요"
        )
        
        if country_group == "상위 10개국":
            country_filter = top_countries[:10]
        elif country_group == "상위 20개국":
            country_filter = top_countries[:20]
        elif country_group == "직접 선택":
            country_filter = st.sidebar.multiselect(
                "분석 대상 국가",
                options=top_countries,
                default=top_countries[:5]
            )
    
    # 4. 시간 범위 설정
    time_filter = None
    if papers_df is not None and 'Year' in papers_df.columns:
        st.sidebar.subheader("📅 분석 기간")
        
        min_year = int(papers_df['Year'].min())
        max_year = int(papers_df['Year'].max())
        
        time_range = st.sidebar.slider(
            "연도 범위",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            help="분석할 시간 범위를 설정하세요"
        )
        
        if time_range != (min_year, max_year):
            time_filter = time_range
    
    # 5. 고급 옵션
    st.sidebar.subheader("⚙️ 고급 옵션")
    
    quality_threshold = st.sidebar.slider(
        "품질 임계값 (Q1 비율)",
        min_value=0.0,
        max_value=100.0,
        value=30.0,
        step=5.0,
        help="연구 품질 분석의 기준점"
    )
    
    show_confidence_intervals = st.sidebar.checkbox(
        "신뢰구간 표시",
        value=True,
        help="예측 분석에서 신뢰구간을 표시합니다"
    )
    
    enable_advanced_analytics = st.sidebar.checkbox(
        "고급 분석 기능",
        value=True,
        help="머신러닝 기반 예측 및 패턴 분석을 활성화합니다"
    )
    
    return {
        'analysis_mode': analysis_mode,
        'tech_filter': tech_filter,
        'country_filter': country_filter,
        'time_filter': time_filter,
        'quality_threshold': quality_threshold,
        'show_confidence_intervals': show_confidence_intervals,
        'enable_advanced_analytics': enable_advanced_analytics
    }

def apply_data_filters(papers_df, patents_df, filters):
    """데이터 필터 적용"""
    filtered_papers = papers_df.copy() if papers_df is not None else None
    filtered_patents = patents_df.copy() if patents_df is not None else None
    
    try:
        # 기술 분야 필터
        if filters['tech_filter'] and filtered_papers is not None:
            filtered_papers = filtered_papers[filtered_papers['label_m_title'].isin(filters['tech_filter'])]
            if filtered_patents is not None:
                filtered_patents = filtered_patents[filtered_patents['label_m_title'].isin(filters['tech_filter'])]
        
        # 국가 필터
        if filters['country_filter'] and filtered_papers is not None:
            filtered_papers = filtered_papers[filtered_papers['Country'].isin(filters['country_filter'])]
            if filtered_patents is not None:
                filtered_patents = filtered_patents[filtered_patents['Country'].isin(filters['country_filter'])]
        
        # 시간 필터
        if filters['time_filter'] and filtered_papers is not None:
            start_year, end_year = filters['time_filter']
            filtered_papers = filtered_papers[(filtered_papers['Year'] >= start_year) & (filtered_papers['Year'] <= end_year)]
            if filtered_patents is not None:
                filtered_patents = filtered_patents[(filtered_patents['Year'] >= start_year) & (filtered_patents['Year'] <= end_year)]
        
        return filtered_papers, filtered_patents
    
    except Exception as e:
        st.error(f"데이터 필터링 중 오류: {e}")
        return papers_df, patents_df

def render_main_header(summary_stats, filters):
    """메인 헤더 렌더링"""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 기술수준조사 전문가 평가 대시보드</h1>
        <p>논문/특허 데이터 기반 종합 분석 · 전문가 의사결정 지원 시스템</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 필터 적용 현황 표시
    if any([filters['tech_filter'], filters['country_filter'], filters['time_filter']]):
        st.info("🔍 **활성 필터**: " + 
               (f"기술분야 {len(filters['tech_filter'])}개 " if filters['tech_filter'] else "") +
               (f"국가 {len(filters['country_filter'])}개 " if filters['country_filter'] else "") +
               (f"기간 {filters['time_filter'][0]}-{filters['time_filter'][1]}년 " if filters['time_filter'] else ""))

def render_analysis_dashboard(papers_df, patents_df, filters):
    """분석 모드별 대시보드 렌더링"""
    analysis_mode = filters['analysis_mode']
    
    if not IMPORTS_SUCCESSFUL:
        st.error("분석 컴포넌트를 로드할 수 없습니다. 필수 파일들을 확인해주세요.")
        return
    
    try:
        if analysis_mode == "🎯 종합 평가 대시보드":
            render_comprehensive_evaluation_dashboard(papers_df, patents_df, filters)
            
        elif analysis_mode == "📈 기술 트렌드 분석":
            render_technology_trends_dashboard(papers_df, patents_df, filters)
            
        elif analysis_mode == "🌍 글로벌 경쟁력 분석":
            render_global_competitiveness_dashboard(papers_df, patents_df)
            
        elif analysis_mode == "🔬 연구 품질 분석":
            render_research_quality_dashboard(papers_df, patents_df, filters)
            
        elif analysis_mode == "💡 혁신 패턴 분석":
            render_innovation_patterns_dashboard(papers_df, patents_df, filters)
            
        elif analysis_mode == "🤝 협력 네트워크 분석":
            render_collaboration_dashboard(papers_df, patents_df)
            
        else:  # 상세 데이터 분석
            render_detailed_data_dashboard(papers_df, patents_df, filters)
    
    except Exception as e:
        st.error(f"대시보드 렌더링 중 오류: {e}")
        st.info("데이터 구조나 필수 컬럼을 확인해주세요.")

def render_comprehensive_evaluation_dashboard(papers_df, patents_df, filters):
    """종합 평가 대시보드"""
    st.header("🎯 종합 기술수준 평가")
    
    # 핵심 요약 메트릭
    render_expert_summary_dashboard(papers_df, patents_df)
    
    st.markdown("---")
    
    # 4개 영역별 분석
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 핵심 지표", 
        "📈 발전 추이", 
        "🌍 국제 비교", 
        "🔮 미래 전망"
    ])
    
    with tab1:
        # 연구 품질 및 혁신 지표
        col1, col2 = st.columns(2)
        with col1:
            render_quality_indicators_analysis(papers_df)
        with col2:
            render_patent_innovation_analysis(patents_df)
    
    with tab2:
        # 기술 발전 타임라인
        render_technology_evolution_timeline(papers_df, patents_df)
    
    with tab3:
        # 국제 벤치마킹
        render_comparative_benchmarking(papers_df, patents_df)
    
    with tab4:
        # 예측 분석
        if filters['enable_advanced_analytics']:
            render_predictive_trends_analysis(papers_df, patents_df)
        else:
            st.info("고급 분석 기능이 비활성화되어 있습니다. 사이드바에서 활성화할 수 있습니다.")

def render_technology_trends_dashboard(papers_df, patents_df, filters):
    """기술 트렌드 분석 대시보드"""
    st.header("📈 기술 발전 트렌드 심화 분석")
    
    # 분석 옵션 선택
    trend_analysis_type = st.selectbox(
        "트렌드 분석 유형",
        [
            "🚀 기술 발전 타임라인",
            "🔮 미래 예측 분석", 
            "🔄 혁신 생명주기",
            "🔗 기술 간 영향 관계",
            "🌟 신흥 기술 탐지",
            "🔀 기술 융합 분석"
        ]
    )
    
    if trend_analysis_type == "🚀 기술 발전 타임라인":
        render_technology_evolution_timeline(papers_df, patents_df)
        
    elif trend_analysis_type == "🔮 미래 예측 분석":
        render_predictive_trends_analysis(papers_df, patents_df)
        
    elif trend_analysis_type == "🔄 혁신 생명주기":
        render_innovation_lifecycle_analysis(papers_df, patents_df)
        
    elif trend_analysis_type == "🔗 기술 간 영향 관계":
        render_cross_technology_impact_analysis(papers_df)
        
    elif trend_analysis_type == "🌟 신흥 기술 탐지":
        render_emerging_technology_detection(papers_df)
        
    else:  # 기술 융합 분석
        render_technology_convergence_analysis(papers_df)

def render_research_quality_dashboard(papers_df, patents_df, filters):
    """연구 품질 분석 대시보드"""
    st.header("🔬 연구 품질 심층 분석")
    
    # 품질 임계값 적용
    quality_threshold = filters['quality_threshold']
    st.info(f"📊 품질 기준: Q1 비율 {quality_threshold}% 이상")
    
    # 품질 분석
    col1, col2 = st.columns(2)
    
    with col1:
        render_quality_indicators_analysis(papers_df)
    
    with col2:
        render_patent_innovation_analysis(patents_df)
    
    st.markdown("---")
    
    # 국제 벤치마킹
    render_comparative_benchmarking(papers_df, patents_df)

def render_innovation_patterns_dashboard(papers_df, patents_df, filters):
    """혁신 패턴 분석 대시보드"""
    st.header("💡 혁신 패턴 심층 분석")
    
    pattern_analysis_type = st.selectbox(
        "혁신 패턴 분석 유형",
        [
            "🔄 기술 생명주기",
            "🌟 신흥 기술 패턴",
            "🔀 기술 융합 트렌드",
            "🔗 기술 상호작용"
        ]
    )
    
    if pattern_analysis_type == "🔄 기술 생명주기":
        render_innovation_lifecycle_analysis(papers_df, patents_df)
        
    elif pattern_analysis_type == "🌟 신흥 기술 패턴":
        render_emerging_technology_detection(papers_df)
        
    elif pattern_analysis_type == "🔀 기술 융합 트렌드":
        render_technology_convergence_analysis(papers_df)
        
    else:  # 기술 상호작용
        render_cross_technology_impact_analysis(papers_df)

def render_collaboration_dashboard(papers_df, patents_df):
    """협력 네트워크 분석 대시보드"""
    st.header("🤝 국제 협력 네트워크 분석")
    
    collaboration_type = st.selectbox(
        "협력 분석 유형",
        [
            "🌐 협력 네트워크 구조",
            "🌟 신흥 강국 분석", 
            "🌍 지역별 리더십"
        ]
    )
    
    if collaboration_type == "🌐 협력 네트워크 구조":
        render_collaborative_network_analysis(papers_df)
        
    elif collaboration_type == "🌟 신흥 강국 분석":
        render_emerging_countries_analysis(papers_df)
        
    else:  # 지역별 리더십
        render_regional_technology_leadership(papers_df)

def render_detailed_data_dashboard(papers_df, patents_df, filters):
    """상세 데이터 분석 대시보드"""
    st.header("📋 상세 데이터 탐색")
    
    data_view_type = st.selectbox(
        "데이터 뷰 선택",
        ["📄 논문 데이터 상세", "⚖️ 특허 데이터 상세", "📊 통계 요약", "🔍 데이터 품질"]
    )
    
    if data_view_type == "📄 논문 데이터 상세":
        render_papers_detail_view(papers_df, filters)
        
    elif data_view_type == "⚖️ 특허 데이터 상세":
        render_patents_detail_view(patents_df, filters)
        
    elif data_view_type == "📊 통계 요약":
        render_statistical_summary(papers_df, patents_df)
        
    else:  # 데이터 품질
        render_data_quality_assessment(papers_df, patents_df)

def render_papers_detail_view(papers_df, filters):
    """논문 데이터 상세 뷰"""
    if papers_df is None or papers_df.empty:
        st.warning("논문 데이터가 없습니다.")
        return
    
    st.subheader("📄 논문 데이터 상세 정보")
    
    # 기본 통계
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 논문 수", f"{papers_df['Total_Papers'].sum():,}")
    with col2:
        st.metric("평균 Q1 비율", f"{papers_df['Q1_Ratio(%)'].mean():.1f}%")
    with col3:
        st.metric("평균 피인용수", f"{papers_df['Avg_Citations'].mean():.1f}")
    with col4:
        st.metric("분석 기간", f"{papers_df['Year'].min()}-{papers_df['Year'].max()}")
    
    # 데이터 테이블
    st.subheader("📊 데이터 테이블")
    
    # 정렬 옵션
    sort_by = st.selectbox(
        "정렬 기준",
        ["Total_Papers", "Q1_Ratio(%)", "Avg_Citations", "Year"]
    )
    
    sorted_data = papers_df.sort_values(sort_by, ascending=False)
    
    # 페이지네이션
    page_size = st.slider("페이지당 행 수", 10, 100, 50)
    total_pages = len(sorted_data) // page_size + (1 if len(sorted_data) % page_size > 0 else 0)
    
    if total_pages > 1:
        page_num = st.number_input("페이지", 1, total_pages, 1) - 1
        start_idx = page_num * page_size
        end_idx = min(start_idx + page_size, len(sorted_data))
        display_data = sorted_data.iloc[start_idx:end_idx]
    else:
        display_data = sorted_data.head(page_size)
    
    st.dataframe(display_data, use_container_width=True)
    
    # 데이터 다운로드
    csv = papers_df.to_csv(index=False)
    st.download_button(
        label="📥 CSV 다운로드",
        data=csv,
        file_name="papers_data.csv",
        mime="text/csv"
    )

def render_patents_detail_view(patents_df, filters):
    """특허 데이터 상세 뷰"""
    if patents_df is None or patents_df.empty:
        st.warning("특허 데이터가 없습니다.")
        return
    
    st.subheader("⚖️ 특허 데이터 상세 정보")
    
    # 기본 통계
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 특허 수", f"{patents_df['Total_Papers'].sum():,}")
    with col2:
        if 'triadic_count' in patents_df.columns:
            st.metric("Triadic 특허", f"{patents_df['triadic_count'].sum():,}")
    with col3:
        if 'avg_claims' in patents_df.columns:
            st.metric("평균 청구항", f"{patents_df['avg_claims'].mean():.1f}")
    with col4:
        st.metric("분석 기간", f"{patents_df['Year'].min()}-{patents_df['Year'].max()}")
    
    # 데이터 테이블
    st.dataframe(patents_df.head(100), use_container_width=True)

def render_statistical_summary(papers_df, patents_df):
    """통계 요약"""
    st.subheader("📊 통계 요약")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if papers_df is not None:
            st.write("**논문 데이터 통계**")
            numeric_cols = papers_df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                st.dataframe(papers_df[numeric_cols].describe(), use_container_width=True)
    
    with col2:
        if patents_df is not None:
            st.write("**특허 데이터 통계**")
            numeric_cols = patents_df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                st.dataframe(patents_df[numeric_cols].describe(), use_container_width=True)

def render_data_quality_assessment(papers_df, patents_df):
    """데이터 품질 평가"""
    st.subheader("🔍 데이터 품질 평가")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if papers_df is not None:
            st.write("**논문 데이터 품질**")
            
            # 결측값 분석
            missing_data = papers_df.isnull().sum()
            missing_pct = (missing_data / len(papers_df)) * 100
            
            quality_df = pd.DataFrame({
                '컬럼': missing_data.index,
                '결측값': missing_data.values,
                '결측비율(%)': missing_pct.values
            })
            quality_df = quality_df[quality_df['결측값'] > 0].sort_values('결측비율(%)', ascending=False)
            
            if not quality_df.empty:
                st.dataframe(quality_df, use_container_width=True, hide_index=True)
            else:
                st.success("✅ 결측값이 없습니다.")
    
    with col2:
        if patents_df is not None:
            st.write("**특허 데이터 품질**")
            
            missing_data = patents_df.isnull().sum()
            missing_pct = (missing_data / len(patents_df)) * 100
            
            quality_df = pd.DataFrame({
                '컬럼': missing_data.index,
                '결측값': missing_data.values,
                '결측비율(%)': missing_pct.values
            })
            quality_df = quality_df[quality_df['결측값'] > 0].sort_values('결측비율(%)', ascending=False)
            
            if not quality_df.empty:
                st.dataframe(quality_df, use_container_width=True, hide_index=True)
            else:
                st.success("✅ 결측값이 없습니다.")

def render_sidebar_summary(papers_df, patents_df, filters):
    """사이드바 요약 정보"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 데이터 현황")
    
    if papers_df is not None:
        paper_count = len(papers_df)
        paper_sum = papers_df['Total_Papers'].sum()
        st.sidebar.metric("논문 레코드", f"{paper_count:,}")
        st.sidebar.metric("총 논문 수", f"{paper_sum:,}")
    
    if patents_df is not None:
        patent_count = len(patents_df)
        patent_sum = patents_df['Total_Papers'].sum()
        st.sidebar.metric("특허 레코드", f"{patent_count:,}")
        st.sidebar.metric("총 특허 수", f"{patent_sum:,}")
    
    # 기술 분야 정보
    if papers_df is not None and 'label_m_title' in papers_df.columns:
        tech_count = papers_df['label_m_title'].nunique()
        st.sidebar.metric("기술 분야", f"{tech_count}개")
    
    # 국가 정보
    if papers_df is not None and 'Country' in papers_df.columns:
        country_count = papers_df['Country'].nunique()
        st.sidebar.metric("분석 국가", f"{country_count}개")

def main():
    """메인 함수"""
    # 데이터 로드
    papers_df, patents_df = load_and_process_data()
    
    # 사이드바 컨트롤
    filters = render_enhanced_sidebar_controls(papers_df, patents_df)
    
    # 데이터 필터링
    filtered_papers, filtered_patents = apply_data_filters(papers_df, patents_df, filters)
    
    # 요약 통계
    summary_stats = get_summary_stats(filtered_papers, filtered_patents)
    
    # 메인 헤더
    render_main_header(summary_stats, filters)
    
    # 메인 대시보드
    if filtered_papers is not None or filtered_patents is not None:
        render_analysis_dashboard(filtered_papers, filtered_patents, filters)
    else:
        st.error("분석할 데이터가 없습니다. 데이터 파일을 확인해주세요.")
    
    # 사이드바 요약
    render_sidebar_summary(filtered_papers, filtered_patents, filters)
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🎯 <strong>기술수준조사 전문가 평가 대시보드</strong></p>
        <p>논문/특허 데이터 기반 과학기술 정책 의사결정 지원 시스템</p>
        <p><small>Built with Streamlit • Data Analytics • Research Intelligence</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()