"""
향상된 전문가용 국가별 분석 컴포넌트
components/enhanced_country.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def render_global_competitiveness_dashboard(papers_df, patents_df):
    """글로벌 경쟁력 대시보드"""
    st.header("🌍 글로벌 기술 경쟁력 분석")
    
    # 핵심 경쟁력 지표
    render_country_competitiveness_index(papers_df, patents_df)
    st.markdown("---")
    
    # 국가별 기술 포트폴리오
    render_country_technology_portfolio(papers_df, patents_df)
    st.markdown("---")
    
    # 국가 간 기술 격차 분석
    render_technology_gap_analysis(papers_df, patents_df)

def render_country_competitiveness_index(papers_df, patents_df):
    """국가별 종합 경쟁력 지수"""
    st.subheader("🏆 국가별 종합 경쟁력 지수")
    
    if papers_df is None or papers_df.empty:
        st.warning("경쟁력 분석을 위한 데이터가 없습니다.")
        return
    
    try:
        # 상위 20개국 분석
        top_countries = papers_df.groupby('Country')['Total_Papers'].sum().nlargest(20).index
        
        competitiveness_data = []
        
        for country in top_countries:
            paper_data = papers_df[papers_df['Country'] == country]
            patent_data = patents_df[patents_df['Country'] == country] if patents_df is not None else pd.DataFrame()
            
            # 연구 규모 지수 (30%)
            total_papers = paper_data['Total_Papers'].sum()
            scale_index = min(100, np.log10(max(1, total_papers)) * 15)
            
            # 연구 품질 지수 (25%)
            if 'Q1_Ratio(%)' in paper_data.columns:
                avg_q1_ratio = paper_data['Q1_Ratio(%)'].mean()
                quality_index = min(100, avg_q1_ratio * 1.5)
            else:
                quality_index = 50
            
            # 연구 영향력 지수 (20%)
            if 'Avg_Citations' in paper_data.columns:
                avg_citations = paper_data['Avg_Citations'].mean()
                impact_index = min(100, avg_citations * 2)
            else:
                impact_index = 50
            
            # 혁신 역량 지수 (15%)
            if not patent_data.empty and 'triadic_count' in patent_data.columns:
                total_patents = patent_data['Total_Papers'].sum()
                triadic_patents = patent_data['triadic_count'].sum()
                innovation_index = min(100, (triadic_patents / max(1, total_patents)) * 200)
            else:
                innovation_index = 0
            
            # 국제화 지수 (10%)
            if not patent_data.empty and 'foreign_filing_intensity' in patent_data.columns:
                avg_foreign_filing = patent_data['foreign_filing_intensity'].mean()
                global_index = min(100, avg_foreign_filing * 10)
            else:
                global_index = 50
            
            # 종합 경쟁력 지수 계산
            total_index = (
                scale_index * 0.30 +
                quality_index * 0.25 +
                impact_index * 0.20 +
                innovation_index * 0.15 +
                global_index * 0.10
            )
            
            # 등급 분류
            if total_index >= 80:
                grade = "A+"
                tier = "글로벌 리더"
            elif total_index >= 70:
                grade = "A"
                tier = "선진국"
            elif total_index >= 60:
                grade = "B+"
                tier = "추격국"
            elif total_index >= 50:
                grade = "B"
                tier = "중진국"
            else:
                grade = "C"
                tier = "개발도상국"
            
            competitiveness_data.append({
                '국가': country,
                '종합지수': total_index,
                '등급': grade,
                '티어': tier,
                '규모지수': scale_index,
                '품질지수': quality_index,
                '영향력지수': impact_index,
                '혁신지수': innovation_index,
                '국제화지수': global_index,
                '논문수': total_papers,
                '특허수': patent_data['Total_Papers'].sum() if not patent_data.empty else 0
            })
        
        if competitiveness_data:
            comp_df = pd.DataFrame(competitiveness_data)
            comp_df = comp_df.sort_values('종합지수', ascending=False)
            
            # 경쟁력 시각화
            col1, col2 = st.columns(2)
            
            with col1:
                # 종합 순위 바 차트
                top_15 = comp_df.head(15)
                fig_bar = px.bar(
                    top_15,
                    x='국가',
                    y='종합지수',
                    color='등급',
                    title='국가별 종합 경쟁력 지수',
                    text='종합지수'
                )
                fig_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                fig_bar.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                # 5차원 레이더 차트 (상위 5개국)
                top_5 = comp_df.head(5)
                
                fig_radar = go.Figure()
                
                categories = ['규모지수', '품질지수', '영향력지수', '혁신지수', '국제화지수']
                
                for i, row in top_5.iterrows():
                    values = [row[cat] for cat in categories]
                    fig_radar.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        name=row['국가'],
                        opacity=0.7
                    ))
                
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=True,
                    title="상위 5개국 경쟁력 프로필",
                    height=400
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            
            # 상세 순위 테이블
            st.subheader("📊 상세 경쟁력 순위")
            
            display_df = comp_df.copy()
            for col in ['종합지수', '규모지수', '품질지수', '영향력지수', '혁신지수', '국제화지수']:
                display_df[col] = display_df[col].round(1)
            
            st.dataframe(
                display_df[['국가', '등급', '티어', '종합지수', '규모지수', '품질지수', '영향력지수', '혁신지수']], 
                use_container_width=True, 
                hide_index=True
            )
            
            # 티어별 분석
            render_tier_analysis(comp_df)
    
    except Exception as e:
        st.error(f"국가별 경쟁력 지수 분석 오류: {e}")

def render_tier_analysis(comp_df):
    """티어별 분석"""
    st.subheader("🎯 경쟁력 티어별 분석")
    
    try:
        tier_analysis = comp_df.groupby('티어').agg({
            '종합지수': ['mean', 'count'],
            '논문수': 'sum',
            '특허수': 'sum'
        }).round(1)
        
        tier_analysis.columns = ['평균지수', '국가수', '총논문수', '총특허수']
        tier_analysis = tier_analysis.reset_index()
        
        # 티어별 메트릭 표시
        cols = st.columns(len(tier_analysis))
        
        for i, row in tier_analysis.iterrows():
            with cols[i]:
                st.metric(
                    row['티어'],
                    f"{row['국가수']}개국",
                    f"평균 {row['평균지수']:.1f}점"
                )
                st.caption(f"논문: {row['총논문수']:,.0f}")
                st.caption(f"특허: {row['총특허수']:,.0f}")
    
    except Exception as e:
        st.warning(f"티어별 분석 오류: {e}")

def render_country_technology_portfolio(papers_df, patents_df):
    """국가별 기술 포트폴리오"""
    st.subheader("📋 국가별 기술 포트폴리오 분석")
    
    if papers_df is None or papers_df.empty or 'label_m_title' not in papers_df.columns:
        st.warning("기술 포트폴리오 분석을 위한 데이터가 없습니다.")
        return
    
    try:
        # 국가 선택
        top_countries = papers_df.groupby('Country')['Total_Papers'].sum().nlargest(15).index.tolist()
        
        selected_countries = st.multiselect(
            "분석할 국가 선택 (최대 5개)",
            options=top_countries,
            default=top_countries[:3],
            max_selections=5
        )
        
        if not selected_countries:
            st.warning("분석할 국가를 선택해주세요.")
            return
        
        # 국가별 기술 분야 분포
        portfolio_data = []
        
        for country in selected_countries:
            country_papers = papers_df[papers_df['Country'] == country]
            
            tech_distribution = country_papers.groupby('label_m_title')['Total_Papers'].sum().sort_values(ascending=False)
            total_papers = tech_distribution.sum()
            
            # 상위 10개 기술 분야
            top_techs = tech_distribution.head(10)
            
            for tech, papers in top_techs.items():
                portfolio_data.append({
                    '국가': country,
                    '기술분야': tech,
                    '논문수': papers,
                    '비율': (papers / total_papers) * 100
                })
        
        if portfolio_data:
            portfolio_df = pd.DataFrame(portfolio_data)
            
            # 기술 포트폴리오 히트맵
            portfolio_pivot = portfolio_df.pivot(index='기술분야', columns='국가', values='비율').fillna(0)
            
            fig_heatmap = px.imshow(
                portfolio_pivot,
                title='국가별 기술 분야 집중도 (%)',
                color_continuous_scale='Viridis',
                aspect='auto'
            )
            fig_heatmap.update_layout(height=600)
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # 포트폴리오 다양성 분석
            render_portfolio_diversity_analysis(portfolio_df, selected_countries)
            
            # 기술 특화 분석
            render_technology_specialization_analysis(papers_df, selected_countries)
    
    except Exception as e:
        st.error(f"기술 포트폴리오 분석 오류: {e}")

def render_portfolio_diversity_analysis(portfolio_df, countries):
    """포트폴리오 다양성 분석"""
    st.subheader("🌈 기술 포트폴리오 다양성")
    
    try:
        diversity_metrics = []
        
        for country in countries:
            country_data = portfolio_df[portfolio_df['국가'] == country]
            
            if not country_data.empty:
                # 허핀달 지수 (집중도)
                proportions = country_data['비율'] / 100
                herfindahl_index = (proportions ** 2).sum()
                diversity_index = 1 - herfindahl_index  # 다양성 지수
                
                # 기술 분야 수
                tech_count = len(country_data)
                
                # 엔트로피 기반 다양성
                entropy = -sum(p * np.log(p) for p in proportions if p > 0)
                normalized_entropy = entropy / np.log(tech_count) if tech_count > 1 else 0
                
                diversity_metrics.append({
                    '국가': country,
                    '다양성지수': diversity_index * 100,
                    '기술분야수': tech_count,
                    '정규화엔트로피': normalized_entropy * 100,
                    '집중도': herfindahl_index * 100
                })
        
        if diversity_metrics:
            diversity_df = pd.DataFrame(diversity_metrics)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 다양성 vs 집중도 산점도
                fig_scatter = px.scatter(
                    diversity_df,
                    x='집중도',
                    y='다양성지수',
                    size='기술분야수',
                    hover_name='국가',
                    title='기술 포트폴리오 다양성 vs 집중도',
                    labels={
                        '집중도': '집중도 (낮을수록 분산)',
                        '다양성지수': '다양성 지수 (높을수록 다양)'
                    }
                )
                fig_scatter.update_layout(height=400)
                st.plotly_chart(fig_scatter, use_container_width=True)
            
            with col2:
                # 다양성 순위
                diversity_rank = diversity_df.sort_values('다양성지수', ascending=False)
                
                fig_bar = px.bar(
                    diversity_rank,
                    x='국가',
                    y='다양성지수',
                    title='기술 포트폴리오 다양성 순위',
                    color='다양성지수',
                    color_continuous_scale='Viridis'
                )
                fig_bar.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # 다양성 메트릭 테이블
            display_diversity = diversity_df.copy()
            for col in ['다양성지수', '정규화엔트로피', '집중도']:
                display_diversity[col] = display_diversity[col].round(1)
            
            st.dataframe(display_diversity, use_container_width=True, hide_index=True)
    
    except Exception as e:
        st.warning(f"포트폴리오 다양성 분석 오류: {e}")

def render_technology_specialization_analysis(papers_df, countries):
    """기술 특화 분석"""
    st.subheader("🎯 국가별 기술 특화 분석")
    
    try:
        # 전체 대비 국가별 특화도 계산 (RCA - Revealed Comparative Advantage)
        specialization_data = []
        
        # 전체 기술 분야별 논문 비율
        global_tech_dist = papers_df.groupby('label_m_title')['Total_Papers'].sum()
        total_global_papers = global_tech_dist.sum()
        global_tech_ratio = global_tech_dist / total_global_papers
        
        for country in countries:
            country_papers = papers_df[papers_df['Country'] == country]
            country_tech_dist = country_papers.groupby('label_m_title')['Total_Papers'].sum()
            total_country_papers = country_tech_dist.sum()
            
            for tech in global_tech_dist.index:
                country_papers_in_tech = country_tech_dist.get(tech, 0)
                country_ratio_in_tech = country_papers_in_tech / total_country_papers if total_country_papers > 0 else 0
                global_ratio_in_tech = global_tech_ratio[tech]
                
                # RCA 계산
                rca = (country_ratio_in_tech / global_ratio_in_tech) if global_ratio_in_tech > 0 else 0
                
                # 특화도 분류
                if rca >= 2.0:
                    specialization_level = "매우 특화"
                elif rca >= 1.5:
                    specialization_level = "특화"
                elif rca >= 1.0:
                    specialization_level = "경쟁적"
                elif rca >= 0.5:
                    specialization_level = "약세"
                else:
                    specialization_level = "매우 약세"
                
                specialization_data.append({
                    '국가': country,
                    '기술분야': tech,
                    'RCA': rca,
                    '특화수준': specialization_level,
                    '국가논문수': country_papers_in_tech,
                    '국가비율': country_ratio_in_tech * 100,
                    '글로벌비율': global_ratio_in_tech * 100
                })
        
        if specialization_data:
            spec_df = pd.DataFrame(specialization_data)
            
            # 각 국가의 상위 특화 분야
            st.subheader("🌟 국가별 상위 특화 분야")
            
            for country in countries:
                country_spec = spec_df[spec_df['국가'] == country].sort_values('RCA', ascending=False).head(5)
                
                st.write(f"**{country}**")
                
                if not country_spec.empty:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # 특화도 바 차트
                        fig_spec = px.bar(
                            country_spec,
                            x='RCA',
                            y='기술분야',
                            orientation='h',
                            title=f'{country} 기술 특화도 (RCA)',
                            color='RCA',
                            color_continuous_scale='RdYlGn'
                        )
                        fig_spec.add_vline(x=1.0, line_dash="dash", line_color="black", annotation_text="경쟁력 기준선")
                        fig_spec.update_layout(height=300)
                        st.plotly_chart(fig_spec, use_container_width=True)
                    
                    with col2:
                        # 특화 수준 분포
                        spec_level_dist = country_spec['특화수준'].value_counts()
                        fig_pie = px.pie(
                            values=spec_level_dist.values,
                            names=spec_level_dist.index,
                            title=f'{country} 특화 수준 분포'
                        )
                        fig_pie.update_layout(height=300)
                        st.plotly_chart(fig_pie, use_container_width=True)
                
                st.markdown("---")
            
            # 국가별 특화 비교 히트맵
            render_specialization_heatmap(spec_df, countries)
    
    except Exception as e:
        st.error(f"기술 특화 분석 오류: {e}")

def render_specialization_heatmap(spec_df, countries):
    """특화도 비교 히트맵"""
    st.subheader("🔥 국가별 기술 특화도 비교")
    
    try:
        # 각 국가별 상위 15개 기술분야의 RCA 히트맵
        top_techs_per_country = set()
        
        for country in countries:
            country_tops = spec_df[spec_df['국가'] == country].nlargest(15, 'RCA')['기술분야'].tolist()
            top_techs_per_country.update(country_tops)
        
        # 히트맵용 데이터 준비
        heatmap_data = []
        for tech in top_techs_per_country:
            row_data = {'기술분야': tech}
            for country in countries:
                country_rca = spec_df[(spec_df['국가'] == country) & (spec_df['기술분야'] == tech)]['RCA']
                row_data[country] = country_rca.iloc[0] if not country_rca.empty else 0
            heatmap_data.append(row_data)
        
        if heatmap_data:
            heatmap_df = pd.DataFrame(heatmap_data)
            heatmap_matrix = heatmap_df.set_index('기술분야')[countries]
            
            # RCA 값이 1 이상인 것만 필터링 (경쟁력 있는 분야)
            competitive_techs = heatmap_matrix[heatmap_matrix.max(axis=1) >= 1.0].index
            filtered_matrix = heatmap_matrix.loc[competitive_techs]
            
            if not filtered_matrix.empty:
                fig_heatmap = px.imshow(
                    filtered_matrix,
                    title='국가별 기술 특화도 비교 (RCA ≥ 1.0)',
                    color_continuous_scale='RdYlGn',
                    aspect='auto'
                )
                
                # RCA=1 기준선 추가
                fig_heatmap.update_traces(
                    hovertemplate='국가: %{x}<br>기술분야: %{y}<br>RCA: %{z:.2f}<extra></extra>'
                )
                
                fig_heatmap.update_layout(height=max(400, len(filtered_matrix) * 20))
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # 특화도 요약 통계
                st.subheader("📊 특화도 요약 통계")
                
                summary_stats = []
                for country in countries:
                    country_data = spec_df[spec_df['국가'] == country]
                    
                    specialized_count = len(country_data[country_data['RCA'] >= 1.5])
                    competitive_count = len(country_data[country_data['RCA'] >= 1.0])
                    avg_rca = country_data['RCA'].mean()
                    max_rca = country_data['RCA'].max()
                    
                    summary_stats.append({
                        '국가': country,
                        '특화분야수': specialized_count,
                        '경쟁분야수': competitive_count,
                        '평균RCA': avg_rca,
                        '최대RCA': max_rca
                    })
                
                summary_df = pd.DataFrame(summary_stats)
                for col in ['평균RCA', '최대RCA']:
                    summary_df[col] = summary_df[col].round(2)
                
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    except Exception as e:
        st.warning(f"특화도 히트맵 생성 오류: {e}")

def render_technology_gap_analysis(papers_df, patents_df):
    """기술 격차 분석"""
    st.subheader("📏 국가 간 기술 격차 분석")
    
    if papers_df is None or papers_df.empty:
        st.warning("기술 격차 분석을 위한 데이터가 없습니다.")
        return
    
    try:
        # 기준 국가 및 비교 국가 선택
        top_countries = papers_df.groupby('Country')['Total_Papers'].sum().nlargest(15).index.tolist()
        
        col1, col2 = st.columns(2)
        
        with col1:
            benchmark_country = st.selectbox(
                "기준 국가 (벤치마크)",
                options=top_countries,
                index=0
            )
        
        with col2:
            compare_countries = st.multiselect(
                "비교 국가들",
                options=[c for c in top_countries if c != benchmark_country],
                default=[c for c in top_countries[1:4] if c != benchmark_country]
            )
        
        if not compare_countries:
            st.warning("비교할 국가를 선택해주세요.")
            return
        
        # 기술 격차 계산
        gap_analysis = calculate_technology_gaps(papers_df, patents_df, benchmark_country, compare_countries)
        
        if gap_analysis:
            # 종합 격차 점수
            render_overall_gap_scores(gap_analysis, benchmark_country)
            
            # 기술 분야별 격차
            render_technology_specific_gaps(gap_analysis, benchmark_country)
            
            # 격차 트렌드 분석
            render_gap_trend_analysis(papers_df, benchmark_country, compare_countries)
    
    except Exception as e:
        st.error(f"기술 격차 분석 오류: {e}")

def calculate_technology_gaps(papers_df, patents_df, benchmark_country, compare_countries):
    """기술 격차 계산"""
    try:
        gap_results = []
        
        # 기준국 데이터
        benchmark_data = papers_df[papers_df['Country'] == benchmark_country]
        benchmark_patents = patents_df[patents_df['Country'] == benchmark_country] if patents_df is not None else pd.DataFrame()
        
        # 기준국 지표 계산
        benchmark_metrics = {
            'total_papers': benchmark_data['Total_Papers'].sum(),
            'avg_citations': benchmark_data['Avg_Citations'].mean() if 'Avg_Citations' in benchmark_data.columns else 0,
            'q1_ratio': benchmark_data['Q1_Ratio(%)'].mean() if 'Q1_Ratio(%)' in benchmark_data.columns else 0,
            'h_index': benchmark_data['H_Index'].mean() if 'H_Index' in benchmark_data.columns else 0,
            'total_patents': benchmark_patents['Total_Papers'].sum() if not benchmark_patents.empty else 0,
            'triadic_patents': benchmark_patents['triadic_count'].sum() if not benchmark_patents.empty and 'triadic_count' in benchmark_patents.columns else 0
        }
        
        for country in compare_countries:
            country_data = papers_df[papers_df['Country'] == country]
            country_patents = patents_df[patents_df['Country'] == country] if patents_df is not None else pd.DataFrame()
            
            # 비교국 지표
            country_metrics = {
                'total_papers': country_data['Total_Papers'].sum(),
                'avg_citations': country_data['Avg_Citations'].mean() if 'Avg_Citations' in country_data.columns else 0,
                'q1_ratio': country_data['Q1_Ratio(%)'].mean() if 'Q1_Ratio(%)' in country_data.columns else 0,
                'h_index': country_data['H_Index'].mean() if 'H_Index' in country_data.columns else 0,
                'total_patents': country_patents['Total_Papers'].sum() if not country_patents.empty else 0,
                'triadic_patents': country_patents['triadic_count'].sum() if not country_patents.empty and 'triadic_count' in country_patents.columns else 0
            }
            
            # 격차 비율 계산 (비교국/기준국)
            gaps = {}
            for metric in benchmark_metrics:
                if benchmark_metrics[metric] > 0:
                    gaps[f'{metric}_gap'] = (country_metrics[metric] / benchmark_metrics[metric]) * 100
                else:
                    gaps[f'{metric}_gap'] = 0 if country_metrics[metric] == 0 else 100
            
            # 종합 격차 점수
            overall_gap = (
                gaps['total_papers_gap'] * 0.3 +
                gaps['q1_ratio_gap'] * 0.25 +
                gaps['avg_citations_gap'] * 0.2 +
                gaps['total_patents_gap'] * 0.15 +
                gaps['h_index_gap'] * 0.1
            )
            
            gap_results.append({
                '국가': country,
                '종합격차': overall_gap,
                **gaps,
                **country_metrics
            })
        
        return gap_results
    
    except Exception as e:
        st.warning(f"기술 격차 계산 오류: {e}")
        return []

def render_overall_gap_scores(gap_analysis, benchmark_country):
    """종합 격차 점수"""
    st.subheader(f"📊 {benchmark_country} 대비 종합 기술 격차")
    
    try:
        gap_df = pd.DataFrame(gap_analysis)
        gap_df = gap_df.sort_values('종합격차', ascending=False)
        
        # 격차 점수 바 차트
        fig_gap = px.bar(
            gap_df,
            x='국가',
            y='종합격차',
            title=f'{benchmark_country} 대비 종합 기술 격차 (%)',
            color='종합격차',
            color_continuous_scale='RdYlGn',
            text='종합격차'
        )
        
        # 100% 기준선 추가
        fig_gap.add_hline(y=100, line_dash="dash", line_color="black", annotation_text="기준국 수준")
        fig_gap.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_gap.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_gap, use_container_width=True)
        
        # 격차 수준 분류
        st.subheader("🎯 격차 수준 분류")
        
        cols = st.columns(len(gap_analysis))
        
        for i, gap_data in enumerate(gap_analysis):
            with cols[i]:
                gap_score = gap_data['종합격차']
                
                if gap_score >= 90:
                    level = "🟢 동등"
                    color = "normal"
                elif gap_score >= 70:
                    level = "🔵 근접"
                    color = "normal"
                elif gap_score >= 50:
                    level = "🟡 격차"
                    color = "inverse"
                else:
                    level = "🔴 큰 격차"
                    color = "inverse"
                
                st.metric(
                    gap_data['국가'],
                    f"{gap_score:.1f}%",
                    delta=level,
                    delta_color=color
                )
    
    except Exception as e:
        st.warning(f"종합 격차 점수 표시 오류: {e}")

def render_technology_specific_gaps(gap_analysis, benchmark_country):
    """기술 분야별 격차"""
    st.subheader("🔍 세부 지표별 격차 분석")
    
    try:
        gap_df = pd.DataFrame(gap_analysis)
        
        # 레이더 차트로 다차원 격차 표시
        metrics = ['total_papers_gap', 'q1_ratio_gap', 'avg_citations_gap', 'total_patents_gap', 'h_index_gap']
        metric_labels = ['논문 규모', '연구 품질', '인용 영향력', '특허 규모', 'H-Index']
        
        fig_radar = go.Figure()
        
        for _, row in gap_df.iterrows():
            values = [row[metric] for metric in metrics]
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=metric_labels,
                fill='toself',
                name=row['국가'],
                opacity=0.7
            ))
        
        # 기준선 (100%) 추가
        fig_radar.add_trace(go.Scatterpolar(
            r=[100] * len(metric_labels),
            theta=metric_labels,
            mode='lines',
            name=f'{benchmark_country} (기준)',
            line=dict(color='black', dash='dash', width=2)
        ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 150])),
            showlegend=True,
            title=f"{benchmark_country} 대비 세부 지표 격차 (%)",
            height=500
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # 세부 격차 테이블
        st.subheader("📋 세부 격차 데이터")
        
        display_gaps = gap_df.copy()
        gap_columns = ['total_papers_gap', 'q1_ratio_gap', 'avg_citations_gap', 'total_patents_gap', 'h_index_gap']
        
        for col in gap_columns:
            display_gaps[col] = display_gaps[col].round(1)
        
        # 컬럼명 변경
        display_gaps = display_gaps.rename(columns={
            'total_papers_gap': '논문규모(%)',
            'q1_ratio_gap': '연구품질(%)',
            'avg_citations_gap': '인용영향력(%)',
            'total_patents_gap': '특허규모(%)',
            'h_index_gap': 'H-Index(%)'
        })
        
        st.dataframe(
            display_gaps[['국가', '논문규모(%)', '연구품질(%)', '인용영향력(%)', '특허규모(%)', 'H-Index(%)']],
            use_container_width=True,
            hide_index=True
        )
    
    except Exception as e:
        st.warning(f"세부 격차 분석 표시 오류: {e}")

def render_gap_trend_analysis(papers_df, benchmark_country, compare_countries):
    """격차 트렌드 분석"""
    st.subheader("📈 격차 변화 트렌드")
    
    try:
        # 연도별 격차 변화 분석
        years = sorted(papers_df['Year'].unique())
        if len(years) >= 3:
            
            trend_data = []
            
            for year in years:
                year_data = papers_df[papers_df['Year'] == year]
                
                # 기준국 연도별 성과
                benchmark_year = year_data[year_data['Country'] == benchmark_country]
                if benchmark_year.empty:
                    continue
                
                benchmark_papers = benchmark_year['Total_Papers'].sum()
                
                for country in compare_countries:
                    country_year = year_data[year_data['Country'] == country]
                    if not country_year.empty:
                        country_papers = country_year['Total_Papers'].sum()
                        gap_ratio = (country_papers / max(1, benchmark_papers)) * 100
                        
                        trend_data.append({
                            'Year': year,
                            '국가': country,
                            '격차비율': gap_ratio
                        })
            
            if trend_data:
                trend_df = pd.DataFrame(trend_data)
                
                # 격차 트렌드 라인 차트
                fig_trend = px.line(
                    trend_df,
                    x='Year',
                    y='격차비율',
                    color='국가',
                    title=f'{benchmark_country} 대비 논문 수 격차 변화',
                    markers=True
                )
                
                fig_trend.add_hline(y=100, line_dash="dash", line_color="black", annotation_text="기준국 수준")
                fig_trend.update_layout(
                    height=400,
                    yaxis_title='격차 비율 (%)',
                    xaxis_title='연도'
                )
                st.plotly_chart(fig_trend, use_container_width=True)
                
                # 격차 변화율 계산
                st.subheader("📊 격차 변화율")
                
                change_analysis = []
                for country in compare_countries:
                    country_trend = trend_df[trend_df['국가'] == country].sort_values('Year')
                    if len(country_trend) >= 2:
                        first_gap = country_trend['격차비율'].iloc[0]
                        last_gap = country_trend['격차비율'].iloc[-1]
                        
                        if first_gap > 0:
                            change_rate = ((last_gap / first_gap) - 1) * 100
                        else:
                            change_rate = 0
                        
                        trend_direction = "📈 격차 축소" if change_rate > 5 else "📉 격차 확대" if change_rate < -5 else "📊 격차 유지"
                        
                        change_analysis.append({
                            '국가': country,
                            '초기격차': first_gap,
                            '최종격차': last_gap,
                            '변화율': change_rate,
                            '트렌드': trend_direction
                        })
                
                if change_analysis:
                    change_df = pd.DataFrame(change_analysis)
                    for col in ['초기격차', '최종격차', '변화율']:
                        change_df[col] = change_df[col].round(1)
                    
                    st.dataframe(change_df, use_container_width=True, hide_index=True)
        else:
            st.info("격차 트렌드 분석을 위해서는 최소 3년의 데이터가 필요합니다.")
    
    except Exception as e:
        st.warning(f"격차 트렌드 분석 오류: {e}")

def render_collaborative_network_analysis(papers_df):
    """국가 간 협력 네트워크 분석"""
    st.subheader("🤝 국가 간 연구 협력 네트워크")
    
    if papers_df is None or papers_df.empty:
        st.warning("협력 네트워크 분석을 위한 데이터가 없습니다.")
        return
    
    try:
        # 국가별 협력 강도 분석 (동일 기술분야 내 활동 기준)
        if 'label_m_title' in papers_df.columns:
            
            collaboration_data = []
            countries = papers_df['Country'].unique()
            
            for tech in papers_df['label_m_title'].unique():
                tech_data = papers_df[papers_df['label_m_title'] == tech]
                tech_countries = tech_data['Country'].unique()
                
                if len(tech_countries) >= 2:
                    # 기술 분야 내 국가 간 잠재적 협력 강도
                    for i, country1 in enumerate(tech_countries):
                        for country2 in tech_countries[i+1:]:
                            country1_papers = tech_data[tech_data['Country'] == country1]['Total_Papers'].sum()
                            country2_papers = tech_data[tech_data['Country'] == country2]['Total_Papers'].sum()
                            
                            # 협력 잠재력 점수 (양국의 연구 활동도 기반)
                            collaboration_potential = min(country1_papers, country2_papers) * np.sqrt(max(country1_papers, country2_papers))
                            
                            collaboration_data.append({
                                '기술분야': tech,
                                '국가1': country1,
                                '국가2': country2,
                                '협력잠재력': collaboration_potential,
                                '국가1_논문수': country1_papers,
                                '국가2_논문수': country2_papers
                            })
            
            if collaboration_data:
                collab_df = pd.DataFrame(collaboration_data)
                
                # 국가 쌍별 총 협력 잠재력
                country_pair_collab = collab_df.groupby(['국가1', '국가2'])['협력잠재력'].sum().reset_index()
                country_pair_collab = country_pair_collab.sort_values('협력잠재력', ascending=False)
                
                # 상위 협력 쌍 시각화
                top_pairs = country_pair_collab.head(15)
                top_pairs['국가쌍'] = top_pairs['국가1'] + ' - ' + top_pairs['국가2']
                
                fig_collab = px.bar(
                    top_pairs,
                    x='국가쌍',
                    y='협력잠재력',
                    title='국가 간 연구 협력 잠재력 상위 15쌍',
                    color='협력잠재력',
                    color_continuous_scale='Viridis'
                )
                fig_collab.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig_collab, use_container_width=True)
                
                # 네트워크 중심성 분석
                render_network_centrality_analysis(country_pair_collab)
                
                # 협력 추천
                render_collaboration_recommendations(collab_df)
    
    except Exception as e:
        st.error(f"협력 네트워크 분석 오류: {e}")

def render_network_centrality_analysis(country_pair_collab):
    """네트워크 중심성 분석"""
    st.subheader("🎯 국가별 네트워크 중심성")
    
    try:
        # 국가별 연결 강도 계산
        centrality_data = {}
        
        for _, row in country_pair_collab.iterrows():
            country1, country2, strength = row['국가1'], row['국가2'], row['협력잠재력']
            
            if country1 not in centrality_data:
                centrality_data[country1] = {'연결수': 0, '총강도': 0, '연결국가': set()}
            if country2 not in centrality_data:
                centrality_data[country2] = {'연결수': 0, '총강도': 0, '연결국가': set()}
            
            centrality_data[country1]['연결수'] += 1
            centrality_data[country1]['총강도'] += strength
            centrality_data[country1]['연결국가'].add(country2)
            
            centrality_data[country2]['연결수'] += 1
            centrality_data[country2]['총강도'] += strength
            centrality_data[country2]['연결국가'].add(country1)
        
        # 중심성 지표 계산
        centrality_results = []
        for country, data in centrality_data.items():
            avg_strength = data['총강도'] / max(1, data['연결수'])
            
            centrality_results.append({
                '국가': country,
                '연결수': data['연결수'],
                '총강도': data['총강도'],
                '평균강도': avg_strength,
                '네트워크중심성': data['연결수'] * np.log10(max(1, avg_strength))
            })
        
        centrality_df = pd.DataFrame(centrality_results)
        centrality_df = centrality_df.sort_values('네트워크중심성', ascending=False)
        
        # 중심성 시각화
        col1, col2 = st.columns(2)
        
        with col1:
            # 네트워크 중심성 순위
            top_central = centrality_df.head(10)
            fig_central = px.bar(
                top_central,
                x='국가',
                y='네트워크중심성',
                title='네트워크 중심성 순위',
                color='네트워크중심성',
                color_continuous_scale='Plasma'
            )
            fig_central.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_central, use_container_width=True)
        
        with col2:
            # 연결수 vs 평균강도 산점도
            fig_scatter = px.scatter(
                centrality_df,
                x='연결수',
                y='평균강도',
                size='총강도',
                hover_name='국가',
                title='연결 다양성 vs 협력 강도',
                labels={
                    '연결수': '협력 국가 수',
                    '평균강도': '평균 협력 강도'
                }
            )
            fig_scatter.update_layout(height=400)
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # 중심성 상세 테이블
        display_centrality = centrality_df.head(15).copy()
        for col in ['총강도', '평균강도', '네트워크중심성']:
            display_centrality[col] = display_centrality[col].round(1)
        
        st.dataframe(display_centrality, use_container_width=True, hide_index=True)
    
    except Exception as e:
        st.warning(f"네트워크 중심성 분석 오류: {e}")

def render_collaboration_recommendations(collab_df):
    """협력 추천 시스템"""
    st.subheader("💡 전략적 협력 추천")
    
    try:
        # 기술 분야별 최적 협력 쌍 추천
        st.write("**기술 분야별 협력 기회**")
        
        top_techs = collab_df.groupby('기술분야')['협력잠재력'].sum().nlargest(10).index
        
        for tech in top_techs[:5]:  # 상위 5개 기술분야
            tech_collab = collab_df[collab_df['기술분야'] == tech].nlargest(3, '협력잠재력')
            
            if not tech_collab.empty:
                st.write(f"**{tech}**")
                
                for _, row in tech_collab.iterrows():
                    country1, country2 = row['국가1'], row['국가2']
                    potential = row['협력잠재력']
                    papers1, papers2 = row['국가1_논문수'], row['국가2_논문수']
                    
                    # 협력 유형 분류
                    if papers1 > papers2 * 2:
                        collab_type = f"{country1} 주도형"
                    elif papers2 > papers1 * 2:
                        collab_type = f"{country2} 주도형"
                    else:
                        collab_type = "균형 협력형"
                    
                    st.write(f"• {country1} ↔ {country2}: {collab_type} (잠재력: {potential:.0f})")
                
                st.write("")
        
        # 협력 갭 분석
        render_collaboration_gap_analysis(collab_df)
    
    except Exception as e:
        st.warning(f"협력 추천 시스템 오류: {e}")

def render_collaboration_gap_analysis(collab_df):
    """협력 갭 분석"""
    st.subheader("🔍 협력 갭 분석")
    
    try:
        # 현재 협력이 부족하지만 잠재력이 높은 분야 식별
        tech_potential = collab_df.groupby('기술분야').agg({
            '협력잠재력': 'sum',
            '국가1': 'nunique'  # 참여 국가 수의 근사치
        }).reset_index()
        
        tech_potential['단위잠재력'] = tech_potential['협력잠재력'] / tech_potential['국가1']
        tech_potential = tech_potential.sort_values('단위잠재력', ascending=False)
        
        # 협력 갭이 큰 기술 분야
        gap_opportunities = tech_potential.head(10)
        
        fig_gap = px.bar(
            gap_opportunities,
            x='기술분야',
            y='단위잠재력',
            title='협력 갭이 큰 기술 분야 (단위 잠재력)',
            color='단위잠재력',
            color_continuous_scale='Oranges'
        )
        fig_gap.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_gap, use_container_width=True)
        
        st.write("**협력 확대 기회가 큰 기술 분야:**")
        for _, row in gap_opportunities.head(5).iterrows():
            st.write(f"• {row['기술분야']}: 단위 잠재력 {row['단위잠재력']:.1f}")
    
    except Exception as e:
        st.warning(f"협력 갭 분석 오류: {e}")

def render_emerging_countries_analysis(papers_df):
    """신흥 강국 분석"""
    st.subheader("🌟 신흥 기술 강국 분석")
    
    if papers_df is None or papers_df.empty:
        st.warning("신흥 강국 분석을 위한 데이터가 없습니다.")
        return
    
    try:
        # 최근 3년 vs 이전 3년 비교로 급성장 국가 식별
        all_years = sorted(papers_df['Year'].unique())
        
        if len(all_years) >= 6:
            recent_years = all_years[-3:]
            previous_years = all_years[-6:-3]
            
            emerging_analysis = []
            
            for country in papers_df['Country'].unique():
                recent_data = papers_df[(papers_df['Country'] == country) & (papers_df['Year'].isin(recent_years))]
                previous_data = papers_df[(papers_df['Country'] == country) & (papers_df['Year'].isin(previous_years))]
                
                recent_papers = recent_data['Total_Papers'].sum()
                previous_papers = previous_data['Total_Papers'].sum()
                
                # 성장률 계산
                if previous_papers > 0:
                    growth_rate = ((recent_papers / previous_papers) - 1) * 100
                else:
                    growth_rate = float('inf') if recent_papers > 0 else 0
                
                # 최근 연구 품질
                recent_quality = recent_data['Q1_Ratio(%)'].mean() if 'Q1_Ratio(%)' in recent_data.columns and not recent_data.empty else 0
                
                # 신흥도 점수 계산
                # 1. 급속 성장 (50%)
                growth_score = min(100, max(0, growth_rate / 3)) * 0.5
                
                # 2. 현재 활동도 (30%)
                activity_score = min(100, recent_papers / 50) * 0.3
                
                # 3. 연구 품질 (20%)
                quality_score = min(100, recent_quality * 2) * 0.2
                
                emerging_score = growth_score + activity_score + quality_score
                
                # 신흥 강국 분류
                if emerging_score >= 70 and recent_papers >= 100:
                    category = "🚀 급부상 강국"
                elif emerging_score >= 50 and recent_papers >= 50:
                    category = "📈 성장 국가"
                elif emerging_score >= 30:
                    category = "🌱 잠재 국가"
                else:
                    category = "📊 안정 국가"
                
                if recent_papers > 0:  # 최근 활동이 있는 국가만
                    emerging_analysis.append({
                        '국가': country,
                        '신흥도점수': emerging_score,
                        '성장률': growth_rate if growth_rate != float('inf') else 999,
                        '최근논문수': recent_papers,
                        '이전논문수': previous_papers,
                        '연구품질': recent_quality,
                        '분류': category
                    })
            
            if emerging_analysis:
                emerging_df = pd.DataFrame(emerging_analysis)
                emerging_df = emerging_df.sort_values('신흥도점수', ascending=False)
                
                # 신흥 강국 시각화
                col1, col2 = st.columns(2)
                
                with col1:
                    # 신흥도 vs 성장률 산점도
                    fig_emerging = px.scatter(
                        emerging_df.head(20),
                        x='성장률',
                        y='신흥도점수',
                        size='최근논문수',
                        color='분류',
                        hover_name='국가',
                        title='신흥 기술 강국 매트릭스',
                        labels={
                            '성장률': '성장률 (%)',
                            '신흥도점수': '신흥도 점수'
                        }
                    )
                    fig_emerging.update_layout(height=400)
                    st.plotly_chart(fig_emerging, use_container_width=True)
                
                with col2:
                    # 분류별 국가 수
                    category_counts = emerging_df['분류'].value_counts()
                    fig_category = px.pie(
                        values=category_counts.values,
                        names=category_counts.index,
                        title='신흥 강국 분류별 분포'
                    )
                    fig_category.update_layout(height=400)
                    st.plotly_chart(fig_category, use_container_width=True)
                
                # 신흥 강국 순위
                st.subheader("🏆 신흥 기술 강국 순위")
                
                display_emerging = emerging_df.head(15).copy()
                display_emerging['신흥도점수'] = display_emerging['신흥도점수'].round(1)
                display_emerging['성장률'] = display_emerging['성장률'].apply(lambda x: f"{x:.1f}%" if x < 999 else "신규")
                display_emerging['연구품질'] = display_emerging['연구품질'].round(1)
                
                st.dataframe(
                    display_emerging[['국가', '분류', '신흥도점수', '성장률', '최근논문수', '연구품질']], 
                    use_container_width=True, 
                    hide_index=True
                )
                
                # 신흥 강국 상세 분석
                render_emerging_country_details(emerging_df, papers_df)
        
        else:
            st.info("신흥 강국 분석을 위해서는 최소 6년의 데이터가 필요합니다.")
    
    except Exception as e:
        st.error(f"신흥 강국 분석 오류: {e}")

def render_emerging_country_details(emerging_df, papers_df):
    """신흥 강국 상세 분석"""
    st.subheader("🔍 신흥 강국 상세 분석")
    
    try:
        # 급부상 강국 선택
        top_emerging = emerging_df[emerging_df['분류'].isin(['🚀 급부상 강국', '📈 성장 국가'])].head(5)
        
        if not top_emerging.empty:
            selected_country = st.selectbox(
                "상세 분석할 신흥 강국 선택",
                options=top_emerging['국가'].tolist()
            )
            
            if selected_country:
                country_data = papers_df[papers_df['Country'] == selected_country]
                
                # 연도별 성장 추이
                yearly_growth = country_data.groupby('Year')['Total_Papers'].sum().reset_index()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # 성장 추이
                    fig_growth = px.line(
                        yearly_growth,
                        x='Year',
                        y='Total_Papers',
                        title=f'{selected_country} 연도별 논문 수 추이',
                        markers=True
                    )
                    fig_growth.update_traces(line_width=3, marker_size=8)
                    fig_growth.update_layout(height=400)
                    st.plotly_chart(fig_growth, use_container_width=True)
                
                with col2:
                    # 기술 분야별 분포
                    if 'label_m_title' in country_data.columns:
                        tech_dist = country_data.groupby('label_m_title')['Total_Papers'].sum().nlargest(8)
                        
                        fig_tech = px.pie(
                            values=tech_dist.values,
                            names=tech_dist.index,
                            title=f'{selected_country} 주요 기술 분야'
                        )
                        fig_tech.update_layout(height=400)
                        st.plotly_chart(fig_tech, use_container_width=True)
                
                # 핵심 성과 지표
                st.subheader(f"📊 {selected_country} 핵심 성과 지표")
                
                recent_years = sorted(country_data['Year'].unique())[-3:]
                recent_data = country_data[country_data['Year'].isin(recent_years)]
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_papers = recent_data['Total_Papers'].sum()
                    st.metric("최근 3년 논문", f"{total_papers:,}")
                
                with col2:
                    if 'Q1_Ratio(%)' in recent_data.columns:
                        avg_q1 = recent_data['Q1_Ratio(%)'].mean()
                        st.metric("평균 Q1 비율", f"{avg_q1:.1f}%")
                
                with col3:
                    if 'Avg_Citations' in recent_data.columns:
                        avg_citations = recent_data['Avg_Citations'].mean()
                        st.metric("평균 피인용수", f"{avg_citations:.1f}")
                
                with col4:
                    tech_diversity = recent_data['label_m_title'].nunique() if 'label_m_title' in recent_data.columns else 0
                    st.metric("기술 다양성", f"{tech_diversity}개 분야")
    
    except Exception as e:
        st.warning(f"신흥 강국 상세 분석 오류: {e}")

def render_regional_technology_leadership(papers_df):
    """지역별 기술 리더십 분석"""
    st.subheader("🌍 지역별 기술 리더십 분석")
    
    if papers_df is None or papers_df.empty:
        st.warning("지역별 리더십 분석을 위한 데이터가 없습니다.")
        return
    
    try:
        # 지역 분류 매핑 (기존 코드와 동일)
        region_mapping = {
            # 북미
            '미국': '북미', 'United States': '북미', 'US': '북미', 'USA': '북미',
            '캐나다': '북미', 'Canada': '북미',
            
            # 유럽
            '영국': '유럽', 'United Kingdom': '유럽', 'UK': '유럽', 'GB': '유럽',
            '독일': '유럽', 'Germany': '유럽', 'DE': '유럽',
            '프랑스': '유럽', 'France': '유럽', 'FR': '유럽',
            '이탈리아': '유럽', 'Italy': '유럽', 'IT': '유럽',
            '스페인': '유럽', 'Spain': '유럽', 'ES': '유럽',
            '네덜란드': '유럽', 'Netherlands': '유럽', 'NL': '유럽',
            '스위스': '유럽', 'Switzerland': '유럽', 'CH': '유럽',
            'EU': '유럽', 'European Union': '유럽',
            
            # 아시아
            '중국': '아시아', 'China': '아시아', 'CN': '아시아',
            '일본': '아시아', 'Japan': '아시아', 'JP': '아시아',
            '한국': '아시아', 'Korea': '아시아', 'KR': '아시아', '대한민국': '아시아',
            '인도': '아시아', 'India': '아시아', 'IN': '아시아',
            '싱가포르': '아시아', 'Singapore': '아시아', 'SG': '아시아',
            
            # 오세아니아
            '호주': '오세아니아', 'Australia': '오세아니아', 'AU': '오세아니아',
            '뉴질랜드': '오세아니아', 'New Zealand': '오세아니아', 'NZ': '오세아니아',
        }
        
        # 지역 분류 적용
        papers_regional = papers_df.copy()
        papers_regional['Region'] = papers_regional['Country'].map(region_mapping).fillna('기타')
        
        # 지역별 기술 분야 리더십 분석
        if 'label_m_title' in papers_df.columns:
            leadership_analysis = []
            
            for tech in papers_df['label_m_title'].unique():
                tech_data = papers_regional[papers_regional['label_m_title'] == tech]
                
                regional_performance = tech_data.groupby('Region').agg({
                    'Total_Papers': 'sum',
                    'Q1_Ratio(%)': 'mean' if 'Q1_Ratio(%)' in tech_data.columns else lambda x: 0,
                    'Avg_Citations': 'mean' if 'Avg_Citations' in tech_data.columns else lambda x: 0
                }).fillna(0)
                
                if not regional_performance.empty:
                    # 각 지역의 해당 기술 분야 리더십 점수
                    max_papers = regional_performance['Total_Papers'].max()
                    
                    for region in regional_performance.index:
                        if regional_performance.loc[region, 'Total_Papers'] > 0:
                            papers_score = (regional_performance.loc[region, 'Total_Papers'] / max_papers) * 100
                            quality_score = regional_performance.loc[region, 'Q1_Ratio(%)'] if 'Q1_Ratio(%)' in regional_performance.columns else 50
                            
                            leadership_score = papers_score * 0.7 + quality_score * 0.3
                            
                            leadership_analysis.append({
                                '기술분야': tech,
                                '지역': region,
                                '리더십점수': leadership_score,
                                '논문수': regional_performance.loc[region, 'Total_Papers'],
                                '연구품질': regional_performance.loc[region, 'Q1_Ratio(%)'] if 'Q1_Ratio(%)' in regional_performance.columns else 0
                            })
            
            if leadership_analysis:
                leadership_df = pd.DataFrame(leadership_analysis)
                
                # 지역별 기술 리더십 히트맵
                leadership_pivot = leadership_df.pivot(index='기술분야', columns='지역', values='리더십점수').fillna(0)
                
                # 리더십이 높은 기술분야만 표시 (상위 15개)
                tech_max_leadership = leadership_pivot.max(axis=1).nlargest(15)
                filtered_leadership = leadership_pivot.loc[tech_max_leadership.index]
                
                fig_leadership = px.imshow(
                    filtered_leadership,
                    title='지역별 기술 분야 리더십 히트맵',
                    color_continuous_scale='RdYlBu_r',
                    aspect='auto'
                )
                fig_leadership.update_layout(height=600)
                st.plotly_chart(fig_leadership, use_container_width=True)
                
                # 지역별 리더십 분야 요약
                render_regional_leadership_summary(leadership_df)
    
    except Exception as e:
        st.error(f"지역별 기술 리더십 분석 오류: {e}")

def render_regional_leadership_summary(leadership_df):
    """지역별 리더십 요약"""
    st.subheader("👑 지역별 기술 리더십 요약")
    
    try:
        regions = leadership_df['지역'].unique()
        
        for region in regions:
            region_data = leadership_df[leadership_df['지역'] == region]
            
            # 해당 지역이 리더인 기술 분야 (리더십 점수 70 이상)
            leading_techs = region_data[region_data['리더십점수'] >= 70].sort_values('리더십점수', ascending=False)
            
            if not leading_techs.empty:
                st.write(f"**{region} 지역 주도 기술 분야:**")
                
                for _, tech in leading_techs.head(5).iterrows():
                    st.write(f"• {tech['기술분야']}: {tech['리더십점수']:.1f}점 (논문 {tech['논문수']:,}편)")
                
                st.write("")
    
    except Exception as e:
        st.warning(f"지역별 리더십 요약 오류: {e}")