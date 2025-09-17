"""
국가별 기술 포트폴리오 컴포넌트
"""
import streamlit as st
import plotly.express as px
import pandas as pd

def render_country_technology(paper_filtered, patent_filtered):
    """국가별 기술 포트폴리오 분석"""
    st.header("🔬 국가별 기술 포트폴리오")
    
    if paper_filtered is None and patent_filtered is None:
        st.info("데이터가 없습니다.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        if paper_filtered is not None:
            st.subheader("논문 기술 분야 분포")
            
            country_col = [c for c in paper_filtered.columns if c.lower() in ['country', '국가']][0]
            tech_col = [c for c in paper_filtered.columns if any(k in c.lower() for k in ['label', 'tech', '기술'])]
            
            if tech_col:
                # 상위 5개국의 기술 분포
                top5 = paper_filtered.groupby(country_col).size().nlargest(5).index
                tech_dist = paper_filtered[paper_filtered[country_col].isin(top5)].groupby(
                    [country_col, tech_col[0]]).size().reset_index(name='count')
                
                fig = px.sunburst(tech_dist, path=[country_col, tech_col[0]], values='count',
                                title="국가-기술 계층 구조")
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if patent_filtered is not None:
            st.subheader("특허 기술 분야 분포")
            
            country_col = [c for c in patent_filtered.columns if c.lower() in ['country', '국가']][0]
            tech_col = [c for c in patent_filtered.columns if any(k in c.lower() for k in ['label', 'tech', '기술'])]
            
            if tech_col:
                top5 = patent_filtered.groupby(country_col).size().nlargest(5).index
                tech_dist = patent_filtered[patent_filtered[country_col].isin(top5)].groupby(
                    [country_col, tech_col[0]]).size().reset_index(name='count')
                
                fig = px.treemap(tech_dist, path=[px.Constant("All"), country_col, tech_col[0]], 
                               values='count', title="특허 기술 분포")
                st.plotly_chart(fig, use_container_width=True)
    
    # 기술 다양성 지수
    st.subheader("국가별 기술 다양성 (Herfindahl Index)")
    
    if paper_filtered is not None:
        country_col = [c for c in paper_filtered.columns if c.lower() in ['country', '국가']][0]
        tech_col = [c for c in paper_filtered.columns if any(k in c.lower() for k in ['label', 'tech', '기술'])]
        
        if tech_col:
            diversity_data = []
            top10 = paper_filtered.groupby(country_col).size().nlargest(10).index
        
            for country in top10:
                country_tech = paper_filtered[paper_filtered[country_col] == country][tech_col[0]].value_counts(normalize=True)
                herfindahl = (country_tech ** 2).sum()
                diversity_data.append({'Country': country, 'Herfindahl': herfindahl})
            
            diversity_df = pd.DataFrame(diversity_data).sort_values('Herfindahl')
            fig = px.bar(diversity_df, x='Country', y='Herfindahl',
                        title="기술 집중도 (낮을수록 다양)",
                        color='Herfindahl', color_continuous_scale='RdYlGn_r')
            st.plotly_chart(fig, use_container_width=True)