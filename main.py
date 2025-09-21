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
    from utils.data_loader import load_data, filter_data, get_summary_stats
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

def get_top_countries(papers_df, patents_df, top_n=20):
    """논문/특허 최다 국가 기준으로 상위 N개국 추출"""
    all_countries = set()
    
    # 논문 상위 국가
    if papers_df is not None and not papers_df.empty:
        # 국가 컬럼 찾기
        country_col = None
        for col in papers_df.columns:
            if col.lower() in ['country', '국가', 'nation']:
                country_col = col
                break
        
        if country_col:
            # 수치 컬럼 찾기
            numeric_col = None
            for col in papers_df.columns:
                if papers_df[col].dtype in ['int64', 'float64'] and col.lower() not in ['year', '연도']:
                    numeric_col = col
                    break
            
            if numeric_col:
                paper_countries = papers_df.groupby(country_col)[numeric_col].sum().nlargest(top_n).index
            else:
                paper_countries = papers_df[country_col].value_counts().head(top_n).index
            all_countries.update(paper_countries)
    
    # 특허 상위 국가
    if patents_df is not None and not patents_df.empty:
        # 국가 컬럼 찾기
        country_col = None
        for col in patents_df.columns:
            if col.lower() in ['country', '국가', 'nation']:
                country_col = col
                break
        
        if country_col:
            # 수치 컬럼 찾기
            numeric_col = None
            for col in patents_df.columns:
                if patents_df[col].dtype in ['int64', 'float64'] and col.lower() not in ['year', '연도']:
                    numeric_col = col
                    break
            
            if numeric_col:
                patent_countries = patents_df.groupby(country_col)[numeric_col].sum().nlargest(top_n).index
            else:
                patent_countries = patents_df[country_col].value_counts().head(top_n).index
            all_countries.update(patent_countries)
    
    return list(all_countries)[:top_n]

