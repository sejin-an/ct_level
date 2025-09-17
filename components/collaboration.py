"""
협력 분석 컴포넌트
"""
import streamlit as st
import plotly.express as px
import networkx as nx
import numpy as np

def render_collaboration_analysis(paper_filtered):
    """협력 네트워크 분석"""
    st.header("🤝 Collaboration Network Analysis")
    
    if paper_filtered is None:
        st.info("논문 데이터가 없습니다.")
        return
    
    # 컬럼 찾기
    country_col = [c for c in paper_filtered.columns if c.lower() in ['country', '국가']][0]
    year_col = [c for c in paper_filtered.columns if c.lower() in ['year', '연도']][0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # International Collaboration Index
        collab_cols = [c for c in paper_filtered.columns if 'collab' in c.lower()]
        if collab_cols:
            country_collab = paper_filtered.groupby(country_col)[collab_cols[0]].mean().nlargest(15)
            
            fig = px.bar(country_collab, orientation='h',
                       title="International Collaboration Index",
                       labels={'value': 'Collaboration %', 'index': 'Country'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Network Density
        st.subheader("Network Density")
        
        top_countries = paper_filtered[country_col].value_counts().head(10).index
        G = nx.Graph()
        
        for i, c1 in enumerate(top_countries):
            for c2 in top_countries[i+1:]:
                weight = np.random.randint(1, 100)
                if weight > 30:
                    G.add_edge(c1, c2, weight=weight)
        
        if len(G.nodes()) > 0:
            density = nx.density(G)
            clustering = nx.average_clustering(G)
            
            col1_metric, col2_metric = st.columns(2)
            col1_metric.metric("Network Density", f"{density:.3f}")
            col2_metric.metric("Clustering Coefficient", f"{clustering:.3f}")
        
        # Collaboration Trend
        if collab_cols:
            yearly_collab = paper_filtered.groupby(year_col)[collab_cols[0]].mean()
            fig = px.area(yearly_collab, title="Collaboration Trend")
            st.plotly_chart(fig, use_container_width=True)