# main.py - 논문/특허 성과 대시보드
import streamlit as st
import os
import pandas as pd

# 유틸리티 가져오기
from utils.data_loader import (
    load_data, create_sample_data, preprocess_data, 
    show_debug_info
)

# 컴포넌트 가져오기
from components.paper_metrics import paper_metrics_section
from components.patent_metrics import patent_metrics_section
from components.comparison import comparison_section
from components.tech_analysis import tech_analysis_section

# 페이지 설정
st.set_page_config(page_title="논문/특허 성과 대시보드", page_icon="📊", layout="wide")

# 상위 20개국 필터링 함수 (Total_Papers 기준)
def get_top20_countries(paper_df, patent_df):
    """논문 Total_Papers 기준 상위 20개국 필터링"""
    # 논문 Total_Papers 기준 상위 국가
    paper_top = []
    if paper_df is not None and 'Country' in paper_df.columns:
        # Total_Papers 컬럼 확인
        paper_metric = None
        for col in ['Total_Papers', '논문 건수', 'total_papers']:
            if col in paper_df.columns:
                paper_metric = col
                break
        
        if paper_metric:
            # 국가별 Total_Papers 합계 계산
            country_papers = paper_df.groupby('Country')[paper_metric].sum()
            # 상위 20개국 선택
            paper_top = country_papers.nlargest(20).index.tolist()
            st.sidebar.success(f"논문 {paper_metric} 기준 상위 20개국 선정 완료")
        else:
            st.sidebar.warning("논문 데이터에 Total_Papers 관련 컬럼을 찾을 수 없습니다.")
    
    # 선택된 국가가 없는 경우 특허 데이터에서 시도
    if not paper_top and patent_df is not None and 'Country' in patent_df.columns:
        patent_metric = None
        for col in ['total_papers_granted', 'patent_count', 'total_papers']:
            if col in patent_df.columns:
                patent_metric = col
                break
        
        if patent_metric:
            country_patents = patent_df.groupby('Country')[patent_metric].sum()
            paper_top = country_patents.nlargest(20).index.tolist()
            st.sidebar.warning("논문 데이터에서 국가를 선정할 수 없어 특허 데이터 기준으로 선정했습니다.")
    
    # 선택된 국가가 20개 미만인 경우 처리
    if len(paper_top) < 20:
        st.sidebar.warning(f"선정된 국가가 {len(paper_top)}개로 20개 미만입니다.")
    
    return paper_top

# 기술 분야 목록 가져오기 함수
def get_tech_categories(df, tech_col, title_col=None):
    """
    기술 분야 목록 가져오기
    
    Parameters:
    -----------
    df : pandas.DataFrame
        데이터프레임
    tech_col : str
        기술 분야 ID 컬럼명 (예: 'label_m')
    title_col : str, optional
        기술 분야 제목 컬럼명 (예: 'label_m_title')
        
    Returns:
    --------
    list
        (id, title) 튜플로 구성된 기술 분야 목록
    """
    if df is None or df.empty or tech_col not in df.columns:
        return []
    
    # 기술 분야 ID 목록
    tech_ids = sorted(df[tech_col].unique())
    
    # 제목이 있는 경우 ID와 함께 반환
    if title_col is not None and title_col in df.columns:
        # ID-제목 매핑 생성
        tech_title_map = {}
        for _, row in df[[tech_col, title_col]].drop_duplicates().iterrows():
            tech_title_map[row[tech_col]] = row[title_col]
        
        # (ID, 제목) 튜플 목록 생성
        return [(tid, tech_title_map.get(tid, str(tid))) for tid in tech_ids]
    else:
        # 제목이 없는 경우 ID만 반환
        return [(tid, str(tid)) for tid in tech_ids]