def render_sidebar_controls(papers_df, patents_df):
    """사이드바 컨트롤 렌더링"""
    st.sidebar.title("⚙️ 대시보드 설정")
    
    # 사용 가능한 필터 가져오기 (함수를 직접 정의)
    available_filters = {}
    
    # 연도 필터 계산
    all_years = []
    for df in [papers_df, patents_df]:
        if df is not None and not df.empty:
            for col in df.columns:
                if col.lower() in ['year', '연도']:
                    years = pd.to_numeric(df[col], errors='coerce').dropna()
                    if not years.empty:
                        all_years.extend(years.tolist())
                    break
    
    if all_years:
        available_filters['year_range'] = (int(min(all_years)), int(max(all_years)))
    
    # 국가 필터 계산
    all_countries = set()
    for df in [papers_df, patents_df]:
        if df is not None and not df.empty:
            for col in df.columns:
                if col.lower() in ['country', '국가', 'nation']:
                    countries = df[col].dropna().unique()
                    all_countries.update(countries)
                    break
    
    available_filters['countries'] = sorted(list(all_countries))
    
    # 라벨 필터 계산 (label_m 우선)
    all_labels = set()
    for df in [papers_df, patents_df]:
        if df is not None and not df.empty:
            if 'label_m' in df.columns:
                labels = df['label_m'].dropna().unique()
                all_labels.update(labels)
            else:
                for col in df.columns:
                    if 'label' in col.lower():
                        labels = df[col].dropna().unique()
                        all_labels.update(labels)
                        break
    
    available_filters['labels'] = sorted(list(all_labels))
    
    # 1. 기술 분야 선택 (label_m) - 첫 번째로 이동
    st.sidebar.subheader("🔬 기술 분야 (label_m)")
    selected_labels = ['전체']
    
    if 'labels' in available_filters and available_filters['labels']:
        # label_m 옵션 생성 (상위 20개만)
        label_options = ['전체'] + [f"{label}: 분류{label}" if str(label).isdigit() 
                                  else str(label) for label in available_filters['labels'][:20]]
        
        selected_labels = st.sidebar.multiselect(
            "기술 분야 선택",
            options=label_options,
            default=['전체'],
            help="분석할 기술 분야를 선택하세요"
        )
        
        # 선택된 개수 표시
        if selected_labels and '전체' not in selected_labels:
            st.sidebar.success(f"✅ 선택된 기술 분야: {len(selected_labels)}개")
    else:
        st.sidebar.info("기술 분야 데이터가 없습니다.")
    
    # 2. 주요 국가 선택 (논문/특허 최다 상위 20개국)
    st.sidebar.subheader("🌍 주요 국가")
    top_countries = get_top_countries(papers_df, patents_df, 20)
    
    if top_countries:
        # 전체 선택/해제 버튼
        col1, col2 = st.sidebar.columns(2)
        with col1:
            select_all = st.button("전체 선택", key="select_all_countries")
        with col2:
            select_none = st.button("전체 해제", key="select_none_countries")
        
        if select_all:
            selected_countries = top_countries
        elif select_none:
            selected_countries = []
        else:
            selected_countries = st.sidebar.multiselect(
                "주요 국가 선택",
                options=['전체'] + top_countries,
                default=['전체'],  # 기본은 전체 선택
                help="논문/특허 최다 상위 20개국"
            )
        
        st.sidebar.info(f"📊 논문/특허 최다 상위 20개국 기준")
    else:
        selected_countries = []
    
    # 3. 연도 범위 설정
    year_min, year_max = 2020, 2024
    if 'year_range' in available_filters:
        year_min, year_max = available_filters['year_range']
    
    st.sidebar.subheader("📅 분석 기간")
    year_range = st.sidebar.slider(
        "연도 범위",
        min_value=int(year_min),
        max_value=int(year_max),
        value=(int(year_min), int(year_max)),
        help="분석할 연도 범위를 선택하세요"
    )
    
    # 4. 분석 모드 선택
    st.sidebar.subheader("🔍 분석 모드")
    analysis_mode = st.sidebar.selectbox(
        "분석 유형",
        ["📊 전체 대시보드", "📈 트렌드 분석", "🌍 국가별 분석", "📋 상세 분석"],
        index=0,
        help="원하는 분석 유형을 선택하세요"
    )
    
    return {
        'year_range': year_range,
        'selected_countries': selected_countries,
        'selected_labels': selected_labels,
        'analysis_mode': analysis_mode
    }

def filter_data_by_controls(papers_df, patents_df, controls):
    """컨트롤에 따라 데이터 필터링 (label_m 지원 추가)"""
    filtered_papers = papers_df.copy() if papers_df is not None else None
    filtered_patents = patents_df.copy() if patents_df is not None else None
    
    # 연도 필터링
    if controls['year_range']:
        for df_name, df in [('papers', filtered_papers), ('patents', filtered_patents)]:
            if df is not None and not df.empty:
                # 연도 컬럼 찾기
                year_col = None
                for col in df.columns:
                    if col.lower() in ['year', '연도']:
                        year_col = col
                        break
                
                if year_col:
                    years = pd.to_numeric(df[year_col], errors='coerce')
                    mask = (years >= controls['year_range'][0]) & (years <= controls['year_range'][1])
                    if df_name == 'papers':
                        filtered_papers = df[mask.fillna(False)]
                    else:
                        filtered_patents = df[mask.fillna(False)]
    
    # 국가 필터링
    if controls['selected_countries'] and '전체' not in controls['selected_countries']:
        for df_name, df in [('papers', filtered_papers), ('patents', filtered_patents)]:
            if df is not None and not df.empty:
                # 국가 컬럼 찾기
                country_col = None
                for col in df.columns:
                    if col.lower() in ['country', '국가', 'nation']:
                        country_col = col
                        break
                
                if country_col:
                    filtered_df = df[df[country_col].isin(controls['selected_countries'])]
                    if df_name == 'papers':
                        filtered_papers = filtered_df
                    else:
                        filtered_patents = filtered_df
    
    # label_m 필터링
    if controls.get('selected_labels') and '전체' not in controls['selected_labels']:
        # 라벨에서 숫자 부분 추출
        actual_labels = []
        for label in controls['selected_labels']:
            if ':' in str(label):
                try:
                    actual_labels.append(int(label.split(':')[0]))
                except ValueError:
                    actual_labels.append(label)
            else:
                actual_labels.append(label)
        
        for df_name, df in [('papers', filtered_papers), ('patents', filtered_patents)]:
            if df is not None and not df.empty and 'label_m' in df.columns:
                filtered_df = df[df['label_m'].isin(actual_labels)]
                if df_name == 'papers':
                    filtered_papers = filtered_df
                else:
                    filtered_patents = filtered_df
    
    return filtered_papers, filtered_patents

