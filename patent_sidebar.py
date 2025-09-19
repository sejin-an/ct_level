import streamlit as st
import pandas as pd

def create_patent_sidebar(data):
    """특허 분석 대시보드용 사이드바 생성 및 필터 설정 반환
    
    Parameters:
    -----------
    data : dict
        레벨별 데이터 사전
        
    Returns:
    --------
    dict
        필터 설정 사전
    """
    st.sidebar.title("🔍 필터 설정")
    st.sidebar.markdown("---")
    
    # 필터 설정 저장할 딕셔너리
    filter_config = {}
    
    # 연도 범위 선택
    with st.sidebar.expander("📅 연도", expanded=True):
        min_year = 2012
        max_year = 2024
        
        # 전체 선택/해제 버튼
        col1, col2 = st.columns(2)
        with col1:
            if st.button("전체선택", key="year_all", use_container_width=True):
                for year in range(min_year, max_year + 1):
                    st.session_state[f"year_{year}"] = True
        with col2:
            if st.button("전체해제", key="year_none", use_container_width=True):
                for year in range(min_year, max_year + 1):
                    st.session_state[f"year_{year}"] = False
        
        # 연도 범위 슬라이더
        year_range = st.slider(
            "연도 범위",
            min_year, max_year, (2015, 2023)
        )
        
        # 연도 체크박스 (3열로 배치)
        num_cols = 3
        cols = st.columns(num_cols)
        
        selected_years = []
        for i, year in enumerate(range(min_year, max_year + 1)):
            with cols[i % num_cols]:
                # 슬라이더 범위 내에 있으면 기본값 True, 아니면 False
                default_value = st.session_state.get(f"year_{year}", 
                                                     year_range[0] <= year <= year_range[1])
                if st.checkbox(f"{year}", value=default_value, key=f"year_{year}"):
                    selected_years.append(year)
        
        filter_config['year_range'] = (min(selected_years), max(selected_years)) if selected_years else (min_year, max_year)
    
    # 국가 선택
    with st.sidebar.expander("🌎 국가", expanded=True):
        all_countries = set()
        for lvl in data:
            if 'metadata' in data[lvl] and 'country' in data[lvl]['metadata'].columns:
                all_countries.update(data[lvl]['metadata']['country'].unique())
        
        all_countries = sorted(list(all_countries))
        
        # 상위 20개국 계산 (모든 레벨 데이터 통합)
        country_totals = {}
        for lvl in data:
            if 'metadata' in data[lvl]:
                metadata = data[lvl]['metadata']
                if 'country' in metadata.columns and 'total_papers' in metadata.columns:
                    for country, papers in metadata.groupby('country')['total_papers'].sum().items():
                        country_totals[country] = country_totals.get(country, 0) + papers
        
        top_countries = sorted(country_totals.items(), key=lambda x: x[1], reverse=True)[:20]
        top_country_names = [c[0] for c in top_countries]
        
        # 전체 선택/해제 버튼
        col1, col2 = st.columns(2)
        with col1:
            if st.button("전체선택", key="country_all", use_container_width=True):
                for country in all_countries:
                    st.session_state[f"country_{country}"] = True
        with col2:
            if st.button("전체해제", key="country_none", use_container_width=True):
                for country in all_countries:
                    st.session_state[f"country_{country}"] = False
        
        # 국가 검색 필터
        country_search = st.text_input("국가 검색", placeholder="검색어 입력")
        if country_search:
            filtered_countries = [c for c in all_countries if country_search.lower() in c.lower()]
        else:
            filtered_countries = all_countries
        
        # 상위 20개국 먼저 보여주기
        top_20_button = st.button("상위 20개국 선택", use_container_width=True)
        if top_20_button:
            for country in all_countries:
                st.session_state[f"country_{country}"] = country in top_country_names
        
        # 국가 목록을 여러 열로 배치
        num_cols = 3  # 3열로 배치
        cols = st.columns(num_cols)
        
        selected_countries = []
        for i, country in enumerate(filtered_countries):
            with cols[i % num_cols]:
                # 상위 20개국이면 기본값 True, 아니면 False
                default_value = st.session_state.get(f"country_{country}", country in top_country_names)
                if st.checkbox(country, value=default_value, key=f"country_{country}"):
                    selected_countries.append(country)
        
        filter_config['selected_countries'] = selected_countries if selected_countries else all_countries
    
    # 분류 레벨 선택
    filter_config['selected_categories'] = {}
    
    # 레벨 2 (1단계 분류) - 2개 카테고리
    with st.sidebar.expander("🔍 1단계 분류 (2개 카테고리)", expanded=True):
        if '2' in data and 'metadata' in data['2'] and 'label' in data['2']['metadata'].columns:
            lvl2_categories = sorted(data['2']['metadata']['label'].unique().tolist())
            
            # 전체 선택/해제 버튼
            col1, col2 = st.columns(2)
            with col1:
                if st.button("전체선택", key="lvl2_all", use_container_width=True):
                    for category in lvl2_categories:
                        st.session_state[f"lvl2_{category}"] = True
            with col2:
                if st.button("전체해제", key="lvl2_none", use_container_width=True):
                    for category in lvl2_categories:
                        st.session_state[f"lvl2_{category}"] = False
            
            selected_lvl2 = []
            # 2개 카테고리 직접 표시
            for category in lvl2_categories:
                default_value = st.session_state.get(f"lvl2_{category}", True)
                if st.checkbox(f"{category}", value=default_value, key=f"lvl2_{category}"):
                    selected_lvl2.append(category)
            
            filter_config['selected_categories']['2'] = selected_lvl2 if selected_lvl2 else lvl2_categories
    
    # 레벨 9 (2단계 분류) - 9개 카테고리
    with st.sidebar.expander("🔍 2단계 분류 (9개 카테고리)", expanded=False):
        if '9' in data and 'metadata' in data['9'] and 'label' in data['9']['metadata'].columns:
            lvl9_categories = sorted(data['9']['metadata']['label'].unique().tolist())
            
            # 전체 선택/해제 버튼
            col1, col2 = st.columns(2)
            with col1:
                if st.button("전체선택", key="lvl9_all", use_container_width=True):
                    for category in lvl9_categories:
                        st.session_state[f"lvl9_{category}"] = True
            with col2:
                if st.button("전체해제", key="lvl9_none", use_container_width=True):
                    for category in lvl9_categories:
                        st.session_state[f"lvl9_{category}"] = False
            
            # 카테고리 검색 필터
            lvl9_search = st.text_input("2단계 분류 검색", placeholder="검색어 입력")
            if lvl9_search:
                filtered_lvl9 = [c for c in lvl9_categories if lvl9_search.lower() in str(c).lower()]
            else:
                filtered_lvl9 = lvl9_categories
            
            # 9개 카테고리 표시 (3열로 배치)
            num_cols = 3
            cols = st.columns(num_cols)
            
            selected_lvl9 = []
            for i, category in enumerate(filtered_lvl9):
                with cols[i % num_cols]:
                    default_value = st.session_state.get(f"lvl9_{category}", True)
                    if st.checkbox(f"{category}", value=default_value, key=f"lvl9_{category}"):
                        selected_lvl9.append(category)
            
            filter_config['selected_categories']['9'] = selected_lvl9 if selected_lvl9 else lvl9_categories
    
    # 레벨 38 (3단계 분류) - 38개 카테고리
    with st.sidebar.expander("🔍 3단계 분류 (38개 카테고리)", expanded=False):
        if '38' in data and 'metadata' in data['38'] and 'label' in data['38']['metadata'].columns:
            lvl38_categories = sorted(data['38']['metadata']['label'].unique().tolist())
            
            # 전체 선택/해제 버튼
            col1, col2 = st.columns(2)
            with col1:
                if st.button("전체선택", key="lvl38_all", use_container_width=True):
                    for category in lvl38_categories:
                        st.session_state[f"lvl38_{category}"] = True
            with col2:
                if st.button("전체해제", key="lvl38_none", use_container_width=True):
                    for category in lvl38_categories:
                        st.session_state[f"lvl38_{category}"] = False
            
            # 카테고리 검색 필터
            lvl38_search = st.text_input("3단계 분류 검색", placeholder="검색어 입력")
            if lvl38_search:
                filtered_lvl38 = [c for c in lvl38_categories if lvl38_search.lower() in str(c).lower()]
            else:
                filtered_lvl38 = lvl38_categories
            
            # 38개 카테고리는 스크롤 가능한 컨테이너에 배치
            with st.container():
                num_cols = 4
                cols = st.columns(num_cols)
                
                selected_lvl38 = []
                for i, category in enumerate(filtered_lvl38):
                    with cols[i % num_cols]:
                        default_value = st.session_state.get(f"lvl38_{category}", True)
                        if st.checkbox(f"{category}", value=default_value, key=f"lvl38_{category}"):
                            selected_lvl38.append(category)
            
            filter_config['selected_categories']['38'] = selected_lvl38 if selected_lvl38 else lvl38_categories
    
    # 레벨 82 (4단계 분류) - 82개 카테고리
    with st.sidebar.expander("🔍 4단계 분류 (82개 카테고리)", expanded=False):
        if '82' in data and 'metadata' in data['82'] and 'label' in data['82']['metadata'].columns:
            lvl82_categories = sorted(data['82']['metadata']['label'].unique().tolist())
            
            # 전체 선택/해제 버튼
            col1, col2 = st.columns(2)
            with col1:
                if st.button("전체선택", key="lvl82_all", use_container_width=True):
                    for category in lvl82_categories:
                        st.session_state[f"lvl82_{category}"] = True
            with col2:
                if st.button("전체해제", key="lvl82_none", use_container_width=True):
                    for category in lvl82_categories:
                        st.session_state[f"lvl82_{category}"] = False
            
            # 카테고리 검색 필터
            lvl82_search = st.text_input("4단계 분류 검색", placeholder="검색어 입력")
            if lvl82_search:
                filtered_lvl82 = [c for c in lvl82_categories if lvl82_search.lower() in str(c).lower()]
            else:
                filtered_lvl82 = lvl82_categories
            
            # 82개 카테고리는 스크롤 가능한 컨테이너에 배치
            with st.container():
                num_cols = 4
                cols = st.columns(num_cols)
                
                selected_lvl82 = []
                for i, category in enumerate(filtered_lvl82):
                    with cols[i % num_cols]:
                        default_value = st.session_state.get(f"lvl82_{category}", True)
                        if st.checkbox(f"{category}", value=default_value, key=f"lvl82_{category}"):
                            selected_lvl82.append(category)
            
            filter_config['selected_categories']['82'] = selected_lvl82 if selected_lvl82 else lvl82_categories
    
    # 현재 보여줄 레벨 선택
    level_names = {
        '2': '1단계 분류 (2개 카테고리)',
        '9': '2단계 분류 (9개 카테고리)',
        '38': '3단계 분류 (38개 카테고리)',
        '82': '4단계 분류 (82개 카테고리)'
    }
    
    level = st.sidebar.selectbox(
        "분석에 사용할 분류 레벨",
        options=list(level_names.keys()),
        format_func=lambda x: level_names[x]
    )
    
    filter_config['level'] = level
    
    return filter_config