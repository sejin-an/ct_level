"""
Citation Analysis 컴포넌트
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def render_citation_analysis(paper_filtered):
    """Citation Impact Analysis 렌더링"""
    st.header("🎯 Citation Impact Analysis")
    
    if paper_filtered is None:
        st.info("논문 데이터가 없습니다.")
        return
    
    # 컬럼 찾기
    year_col = [c for c in paper_filtered.columns if c.lower() in ['year', '연도']][0]
    papers_col = [c for c in paper_filtered.columns if 'total' in c.lower() and 'paper' in c.lower()][0]
    country_col = [c for c in paper_filtered.columns if c.lower() in ['country', '국가']][0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # h-index by country
        h_col = [c for c in paper_filtered.columns if 'h_index' in c.lower()]
        if h_col:
            country_h = paper_filtered.groupby(country_col)[h_col[0]].mean().nlargest(10)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=country_h.index, y=country_h.values, name='h-index'))
            fig.update_layout(title="Bibliometric Indices by Country",
                            xaxis_title="Country", yaxis_title="Index Value")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # CPP trend
        citation_cols = [c for c in paper_filtered.columns if 'citation' in c.lower()]
        if citation_cols:
            yearly_citations = paper_filtered.groupby(year_col).agg({
                papers_col: 'sum',
                citation_cols[0]: 'sum'
            })
            yearly_citations['CPP'] = yearly_citations[citation_cols[0]] / yearly_citations[papers_col]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=yearly_citations.index, 
                                    y=yearly_citations['CPP'],
                                    mode='lines+markers'))
            fig.update_layout(title="Citations per Paper (CPP) Trend",
                            xaxis_title="Year", yaxis_title="CPP")
            st.plotly_chart(fig, use_container_width=True)
    
    # FWCI
    st.subheader("📊 Field-Weighted Citation Impact")
    
    tech_col = [c for c in paper_filtered.columns if any(k in c.lower() for k in ['label', 'tech', '기술'])]
    citation_cols = [c for c in paper_filtered.columns if 'citation' in c.lower()]
    
    if tech_col and citation_cols:
        field_impact = paper_filtered.groupby(tech_col[0]).agg({
            citation_cols[0]: 'mean',
            papers_col: 'sum'
        }).round(2)
        field_impact['FWCI'] = field_impact[citation_cols[0]] / field_impact[citation_cols[0]].mean()
        
        fig = px.scatter(field_impact.reset_index(), 
                       x=papers_col, y='FWCI',
                       size=citation_cols[0], 
                       hover_name=tech_col[0],
                       title="Field-Weighted Citation Impact",
                       labels={'FWCI': 'FWCI (1.0 = average)'})
        fig.add_hline(y=1, line_dash="dash", line_color="red")
        st.plotly_chart(fig, use_container_width=True)