def render_full_dashboard(papers_df, patents_df, summary, controls):
    """전체 대시보드 렌더링 (세로 레이아웃)"""
    if IMPORTS_SUCCESSFUL:
        # 1. 요약 메트릭
        render_summary_metrics(summary)
        st.markdown("---")
        
        # 2. 트렌드 분석
        render_basic_timeseries(papers_df, patents_df)
        st.markdown("---")
        
        # 3. 기술 분야별 분석 (label_m 선택된 경우)
        if controls.get('selected_labels') and '전체' not in controls.get('selected_labels', []):
            render_label_analysis_dashboard(papers_df, patents_df, controls['selected_labels'])
            st.markdown("---")
        
        # 4. 국가별 분석
        render_top_countries_metrics(papers_df, top_n=5)
        st.markdown("---")
        
        # 5. 비교 게이지
        render_comparison_gauge(papers_df, patents_df)
        st.markdown("---")
        
        # 6. 국가별 트렌드
        render_country_trends(papers_df, patents_df, top_n=10)
    else:
        st.error("컴포넌트를 로드할 수 없어 대시보드를 표시할 수 없습니다.")

def render_label_analysis_dashboard(papers_df, patents_df, selected_labels):
    """기술 분야별 분석 대시보드 (세로 레이아웃, label_s 활용)"""
    st.subheader("🔬 선택된 기술 분야 분석")
    
    # 실제 라벨 값 추출
    actual_labels = []
    for label in selected_labels:
        if ':' in str(label):
            try:
                actual_labels.append(int(label.split(':')[0]))
            except ValueError:
                actual_labels.append(label)
        else:
            actual_labels.append(label)
    
    # label_s 세부 분석 (세로 배치)
    st.subheader("📊 label_s 세부 분류")
    col1, col2 = st.columns(2)
    with col1:
        if papers_df is not None:
            render_label_s_analysis(papers_df, actual_labels, "논문")
    with col2:
        if patents_df is not None:
            render_label_s_analysis(patents_df, actual_labels, "특허")
    
    st.markdown("---")
    
    # 시계열 추이 (세로 배치)
    st.subheader("📈 기술 분야 시계열 추이")
    render_label_timeseries_analysis(papers_df, patents_df, actual_labels)

