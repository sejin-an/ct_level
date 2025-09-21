"""
기술수준조사 서지분석 대시보드 - 메인
main.py
"""

import streamlit as st
import sys
import os
import warnings
import pandas as pd
import numpy as np
warnings.filterwarnings('ignore')

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 페이지 설정
st.set_page_config(
    page_title="🎯 기술수준조사 전문가 평가 대시보드",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 컴포넌트 import
try:
    from utils.data_loader import load_data, get_summary_stats
    from components.trends import render_basic_timeseries
    
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    st.error(f"모듈 import 오류: {e}")
    st.info("utils/data_loader.py, components/trends.py 파일을 확인하세요.")
    IMPORTS_SUCCESSFUL = False

# 스타일링
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

def render_summary_metrics(summary):
    """요약 메트릭"""
    st.subheader("📊 주요 지표")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        paper_count = summary.get('paper_count', 0)
        st.metric("📄 총 논문 수", f"{paper_count:,}")
    
    with col2:
        patent_count = summary.get('patent_count', 0)
        st.metric("⚖️ 총 특허 수", f"{patent_count:,}")
    
    with col3:
        year_range = summary.get('year_range')
        if year_range:
            year_display = f"{year_range[0]}-{year_range[1]}"
            st.metric("📅 분석 기간", year_display)
        else:
            st.metric("📅 분석 기간", "N/A")
    
    with col4:
        country_count = summary.get('country_count', 0)
        st.metric("🌍 국가 수", f"{country_count}")

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
            import plotly.express as px
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
            import plotly.express as px
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
    """특허 혁신 분석"""
    if patents_df is None or patents_df.empty:
        st.warning("특허 데이터가 없습니다.")
        return
    
    st.subheader("💡 혁신 지표 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Triadic 특허 비율
        if 'triadic_count' in patents_df.columns:
            import plotly.express as px
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
            import plotly.express as px
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
        import plotly.express as px
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
            import plotly.express as px
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
        import plotly.express as px
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
        import plotly.express as px
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

def render_country_trends_simple(papers_df, patents_df, top_n=10):
    """국가별 트렌드 분석 (간단 버전)"""
    if papers_df is None or papers_df.empty:
        st.warning("국가별 트렌드 분석을 위한 데이터가 없습니다.")
        return
    
    st.subheader("🌍 상위 국가별 시계열 트렌드")
    
    # 상위 국가 선택
    top_countries = papers_df.groupby('Country')['Total_Papers'].sum().nlargest(top_n).index.tolist()
    
    # 연도별 국가별 데이터
    country_yearly = papers_df[papers_df['Country'].isin(top_countries)].groupby(['Year', 'Country'])['Total_Papers'].sum().reset_index()
    
    if not country_yearly.empty:
        import plotly.express as px
        fig = px.line(
            country_yearly,
            x='Year',
            y='Total_Papers',
            color='Country',
            title=f'상위 {top_n}개국 연도별 논문 수 추이',
            markers=True
        )
        fig.update_traces(line_width=2, marker_size=6)
        fig.update_layout(height=500, legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, use_container_width=True)
        
        # 국가별 요약 통계
        st.subheader("📊 상위 국가 요약 통계")
        country_stats = papers_df[papers_df['Country'].isin(top_countries)].groupby('Country').agg({
            'Total_Papers': 'sum',
            'Q1_Ratio(%)': 'mean',
            'Avg_Citations': 'mean'
        }).round(2)
        country_stats = country_stats.sort_values('Total_Papers', ascending=False)
        country_stats.insert(0, '순위', range(1, len(country_stats) + 1))
        
        st.dataframe(country_stats, use_container_width=True)
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

def render_sidebar_controls(papers_df, patents_df):
    """사이드바 컨트롤"""
    st.sidebar.markdown("""
    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; color: white; margin-bottom: 1rem;'>
        <h2>🎯 전문가 분석 설정</h2>
        <p>기술수준조사 평가자료</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 기술 분야 필터
    tech_filter = None
    if papers_df is not None and 'label_m_title' in papers_df.columns:
        st.sidebar.subheader("🔬 기술 분야 필터")
        
        tech_options = ['전체'] + sorted(papers_df['label_m_title'].unique())
        selected_techs = st.sidebar.multiselect(
            "분석 대상 기술 분야",
            options=tech_options,
            default=['전체'],
            help="특정 기술 분야로 분석을 제한할 수 있습니다"
        )
        
        if '전체' not in selected_techs and selected_techs:
            tech_filter = selected_techs
            st.sidebar.success(f"✅ 선택된 기술 분야: {len(selected_techs)}개")
    
    # 국가 그룹 선택
    country_filter = None
    if papers_df is not None and 'Country' in papers_df.columns:
        st.sidebar.subheader("🌍 국가 그룹")
        
        # 주요국 자동 식별
        top_countries = papers_df.groupby('Country')['Total_Papers'].sum().nlargest(20).index.tolist()
        
        country_group = st.sidebar.selectbox(
            "분석 대상 국가군",
            ["전체 국가", "상위 10개국", "상위 20개국", "직접 선택"],
            help="분석할 국가 범위를 설정하세요"
        )
        
        if country_group == "상위 10개국":
            country_filter = top_countries[:10]
        elif country_group == "상위 20개국":
            country_filter = top_countries[:20]
        elif country_group == "직접 선택":
            country_filter = st.sidebar.multiselect(
                "분석 대상 국가",
                options=top_countries,
                default=top_countries[:5]
            )
    
    # 시간 범위 설정
    time_filter = None
    if papers_df is not None and 'Year' in papers_df.columns:
        st.sidebar.subheader("📅 분석 기간")
        
        try:
            # Year 컬럼을 숫자로 변환하고 결측값 제거
            years = pd.to_numeric(papers_df['Year'], errors='coerce').dropna()
            
            if not years.empty:
                min_year = int(years.min())
                max_year = int(years.max())
                
                time_range = st.sidebar.slider(
                    "연도 범위",
                    min_value=min_year,
                    max_value=max_year,
                    value=(min_year, max_year),
                    help="분석할 시간 범위를 설정하세요"
                )
                
                if time_range != (min_year, max_year):
                    time_filter = time_range
            else:
                st.sidebar.warning("유효한 연도 데이터가 없습니다.")
        except Exception as e:
            st.sidebar.error(f"연도 범위 설정 오류: {e}")
    
    return {
        'tech_filter': tech_filter,
        'country_filter': country_filter,
        'time_filter': time_filter
    }

def apply_data_filters(papers_df, patents_df, filters):
    """데이터 필터 적용"""
    filtered_papers = papers_df.copy() if papers_df is not None else None
    filtered_patents = patents_df.copy() if patents_df is not None else None
    
    try:
        # 기술 분야 필터
        if filters['tech_filter'] and filtered_papers is not None:
            filtered_papers = filtered_papers[filtered_papers['label_m_title'].isin(filters['tech_filter'])]
            if filtered_patents is not None:
                filtered_patents = filtered_patents[filtered_patents['label_m_title'].isin(filters['tech_filter'])]
        
        # 국가 필터
        if filters['country_filter'] and filtered_papers is not None:
            filtered_papers = filtered_papers[filtered_papers['Country'].isin(filters['country_filter'])]
            if filtered_patents is not None:
                filtered_patents = filtered_patents[filtered_patents['Country'].isin(filters['country_filter'])]
        
        # 시간 필터
        if filters['time_filter'] and filtered_papers is not None:
            start_year, end_year = filters['time_filter']
            # Year 컬럼을 숫자로 변환
            years = pd.to_numeric(filtered_papers['Year'], errors='coerce')
            mask = (years >= start_year) & (years <= end_year)
            filtered_papers = filtered_papers[mask.fillna(False)]
            
            if filtered_patents is not None:
                years_patents = pd.to_numeric(filtered_patents['Year'], errors='coerce')
                mask_patents = (years_patents >= start_year) & (years_patents <= end_year)
                filtered_patents = filtered_patents[mask_patents.fillna(False)]
        
        return filtered_papers, filtered_patents
    
    except Exception as e:
        st.error(f"데이터 필터링 중 오류: {e}")
        return papers_df, patents_df

def main():
    """메인 함수"""
    # 제목
    st.markdown("""
    <div class="main-header">
        <h1>🎯 기술수준조사 전문가 평가 대시보드</h1>
        <p>논문/특허 데이터 기반 종합 분석 · 전문가 의사결정 지원 시스템</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 데이터 로드
    if not IMPORTS_SUCCESSFUL:
        st.error("필수 모듈을 로드할 수 없습니다.")
        return
    
    papers_df, patents_df = load_data()
    
    if papers_df is None and patents_df is None:
        st.error("분석할 데이터가 없습니다. 데이터 파일을 확인해주세요.")
        return
    
    # 사이드바 컨트롤
    filters = render_sidebar_controls(papers_df, patents_df)
    
    # 데이터 필터링
    filtered_papers, filtered_patents = apply_data_filters(papers_df, patents_df, filters)
    
    # 요약 통계
    summary_stats = get_summary_stats(filtered_papers, filtered_patents)
    
    # 필터 적용 현황 표시
    if any([filters['tech_filter'], filters['country_filter'], filters['time_filter']]):
        st.info("🔍 **활성 필터**: " + 
               (f"기술분야 {len(filters['tech_filter'])}개 " if filters['tech_filter'] else "") +
               (f"국가 {len(filters['country_filter'])}개 " if filters['country_filter'] else "") +
               (f"기간 {filters['time_filter'][0]}-{filters['time_filter'][1]}년 " if filters['time_filter'] else ""))
    
    # 1. 요약 메트릭
    render_summary_metrics(summary_stats)
    st.markdown("---")
    
    # 2. 연구 품질 & 혁신 분석
    col1, col2 = st.columns(2)
    with col1:
        render_research_quality_analysis(filtered_papers)
    with col2:
        render_innovation_analysis(filtered_patents)
    
    st.markdown("---")
    
    # 3. 기본 트렌드 분석 (기존 컴포넌트 사용)
    if IMPORTS_SUCCESSFUL:
        render_basic_timeseries(filtered_papers, filtered_patents)
        st.markdown("---")
    
    # 4. 국가별 비교
    render_country_comparison(filtered_papers, filtered_patents)
    st.markdown("---")
    
    # 5. 국가별 트렌드 (직접 구현)
    render_country_trends_simple(filtered_papers, filtered_patents, top_n=10)
        st.markdown("---")
    
    # 6. 기술 분야 트렌드
    render_technology_trends(filtered_papers)
    st.markdown("---")
    
    # 7. 종합 순위
    render_comprehensive_ranking(filtered_papers, filtered_patents)
    
    # 사이드바 요약
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 데이터 현황")
    
    if filtered_papers is not None:
        paper_count = len(filtered_papers)
        paper_sum = filtered_papers['Total_Papers'].sum()
        st.sidebar.metric("논문 레코드", f"{paper_count:,}")
        st.sidebar.metric("총 논문 수", f"{paper_sum:,}")
    
    if filtered_patents is not None:
        patent_count = len(filtered_patents)
        patent_sum = filtered_patents['Total_Papers'].sum()
        st.sidebar.metric("특허 레코드", f"{patent_count:,}")
        st.sidebar.metric("총 특허 수", f"{patent_sum:,}")

if __name__ == "__main__":
    main()