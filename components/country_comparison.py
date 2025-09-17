"""
국가별 종합 비교 컴포넌트
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render_country_comparison(paper_filtered, patent_filtered):
    """국가별 종합 비교"""
    st.header("🌍 국가별 종합 비교")
    
    if paper_filtered is None and patent_filtered is None:
        st.info("데이터가 없습니다.")
        return
    
    # Top 10 국가 선정
    country_col_paper = [c for c in paper_filtered.columns if c.lower() in ['country', '국가']][0] if paper_filtered is not None else None
    country_col_patent = [c for c in patent_filtered.columns if c.lower() in ['country', '국가']][0] if patent_filtered is not None else None
    
    # 국가별 집계
    if paper_filtered is not None:
        papers_col = [c for c in paper_filtered.columns if 'total' in c.lower() and 'paper' in c.lower()][0]
        h_col = [c for c in paper_filtered.columns if 'h_index' in c.lower()]
        
        # agg_dict 구성
        agg_dict = {papers_col: 'sum'}
        if h_col:
            agg_dict[h_col[0]] = 'mean'
        
        paper_metrics = paper_filtered.groupby(country_col_paper).agg(agg_dict)
        paper_metrics.columns = ['논문수', 'H-index'] if h_col else ['논문수']
        top_countries = paper_metrics.nlargest(10, '논문수').index
    
    if patent_filtered is not None:
        patents_col = [c for c in patent_filtered.columns if 'total' in c.lower() and 'paper' in c.lower()][0]
        triadic_col = [c for c in patent_filtered.columns if 'triadic' in c.lower()]
        
        # agg_dict 구성
        agg_dict = {patents_col: 'sum'}
        if triadic_col:
            agg_dict[triadic_col[0]] = 'mean'
        
        patent_metrics = patent_filtered.groupby(country_col_patent).agg(agg_dict)
        patent_metrics.columns = ['특허수', 'Triadic비율'] if triadic_col else ['특허수']
    
    # 레이더 차트 - 상위 5개국 비교
    st.subheader("상위 5개국 다차원 비교")
    
    fig = go.Figure()
    
    for country in top_countries[:5]:
        if country in paper_metrics.index:
            values = [
                paper_metrics.loc[country, '논문수'] / paper_metrics['논문수'].max(),
                paper_metrics.loc[country, 'H-index'] / paper_metrics['H-index'].max(),
                patent_metrics.loc[country, '특허수'] / patent_metrics['특허수'].max() if country in patent_metrics.index else 0,
                patent_metrics.loc[country, 'Triadic비율'] / patent_metrics['Triadic비율'].max() if country in patent_metrics.index else 0
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=['논문 생산성', 'H-index', '특허 출원', 'Triadic 특허'],
                fill='toself',
                name=country
            ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        title="국가별 종합 역량"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 순위표
    st.subheader("국가별 순위")
    
    if paper_filtered is not None and patent_filtered is not None:
        merged = pd.merge(paper_metrics, patent_metrics, left_index=True, right_index=True, how='outer').fillna(0)
        merged['종합점수'] = (
            merged['논문수']/merged['논문수'].max()*0.3 + 
            merged['H-index']/merged['H-index'].max()*0.3 +
            merged['특허수']/merged['특허수'].max()*0.2 +
            merged['Triadic비율']/merged['Triadic비율'].max()*0.2
        )
        
        top20 = merged.nlargest(20, '종합점수')
        st.dataframe(top20.style.background_gradient(cmap='RdYlGn', subset=['종합점수']), 
                    use_container_width=True)