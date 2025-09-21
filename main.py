"""
기술수준조사 서지분석 대시보드 - 메인 (Year 컬럼 안전 처리)
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

def safe_get_year_data(df, year_col='Year'):
    """Year 컬럼을 안전하게 처리하는 함수"""
    if df is None or df.empty or year_col not in df.columns:
        return df, []
    
    try:
        # Year 컬럼을 숫자로 변환
        df_clean = df.copy()
        df_clean['Year_numeric'] = pd.to_numeric(df_clean[year_col], errors='coerce')
        df_clean = df_clean.dropna(subset=['Year_numeric'])
        
        # 유효한 연도 목록
        valid_years = sorted(df_clean['Year_numeric'].unique())
        
        return df_clean, valid_years
    except Exception:
        return df, []

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
    """논문의 질적지표 비교"""
    if papers_df is None or papers_df.empty:
        st.warning("논문 데이터가 없습니다.")
        return
    
    st.subheader("🔬 논문의 질적지표 비교")
    
    try:
        # 상위 10개국 선정
        top_countries = papers_df.groupby('Country')['Total_Papers'].sum().nlargest(10).index.tolist()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 1. 국가별 Q1-Q4 스택형 차트
            if all(col in papers_df.columns for col in ['Q1', 'Q2', 'Q3', 'Q4']):
                import plotly.express as px
                import plotly.graph_objects as go
                
                country_q_data = papers_df[papers_df['Country'].isin(top_countries)].groupby('Country')[['Q1', 'Q2', 'Q3', 'Q4']].sum()
                
                fig_stack = go.Figure()
                fig_stack.add_trace(go.Bar(name='Q1', x=country_q_data.index, y=country_q_data['Q1']))
                fig_stack.add_trace(go.Bar(name='Q2', x=country_q_data.index, y=country_q_data['Q2']))
                fig_stack.add_trace(go.Bar(name='Q3', x=country_q_data.index, y=country_q_data['Q3']))
                fig_stack.add_trace(go.Bar(name='Q4', x=country_q_data.index, y=country_q_data['Q4']))
                
                fig_stack.update_layout(
                    barmode='stack',
                    title='국가별 저널 품질 분포 (Q1-Q4)',
                    height=400,
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig_stack, use_container_width=True)
        
        with col2:
            # 2. 최근5년/과거5년 Q1비율 비교
            if 'Q1_Ratio(%)' in papers_df.columns:
                papers_clean, valid_years = safe_get_year_data(papers_df)
                
                if valid_years and len(valid_years) >= 10:
                    recent_years = sorted(valid_years)[-5:]
                    past_years = sorted(valid_years)[-10:-5]
                    
                    recent_data = papers_clean[papers_clean['Year_numeric'].isin(recent_years)]
                    past_data = papers_clean[papers_clean['Year_numeric'].isin(past_years)]
                    
                    recent_q1 = recent_data[recent_data['Country'].isin(top_countries)].groupby('Country')['Q1_Ratio(%)'].mean()
                    past_q1 = past_data[past_data['Country'].isin(top_countries)].groupby('Country')['Q1_Ratio(%)'].mean()
                    
                    comparison_df = pd.DataFrame({
                        '과거5년': past_q1,
                        '최근5년': recent_q1
                    }).fillna(0)
                    
                    fig_comp = px.bar(
                        comparison_df,
                        title='최근5년 vs 과거5년 Q1 비율 비교',
                        barmode='group'
                    )
                    fig_comp.update_layout(height=400, xaxis_tickangle=-45)
                    st.plotly_chart(fig_comp, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # 3. 국가별 누적 피인용 규모
            if 'Total_Citations' in papers_df.columns:
                papers_clean, valid_years = safe_get_year_data(papers_df)
                
                if valid_years and not papers_clean.empty:
                    citation_data = papers_clean[papers_clean['Country'].isin(top_countries[:5])].groupby(['Year_numeric', 'Country'])['Total_Citations'].sum().reset_index()
                    citation_data.columns = ['Year', 'Country', 'Total_Citations']
                    
                    fig_citation = px.line(
                        citation_data,
                        x='Year',
                        y='Total_Citations',
                        color='Country',
                        title='국가별 연도별 총 피인용수',
                        markers=True
                    )
                    fig_citation.update_layout(height=400)
                    st.plotly_chart(fig_citation, use_container_width=True)
        
        with col4:
            # 4. H-Index와 Avg_mrnif 시계열
            if 'H_Index' in papers_df.columns:
                papers_clean, valid_years = safe_get_year_data(papers_df)
                
                if valid_years and not papers_clean.empty:
                    h_index_data = papers_clean[papers_clean['Country'].isin(top_countries[:5])].groupby(['Year_numeric', 'Country'])['H_Index'].mean().reset_index()
                    h_index_data.columns = ['Year', 'Country', 'H_Index']
                    
                    fig_h_index = px.line(
                        h_index_data,
                        x='Year',
                        y='H_Index',
                        color='Country',
                        title='국가별 H-Index 추이',
                        markers=True
                    )
                    fig_h_index.update_layout(height=400)
                    st.plotly_chart(fig_h_index, use_container_width=True)
    
    except Exception as e:
        st.error(f"논문 질적지표 분석 오류: {e}")

def render_innovation_analysis(patents_df):
    """특허의 질적지표 비교"""
    if patents_df is None or patents_df.empty:
        st.warning("특허 데이터가 없습니다.")
        return
    
    st.subheader("💡 특허의 질적지표 비교")
    
    try:
        import plotly.express as px
        
        # 상위 10개국 선정
        top_countries = patents_df.groupby('Country')['Total_Papers'].sum().nlargest(10).index.tolist()
        patents_clean, valid_years = safe_get_year_data(patents_df)
        
        if not valid_years or len(valid_years) < 10:
            st.warning("충분한 연도 데이터가 없습니다.")
            return
        
        recent_years = sorted(valid_years)[-5:]
        past_years = sorted(valid_years)[-10:-5]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 1. IP4 특허 수 비교
            if 'ip4_count' in patents_df.columns:
                recent_data = patents_clean[patents_clean['Year_numeric'].isin(recent_years)]
                past_data = patents_clean[patents_clean['Year_numeric'].isin(past_years)]
                
                recent_ip4 = recent_data[recent_data['Country'].isin(top_countries)].groupby('Country')['ip4_count'].sum()
                past_ip4 = past_data[past_data['Country'].isin(top_countries)].groupby('Country')['ip4_count'].sum()
                
                ip4_comparison = pd.DataFrame({
                    '과거5년': past_ip4,
                    '최근5년': recent_ip4
                }).fillna(0)
                
                fig_ip4 = px.bar(
                    ip4_comparison,
                    title='IP4 특허 수 비교 (과거5년 vs 최근5년)',
                    barmode='group'
                )
                fig_ip4.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig_ip4, use_container_width=True)
        
        with col2:
            # 2. 특허 피인용수 비교
            if 'total_citations' in patents_df.columns:
                recent_citations = recent_data[recent_data['Country'].isin(top_countries)].groupby('Country')['total_citations'].sum()
                past_citations = past_data[past_data['Country'].isin(top_countries)].groupby('Country')['total_citations'].sum()
                
                citations_comparison = pd.DataFrame({
                    '과거5년': past_citations,
                    '최근5년': recent_citations
                }).fillna(0)
                
                fig_citations = px.bar(
                    citations_comparison,
                    title='특허 피인용수 비교 (과거5년 vs 최근5년)',
                    barmode='group'
                )
                fig_citations.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig_citations, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # 3. 총 청구항 수 비교
            if 'total_claims' in patents_df.columns:
                recent_claims = recent_data[recent_data['Country'].isin(top_countries)].groupby('Country')['total_claims'].sum()
                past_claims = past_data[past_data['Country'].isin(top_countries)].groupby('Country')['total_claims'].sum()
                
                claims_comparison = pd.DataFrame({
                    '과거5년': past_claims,
                    '최근5년': recent_claims
                }).fillna(0)
                
                fig_claims = px.bar(
                    claims_comparison,
                    title='총 청구항 수 비교 (과거5년 vs 최근5년)',
                    barmode='group'
                )
                fig_claims.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig_claims, use_container_width=True)
        
        with col4:
            # 4. 해외출원 강도 비교
            if 'foreign_filing_intensity' in patents_df.columns:
                recent_foreign = recent_data[recent_data['Country'].isin(top_countries)].groupby('Country')['foreign_filing_intensity'].mean()
                past_foreign = past_data[past_data['Country'].isin(top_countries)].groupby('Country')['foreign_filing_intensity'].mean()
                
                foreign_comparison = pd.DataFrame({
                    '과거5년': past_foreign,
                    '최근5년': recent_foreign
                }).fillna(0)
                
                fig_foreign = px.bar(
                    foreign_comparison,
                    title='해외출원 강도 비교 (과거5년 vs 최근5년)',
                    barmode='group'
                )
                fig_foreign.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig_foreign, use_container_width=True)
    
    except Exception as e:
        st.error(f"특허 질적지표 분석 오류: {e}")

def render_country_comparison(papers_df, patents_df):
    """국가별 비교"""
    st.subheader("🌍 국가별 성과 비교")
    
    if papers_df is None or papers_df.empty:
        st.warning("국가별 분석을 위한 데이터가 없습니다.")
        return
    
    try:
        # 상위 15개국
        top_countries = papers_df.groupby('Country')['Total_Papers'].sum().nlargest(15)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 논문 수 순위 - 세로형 바차트 + 숫자 표기
            import plotly.express as px
            fig_papers = px.bar(
                x=top_countries.index,
                y=top_countries.values,
                title='상위 15개국 논문 수',
                labels={'x': '국가', 'y': '논문 수'},
                text=top_countries.values
            )
            fig_papers.update_traces(texttemplate='%{text:,}', textposition='outside')
            fig_papers.update_layout(height=500, xaxis_tickangle=-45)
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
    except Exception as e:
        st.error(f"국가별 비교 분석 오류: {e}")

def render_technology_trends(papers_df):
    """기술 분야별 트렌드"""
    if papers_df is None or papers_df.empty or 'label_s_title' not in papers_df.columns:
        st.warning("기술 분야 분석을 위한 데이터가 없습니다.")
        return
    
    st.subheader("🚀 기술 분야별 트렌드")
    
    try:
        # 상위 10개 기술 분야
        top_techs = papers_df.groupby('label_s_title')['Total_Papers'].sum().nlargest(10)
        
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
            papers_clean, valid_years = safe_get_year_data(papers_df)
            
            if valid_years and not papers_clean.empty:
                import plotly.express as px
                top_5_techs = top_techs.head(5).index.tolist()
                tech_yearly = papers_clean[papers_clean['label_s_title'].isin(top_5_techs)].groupby(['Year_numeric', 'label_s_title'])['Total_Papers'].sum().reset_index()
                tech_yearly.columns = ['Year', 'label_s_title', 'Total_Papers']
                
                fig_tech_trend = px.line(
                    tech_yearly,
                    x='Year',
                    y='Total_Papers',
                    color='label_s_title',
                    title='주요 기술 분야 연도별 추이',
                    markers=True
                )
                fig_tech_trend.update_layout(height=400)
                st.plotly_chart(fig_tech_trend, use_container_width=True)
            else:
                st.warning("기술 분야 시계열 데이터가 없습니다.")
    except Exception as e:
        st.error(f"기술 분야 트렌드 분석 오류: {e}")

def render_country_trends_simple(papers_df, patents_df, top_n=10):
    """국가별 연도별 순위 트렌드"""
    if papers_df is None or papers_df.empty:
        st.warning("국가별 트렌드 분석을 위한 데이터가 없습니다.")
        return
    
    st.subheader("🌍 상위 국가별 연도별 순위 트렌드")
    
    try:
        import plotly.express as px
        
        # 상위 국가 선택
        top_countries = papers_df.groupby('Country')['Total_Papers'].sum().nlargest(top_n).index.tolist()
        
        # Year 컬럼 안전 처리
        papers_clean, valid_years = safe_get_year_data(papers_df)
        
        if valid_years and not papers_clean.empty:
            # 연도별 국가별 데이터 (피인용수 포함)
            country_yearly = papers_clean[papers_clean['Country'].isin(top_countries)].groupby(['Year_numeric', 'Country']).agg({
                'Total_Papers': 'sum',
                'Total_Citations': 'sum' if 'Total_Citations' in papers_clean.columns else lambda x: 0
            }).reset_index()
            country_yearly.columns = ['Year', 'Country', 'Total_Papers', 'Total_Citations']
            
            # 연도별 순위 계산
            country_yearly['Rank'] = country_yearly.groupby('Year')['Total_Papers'].rank(method='dense', ascending=False)
            
            # 애니메이션 바 차트 (순위 기반)
            fig = px.bar(
                country_yearly,
                x='Total_Papers',
                y='Country',
                orientation='h',
                animation_frame='Year',
                color='Total_Citations' if 'Total_Citations' in country_yearly.columns else 'Total_Papers',
                title=f'상위 {top_n}개국 연도별 논문 수 순위 변화',
                labels={'Total_Papers': '논문 수', 'Total_Citations': '피인용수'},
                range_x=[0, country_yearly['Total_Papers'].max() * 1.1],
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(
                height=600,
                yaxis={'categoryorder': 'total ascending'},
                showlegend=False
            )
            
            # 애니메이션 속도 조정
            fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1000
            fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 500
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 국가별 요약 통계
            st.subheader("📊 상위 국가 요약 통계")
            country_stats = papers_df[papers_df['Country'].isin(top_countries)].groupby('Country').agg({
                'Total_Papers': 'sum',
                'Q1_Ratio(%)': 'mean' if 'Q1_Ratio(%)' in papers_df.columns else lambda x: 0,
                'Avg_Citations': 'mean' if 'Avg_Citations' in papers_df.columns else lambda x: 0
            }).round(2)
            country_stats = country_stats.sort_values('Total_Papers', ascending=False)
            country_stats.insert(0, '순위', range(1, len(country_stats) + 1))
            
            st.dataframe(country_stats, use_container_width=True)
        else:
            st.warning("국가별 트렌드 데이터가 없습니다.")
    except Exception as e:
        st.error(f"국가별 트렌드 분석 오류: {e}")

def render_comprehensive_ranking(papers_df, patents_df):
    """종합 순위"""
    st.subheader("🏆 국가별 종합 순위")
    
    if papers_df is None or papers_df.empty:
        st.warning("순위 분석을 위한 데이터가 없습니다.")
        return
    
    try:
        # 컬럼 존재 확인
        required_cols = ['Country', 'Total_Papers']
        missing_cols = [col for col in required_cols if col not in papers_df.columns]
        
        if missing_cols:
            st.error(f"필수 컬럼 누락: {missing_cols}")
            st.info("사용 가능한 컬럼:")
            st.write(list(papers_df.columns))
            return
        
        # 논문 데이터 집계
        paper_summary = papers_df.groupby('Country').agg({
            'Total_Papers': 'sum',
            'Q1_Ratio(%)': 'mean' if 'Q1_Ratio(%)' in papers_df.columns else lambda x: 0,
            'Avg_Citations': 'mean' if 'Avg_Citations' in papers_df.columns else lambda x: 0,
            'H_Index': 'mean' if 'H_Index' in papers_df.columns else lambda x: 0
        }).round(2)
        
        # 특허 데이터 집계 (있는 경우)
        if patents_df is not None and not patents_df.empty and 'Country' in patents_df.columns:
            # 특허 데이터의 실제 컬럼 확인
            patent_count_col = None
            for col in ['Total_Papers', 'total_papers', 'Patent_Count', 'count']:
                if col in patents_df.columns:
                    patent_count_col = col
                    break
            
            if patent_count_col:
                patent_agg = {patent_count_col: 'sum'}
                if 'triadic_count' in patents_df.columns:
                    patent_agg['triadic_count'] = 'sum'
                
                patent_summary = patents_df.groupby('Country').agg(patent_agg).round(2)
                patent_summary.columns = ['Patent_Count'] + (['Triadic_Count'] if 'triadic_count' in patents_df.columns else [])
                
                # 병합
                combined_ranking = paper_summary.merge(patent_summary, left_index=True, right_index=True, how='left')
                combined_ranking = combined_ranking.fillna(0)
            else:
                combined_ranking = paper_summary
        else:
            combined_ranking = paper_summary
        
        # 상위 20개국
        top_20 = combined_ranking.nlargest(20, 'Total_Papers')
        top_20.insert(0, '순위', range(1, len(top_20) + 1))
        
        st.dataframe(top_20, use_container_width=True)
        
    except Exception as e:
        st.error(f"종합 순위 분석 오류: {e}")
        # 디버깅 정보
        if papers_df is not None:
            st.write("논문 데이터 컬럼:", list(papers_df.columns))
        if patents_df is not None:
            st.write("특허 데이터 컬럼:", list(patents_df.columns))

def render_sidebar_controls(papers_df, patents_df):
    """사이드바 컨트롤 (단순화)"""
    st.sidebar.markdown("""
    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; color: white; margin-bottom: 1rem;'>
        <h2>🎯 기술수준조사</h2>
        <p>평가자료 분석</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 기술 분야 라디오 버튼으로 선택
    tech_filter = None
    if papers_df is not None and not papers_df.empty and 'label_m_title' in papers_df.columns:
        st.sidebar.subheader("🔬 기술 분야")
        
        try:
            tech_options = sorted(papers_df['label_m_title'].unique())
            selected_tech = st.sidebar.radio(
                "분석 대상 선택",
                options=['전체'] + tech_options,
                index=0
            )
            
            if selected_tech != '전체':
                tech_filter = [selected_tech]
        except Exception as e:
            st.sidebar.error(f"기술 분야 로드 오류: {e}")
    
    return {
        'tech_filter': tech_filter,
        'country_filter': None,
        'time_filter': None
    }

