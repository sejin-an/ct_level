"""
향상된 전문가용 평가자료 메트릭 컴포넌트
components/enhanced_metrics.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def render_expert_summary_dashboard(papers_df, patents_df):
    """전문가용 종합 요약 대시보드"""
    st.header("🎯 기술수준 평가 종합 요약")
    
    # 핵심 지표 요약
    render_technology_excellence_metrics(papers_df, patents_df)
    st.markdown("---")
    
    # 기술 분야별 경쟁력 비교
    render_technology_competitiveness_matrix(papers_df, patents_df)
    st.markdown("---")
    
    # 국가별 기술 포지셔닝
    render_country_technology_positioning(papers_df, patents_df)

def render_technology_excellence_metrics(papers_df, patents_df):
    """기술 우수성 핵심 지표"""
    st.subheader("🏆 기술 우수성 핵심 지표")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_research_quality_score(papers_df)
    
    with col2:
        render_innovation_impact_score(patents_df)
    
    with col3:
        render_global_competitiveness_index(papers_df, patents_df)
    
    with col4:
        render_technology_maturity_index(papers_df, patents_df)

def render_research_quality_score(papers_df):
    """연구 품질 점수"""
    try:
        if papers_df is None or papers_df.empty:
            st.metric("🔬 연구 품질 점수", "N/A")
            return
        
        # Q1 비율과 H-Index를 활용한 품질 점수 계산
        if 'Q1_Ratio(%)' in papers_df.columns and 'H_Index' in papers_df.columns:
            # 최신 3년 데이터로 계산
            recent_years = papers_df['Year'].nlargest(3).unique()
            recent_data = papers_df[papers_df['Year'].isin(recent_years)]
            
            avg_q1_ratio = recent_data['Q1_Ratio(%)'].mean()
            avg_h_index = recent_data['H_Index'].mean()
            
            # 정규화된 품질 점수 (0-100)
            quality_score = min(100, (avg_q1_ratio * 0.6 + (avg_h_index / 200) * 100 * 0.4))
            
            # 등급 분류
            if quality_score >= 80:
                grade = "A+ 우수"
                color = "normal"
            elif quality_score >= 70:
                grade = "A 양호"
                color = "normal"
            elif quality_score >= 60:
                grade = "B 보통"
                color = "inverse"
            else:
                grade = "C 개선필요"
                color = "inverse"
            
            st.metric(
                "🔬 연구 품질 점수",
                f"{quality_score:.1f}점",
                delta=grade,
                delta_color=color,
                help=f"Q1 비율: {avg_q1_ratio:.1f}%, H-Index: {avg_h_index:.1f}"
            )
        else:
            st.metric("🔬 연구 품질 점수", "데이터 부족")
            
    except Exception as e:
        st.metric("🔬 연구 품질 점수", "계산 오류")

def render_innovation_impact_score(patents_df):
    """혁신 영향력 점수"""
    try:
        if patents_df is None or patents_df.empty:
            st.metric("💡 혁신 영향력 점수", "N/A")
            return
        
        # Triadic 특허와 중요 특허 비율로 계산
        if 'triadic_count' in patents_df.columns and 'important_patents_count' in patents_df.columns:
            recent_years = patents_df['Year'].nlargest(3).unique()
            recent_data = patents_df[patents_df['Year'].isin(recent_years)]
            
            total_patents = recent_data['Total_Papers'].sum()
            triadic_patents = recent_data['triadic_count'].sum()
            important_patents = recent_data['important_patents_count'].sum()
            
            if total_patents > 0:
                triadic_ratio = (triadic_patents / total_patents) * 100
                important_ratio = (important_patents / total_patents) * 100
                
                # 혁신 점수 계산
                innovation_score = min(100, triadic_ratio * 0.6 + important_ratio * 0.4)
                
                if innovation_score >= 15:
                    grade = "A+ 혁신적"
                    color = "normal"
                elif innovation_score >= 10:
                    grade = "A 우수"
                    color = "normal"
                elif innovation_score >= 5:
                    grade = "B 보통"
                    color = "inverse"
                else:
                    grade = "C 개선필요"
                    color = "inverse"
                
                st.metric(
                    "💡 혁신 영향력 점수",
                    f"{innovation_score:.1f}점",
                    delta=grade,
                    delta_color=color,
                    help=f"Triadic: {triadic_ratio:.1f}%, 중요특허: {important_ratio:.1f}%"
                )
            else:
                st.metric("💡 혁신 영향력 점수", "0점")
        else:
            st.metric("💡 혁신 영향력 점수", "데이터 부족")
            
    except Exception as e:
        st.metric("💡 혁신 영향력 점수", "계산 오류")

def render_global_competitiveness_index(papers_df, patents_df):
    """글로벌 경쟁력 지수"""
    try:
        # 논문과 특허의 복합 지수
        paper_score = 0
        patent_score = 0
        
        if papers_df is not None and not papers_df.empty:
            total_papers = papers_df['Total_Papers'].sum()
            paper_score = min(50, np.log10(max(1, total_papers)) * 10)
        
        if patents_df is not None and not patents_df.empty:
            total_patents = patents_df['Total_Papers'].sum()
            patent_score = min(50, np.log10(max(1, total_patents)) * 10)
        
        competitiveness_index = paper_score + patent_score
        
        if competitiveness_index >= 80:
            level = "글로벌 리더"
            color = "normal"
        elif competitiveness_index >= 60:
            level = "선진국 수준"
            color = "normal"
        elif competitiveness_index >= 40:
            level = "중진국 수준"
            color = "inverse"
        else:
            level = "개발도상국"
            color = "inverse"
        
        st.metric(
            "🌍 글로벌 경쟁력",
            f"{competitiveness_index:.0f}점",
            delta=level,
            delta_color=color,
            help="논문/특허 규모 및 품질 종합 평가"
        )
        
    except Exception as e:
        st.metric("🌍 글로벌 경쟁력", "계산 오류")

def render_technology_maturity_index(papers_df, patents_df):
    """기술 성숙도 지수"""
    try:
        maturity_score = 50  # 기본값
        
        # 논문-특허 비율로 성숙도 판단
        if papers_df is not None and patents_df is not None:
            paper_count = len(papers_df)
            patent_count = len(patents_df)
            total_count = paper_count + patent_count
            
            if total_count > 0:
                patent_ratio = (patent_count / total_count) * 100
                
                # 특허 비율이 높을수록 상용화에 가까움
                if patent_ratio >= 40:
                    maturity_score = 85
                    level = "상용화 단계"
                    color = "normal"
                elif patent_ratio >= 25:
                    maturity_score = 70
                    level = "개발 후기"
                    color = "normal"
                elif patent_ratio >= 15:
                    maturity_score = 55
                    level = "개발 중기"
                    color = "inverse"
                else:
                    maturity_score = 35
                    level = "연구 단계"
                    color = "inverse"
                
                st.metric(
                    "🔄 기술 성숙도",
                    f"{maturity_score:.0f}점",
                    delta=level,
                    delta_color=color,
                    help=f"특허 비율: {patent_ratio:.1f}%"
                )
            else:
                st.metric("🔄 기술 성숙도", "N/A")
        else:
            st.metric("🔄 기술 성숙도", "데이터 부족")
            
    except Exception as e:
        st.metric("🔄 기술 성숙도", "계산 오류")

def render_technology_competitiveness_matrix(papers_df, patents_df):
    """기술 분야별 경쟁력 매트릭스"""
    st.subheader("📊 기술 분야별 경쟁력 분석")
    
    if papers_df is None or papers_df.empty:
        st.warning("논문 데이터가 없어 기술 분야별 분석을 할 수 없습니다.")
        return
    
    try:
        # Label_m별 종합 분석
        if 'label_m_title' in papers_df.columns:
            # 기술 분야별 집계
            tech_analysis = []
            
            for label_m in papers_df['Label_m'].unique():
                paper_data = papers_df[papers_df['Label_m'] == label_m]
                patent_data = patents_df[patents_df['Label_m'] == label_m] if patents_df is not None else pd.DataFrame()
                
                tech_title = paper_data['label_m_title'].iloc[0] if not paper_data.empty else f"기술분야 {label_m}"
                
                # 논문 지표
                paper_count = paper_data['Total_Papers'].sum()
                avg_citations = paper_data['Avg_Citations'].mean() if 'Avg_Citations' in paper_data.columns else 0
                q1_ratio = paper_data['Q1_Ratio(%)'].mean() if 'Q1_Ratio(%)' in paper_data.columns else 0
                
                # 특허 지표
                patent_count = patent_data['Total_Papers'].sum() if not patent_data.empty else 0
                triadic_count = patent_data['triadic_count'].sum() if not patent_data.empty and 'triadic_count' in patent_data.columns else 0
                
                # 종합 점수 계산
                research_intensity = min(100, np.log10(max(1, paper_count)) * 25)
                quality_score = min(100, q1_ratio * 1.2)
                innovation_score = min(100, (triadic_count / max(1, patent_count)) * 100 * 5) if patent_count > 0 else 0
                
                tech_analysis.append({
                    '기술분야': tech_title,
                    '논문수': paper_count,
                    '특허수': patent_count,
                    '연구집약도': research_intensity,
                    '품질점수': quality_score,
                    '혁신점수': innovation_score,
                    'Q1비율': q1_ratio,
                    '평균인용': avg_citations
                })
            
            if tech_analysis:
                tech_df = pd.DataFrame(tech_analysis)
                
                # 상위 10개 기술분야만 표시
                tech_df_top = tech_df.nlargest(10, '논문수')
                
                # 버블 차트: 품질 vs 혁신
                fig = px.scatter(
                    tech_df_top,
                    x='품질점수',
                    y='혁신점수',
                    size='논문수',
                    color='연구집약도',
                    hover_name='기술분야',
                    title='기술분야별 품질-혁신 포지셔닝',
                    labels={
                        '품질점수': '연구 품질 (Q1 비율 기준)',
                        '혁신점수': '혁신 영향력 (Triadic 특허 기준)',
                        '연구집약도': '연구 집약도'
                    },
                    color_continuous_scale='Viridis'
                )
                fig.update_traces(marker=dict(line=dict(width=1, color='white')))
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                # 상세 테이블
                st.subheader("📋 기술분야별 상세 지표")
                display_df = tech_df_top.copy()
                for col in ['연구집약도', '품질점수', '혁신점수', 'Q1비율', '평균인용']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].round(1)
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"기술 분야별 경쟁력 분석 오류: {e}")

def render_country_technology_positioning(papers_df, patents_df):
    """국가별 기술 포지셔닝"""
    st.subheader("🌍 주요국 기술 포지셔닝")
    
    if papers_df is None or papers_df.empty:
        st.warning("국가별 분석을 위한 데이터가 없습니다.")
        return
    
    try:
        # 상위 15개국 분석
        top_countries = papers_df.groupby('Country')['Total_Papers'].sum().nlargest(15).index
        
        country_analysis = []
        
        for country in top_countries:
            paper_data = papers_df[papers_df['Country'] == country]
            patent_data = patents_df[patents_df['Country'] == country] if patents_df is not None else pd.DataFrame()
            
            # 논문 지표
            total_papers = paper_data['Total_Papers'].sum()
            avg_citations = paper_data['Total_Citations'].sum() / max(1, total_papers)
            q1_papers = paper_data['Q1'].sum() if 'Q1' in paper_data.columns else 0
            h_index_avg = paper_data['H_Index'].mean() if 'H_Index' in paper_data.columns else 0
            
            # 특허 지표
            total_patents = patent_data['Total_Papers'].sum() if not patent_data.empty else 0
            triadic_patents = patent_data['triadic_count'].sum() if not patent_data.empty and 'triadic_count' in patent_data.columns else 0
            important_patents = patent_data['important_patents_count'].sum() if not patent_data.empty and 'important_patents_count' in patent_data.columns else 0
            
            # 종합 점수 계산
            research_scale = min(100, np.log10(max(1, total_papers)) * 20)
            research_quality = min(100, (q1_papers / max(1, total_papers)) * 100 * 2)
            innovation_power = min(100, (triadic_patents / max(1, total_patents)) * 100 * 3) if total_patents > 0 else 0
            
            country_analysis.append({
                '국가': country,
                '논문수': total_papers,
                '특허수': total_patents,
                '연구규모': research_scale,
                '연구품질': research_quality,
                '혁신역량': innovation_power,
                '평균인용': avg_citations,
                'H지수': h_index_avg
            })
        
        if country_analysis:
            country_df = pd.DataFrame(country_analysis)
            
            # 3D 산점도: 규모-품질-혁신
            fig = px.scatter_3d(
                country_df,
                x='연구규모',
                y='연구품질', 
                z='혁신역량',
                size='논문수',
                color='H지수',
                hover_name='국가',
                title='주요국 3차원 기술 포지셔닝',
                labels={
                    '연구규모': '연구 규모',
                    '연구품질': '연구 품질', 
                    '혁신역량': '혁신 역량'
                },
                color_continuous_scale='Plasma'
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
            
            # 히트맵으로 종합 비교
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔥 종합 역량 히트맵")
                heatmap_data = country_df.set_index('국가')[['연구규모', '연구품질', '혁신역량']]
                
                fig_heatmap = px.imshow(
                    heatmap_data.T,
                    title="국가별 기술역량 비교",
                    color_continuous_scale='RdYlBu_r',
                    aspect='auto'
                )
                fig_heatmap.update_layout(height=400)
                st.plotly_chart(fig_heatmap, use_container_width=True)
            
            with col2:
                st.subheader("🏆 국가별 순위")
                # 종합 점수로 순위 매기기
                country_df['종합점수'] = (country_df['연구규모'] * 0.4 + 
                                    country_df['연구품질'] * 0.3 + 
                                    country_df['혁신역량'] * 0.3)
                
                ranking_df = country_df.nlargest(10, '종합점수')[['국가', '종합점수', '논문수', '특허수']].copy()
                ranking_df['순위'] = range(1, len(ranking_df) + 1)
                ranking_df['종합점수'] = ranking_df['종합점수'].round(1)
                
                st.dataframe(
                    ranking_df[['순위', '국가', '종합점수', '논문수', '특허수']], 
                    use_container_width=True, 
                    hide_index=True
                )
    
    except Exception as e:
        st.error(f"국가별 기술 포지셔닝 분석 오류: {e}")

def render_quality_indicators_analysis(papers_df):
    """연구 품질 지표 심화 분석"""
    st.subheader("🔬 연구 품질 지표 심화 분석")
    
    if papers_df is None or papers_df.empty:
        st.warning("연구 품질 분석을 위한 데이터가 없습니다.")
        return
    
    try:
        # Q1-Q4 분포 분석
        if all(col in papers_df.columns for col in ['Q1', 'Q2', 'Q3', 'Q4']):
            
            # 연도별 품질 트렌드
            yearly_quality = papers_df.groupby('Year')[['Q1', 'Q2', 'Q3', 'Q4']].sum()
            yearly_quality['Total'] = yearly_quality.sum(axis=1)
            yearly_quality['Q1_Ratio'] = (yearly_quality['Q1'] / yearly_quality['Total']) * 100
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 품질 분포 파이 차트 (최신년도)
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
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Q1 비율 시계열
                fig_trend = px.line(
                    x=yearly_quality.index,
                    y=yearly_quality['Q1_Ratio'],
                    title='Q1 저널 비율 연도별 추이',
                    markers=True
                )
                fig_trend.update_traces(line_width=3, marker_size=8)
                fig_trend.update_layout(
                    height=400,
                    yaxis_title='Q1 비율 (%)',
                    xaxis_title='연도'
                )
                st.plotly_chart(fig_trend, use_container_width=True)
            
            # 품질 지표 요약
            st.subheader("📊 품질 지표 요약")
            
            col1, col2, col3, col4 = st.columns(4)
            
            latest_q1_ratio = yearly_quality['Q1_Ratio'].iloc[-1]
            trend_change = yearly_quality['Q1_Ratio'].iloc[-1] - yearly_quality['Q1_Ratio'].iloc[-2] if len(yearly_quality) > 1 else 0
            
            with col1:
                st.metric("Q1 저널 비율", f"{latest_q1_ratio:.1f}%", f"{trend_change:+.1f}%p")
            
            with col2:
                avg_citations = papers_df['Avg_Citations'].mean()
                st.metric("평균 피인용수", f"{avg_citations:.1f}")
            
            with col3:
                avg_h_index = papers_df['H_Index'].mean()
                st.metric("평균 H-Index", f"{avg_h_index:.1f}")
            
            with col4:
                if 'Avg_mrnif' in papers_df.columns:
                    avg_mrnif = papers_df['Avg_mrnif'].mean()
                    st.metric("평균 MRNIF", f"{avg_mrnif:.1f}")
    
    except Exception as e:
        st.error(f"연구 품질 지표 분석 오류: {e}")

def render_patent_innovation_analysis(patents_df):
    """특허 혁신 지표 심화 분석"""
    st.subheader("💡 특허 혁신 지표 심화 분석")
    
    if patents_df is None or patents_df.empty:
        st.warning("특허 혁신 분석을 위한 데이터가 없습니다.")
        return
    
    try:
        # 특허 품질 지표 분석
        col1, col2 = st.columns(2)
        
        with col1:
            # Triadic vs 일반 특허 비교
            if 'triadic_count' in patents_df.columns:
                yearly_patents = patents_df.groupby('Year').agg({
                    'Total_Papers': 'sum',
                    'triadic_count': 'sum',
                    'important_patents_count': 'sum'
                }).reset_index()
                
                yearly_patents['Triadic_Ratio'] = (yearly_patents['triadic_count'] / yearly_patents['Total_Papers']) * 100
                yearly_patents['Important_Ratio'] = (yearly_patents['important_patents_count'] / yearly_patents['Total_Papers']) * 100
                
                fig = px.line(
                    yearly_patents,
                    x='Year',
                    y=['Triadic_Ratio', 'Important_Ratio'],
                    title='고품질 특허 비율 추이',
                    markers=True
                )
                fig.update_layout(
                    height=400,
                    yaxis_title='비율 (%)',
                    legend_title='특허 유형'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 특허 인용 분석
            if 'total_citations' in patents_df.columns:
                citation_data = patents_df.groupby('Year')['total_citations'].sum().reset_index()
                
                fig = px.bar(
                    citation_data,
                    x='Year',
                    y='total_citations',
                    title='연도별 특허 피인용수',
                    color='total_citations',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # 특허 강도 지표
        st.subheader("📈 특허 강도 지표")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'avg_claims' in patents_df.columns:
                avg_claims = patents_df['avg_claims'].mean()
                st.metric("평균 청구항 수", f"{avg_claims:.1f}")
        
        with col2:
            if 'foreign_filing_intensity' in patents_df.columns:
                avg_foreign = patents_df['foreign_filing_intensity'].mean()
                st.metric("해외출원 강도", f"{avg_foreign:.1f}")
        
        with col3:
            if 'total_family_countries' in patents_df.columns:
                avg_family = patents_df['total_family_countries'].mean()
                st.metric("평균 패밀리 국가", f"{avg_family:.1f}")
        
        with col4:
            # 특허 활용도 (granted ratio)
            if 'total_papers_granted' in patents_df.columns:
                total_filed = patents_df['Total_Papers'].sum()
                total_granted = patents_df['total_papers_granted'].sum()
                grant_rate = (total_granted / total_filed) * 100 if total_filed > 0 else 0
                st.metric("특허 등록률", f"{grant_rate:.1f}%")
    
    except Exception as e:
        st.error(f"특허 혁신 지표 분석 오류: {e}")

def render_comparative_benchmarking(papers_df, patents_df):
    """국제 벤치마킹 분석"""
    st.subheader("🌐 국제 벤치마킹 분석")
    
    if papers_df is None or papers_df.empty:
        st.warning("벤치마킹 분석을 위한 데이터가 없습니다.")
        return
    
    try:
        # 주요국 vs 기타국 비교
        major_countries = ['미국', '중국', '일본', '독일', '영국', '한국', 'US', 'China', 'Japan', 'Germany', 'UK', 'Korea']
        
        papers_df['Country_Group'] = papers_df['Country'].apply(
            lambda x: '주요국' if any(country in str(x) for country in major_countries) else '기타국'
        )
        
        # 국가 그룹별 비교
        group_comparison = papers_df.groupby(['Year', 'Country_Group']).agg({
            'Total_Papers': 'sum',
            'Q1': 'sum',
            'Total_Citations': 'sum',
            'H_Index': 'mean'
        }).reset_index()
        
        group_comparison['Q1_Ratio'] = (group_comparison['Q1'] / group_comparison['Total_Papers']) * 100
        group_comparison['Avg_Citations'] = group_comparison['Total_Citations'] / group_comparison['Total_Papers']
        
        # 시각화
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('논문 수 비교', 'Q1 비율 비교', '평균 피인용수 비교', 'H-Index 비교'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        for group in ['주요국', '기타국']:
            group_data = group_comparison[group_comparison['Country_Group'] == group]
            color = '#1f77b4' if group == '주요국' else '#ff7f0e'
            
            fig.add_trace(
                go.Scatter(x=group_data['Year'], y=group_data['Total_Papers'], 
                          name=f'{group} 논문수', line=dict(color=color)),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=group_data['Year'], y=group_data['Q1_Ratio'], 
                          name=f'{group} Q1비율', line=dict(color=color)),
                row=1, col=2
            )
            
            fig.add_trace(
                go.Scatter(x=group_data['Year'], y=group_data['Avg_Citations'], 
                          name=f'{group} 평균인용', line=dict(color=color)),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=group_data['Year'], y=group_data['H_Index'], 
                          name=f'{group} H-Index', line=dict(color=color)),
                row=2, col=2
            )
        
        fig.update_layout(height=600, title_text="주요국 vs 기타국 연구성과 벤치마킹")
        st.plotly_chart(fig, use_container_width=True)
        
        # 벤치마킹 요약 테이블
        st.subheader("📋 벤치마킹 요약")
        
        latest_year = papers_df['Year'].max()
        latest_comparison = group_comparison[group_comparison['Year'] == latest_year]
        
        if not latest_comparison.empty:
            benchmark_summary = latest_comparison.pivot(
                index=None, columns='Country_Group', 
                values=['Total_Papers', 'Q1_Ratio', 'Avg_Citations', 'H_Index']
            ).round(2)
            
            st.dataframe(benchmark_summary, use_container_width=True)
    
    except Exception as e:
        st.error(f"국제 벤치마킹 분석 오류: {e}")