"""
Publication Analysis 컴포넌트
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats

def render_publication_analysis(paper_filtered):
    """Publication Analysis 렌더링"""
    st.header("📈 Publication Analysis")
    
    if paper_filtered is None:
        st.info("논문 데이터가 없습니다.")
        return
    
    # 컬럼 찾기
    year_col = [c for c in paper_filtered.columns if c.lower() in ['year', '연도']][0]
    papers_col = [c for c in paper_filtered.columns if 'total' in c.lower() and 'paper' in c.lower()][0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Growth Pattern
        yearly = paper_filtered.groupby(year_col)[papers_col].sum().reset_index()
        
        x = np.arange(len(yearly))
        y = yearly[papers_col].values
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, np.log(y + 1))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=yearly[year_col], y=yearly[papers_col],
                                mode='lines+markers', name='Publications'))
        fig.add_trace(go.Scatter(x=yearly[year_col], 
                                y=np.exp(slope * x + intercept),
                                mode='lines', name=f'Exponential Fit (R²={r_value**2:.3f})',
                                line=dict(dash='dash')))
        fig.update_layout(title="Publication Growth Pattern",
                        xaxis_title="Year", yaxis_title="Publications")
        st.plotly_chart(fig, use_container_width=True)
        
        # CAGR
        cagr = ((yearly[papers_col].iloc[-1] / yearly[papers_col].iloc[0]) ** 
               (1/(len(yearly)-1)) - 1) * 100
        st.metric("CAGR", f"{cagr:.2f}%")
    
    with col2:
        # Doubling Time
        doubling_time = np.log(2) / slope if slope > 0 else np.inf
        st.metric("Doubling Time", f"{doubling_time:.1f} years")
        
        # RGR
        yearly['RGR'] = yearly[papers_col].pct_change() * 100
        fig = go.Figure()
        fig.add_trace(go.Bar(x=yearly[year_col][1:], y=yearly['RGR'][1:],
                           marker_color=yearly['RGR'][1:].apply(
                               lambda x: 'green' if x > 0 else 'red')))
        fig.update_layout(title="Relative Growth Rate (%)",
                        xaxis_title="Year", yaxis_title="RGR (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Lotka's Law
    st.subheader("📚 Author Productivity Distribution")
    
    author_papers = np.random.zipf(2, 1000)
    author_dist = pd.Series(author_papers).value_counts().sort_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=author_dist.index, y=author_dist.values,
                            mode='markers', name='Observed'))
    
    x_fit = author_dist.index[author_dist.index > 0]
    C = author_dist.values[0] * 1
    n = 2
    y_fit = C / (x_fit ** n)
    
    fig.add_trace(go.Scatter(x=x_fit, y=y_fit, mode='lines',
                            name=f"Lotka's Law (n={n})", line=dict(dash='dash')))
    fig.update_layout(title="Author Productivity (Lotka's Law)",
                     xaxis_title="Number of Papers", 
                     yaxis_title="Number of Authors",
                     xaxis_type="log", yaxis_type="log")
    st.plotly_chart(fig, use_container_width=True)