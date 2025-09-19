# components/tech_analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px

def render_technology_distribution(df, tech_col='label_m', title_col='label_m_title'):
    """기술 분류별 분포 시각화"""
    if df is None or df.empty or tech_col not in df.columns:
        st.warning(f"표시할 {tech_col} 데이터가 없습니다.")
        return
    
    # 기술 분류별 집계
    if title_col in df.columns:
        # 제목 컬럼이 있는 경우
        tech_counts = df.groupby([tech_col, title_col]).size().reset_index(name='count')
        tech_counts['label'] = tech_counts.apply(lambda x: f"{x[tech_col]}: {x[title_col]}", axis=1)
    else:
        # 제목 컬럼이 없는 경우
        tech_counts = df.groupby(tech_col).size().reset_index(name='count')
        tech_counts['label'] = tech_counts[tech_col].astype(str)
    
    # 정렬
    tech_counts = tech_counts.sort_values('count', ascending=False)
    
    # 상위 20개만 선택
    if len(tech_counts) > 20:
        tech_counts = tech_counts.head(20)
    
    # 트리맵 생성
    fig = px.treemap(
        tech_counts,
        path=['label'],
        values='count',
        title=f"기술 분류별 분포 ({tech_col})",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_country_tech_heatmap(df, countries, tech_col='label_m', title_col='label_m_title'):
    """국가별 기술 분포 히트맵"""
    if df is None or df.empty or 'Country' not in df.columns or tech_col not in df.columns:
        st.warning(f"표시할 국가-기술 데이터가 없습니다.")
        return
    
    # 선택한 국가만 필터링
    filtered_df = df[df['Country'].isin(countries)].copy()
    
    if filtered_df.empty:
        st.warning("선택한 국가의 데이터가 없습니다.")
        return
    
    # 기술 분류 컬럼 준비
    if title_col in filtered_df.columns:
        # 기술 분류 이름이 있는 경우
        tech_label = filtered_df[title_col]
    else:
        # 기술 분류 ID만 있는 경우
        tech_label = filtered_df[tech_col].astype(str)
    
    # 기술 분류 목록 (상위 10개)
    top_techs = filtered_df.groupby(tech_col).size().nlargest(10).index.tolist()
    
    # 국가-기술 분류 교차표
    country_tech = pd.crosstab(filtered_df['Country'], filtered_df[tech_col])
    
    # 상위 기술만 선택
    country_tech = country_tech.fillna(0)
    
    # 선택한 국가만 필터링
    if not all(country in country_tech.index for country in countries):
        st.warning("일부 국가에 대한 기술 분포 데이터가 없습니다.")
        # 있는 국가만 선택
        valid_countries = [c for c in countries if c in country_tech.index]
        if not valid_countries:
            return
        country_tech = country_tech.loc[valid_countries]
    else:
        country_tech = country_tech.loc[countries]
    
    # 히트맵 생성
    fig = px.imshow(
        country_tech,
        labels=dict(x="기술 분류", y="국가", color="건수"),
        title="국가별 기술 분포 히트맵",
        color_continuous_scale="Viridis"
    )
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

def tech_analysis_section(paper_df, patent_df, selected_countries, tech_level="38대 분류"):
    """기술 분류 분석 섹션"""
    st.header("기술 분류 분석")
    
    # 기술 분류 컬럼 설정
    tech_col = 'label_m' if tech_level == "38대 분류" else 'label_s'
    tech_title_col = 'label_m_title' if tech_level == "38대 분류" else 'label_s_title'
    
    # 기술 분류별 분포
    st.subheader(f"{tech_level} 분포")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### 논문 기술 분류")
        render_technology_distribution(paper_df, tech_col, tech_title_col)
    
    with col2:
        st.write("#### 특허 기술 분류")
        render_technology_distribution(patent_df, tech_col, tech_title_col)
    
    # 국가별 기술 분포
    st.subheader("국가별 기술 분포")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### 논문 국가-기술 분포")
        render_country_tech_heatmap(paper_df, selected_countries, tech_col, tech_title_col)
    
    with col2:
        st.write("#### 특허 국가-기술 분포")
        render_country_tech_heatmap(patent_df, selected_countries, tech_col, tech_title_col)