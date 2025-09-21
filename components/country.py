"""
국가별 비교 분석 컴포넌트
components/country.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def render_country_trends(papers_df: pd.DataFrame, patents_df: pd.DataFrame, top_n: int = 10):
    """국가별 트렌드 분석"""
    st.subheader("🌍 국가별 시계열 트렌드")
    
    if papers_df.empty or 'Country' not in papers_df.columns or 'Year' not in papers_df.columns:
        st.warning("국가별 시계열 데이터가 없습니다.")
        return []
    
    # 국가별 연도별 집계
    country_yearly = papers_df.groupby(['Year', 'Country']).size().reset_index(name='Count')
    
    # 상위 N개국 선택
    top_countries = papers_df['Country'].value_counts().head(top_n).index.tolist()
    country_yearly_filtered = country_yearly[country_yearly['Country'].isin(top_countries)]
    
    fig = px.line(
        country_yearly_filtered,
        x='Year',
        y='Count',
        color='Country',
        title=f'🌍 상위 {top_n}개국 연도별 논문 수 추이',
        markers=True
    )
    fig.update_traces(line_width=2, marker_size=6)
    fig.update_layout(height=500, legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig, use_container_width=True)
    
    return top_countries

def render_country_detail_analysis(papers_df: pd.DataFrame, selected_countries: list):
    """선택 국가 상세 분석"""
    if not selected_countries or papers_df.empty:
        return
    
    st.subheader("🔍 선택 국가 상세 분석")
    
    # 필터링된 데이터
    filtered_papers = papers_df[papers_df['Country'].isin(selected_countries)]
    
    if filtered_papers.empty:
        st.warning("선택된 국가의 데이터가 없습니다.")
        return
    
    # 연도별 추이
    country_yearly = filtered_papers.groupby(['Year', 'Country']).size().reset_index(name='Count')
    
    fig = px.line(
        country_yearly,
        x='Year',
        y='Count',
        color='Country',
        title='선택 국가 상세 트렌드',
        markers=True
    )
    fig.update_traces(line_width=3, marker_size=8)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # 국가별 요약 통계
    render_country_summary_stats(filtered_papers)

def render_country_summary_stats(papers_df: pd.DataFrame):
    """국가별 요약 통계"""
    if papers_df.empty or 'Country' not in papers_df.columns:
        return
    
    st.subheader("📊 국가별 요약 통계")
    
    # 국가별 집계
    country_stats = papers_df.groupby('Country').agg({
        'Year': ['min', 'max', 'nunique'],
        'Country': 'size'
    }).round(2)
    
    # 컬럼명 정리
    country_stats.columns = ['최초_연도', '최종_연도', '활동_연수', '총_논문수']
    country_stats = country_stats.reset_index()
    
    # 연평균 논문 수 계산
    country_stats['연평균_논문수'] = (country_stats['총_논문수'] / country_stats['활동_연수']).round(1)
    
    # 테이블 표시
    st.dataframe(country_stats, use_container_width=True, hide_index=True)

def render_country_comparison_matrix(papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """국가별 비교 매트릭스"""
    st.subheader("🎯 국가별 포지셔닝 매트릭스")
    
    if papers_df.empty or 'Country' not in papers_df.columns:
        st.warning("국가별 데이터가 없습니다.")
        return
    
    # 국가별 논문 수 집계
    paper_counts = papers_df['Country'].value_counts()
    
    # 특허 수 집계 (있는 경우)
    patent_counts = pd.Series(dtype=int)
    if not patents_df.empty and 'Country' in patents_df.columns:
        patent_counts = patents_df['Country'].value_counts()
    
    # 통합 데이터 생성
    comparison_data = []
    for country in paper_counts.index:
        comparison_data.append({
            'Country': country,
            'Papers': paper_counts.get(country, 0),
            'Patents': patent_counts.get(country, 0) if not patent_counts.empty else 0
        })
    
    if comparison_data:
        comp_df = pd.DataFrame(comparison_data)
        
        # 산점도 생성
        fig = px.scatter(
            comp_df,
            x='Papers',
            y='Patents',
            text='Country',
            title='국가별 논문 vs 특허 포지셔닝',
            size='Papers',
            hover_data=['Country', 'Papers', 'Patents']
        )
        
        # 텍스트 위치 조정
        fig.update_traces(textposition="top center")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # 사분면 분석
        render_quadrant_analysis(comp_df)

def render_quadrant_analysis(comp_df: pd.DataFrame):
    """사분면 분석"""
    if comp_df.empty:
        return
    
    # 중앙값 기준으로 사분면 나누기
    paper_median = comp_df['Papers'].median()
    patent_median = comp_df['Patents'].median()
    
    # 사분면 분류
    def classify_quadrant(row):
        if row['Papers'] >= paper_median and row['Patents'] >= patent_median:
            return "🟢 리더 (High-High)"
        elif row['Papers'] >= paper_median and row['Patents'] < patent_median:
            return "🔵 연구 중심 (High-Low)"
        elif row['Papers'] < paper_median and row['Patents'] >= patent_median:
            return "🟡 상용화 중심 (Low-High)"
        else:
            return "🔴 신흥 국가 (Low-Low)"
    
    comp_df['Quadrant'] = comp_df.apply(classify_quadrant, axis=1)
    
    # 사분면별 국가 수
    quadrant_counts = comp_df['Quadrant'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**사분면별 국가 분포:**")
        for quadrant, count in quadrant_counts.items():
            st.write(f"- {quadrant}: {count}개국")
    
    with col2:
        # 각 사분면의 대표 국가
        st.write("**사분면별 대표 국가:**")
        for quadrant in quadrant_counts.index:
            countries = comp_df[comp_df['Quadrant'] == quadrant]['Country'].head(3).tolist()
            st.write(f"- {quadrant}: {', '.join(countries)}")

def render_country_ranking(papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """국가별 순위"""
    st.subheader("🏆 국가별 순위")
    
    tab1, tab2, tab3 = st.tabs(["📄 논문 순위", "⚖️ 특허 순위", "🌟 종합 순위"])
    
    with tab1:
        if not papers_df.empty and 'Country' in papers_df.columns:
            paper_ranking = papers_df['Country'].value_counts().reset_index()
            paper_ranking.columns = ['국가', '논문 수']
            paper_ranking['순위'] = range(1, len(paper_ranking) + 1)
            
            # 상위 20개국만 표시
            st.dataframe(
                paper_ranking.head(20)[['순위', '국가', '논문 수']], 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("논문 데이터가 없습니다.")
    
    with tab2:
        if not patents_df.empty and 'Country' in patents_df.columns:
            patent_ranking = patents_df['Country'].value_counts().reset_index()
            patent_ranking.columns = ['국가', '특허 수']
            patent_ranking['순위'] = range(1, len(patent_ranking) + 1)
            
            st.dataframe(
                patent_ranking.head(20)[['순위', '국가', '특허 수']], 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("특허 데이터가 없습니다.")
    
    with tab3:
        # 종합 순위 (논문 + 특허)
        if not papers_df.empty and 'Country' in papers_df.columns:
            paper_counts = papers_df['Country'].value_counts()
            patent_counts = patents_df['Country'].value_counts() if not patents_df.empty and 'Country' in patents_df.columns else pd.Series(dtype=int)
            
            # 통합 순위 계산
            all_countries = set(paper_counts.index) | set(patent_counts.index)
            combined_ranking = []
            
            for country in all_countries:
                papers = paper_counts.get(country, 0)
                patents = patent_counts.get(country, 0)
                total = papers + patents
                
                combined_ranking.append({
                    '국가': country,
                    '논문 수': papers,
                    '특허 수': patents,
                    '총합': total
                })
            
            combined_df = pd.DataFrame(combined_ranking)
            combined_df = combined_df.sort_values('총합', ascending=False).reset_index(drop=True)
            combined_df['순위'] = range(1, len(combined_df) + 1)
            
            st.dataframe(
                combined_df.head(20)[['순위', '국가', '논문 수', '특허 수', '총합']], 
                use_container_width=True, 
                hide_index=True
            )

def render_country_growth_analysis(papers_df: pd.DataFrame):
    """국가별 성장 분석"""
    if papers_df.empty or 'Country' not in papers_df.columns or 'Year' not in papers_df.columns:
        return
    
    st.subheader("📈 국가별 성장률 분석")
    
    # 상위 10개국의 성장률 계산
    top_countries = papers_df['Country'].value_counts().head(10).index.tolist()
    
    growth_data = []
    for country in top_countries:
        country_data = papers_df[papers_df['Country'] == country]
        yearly_counts = country_data.groupby('Year').size()
        
        if len(yearly_counts) > 1:
            # 연평균 성장률 계산
            first_year_count = yearly_counts.iloc[0]
            last_year_count = yearly_counts.iloc[-1]
            years_span = yearly_counts.index[-1] - yearly_counts.index[0]
            
            if years_span > 0 and first_year_count > 0:
                cagr = ((last_year_count / first_year_count) ** (1/years_span) - 1) * 100
                growth_data.append({
                    'Country': country,
                    'CAGR': cagr,
                    'First_Year': yearly_counts.index[0],
                    'Last_Year': yearly_counts.index[-1],
                    'Growth_Period': years_span
                })
    
    if growth_data:
        growth_df = pd.DataFrame(growth_data)
        growth_df = growth_df.sort_values('CAGR', ascending=False)
        
        # 성장률 차트
        fig = px.bar(
            growth_df,
            x='Country',
            y='CAGR',
            title='상위 10개국 연평균 성장률 (CAGR)',
            color='CAGR',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # 성장률 테이블
        display_growth = growth_df.copy()
        display_growth['CAGR'] = display_growth['CAGR'].round(2)
        display_growth.columns = ['국가', '연평균성장률(%)', '시작연도', '종료연도', '분석기간(년)']
        
        st.dataframe(display_growth, use_container_width=True, hide_index=True)

def render_regional_analysis(papers_df: pd.DataFrame):
    """지역별 분석 (간단한 버전)"""
    if papers_df.empty or 'Country' not in papers_df.columns:
        return
    
    st.subheader("🌏 지역별 분석")
    
    # 간단한 지역 분류
    region_mapping = {
        '미국': '북미',
        '캐나다': '북미',
        '영국': '유럽',
        '독일': '유럽',
        '프랑스': '유럽',
        '이탈리아': '유럽',
        '스페인': '유럽',
        'EU': '유럽',
        '일본': '아시아',
        '중국': '아시아',
        '한국': '아시아',
        '인도': '아시아',
        '호주': '오세아니아',
        '뉴질랜드': '오세아니아'
    }
    
    # 지역 분류 적용
    papers_df_region = papers_df.copy()
    papers_df_region['Region'] = papers_df_region['Country'].map(region_mapping).fillna('기타')
    
    # 지역별 집계
    region_counts = papers_df_region['Region'].value_counts()
    
    if len(region_counts) > 1:
        # 파이 차트
        fig = px.pie(
            values=region_counts.values,
            names=region_counts.index,
            title='지역별 논문 분포'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # 지역별 통계
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**지역별 논문 수:**")
            for region, count in region_counts.items():
                percentage = (count / region_counts.sum()) * 100
                st.write(f"- {region}: {count:,}편 ({percentage:.1f}%)")
        
        with col2:
            if 'Year' in papers_df_region.columns:
                # 지역별 평균 연도 (활동 시기)
                region_years = papers_df_region.groupby('Region')['Year'].agg(['min', 'max', 'mean']).round(1)
                region_years.columns = ['최초연도', '최종연도', '평균연도']
                st.write("**지역별 활동 시기:**")
                st.dataframe(region_years, use_container_width=True)