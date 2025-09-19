# components/patent_metrics.py
import streamlit as st
import plotly.express as px
from utils.helpers import get_available_metrics

def render_patent_metrics(patent_df, countries, metrics):
    """특허 지표 시각화"""
    if patent_df is None or patent_df.empty or 'Country' not in patent_df.columns:
        st.warning("표시할 특허 데이터가 없습니다.")
        return
    
    # 선택한 국가만 필터링
    filtered_df = patent_df[patent_df['Country'].isin(countries)].copy()
    
    if filtered_df.empty:
        st.warning("선택한 국가의 특허 데이터가 없습니다.")
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
            color_continuous_scale='Greens',
            height=400
        )
        
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

def patent_metrics_section(patent_df, selected_countries):
    """특허 지표 섹션"""
    st.header("특허 성과 지표")
    
    # 특허 총량 지표
    st.subheader("특허 총량 지표")
    patent_volume_metrics = [
        ('total_papers_granted', '특허 수'),
        ('patent_count', '특허 수'),
        ('patent_share', '특허 점유율 (%)'),
        ('growth_rate', '특허 증가율 (%)')
    ]
    render_patent_metrics(patent_df, selected_countries, patent_volume_metrics)
    
    # 특허 영향력 지표
    st.subheader("특허 영향력 지표")
    patent_impact_metrics = [
        ('total_citations', '총 인용 수'),
        ('avg_citations', '평균 인용 수'),
        ('h_index', 'H-Index'),
        ('patent_impact', '특허 영향력')
    ]
    render_patent_metrics(patent_df, selected_countries, patent_impact_metrics)
    
    # 특허 품질 지표
    st.subheader("특허 품질 지표")
    patent_quality_metrics = [
        ('triadic_ratio', 'Triadic 특허 비율'),
        ('important_patent_share', '중요 특허 비율'),
        ('important_patents_ratio', '중요 특허 비율'),
        ('foreign_filing_intensity', '해외 출원 강도'),
        ('avg_claims', '평균 청구항 수'),
        ('claims_per_patent', '평균 청구항 수')
    ]
    render_patent_metrics(patent_df, selected_countries, patent_quality_metrics)