def render_label_s_analysis(df, label_m_values, data_type):
    """label_s 기반 세부 분석"""
    try:
        if df is None or df.empty:
            st.info(f"{data_type} 데이터가 없습니다.")
            return
        
        # label_m으로 필터링
        if 'label_m' in df.columns:
            filtered_df = df[df['label_m'].isin(label_m_values)]
        else:
            st.warning(f"{data_type} 데이터에 label_m이 없습니다.")
            return
        
        if filtered_df.empty:
            st.warning(f"선택된 기술 분야에 대한 {data_type} 데이터가 없습니다.")
            return
        
        # label_s 분석
        if 'label_s' in filtered_df.columns:
            # 수치 컬럼 찾기
            numeric_col = None
            for col in filtered_df.columns:
                if filtered_df[col].dtype in ['int64', 'float64'] and col.lower() not in ['year', '연도', 'label_m', 'label_s']:
                    numeric_col = col
                    break
            
            # label_s별 집계
            if numeric_col:
                label_s_summary = filtered_df.groupby('label_s')[numeric_col].sum().sort_values(ascending=False).head(10)
            else:
                label_s_summary = filtered_df['label_s'].value_counts().head(10)
                numeric_col = 'Count'
            
            # 막대 차트
            import plotly.express as px
            fig = px.bar(
                x=label_s_summary.index,
                y=label_s_summary.values,
                title=f'{data_type} - label_s 세부 분류 (상위 10개)',
                labels={'x': 'label_s', 'y': numeric_col}
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
            
            # 요약 메트릭
            if numeric_col != 'Count':
                total_value = filtered_df[numeric_col].sum()
            else:
                total_value = len(filtered_df)
                
            unique_labels = filtered_df['label_s'].nunique()
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric(f"{data_type} 총계", f"{total_value:,.0f}")
            with col_b:
                st.metric("세부 분류 수", f"{unique_labels}개")
        else:
            st.info(f"{data_type} 데이터에 label_s가 없습니다.")
            
    except Exception as e:
        st.error(f"{data_type} label_s 분석 오류: {e}")

def render_label_timeseries_analysis(papers_df, patents_df, label_m_values):
    """라벨별 시계열 분석 (세로 배치)"""
    
    # 논문 시계열
    if papers_df is not None:
        render_single_label_timeseries(papers_df, label_m_values, "논문")
    
    # 특허 시계열  
    if patents_df is not None:
        render_single_label_timeseries(patents_df, label_m_values, "특허")

def render_single_label_timeseries(df, label_m_values, data_type):
    """단일 데이터의 라벨별 시계열"""
    try:
        if df is None or df.empty or 'label_m' not in df.columns:
            st.info(f"{data_type} 라벨 데이터가 없습니다.")
            return
        
        # label_m으로 필터링
        filtered_df = df[df['label_m'].isin(label_m_values)]
        
        if filtered_df.empty:
            return
        
        # 컬럼 찾기
        year_col = None
        for col in filtered_df.columns:
            if col.lower() in ['year', '연도']:
                year_col = col
                break
        
        numeric_col = None
        for col in filtered_df.columns:
            if filtered_df[col].dtype in ['int64', 'float64'] and col.lower() not in ['year', '연도', 'label_m', 'label_s']:
                numeric_col = col
                break
        
        if year_col and numeric_col:
            # 연도별 집계
            yearly_data = filtered_df.groupby(year_col)[numeric_col].sum().reset_index()
            
            import plotly.express as px
            fig = px.line(
                yearly_data,
                x=year_col,
                y=numeric_col,
                title=f'{data_type} 시계열 추이',
                markers=True
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"{data_type} 연도별 시계열 분석에 필요한 컬럼을 찾을 수 없습니다.")
            
    except Exception as e:
        st.error(f"{data_type} 시계열 분석 오류: {e}")

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
            if controls['selected_countries'] and '전체' not in controls['selected_countries']:
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
    
    selected_country_count = 0
    if controls['selected_countries']:
        if '전체' in controls['selected_countries']:
            selected_country_count = summary['country_count']
        else:
            selected_country_count = len(controls['selected_countries'])
    
    st.sidebar.info(f"""
    **필터링된 데이터:**
    - 논문: {summary['paper_count']:,}건
    - 특허: {summary['patent_count']:,}건
    - 총계: {summary['total_count']:,}건
    - 선택 국가: {selected_country_count}개
    """)
    
    if summary['year_range']:
        st.sidebar.success(f"📅 분석 기간: {summary['year_range'][0]}-{summary['year_range'][1]}년")

def main():
    # 제목
    st.title("📈 기술수준조사 시계열 대시보드")
    st.caption("논문 및 특허 데이터의 스마트 분석 전문 대시보드")
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

if __name__ == "__main__":
    main()