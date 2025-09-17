"""
국가별 협력 네트워크 컴포넌트
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import numpy as np

def render_country_collaboration(paper_filtered):
    """국가별 협력 분석"""
    st.header("🤝 국가별 협력 네트워크")
    
    if paper_filtered is None:
        st.info("데이터가 없습니다.")
        return
    
    country_col = [c for c in paper_filtered.columns if c.lower() in ['country', '국가']][0]
    year_col = [c for c in paper_filtered.columns if c.lower() in ['year', '연도']][0]
    collab_cols = [c for c in paper_filtered.columns if 'collab' in c.lower()]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 국가별 국제협력 비율
        if collab_cols:
            country_collab = paper_filtered.groupby(country_col)[collab_cols[0]].mean().nlargest(15)
            
            fig = px.bar(country_collab, orientation='h',
                        title="국가별 국제협력 비율",
                        color=country_collab.values,
                        color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 협력 네트워크 강도
        top10 = paper_filtered.groupby(country_col).size().nlargest(10).index
        
        # 국가 간 협력 매트릭스 (시뮬레이션)
        collab_matrix = np.random.rand(len(top10), len(top10))
        np.fill_diagonal(collab_matrix, 0)
        
        fig = go.Figure(data=go.Heatmap(
            z=collab_matrix,
            x=top10,
            y=top10,
            colorscale='Viridis'
        ))
        fig.update_layout(title="국가 간 협력 강도")
        st.plotly_chart(fig, use_container_width=True)
    
    # 시계열 협력 추이
    if collab_cols:
        st.subheader("주요국 협력 추이")
        top5 = paper_filtered.groupby(country_col).size().nlargest(5).index
        
        collab_trend = paper_filtered[paper_filtered[country_col].isin(top5)].groupby(
            [year_col, country_col])[collab_cols[0]].mean().reset_index()
        
        fig = px.line(collab_trend, x=year_col, y=collab_cols[0], color=country_col,
                     markers=True, title="국가별 협력 비율 변화")
        st.plotly_chart(fig, use_container_width=True)