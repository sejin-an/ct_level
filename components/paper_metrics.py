# components/paper_metrics.py
import streamlit as st
import plotly.express as px
from utils.helpers import get_available_metrics

def render_paper_metrics(paper_df, countries, metrics):
    """논문 지표 시각화"""
    if paper_df is None or paper_df.empty or 'Country' not in paper_df.columns:
        st.warning("표시할 논문 데이터가 없습니다.")
        return
    
    # 선택한 국가만 필터링
    filtered_df = paper_df[paper_df['Country'].isin(countries)].copy()
    
    if filtered_df.empty:
        st.warning("선택한 국가의 논문 데이터가 없습니다.")
        return
    
    # 사용 가능한 지표 확인
    available_metrics = get_available_metrics(filtered_df, metrics)
    
    if not available_metrics:
        st.warning(f"표시할 지표가 없습니다. 사용 가능한 컬럼: {', '.join(filtered_df.columns)}")
        return
    
    # 지표별 시각화
    for metric, metric_name in available_metrics:
        # 국가별 지표 값 계산
        country_metric = filtered_df.groupby('Country')[metric].mean().reset_index()
        country_metric = country_metric.sort_values(metric, ascending=False)
        
        # 바차트 생성
        fig = px.bar(
            country_metric,
            x='Country',
            y=metric,
            title=f"국가별 {metric_name}",
            labels={'Country': '국가', metric: metric_name},
            color=metric,
            color_continuous_scale='Blues',
            height=400
        )
        
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

def paper_metrics_section(paper_df, selected_countries):
    """논문 지표 섹션"""
    st.header("논문 성과 지표")
    
    # 논문 총량 지표
    st.subheader("논문 총량 지표")
    paper_volume_metrics = [
        ('논문 건수', '논문 수'),
        ('Total_Papers', '논문 수'),
        ('논문 점유율(%)', '논문 점유율 (%)'),
        ('논문 증가율(%)', '논문 증가율 (%)')
    ]
    render_paper_metrics(paper_df, selected_countries, paper_volume_metrics)
    
    # 논문 영향력 지표
    st.subheader("논문 영향력 지표")
    paper_impact_metrics = [
        ('Total_Citations', '총 인용 수'),
        ('Avg_Citations', '평균 인용 수'),
        ('H_Index', 'H-Index'),
        ('H-index', 'H-Index'),
        ('논문 영향력', '논문 영향력')
    ]
    render_paper_metrics(paper_df, selected_countries, paper_impact_metrics)
    
    # 논문 품질 지표
    st.subheader("논문 품질 지표")
    paper_quality_metrics = [
        ('Top10_Ratio(%)', 'Top 10% 논문 비율 (%)'),
        ('Top 10% 비율(%)', 'Top 10% 논문 비율 (%)'),
        ('Q1_Ratio(%)', 'Q1 논문 비율 (%)'),
        ('Q1 논문 비율(%)', 'Q1 논문 비율 (%)'),
        ('Avg_mrnif', '평균 MRNIF'),
        ('MRNIF 평균', '평균 MRNIF'),
        ('Collaboration_Ratio(%)', '국제협력 비율 (%)'),
        ('국제협력 비율(%)', '국제협력 비율 (%)')
    ]
    render_paper_metrics(paper_df, selected_countries, paper_quality_metrics)