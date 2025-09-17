"""
Bradford's Law 컴포넌트
"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go

def render_bradford_analysis(paper_filtered):
    """Bradford's Law Analysis 렌더링"""
    st.header("📊 Bradford's Law & Core Journals")
    
    if paper_filtered is None:
        st.info("논문 데이터가 없습니다.")
        return
    
    st.subheader("Journal Concentration (Bradford's Law)")
    
    # Simulate journal distribution
    n_journals = 1000
    journal_papers = np.random.zipf(1.5, n_journals)
    journal_papers = np.sort(journal_papers)[::-1]
    cumsum_papers = np.cumsum(journal_papers)
    cumsum_ratio = cumsum_papers / cumsum_papers[-1]
    
    # Bradford zones
    zone1 = np.where(cumsum_ratio <= 0.33)[0][-1] if len(np.where(cumsum_ratio <= 0.33)[0]) > 0 else 0
    zone2 = np.where(cumsum_ratio <= 0.67)[0][-1] if len(np.where(cumsum_ratio <= 0.67)[0]) > 0 else 0
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.arange(n_journals), y=cumsum_ratio,
                            mode='lines', name='Cumulative Papers'))
    
    fig.add_vline(x=zone1, line_dash="dash", line_color="green", annotation_text="Zone 1")
    fig.add_vline(x=zone2, line_dash="dash", line_color="orange", annotation_text="Zone 2")
    fig.add_hline(y=0.33, line_dash="dot", line_color="gray")
    fig.add_hline(y=0.67, line_dash="dot", line_color="gray")
    
    fig.update_layout(title="Bradford's Law - Journal Distribution",
                     xaxis_title="Journal Rank", 
                     yaxis_title="Cumulative Paper Ratio")
    st.plotly_chart(fig, use_container_width=True)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Core Journals (Zone 1)", f"{zone1}")
    col2.metric("Zone 2 Journals", f"{zone2 - zone1}")
    col3.metric("Peripheral Journals", f"{n_journals - zone2}")