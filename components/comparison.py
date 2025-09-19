# components/comparison.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def render_comparison_chart(paper_df, patent_df, countries, paper_metric, patent_metric, title):
    """논문/특허 성과 비교 시각화"""
    if (paper_df is None or paper_df.empty or 'Country' not in paper_df.columns or 
        patent_df is None or patent_df.empty or 'Country' not in patent_df.columns):
        st.warning("비교 차트를 위한 데이터가 부족합니다.")
        return
    
    # 지표 확인
    if paper_metric not in paper_df.columns:
        st.warning(f"논문 지표 '{paper_metric}'를 찾을 수 없습니다.")
        return
    
    if patent_metric not in patent_df.columns:
        st.warning(f"특허 지표 '{patent_metric}'를 찾을 수 없습니다.")
        return
    
    # 선택한 국가만 필터링
    filtered_paper = paper_df[paper_df['Country'].isin(countries)].copy()
    filtered_patent = patent_df[patent_df['Country'].isin(countries)].copy()
    
    if filtered_paper.empty or filtered_patent.empty:
        st.warning("선택한 국가의 데이터가 부족합니다.")
        return
    
    # 데이터 준비
    paper_data = filtered_paper.groupby('Country')[paper_metric].mean()
    patent_data = filtered_patent.groupby('Country')[patent_metric].mean()
    
    # 공통 국가만 선택
    common_countries = list(set(paper_data.index) & set(patent_data.index))
    
    if not common_countries:
        st.warning("논문과 특허 데이터에 공통된 국가가 없습니다.")
        return
    
    # 데이터프레임 생성
    comparison_data = pd.DataFrame({
        '논문': paper_data.loc[common_countries],
        '특허': patent_data.loc[common_countries]
    }).reset_index()
    
    # 값 정규화 (0-1 스케일)
    for col in ['논문', '특허']:
        if comparison_data[col].max() > 0:
            comparison_data[f'{col}_norm'] = comparison_data[col] / comparison_data[col].max()
        else:
            comparison_data[f'{col}_norm'] = 0
    
    # NaN 값 처리
    comparison_data['논문_norm'] = comparison_data['논문_norm'].fillna(0)
    comparison_data['특허_norm'] = comparison_data['특허_norm'].fillna(0)
    
    # 크기 계산 (NaN 값 방지)
    size_values = []
    for x, y in zip(comparison_data['논문_norm'], comparison_data['특허_norm']):
        size = (x + y) * 50
        # NaN 체크 및 최소 크기 설정
        if np.isnan(size) or size <= 0:
            size = 10  # 기본 최소 크기
        size_values.append(size)
    
    # 산점도 생성
    fig = px.scatter(
        comparison_data,
        x='논문_norm',
        y='특허_norm',
        text='Country',
        title=title,
        labels={'논문_norm': '논문 성과 (정규화)', '특허_norm': '특허 성과 (정규화)'},
        color='Country',
        size=size_values,  # 수정된 크기 값 사용
        hover_data={'Country': True, '논문': True, '특허': True, '논문_norm': False, '특허_norm': False}
    )
    
    # 참조선 추가
    fig.add_shape(
        type="line", line=dict(dash="dash", width=1, color="gray"),
        x0=0, y0=0, x1=1, y1=1
    )
    
    fig.update_traces(
        textposition='top center',
        marker=dict(line=dict(width=1, color='DarkSlateGrey'))
    )
    
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

def comparison_section(paper_df, patent_df, selected_countries):
    """비교 분석 섹션"""
    st.header("논문/특허 성과 비교")
    
    # 비교할 지표 선택
    paper_metric_options = {
        '논문 건수': '논문 건수',
        'Total_Papers': 'Total_Papers',
        'Total_Citations': 'Total_Citations',
        'Avg_Citations': 'Avg_Citations',
        'H_Index': 'H_Index',
        'H-index': 'H-index',
        'Top10_Ratio(%)': 'Top10_Ratio(%)',
        'Q1_Ratio(%)': 'Q1_Ratio(%)'
    }
    
    patent_metric_options = {
        'total_papers_granted': 'total_papers_granted',
        'total_citations': 'total_citations',
        'avg_citations': 'avg_citations',
        'h_index': 'h_index',
        'triadic_ratio': 'triadic_ratio',
        'patent_impact': 'patent_impact'
    }
    
    # 사용 가능한 지표만 필터링
    available_paper_metrics = {k: v for k, v in paper_metric_options.items() if k in paper_df.columns}
    available_patent_metrics = {k: v for k, v in patent_metric_options.items() if k in patent_df.columns}
    
    if not available_paper_metrics or not available_patent_metrics:
        st.warning("비교할 수 있는 지표가 충분하지 않습니다.")
    else:
        # 사용자 선택 옵션
        col1, col2 = st.columns(2)
        
        with col1:
            selected_paper_metric = st.selectbox(
                "논문 지표 선택",
                options=list(available_paper_metrics.keys()),
                format_func=lambda x: paper_metric_options[x]
            )
        
        with col2:
            selected_patent_metric = st.selectbox(
                "특허 지표 선택",
                options=list(available_patent_metrics.keys()),
                format_func=lambda x: patent_metric_options[x]
            )
        
        # 총량 비교
        st.subheader(f"{paper_metric_options[selected_paper_metric]} vs {patent_metric_options[selected_patent_metric]}")
        render_comparison_chart(
            paper_df, patent_df, selected_countries,
            selected_paper_metric, selected_patent_metric,
            f'국가별 {paper_metric_options[selected_paper_metric]}와 {patent_metric_options[selected_patent_metric]} 비교 (정규화)'
        )