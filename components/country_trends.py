"""
국가별 시계열 추이 컴포넌트
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def render_country_trends(paper_filtered, patent_filtered):
    """국가별 시계열 분석"""
    st.header("📈 국가별 시계열 추이")
    
    if paper_filtered is None:
        st.info("데이터가 없습니다.")
        return
    
    # 컬럼 찾기
    year_col = [c for c in paper_filtered.columns if c.lower() in ['year', '연도']][0]
    country_col = [c for c in paper_filtered.columns if c.lower() in ['country', '국가']][0]
    papers_col = [c for c in paper_filtered.columns if 'total' in c.lower() and 'paper' in c.lower()][0]
    
    # 상위 10개국 선정
    top10 = paper_filtered.groupby(country_col)[papers_col].sum().nlargest(10).index
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 논문 추이 - 상위 5개국
        st.subheader("논문 생산 추이 (Top 5)")
        country_yearly = paper_filtered[paper_filtered[country_col].isin(top10[:5])].groupby([year_col, country_col])[papers_col].sum().reset_index()
        
        fig = px.line(country_yearly, x=year_col, y=papers_col, color=country_col,
                     markers=True, title="상위 5개국 논문 추이")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 성장률 비교
        st.subheader("연평균 성장률 (CAGR)")
        cagr_data = []
        for country in top10:
            country_data = paper_filtered[paper_filtered[country_col] == country].groupby(year_col)[papers_col].sum()
            if len(country_data) > 1:
                cagr = ((country_data.iloc[-1] / country_data.iloc[0]) ** (1/(len(country_data)-1)) - 1) * 100
                cagr_data.append({'Country': country, 'CAGR': cagr})
        
        if cagr_data:
            cagr_df = pd.DataFrame(cagr_data).sort_values('CAGR', ascending=False)
            fig = px.bar(cagr_df, x='Country', y='CAGR', 
                        color='CAGR', color_continuous_scale='RdYlGn',
                        title="국가별 CAGR (%)")
            st.plotly_chart(fig, use_container_width=True)
    
    # H-index 시계열
    st.subheader("국가별 H-index 추이")
    h_col = [c for c in paper_filtered.columns if 'h_index' in c.lower()]
    if h_col:
        h_yearly = paper_filtered[paper_filtered[country_col].isin(top10[:5])].groupby([year_col, country_col])[h_col[0]].mean().reset_index()
        
        fig = px.line(h_yearly, x=year_col, y=h_col[0], color=country_col,
                     markers=True, title="H-index 시계열 변화")
        st.plotly_chart(fig, use_container_width=True)
    
    # 시장 점유율 변화
    st.subheader("글로벌 시장 점유율 변화")
    
    yearly_total = paper_filtered.groupby(year_col)[papers_col].sum()
    market_share = []
    
    for country in top10[:5]:
        country_yearly = paper_filtered[paper_filtered[country_col] == country].groupby(year_col)[papers_col].sum()
        share = (country_yearly / yearly_total * 100).reset_index()
        share['Country'] = country
        market_share.append(share)
    
    if market_share:
        share_df = pd.concat(market_share)
        fig = px.area(share_df, x=year_col, y=papers_col, color='Country',
                     title="시장 점유율 변화 (%)")
        st.plotly_chart(fig, use_container_width=True)