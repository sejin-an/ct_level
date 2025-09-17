"""
국가별 인용 영향력 컴포넌트
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_country_citation(paper_filtered):
    """국가별 인용 영향력 분석"""
    st.header("🎯 국가별 인용 영향력")
    
    if paper_filtered is None:
        st.info("데이터가 없습니다.")
        return
    
    country_col = [c for c in paper_filtered.columns if c.lower() in ['country', '국가']][0]
    year_col = [c for c in paper_filtered.columns if c.lower() in ['year', '연도']][0]
    citation_cols = [c for c in paper_filtered.columns if 'citation' in c.lower()]
    papers_col = [c for c in paper_filtered.columns if 'total' in c.lower() and 'paper' in c.lower()][0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CPP by Country
        if citation_cols:
            country_cpp = paper_filtered.groupby(country_col).apply(
                lambda x: x[citation_cols[0]].sum() / x[papers_col].sum()
            ).nlargest(15)
            
            fig = px.bar(country_cpp, orientation='h',
                        title="국가별 논문당 인용수 (CPP)",
                        labels={'value': 'CPP', 'index': 'Country'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top 10% Papers Ratio
        top10_cols = [c for c in paper_filtered.columns if 'top10' in c.lower()]
        if top10_cols:
            country_top10 = paper_filtered.groupby(country_col)[top10_cols[0]].mean().nlargest(15)
            
            fig = px.bar(country_top10, orientation='h',
                        title="국가별 Top 10% 논문 비율",
                        color=country_top10.values,
                        color_continuous_scale='RdYlGn')
            st.plotly_chart(fig, use_container_width=True)
    
    # FWCI 국가별 비교
    st.subheader("Field-Weighted Citation Impact")
    if citation_cols:
        top10 = paper_filtered.groupby(country_col)[papers_col].sum().nlargest(10).index
        fwci_data = []
        
        for country in top10:
            country_data = paper_filtered[paper_filtered[country_col] == country]
            avg_citation = country_data[citation_cols[0]].mean()
            global_avg = paper_filtered[citation_cols[0]].mean()
            fwci = avg_citation / global_avg if global_avg > 0 else 0
            fwci_data.append({'Country': country, 'FWCI': fwci})
        
        fwci_df = pd.DataFrame(fwci_data)
        fig = px.scatter(fwci_df, x='Country', y='FWCI', size='FWCI',
                        title="국가별 FWCI (1.0 = Global Average)")
        fig.add_hline(y=1, line_dash="dash", line_color="red")
        st.plotly_chart(fig, use_container_width=True)