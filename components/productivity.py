"""
생산성 분석 컴포넌트
"""
import streamlit as st
import plotly.express as px

def render_productivity_analysis(df, col_mapping):
    """생산성 분석"""
    st.subheader("📈 생산성 분석")
    
    # 생산성 관련 컬럼 찾기
    if 'productivity_score' in col_mapping and col_mapping['productivity_score'] in df.columns:
        prod_col = col_mapping['productivity_score']
        
        # 분포 히스토그램
        fig = px.histogram(df, x=prod_col, nbins=30, 
                          title="생산성 점수 분포")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("생산성 데이터가 없습니다.")