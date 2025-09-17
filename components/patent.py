"""
Patent Analysis 컴포넌트
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def render_patent_analysis(patent_filtered):
    """Patent Landscape Analysis 렌더링"""
    st.header("🔬 Patent Landscape Analysis")
    
    if patent_filtered is None:
        st.info("특허 데이터가 없습니다.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Herfindahl Index
        tech_col = [c for c in patent_filtered.columns if any(k in c.lower() for k in ['label', 'tech'])]
        if tech_col:
            tech_dist = patent_filtered[tech_col[0]].value_counts(normalize=True)
            herfindahl = (tech_dist ** 2).sum()
            
            st.metric("Herfindahl Index", f"{herfindahl:.3f}")
            st.caption("Lower values indicate higher diversity")
            
            # Technology distribution
            tech_df = tech_dist.head(20).reset_index()
            tech_df.columns = ['technology', 'proportion']
            fig = px.treemap(tech_df,
                           path=['technology'], values='proportion',
                           title="Patent Technology Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Patent Quality
        triadic_cols = [c for c in patent_filtered.columns if 'triadic' in c.lower()]
        family_cols = [c for c in patent_filtered.columns if 'family' in c.lower()]
        
        if triadic_cols and family_cols:
            quality_metrics = patent_filtered.agg({
                triadic_cols[0]: 'mean',
                family_cols[0]: 'mean'
            })
            
            fig = go.Figure()
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=quality_metrics[triadic_cols[0]] * 100,
                title={'text': "Triadic Patent Ratio (%)"},
                gauge={'axis': {'range': [None, 100]},
                      'bar': {'color': "darkblue"},
                      'steps': [
                          {'range': [0, 50], 'color': "lightgray"},
                          {'range': [50, 100], 'color': "gray"}],
                      'threshold': {'line': {'color': "red", 'width': 4},
                                  'thickness': 0.75, 'value': 90}}))
            st.plotly_chart(fig, use_container_width=True)
    
    # Forward Citations
    st.subheader("Patent Forward Citations")
    
    citation_cols = [c for c in patent_filtered.columns if 'citation' in c.lower()]
    if citation_cols:
        fig = px.histogram(patent_filtered, x=citation_cols[0],
                         title="Forward Citation Distribution",
                         nbins=50)
        st.plotly_chart(fig, use_container_width=True)