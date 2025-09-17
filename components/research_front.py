"""
Research Front 컴포넌트
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def render_research_front(paper_filtered):
    """Research Front Analysis 렌더링"""
    st.header("🌐 Research Front & Emerging Topics")
    
    if paper_filtered is None:
        st.info("논문 데이터가 없습니다.")
        return
    
    # 컬럼 찾기
    tech_col = [c for c in paper_filtered.columns if any(k in c.lower() for k in ['label', 'tech', '기술'])]
    year_col = [c for c in paper_filtered.columns if c.lower() in ['year', '연도']][0]
    
    # Burst Detection
    st.subheader("📈 Research Burst Detection")
    
    if tech_col:
        recent_years = paper_filtered[year_col].max() - 2
        
        recent_tech = paper_filtered[paper_filtered[year_col] >= recent_years].groupby(tech_col[0]).size()
        total_tech = paper_filtered.groupby(tech_col[0]).size()
        
        burst_strength = (recent_tech / 3) / (total_tech / len(paper_filtered[year_col].unique()))
        burst_strength = burst_strength.sort_values(ascending=False).head(15)
        
        fig = px.bar(burst_strength, 
                    title="Emerging Research Topics (Burst Strength)",
                    labels={'value': 'Burst Strength', 'index': 'Technology'},
                    color=burst_strength.values,
                    color_continuous_scale='Reds')
        fig.add_hline(y=1, line_dash="dash", annotation_text="Baseline")
        st.plotly_chart(fig, use_container_width=True)
    
    # Technology Life Cycle
    st.subheader("🔄 Technology Life Cycle")
    
    if tech_col:
        top_techs = paper_filtered[tech_col[0]].value_counts().head(5).index
        
        fig = go.Figure()
        for tech in top_techs:
            tech_data = paper_filtered[paper_filtered[tech_col[0]] == tech]
            yearly_tech = tech_data.groupby(year_col).size()
            yearly_tech_norm = yearly_tech / yearly_tech.max()
            
            fig.add_trace(go.Scatter(x=yearly_tech_norm.index, 
                                    y=yearly_tech_norm.values,
                                    mode='lines+markers',
                                    name=tech))
        
        fig.update_layout(title="Technology Life Cycle Patterns",
                        xaxis_title="Year",
                        yaxis_title="Normalized Activity")
        st.plotly_chart(fig, use_container_width=True)
    
    # Research Velocity
    col1, col2 = st.columns(2)
    
    with col1:
        yearly = paper_filtered.groupby(year_col).size()
        velocity = yearly.diff()
        acceleration = velocity.diff()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=velocity.index, y=velocity.values,
                                mode='lines+markers', name='Velocity'))
        fig.add_trace(go.Scatter(x=acceleration.index, y=acceleration.values,
                                mode='lines+markers', name='Acceleration'))
        fig.update_layout(title="Research Velocity & Acceleration",
                        xaxis_title="Year", yaxis_title="Change Rate")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Innovation Index
        if 'mrnif' in paper_filtered.columns.str.lower().str.join(''):
            mrnif_col = [c for c in paper_filtered.columns if 'mrnif' in c.lower()][0]
            yearly_innovation = paper_filtered.groupby(year_col)[mrnif_col].mean()
            
            fig = px.line(yearly_innovation, 
                        title="Innovation Index Trend (mRNIF)",
                        markers=True)
            st.plotly_chart(fig, use_container_width=True)