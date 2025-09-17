"""
국가별 특허 경쟁력 컴포넌트
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def render_country_patent(patent_filtered):
    """국가별 특허 경쟁력 분석"""
    st.header("🔬 국가별 특허 경쟁력")
    
    if patent_filtered is None:
        st.info("특허 데이터가 없습니다.")
        return
    
    country_col = [c for c in patent_filtered.columns if c.lower() in ['country', '국가']][0]
    year_col = [c for c in patent_filtered.columns if c.lower() in ['year', '연도']][0]
    patents_col = [c for c in patent_filtered.columns if 'total' in c.lower() and 'paper' in c.lower()][0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Triadic 특허 비율
        triadic_cols = [c for c in patent_filtered.columns if 'triadic' in c.lower()]
        if triadic_cols:
            country_triadic = patent_filtered.groupby(country_col)[triadic_cols[0]].mean().nlargest(15)
            
            fig = px.bar(country_triadic, orientation='h',
                        title="국가별 Triadic 특허 비율",
                        color=country_triadic.values,
                        color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 특허 패밀리 크기
        family_cols = [c for c in patent_filtered.columns if 'family' in c.lower()]
        if family_cols:
            country_family = patent_filtered.groupby(country_col)[family_cols[0]].mean().nlargest(15)
            
            fig = px.bar(country_family, orientation='h',
                        title="국가별 평균 특허 패밀리 크기",
                        color=country_family.values,
                        color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)
    
    # 특허 품질 지표 시계열
    st.subheader("주요국 특허 품질 추이")
    
    top5 = patent_filtered.groupby(country_col)[patents_col].sum().nlargest(5).index
    
    if triadic_cols:
        quality_trend = patent_filtered[patent_filtered[country_col].isin(top5)].groupby(
            [year_col, country_col])[triadic_cols[0]].mean().reset_index()
        
        fig = px.line(quality_trend, x=year_col, y=triadic_cols[0], color=country_col,
                     markers=True, title="Triadic 특허 비율 변화")
        st.plotly_chart(fig, use_container_width=True)
    
    # 특허 인용 영향력
    citation_cols = [c for c in patent_filtered.columns if 'citation' in c.lower()]
    if citation_cols:
        st.subheader("국가별 특허 인용 영향력")
        
        country_citation = patent_filtered.groupby(country_col)[citation_cols[0]].mean().nlargest(10)
        
        citation_df = country_citation.reset_index()
        citation_df.columns = ['Country', 'Citations']
        
        fig = px.scatter(citation_df, 
                        x='Country', y='Citations',
                        size='Citations',
                        title="평균 특허 인용수")
        st.plotly_chart(fig, use_container_width=True)