def apply_data_filters(papers_df, patents_df, filters):
    """데이터 필터 적용"""
    filtered_papers = papers_df.copy() if papers_df is not None else None
    filtered_patents = patents_df.copy() if patents_df is not None else None
    
    try:
        # 기술 분야 필터
        if filters['tech_filter'] and filtered_papers is not None and 'label_m_title' in filtered_papers.columns:
            filtered_papers = filtered_papers[filtered_papers['label_m_title'].isin(filters['tech_filter'])]
            if filtered_patents is not None and 'label_m_title' in filtered_patents.columns:
                filtered_patents = filtered_patents[filtered_patents['label_m_title'].isin(filters['tech_filter'])]
        
        # 국가 필터
        if filters['country_filter'] and filtered_papers is not None and 'Country' in filtered_papers.columns:
            filtered_papers = filtered_papers[filtered_papers['Country'].isin(filters['country_filter'])]
            if filtered_patents is not None and 'Country' in filtered_patents.columns:
                filtered_patents = filtered_patents[filtered_patents['Country'].isin(filters['country_filter'])]
        
        # 시간 필터
        if filters['time_filter'] and filtered_papers is not None and 'Year' in filtered_papers.columns:
            start_year, end_year = filters['time_filter']
            papers_clean, _ = safe_get_year_data(filtered_papers)
            if not papers_clean.empty:
                filtered_papers = papers_clean[(papers_clean['Year_numeric'] >= start_year) & (papers_clean['Year_numeric'] <= end_year)]
            
            if filtered_patents is not None and 'Year' in filtered_patents.columns:
                patents_clean, _ = safe_get_year_data(filtered_patents)
                if not patents_clean.empty:
                    filtered_patents = patents_clean[(patents_clean['Year_numeric'] >= start_year) & (patents_clean['Year_numeric'] <= end_year)]
        
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
    
    # 필터 적용 현황 표시 (기술 분야만)
    if filters['tech_filter']:
        st.info(f"🔬 **선택된 기술 분야**: {filters['tech_filter'][0]}")
    
    # 1. 요약 메트릭
    render_summary_metrics(summary_stats)
    st.markdown("---")
    
    # 2. 기본 트렌드 분석 (기존 컴포넌트 사용)
    if IMPORTS_SUCCESSFUL:
        render_basic_timeseries(filtered_papers, filtered_patents)
        st.markdown("---")
    
    # 3. 연구 품질 & 혁신 분석
    col1, col2 = st.columns(2)
    with col1:
        render_research_quality_analysis(filtered_papers)
    with col2:
        render_innovation_analysis(filtered_patents)
    
    st.markdown("---")
    
    # 4. 국가별 비교
    render_country_comparison(filtered_papers, filtered_patents)
    st.markdown("---")
    
    # 5. 국가별 트렌드
    render_country_trends_simple(filtered_papers, filtered_patents, top_n=10)
    st.markdown("---")
    
    # 6. 기술 분야 트렌드
    render_technology_trends(filtered_papers)
    st.markdown("---")
    
    # 7. 종합 순위
    render_comprehensive_ranking(filtered_papers, filtered_patents)

if __name__ == "__main__":
    main()