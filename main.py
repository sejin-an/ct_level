"""
기술수준조사 서지분석 통합 대시보드
main.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="기술수준조사 서지분석 대시보드",
    page_icon="📈",
    layout="wide"
)

@st.cache_data
def load_data():
    """엑셀 파일에서 데이터 로드"""
    try:
        papers_df = pd.read_excel('_통합평가자료.xlsx', sheet_name='논문')
        patents_df = pd.read_excel('_통합평가자료.xlsx', sheet_name='특허')
        st.sidebar.success(f"✅ 데이터 로드 완료")
        st.sidebar.info(f"논문: {len(papers_df):,}건, 특허: {len(patents_df):,}건")
        return papers_df, patents_df
    except Exception as e:
        st.sidebar.error(f"데이터 로드 실패: {e}")
        return None, None

def render_summary_metrics(papers_df, patents_df):
    """요약 통계 메트릭"""
    st.subheader("📊 주요 지표")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if papers_df is not None:
            total_papers = papers_df['Total_Papers'].sum()
            st.metric("📄 총 논문 수", f"{total_papers:,}")
        else:
            st.metric("📄 총 논문 수", "N/A")
    
    with col2:
        if patents_df is not None:
            total_patents = patents_df['Total_Papers'].sum()
            st.metric("⚖️ 총 특허 수", f"{total_patents:,}")
        else:
            st.metric("⚖️ 총 특허 수", "N/A")
    
    with col3:
        if papers_df is not None:
            countries = papers_df['Country'].nunique()
            st.metric("🌍 분석 국가", f"{countries}개")
        else:
            st.metric("🌍 분석 국가", "N/A")
    
    with col4:
        if papers_df is not None:
            year_range = f"{papers_df['Year'].min()}-{papers_df['Year'].max()}"
            st.metric("📅 분석 기간", year_range)
        else:
            st.metric("📅 분석 기간", "N/A")

def render_research_quality_analysis(papers_df):
    """연구 품질 분석"""
    if papers_df is None or papers_df.empty:
        st.warning("논문 데이터가 없습니다.")
        return
    
    st.subheader("🔬 연구 품질 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Q1-Q4 분포
        if all(col in papers_df.columns for col in ['Q1', 'Q2', 'Q3', 'Q4']):
            latest_year = papers_df['Year'].max()
            latest_data = papers_df[papers_df['Year'] == latest_year]
            
            q_totals = [
                latest_data['Q1'].sum(),
                latest_data['Q2'].sum(), 
                latest_data['Q3'].sum(),
                latest_data['Q4'].sum()
            ]
            
            fig_pie = px.pie(
                values=q_totals,
                names=['Q1 (최상위)', 'Q2 (상위)', 'Q3 (중위)', 'Q4 (하위)'],
                title=f'{latest_year}년 저널 품질 분포'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Q1 비율 트렌드
        if 'Q1_Ratio(%)' in papers_df.columns:
            yearly_q1 = papers_df.groupby('Year')['Q1_Ratio(%)'].mean().reset_index()
            
            fig_trend = px.line(
                yearly_q1,
                x='Year',
                y='Q1_Ratio(%)',
                title='Q1 저널 비율 연도별 추이',
                markers=True
            )
            fig_trend.update_traces(line_width=3, marker_size=8)
            st.plotly_chart(fig_trend, use_container_width=True)

def render_innovation_analysis(patents_df):
    """혁신 분석"""
    if patents_df is None or patents_df.empty:
        st.warning("특허 데이터가 없습니다.")
        return
    
    st.subheader("💡 혁신 지표 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Triadic 특허 비율
        if 'triadic_count' in patents_df.columns:
            yearly_patents = patents_df.groupby('Year').agg({
                'Total_Papers': 'sum',
                'triadic_count': 'sum'
            }).reset_index()
            
            yearly_patents['Triadic_Ratio'] = (yearly_patents['triadic_count'] / yearly_patents['Total_Papers']) * 100
            
            fig_triadic = px.line(
                yearly_patents,
                x='Year',
                y='Triadic_Ratio',
                title='Triadic 특허 비율 추이',
                markers=True
            )
            fig_triadic.update_traces(line_width=3, marker_size=8)
            st.plotly_chart(fig_triadic, use_container_width=True)
    
    with col2:
        # 특허 인용 분석
        if 'total_citations' in patents_df.columns:
            citation_data = patents_df.groupby('Year')['total_citations'].sum().reset_index()
            
            fig_citations = px.bar(
                citation_data,
                x='Year',
                y='total_citations',
                title='연도별 특허 피인용수',
                color='total_citations',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_citations, use_container_width=True)

def render_country_comparison(papers_df, patents_df):
    """국가별 비교"""
    st.subheader("🌍 국가별 성과 비교")
    
    if papers_df is None or papers_df.empty:
        st.warning("국가별 분석을 위한 데이터가 없습니다.")
        return
    
    # 상위 15개국
    top_countries = papers_df.groupby('Country')['Total_Papers'].sum().nlargest(15)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 논문 수 순위
        fig_papers = px.bar(
            x=top_countries.values,
            y=top_countries.index,
            orientation='h',
            title='상위 15개국 논문 수',
            labels={'x': '논문 수', 'y': '국가'}
        )
        fig_papers.update_layout(height=500)
        st.plotly_chart(fig_papers, use_container_width=True)
    
    with col2:
        # 국가별 연구 품질
        if 'Q1_Ratio(%)' in papers_df.columns:
            country_quality = papers_df.groupby('Country').agg({
                'Total_Papers': 'sum',
                'Q1_Ratio(%)': 'mean'
            }).reset_index()
            
            # 상위 15개국만
            top_15_countries = top_countries.index.tolist()
            country_quality_top = country_quality[country_quality['Country'].isin(top_15_countries)]
            
            fig_quality = px.scatter(
                country_quality_top,
                x='Total_Papers',
                y='Q1_Ratio(%)',
                hover_name='Country',
                title='국가별 논문 규모 vs 품질',
                labels={'Total_Papers': '총 논문 수', 'Q1_Ratio(%)': 'Q1 비율 (%)'}
            )
            st.plotly_chart(fig_quality, use_container_width=True)

def render_technology_trends(papers_df):
    """기술 분야별 트렌드"""
    if papers_df is None or papers_df.empty or 'label_m_title' not in papers_df.columns:
        st.warning("기술 분야 분석을 위한 데이터가 없습니다.")
        return
    
    st.subheader("🚀 기술 분야별 트렌드")
    
    # 상위 10개 기술 분야
    top_techs = papers_df.groupby('label_m_title')['Total_Papers'].sum().nlargest(10)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 기술 분야별 논문 수
        fig_tech = px.bar(
            x=top_techs.values,
            y=top_techs.index,
            orientation='h',
            title='상위 10개 기술 분야',
            labels={'x': '논문 수', 'y': '기술 분야'}
        )
        fig_tech.update_layout(height=400)
        st.plotly_chart(fig_tech, use_container_width=True)
    
    with col2:
        # 기술 분야별 시계열 (상위 5개)
        top_5_techs = top_techs.head(5).index.tolist()
        tech_yearly = papers_df[papers_df['label_m_title'].isin(top_5_techs)].groupby(['Year', 'label_m_title'])['Total_Papers'].sum().reset_index()
        
        fig_tech_trend = px.line(
            tech_yearly,
            x='Year',
            y='Total_Papers',
            color='label_m_title',
            title='주요 기술 분야 연도별 추이',
            markers=True
        )
        fig_tech_trend.update_layout(height=400)
        st.plotly_chart(fig_tech_trend, use_container_width=True)

def render_comprehensive_ranking(papers_df, patents_df):
    """종합 순위"""
    st.subheader("🏆 국가별 종합 순위")
    
    if papers_df is None or papers_df.empty:
        st.warning("순위 분석을 위한 데이터가 없습니다.")
        return
    
    # 논문 데이터 집계
    paper_summary = papers_df.groupby('Country').agg({
        'Total_Papers': 'sum',
        'Q1_Ratio(%)': 'mean',
        'Avg_Citations': 'mean',
        'H_Index': 'mean'
    }).round(2)
    
    # 특허 데이터 집계 (있는 경우)
    if patents_df is not None and not patents_df.empty:
        patent_summary = patents_df.groupby('Country').agg({
            'Total_Papers': 'sum',
            'triadic_count': 'sum'
        }).round(2)
        patent_summary.columns = ['Patent_Count', 'Triadic_Count']
        
        # 병합
        combined_ranking = paper_summary.merge(patent_summary, left_index=True, right_index=True, how='left')
        combined_ranking = combined_ranking.fillna(0)
    else:
        combined_ranking = paper_summary
    
    # 상위 20개국
    top_20 = combined_ranking.nlargest(20, 'Total_Papers')
    top_20.insert(0, '순위', range(1, len(top_20) + 1))
    
    st.dataframe(top_20, use_container_width=True)

def main():
    # 제목
    st.title("📈 기술수준조사 서지분석 대시보드")
    st.caption("논문 및 특허 데이터 통합 분석")
    st.markdown("---")
    
    # 데이터 로드
    papers_df, patents_df = load_data()
    
    if papers_df is None and patents_df is None:
        st.error("데이터를 로드할 수 없습니다. '_통합평가자료.xlsx' 파일을 확인해주세요.")
        st.stop()
    
    # 1. 요약 메트릭
    render_summary_metrics(papers_df, patents_df)
    st.markdown("---")
    
    # 2. 연구 품질 & 혁신 분석
    col1, col2 = st.columns(2)
    with col1:
        render_research_quality_analysis(papers_df)
    with col2:
        render_innovation_analysis(patents_df)
    
    st.markdown("---")
    
    # 3. 국가별 비교
    render_country_comparison(papers_df, patents_df)
    st.markdown("---")
    
    # 4. 기술 분야 트렌드
    render_technology_trends(papers_df)
    st.markdown("---")
    
    # 5. 종합 순위
    render_comprehensive_ranking(papers_df, patents_df)

if __name__ == "__main__":
    main()