def main():
    """메인 함수"""
    # 대시보드 제목
    st.title("📊 논문/특허 성과 대시보드")
    st.markdown("## 상위 20개국 기준 논문 및 특허 성과 분석")
    
    # 사이드바 설정
    st.sidebar.title("🔍 데이터 설정")
    
    # 파일 경로 목록
    file_paths = [
        "_통합평가자료.xlsx",
        "통합평가자료.xlsx",
        "./통합평가자료.xlsx",
        "../통합평가자료.xlsx"
    ]
    
    # 파일 경로 선택
    file_path = st.sidebar.selectbox(
        "데이터 파일 선택",
        options=file_paths,
        index=0
    )
    
    # 사용자 지정 파일 경로
    use_custom_path = st.sidebar.checkbox("사용자 지정 파일 경로 사용")
    if use_custom_path:
        custom_path = st.sidebar.text_input("파일 경로 입력", "")
        if custom_path:
            file_path = custom_path
    
    # 데이터 로드
    df = load_data(file_path)
    
    # 데이터 로드 실패 시 샘플 데이터 사용
    if df is None:
        st.warning(f"파일을 로드할 수 없습니다: {file_path}")
        use_sample = st.checkbox("샘플 데이터 사용", value=True)
        if use_sample:
            df = create_sample_data()
            st.info("샘플 데이터를 사용합니다.")
        else:
            st.stop()
    
    # 데이터 전처리
    paper_df, patent_df = preprocess_data(df)
    
    # 디버깅 정보 표시
    show_debug = st.sidebar.checkbox("디버깅 정보 표시")
    if show_debug:
        show_debug_info(df, paper_df, patent_df)
    
    # 상위 20개국 필터링 (Total_Papers 기준)
    st.sidebar.markdown("### 국가 선정")
    st.sidebar.markdown("논문 Total_Papers 기준 상위 20개국이 자동으로 선정됩니다.")
    
    top_countries = get_top20_countries(paper_df, patent_df)
    
    # 선정된 국가 목록 표시
    if top_countries:
        st.sidebar.markdown(f"**선정된 {len(top_countries)}개국:**")
        countries_df = pd.DataFrame({'국가': top_countries})
        st.sidebar.dataframe(countries_df, hide_index=True)
    
    # 국가 선택 옵션
    selected_countries = st.sidebar.multiselect(
        "분석할 국가 선택",
        options=top_countries,
        default=top_countries  # 모든 상위 국가를 기본값으로 설정
    )
    
    if not selected_countries:
        selected_countries = top_countries
        st.sidebar.info("국가가 선택되지 않아 모든 상위 국가를 기본값으로 설정합니다.")
    
    # 기술 분류 옵션
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 기술 분류 설정")
    
    tech_level = st.sidebar.radio(
        "기술 분류 레벨",
        options=["38대 분류", "82대 분류"],
        index=0
    )
    
    # 선택한 분류 레벨에 따라 기술 분야 목록 가져오기
    if tech_level == "38대 분류":
        tech_col = 'label_m'
        title_col = 'label_m_title'
    else:  # "82대 분류"
        tech_col = 'label_s'
        title_col = 'label_s_title'
    
    # 기술 분야 목록 가져오기 (논문과 특허 데이터 모두에서)
    paper_techs = get_tech_categories(paper_df, tech_col, title_col)
    patent_techs = get_tech_categories(patent_df, tech_col, title_col)
    
    # 중복 제거하여 통합
    all_techs = []
    tech_ids = set()
    for tid, title in paper_techs + patent_techs:
        if tid not in tech_ids:
            all_techs.append((tid, title))
            tech_ids.add(tid)
    
    # ID 기준 정렬
    all_techs.sort(key=lambda x: x[0])
    
    # 기술 분야 선택
    st.sidebar.markdown(f"**{tech_level}에서 분석할 기술 분야를 선택하세요:**")
    
    # 기술 분야가 많은 경우 검색 필터 추가
    if len(all_techs) > 10:
        search_term = st.sidebar.text_input("기술 분야 검색", "")
        if search_term:
            filtered_techs = [(tid, title) for tid, title in all_techs 
                             if search_term.lower() in str(title).lower() or search_term.lower() in str(tid).lower()]
        else:
            filtered_techs = all_techs
    else:
        filtered_techs = all_techs
    
    # 기술 분야 선택 옵션
    tech_options = ["전체"] + [f"{tid}: {title}" for tid, title in filtered_techs]
    selected_techs = st.sidebar.multiselect(
        "기술 분야 선택",
        options=tech_options,
        default=["전체"]
    )
    
    # 선택된 기술 분야 ID 추출
    if "전체" in selected_techs:
        selected_tech_ids = [tid for tid, _ in all_techs]
    else:
        selected_tech_ids = [int(tech.split(":")[0]) for tech in selected_techs]
    
    # 선택된 기술 분야로 데이터 필터링
    if "전체" not in selected_techs:
        if paper_df is not None and tech_col in paper_df.columns:
            paper_df = paper_df[paper_df[tech_col].isin(selected_tech_ids)].copy()
        
        if patent_df is not None and tech_col in patent_df.columns:
            patent_df = patent_df[patent_df[tech_col].isin(selected_tech_ids)].copy()
    
    # 필터링 후 데이터가 비어있는지 확인
    if (paper_df is None or paper_df.empty) and (patent_df is None or patent_df.empty):
        st.warning("선택한 조건에 맞는 데이터가 없습니다. 필터를 조정해보세요.")
        return
    
    # 대시보드 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📝 논문 지표", "🔬 특허 지표", "📊 성과 비교", "🔍 기술 분류 분석"])
    
    with tab1:
        paper_metrics_section(paper_df, selected_countries)
    
    with tab2:
        patent_metrics_section(patent_df, selected_countries)
    
    with tab3:
        comparison_section(paper_df, patent_df, selected_countries)
    
    with tab4:
        tech_analysis_section(paper_df, patent_df, selected_countries, tech_level)
    
    # 푸터
    st.markdown("---")
    st.caption("© 2025 논문/특허 성과 대시보드")

if __name__ == "__main__":
    main()