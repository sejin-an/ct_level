"""
기술수준조사 시계열 분석 대시보드
단순화 버전 - 시계열 차트에 집중
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="기술수준조사 시계열 대시보드",
    page_icon="📈",
    layout="wide"
)

def load_and_sample_data():
    """데이터 로드 및 샘플링"""
    try:
        # 샘플 크기 선택
        sample_size = st.sidebar.selectbox(
            "📊 데이터 샘플 크기",
            [1000, 5000, 10000, "전체"],
            index=1,
            help="분석할 데이터 크기를 선택하세요"
        )
        
        if sample_size == "전체":
            df = pd.read_excel('_통합평가자료.xlsx')
            st.info(f"📊 전체 데이터 로드: {len(df):,}행")
        else:
            df = pd.read_excel('_통합평가자료.xlsx', nrows=sample_size)
            st.info(f"📊 샘플 데이터 로드: {len(df):,}행")
        
        # 컬럼명 정리
        df.columns = df.columns.str.strip()
        return df
        
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return pd.DataFrame()

def simple_preprocess(df):
    """단순 전처리 - 오류 방지"""
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    
    # Year 컬럼 처리
    if 'Year' in df.columns:
        # 유효한 연도만 필터링
        df_clean = df.copy()
        df_clean['Year'] = pd.to_numeric(df_clean['Year'], errors='coerce')
        df_clean = df_clean[(df_clean['Year'] >= 2000) & (df_clean['Year'] <= 2030)]
        
        # 논문/특허 구분
        if '구분' in df_clean.columns:
            papers = df_clean[df_clean['구분'].astype(str).str.contains('논문|1\\.', na=False)]
            patents = df_clean[df_clean['구분'].astype(str).str.contains('특허|2\\.', na=False)]
        else:
            papers = df_clean.copy()
            patents = pd.DataFrame()
        
        st.success(f"✅ 유효 데이터: 논문 {len(papers)}행, 특허 {len(patents)}행")
        return papers, patents
    else:
        st.warning("Year 컬럼이 없습니다.")
        return pd.DataFrame(), pd.DataFrame()

def render_timeseries_charts(papers_df, patents_df):
    """시계열 차트 렌더링"""
    st.subheader("📈 시계열 분석")
    
    if papers_df.empty and patents_df.empty:
        st.warning("시계열 데이터가 없습니다.")
        return
    
    # 차트 타입 선택
    chart_type = st.selectbox(
        "차트 유형",
        ["연도별 개수", "국가별 트렌드", "누적 추이"],
        index=0
    )
    
    if chart_type == "연도별 개수":
        render_yearly_counts(papers_df, patents_df)
    elif chart_type == "국가별 트렌드":
        render_country_trends(papers_df, patents_df)
    else:
        render_cumulative_trends(papers_df, patents_df)

def render_yearly_counts(papers_df, patents_df):
    """연도별 개수 차트"""
    col1, col2 = st.columns(2)
    
    with col1:
        if not papers_df.empty:
            # 논문 연도별 집계
            papers_yearly = papers_df.groupby('Year').size().reset_index(name='Count')
            
            fig = px.line(
                papers_yearly,
                x='Year',
                y='Count',
                title='📄 연도별 논문 수',
                markers=True
            )
            fig.update_traces(line_color='#1f77b4', line_width=3, marker_size=8)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not patents_df.empty:
            # 특허 연도별 집계
            patents_yearly = patents_df.groupby('Year').size().reset_index(name='Count')
            
            fig = px.line(
                patents_yearly,
                x='Year',
                y='Count',
                title='⚖️ 연도별 특허 수',
                markers=True
            )
            fig.update_traces(line_color='#ff7f0e', line_width=3, marker_size=8)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

def render_country_trends(papers_df, patents_df):
    """국가별 트렌드"""
    if papers_df.empty:
        st.warning("논문 데이터가 없습니다.")
        return
    
    # 국가별 연도별 집계
    if 'Country' in papers_df.columns:
        country_yearly = papers_df.groupby(['Year', 'Country']).size().reset_index(name='Count')
        
        # 상위 10개국만 표시
        top_countries = papers_df['Country'].value_counts().head(10).index.tolist()
        country_yearly_filtered = country_yearly[country_yearly['Country'].isin(top_countries)]
        
        fig = px.line(
            country_yearly_filtered,
            x='Year',
            y='Count',
            color='Country',
            title='🌍 상위 10개국 연도별 논문 수 추이',
            markers=True
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # 국가 선택 옵션
        st.subheader("특정 국가 상세 분석")
        selected_countries = st.multiselect(
            "분석할 국가 선택",
            options=sorted(papers_df['Country'].unique()),
            default=top_countries[:3],
            max_selections=5
        )
        
        if selected_countries:
            filtered_data = country_yearly[country_yearly['Country'].isin(selected_countries)]
            fig = px.line(
                filtered_data,
                x='Year',
                y='Count',
                color='Country',
                title=f'선택 국가 상세 트렌드',
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Country 컬럼이 없습니다.")

def render_cumulative_trends(papers_df, patents_df):
    """누적 추이"""
    col1, col2 = st.columns(2)
    
    with col1:
        if not papers_df.empty:
            papers_yearly = papers_df.groupby('Year').size().reset_index(name='Count')
            papers_yearly['Cumulative'] = papers_yearly['Count'].cumsum()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=papers_yearly['Year'],
                y=papers_yearly['Cumulative'],
                mode='lines+markers',
                name='누적 논문 수',
                fill='tonexty',
                line=dict(color='#1f77b4', width=3)
            ))
            fig.update_layout(
                title='📄 논문 누적 추이',
                height=400,
                xaxis_title='연도',
                yaxis_title='누적 논문 수'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not patents_df.empty:
            patents_yearly = patents_df.groupby('Year').size().reset_index(name='Count')
            patents_yearly['Cumulative'] = patents_yearly['Count'].cumsum()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=patents_yearly['Year'],
                y=patents_yearly['Cumulative'],
                mode='lines+markers',
                name='누적 특허 수',
                fill='tonexty',
                line=dict(color='#ff7f0e', width=3)
            ))
            fig.update_layout(
                title='⚖️ 특허 누적 추이',
                height=400,
                xaxis_title='연도',
                yaxis_title='누적 특허 수'
            )
            st.plotly_chart(fig, use_container_width=True)

def render_summary_stats(papers_df, patents_df):
    """요약 통계"""
    st.subheader("📊 요약 통계")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        paper_count = len(papers_df) if not papers_df.empty else 0
        st.metric("📄 총 논문 수", f"{paper_count:,}")
    
    with col2:
        patent_count = len(patents_df) if not patents_df.empty else 0
        st.metric("⚖️ 총 특허 수", f"{patent_count:,}")
    
    with col3:
        if not papers_df.empty and 'Year' in papers_df.columns:
            year_range = f"{papers_df['Year'].min():.0f}-{papers_df['Year'].max():.0f}"
            st.metric("📅 분석 기간", year_range)
        else:
            st.metric("📅 분석 기간", "N/A")
    
    with col4:
        if not papers_df.empty and 'Country' in papers_df.columns:
            country_count = papers_df['Country'].nunique()
            st.metric("🌍 국가 수", f"{country_count}")
        else:
            st.metric("🌍 국가 수", "N/A")

def render_data_table(papers_df, patents_df):
    """데이터 테이블"""
    st.subheader("📋 데이터 테이블")
    
    tab1, tab2 = st.tabs(["📄 논문 데이터", "⚖️ 특허 데이터"])
    
    with tab1:
        if not papers_df.empty:
            # 주요 컬럼만 표시
            display_cols = []
            for col in ['Year', 'Country', '구분', 'Total_Papers', 'H_Index']:
                if col in papers_df.columns:
                    display_cols.append(col)
            
            if display_cols:
                st.dataframe(papers_df[display_cols].head(100), use_container_width=True)
            else:
                st.dataframe(papers_df.head(100), use_container_width=True)
        else:
            st.info("논문 데이터가 없습니다.")
    
    with tab2:
        if not patents_df.empty:
            # 주요 컬럼만 표시
            display_cols = []
            for col in ['Year', 'Country', '구분']:
                if col in patents_df.columns:
                    display_cols.append(col)
            
            if display_cols:
                st.dataframe(patents_df[display_cols].head(100), use_container_width=True)
            else:
                st.dataframe(patents_df.head(100), use_container_width=True)
        else:
            st.info("특허 데이터가 없습니다.")

def main():
    # 제목
    st.title("📈 기술수준조사 시계열 대시보드")
    st.caption("시계열 트렌드 분석에 집중한 단순 대시보드")
    st.markdown("---")
    
    # 사이드바
    st.sidebar.title("⚙️ 설정")
    
    # 데이터 로드
    df = load_and_sample_data()
    
    if df.empty:
        st.error("데이터를 로드할 수 없습니다.")
        return
    
    # 간단한 전처리
    papers_df, patents_df = simple_preprocess(df)
    
    # 메인 콘텐츠
    # 1. 요약 통계
    render_summary_stats(papers_df, patents_df)
    st.markdown("---")
    
    # 2. 시계열 차트
    render_timeseries_charts(papers_df, patents_df)
    st.markdown("---")
    
    # 3. 데이터 테이블 (옵션)
    if st.checkbox("📋 데이터 테이블 보기", value=False):
        render_data_table(papers_df, patents_df)
    
    # 사이드바 정보
    st.sidebar.markdown("---")
    st.sidebar.info(f"""
    **📊 현재 분석 데이터**
    - 논문: {len(papers_df):,}행
    - 특허: {len(patents_df):,}행
    - 총계: {len(df):,}행
    """)

if __name__ == "__main__":
    main()