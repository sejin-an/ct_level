"""
국가별 비교 분석 컴포넌트 (개선 버전)
components/country.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def safe_get_column(df, keywords):
    """안전하게 컬럼 찾기"""
    if df is None or df.empty:
        return None
    
    for col in df.columns:
        if any(keyword.lower() in col.lower() for keyword in keywords):
            return col
    return None

def safe_get_numeric_column(df, keywords):
    """안전하게 숫자형 컬럼 찾기"""
    if df is None or df.empty:
        return None
    
    for col in df.columns:
        if any(keyword.lower() in col.lower() for keyword in keywords):
            try:
                pd.to_numeric(df[col], errors='coerce')
                return col
            except:
                continue
    return None

def render_country_trends(papers_df: pd.DataFrame, patents_df: pd.DataFrame, top_n: int = 10):
    """국가별 트렌드 분석"""
    st.subheader("🌍 국가별 시계열 트렌드")
    
    if papers_df is None or papers_df.empty:
        st.warning("국가별 시계열 데이터가 없습니다.")
        return []
    
    try:
        # 컬럼 찾기
        year_col = safe_get_column(papers_df, ['year', '연도'])
        country_col = safe_get_column(papers_df, ['country', '국가', 'nation'])
        paper_col = safe_get_numeric_column(papers_df, ['total', 'paper', '논문'])
        
        if not all([year_col, country_col]):
            st.warning("필요한 컬럼(연도, 국가)을 찾을 수 없습니다.")
            return []
        
        # 상위 N개국 선택
        if paper_col:
            top_countries = papers_df.groupby(country_col)[paper_col].sum().nlargest(top_n).index.tolist()
        else:
            top_countries = papers_df[country_col].value_counts().head(top_n).index.tolist()
        
        # 국가별 연도별 집계
        if paper_col:
            country_yearly = papers_df[papers_df[country_col].isin(top_countries)].groupby([year_col, country_col])[paper_col].sum().reset_index()
        else:
            country_yearly = papers_df[papers_df[country_col].isin(top_countries)].groupby([year_col, country_col]).size().reset_index(name='Count')
            paper_col = 'Count'
        
        # 시계열 차트
        fig = px.line(
            country_yearly,
            x=year_col,
            y=paper_col,
            color=country_col,
            title=f'🌍 상위 {top_n}개국 연도별 추이',
            markers=True
        )
        fig.update_traces(line_width=2, marker_size=6)
        fig.update_layout(height=500, legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, use_container_width=True)
        
        # 국가별 상세 분석
        render_country_detailed_metrics(papers_df, top_countries, year_col, country_col, paper_col)
        
        return top_countries
        
    except Exception as e:
        st.error(f"국가별 트렌드 분석 오류: {e}")
        return []

def render_country_detailed_metrics(df, countries, year_col, country_col, paper_col):
    """국가별 상세 메트릭"""
    try:
        st.subheader("📊 상위 국가 상세 지표")
        
        # 5개씩 컬럼으로 표시
        cols = st.columns(5)
        
        for i, country in enumerate(countries[:10]):  # 최대 10개국
            col_idx = i % 5
            
            with cols[col_idx]:
                country_data = df[df[country_col] == country]
                
                if not country_data.empty:
                    # 총량
                    total_count = country_data[paper_col].sum() if paper_col in country_data.columns else len(country_data)
                    
                    # 연도별 데이터가 있으면 성장률 계산
                    yearly_data = country_data.groupby(year_col)[paper_col].sum() if paper_col in country_data.columns else country_data.groupby(year_col).size()
                    
                    growth_rate = None
                    if len(yearly_data) > 1:
                        growth_rate = yearly_data.pct_change().mean() * 100
                    
                    st.metric(
                        label=f"🌍 {country}",
                        value=f"{total_count:,}",
                        delta=f"{growth_rate:.1f}%" if growth_rate is not None else None,
                        help="총 건수 및 평균 성장률"
                    )
                    
                    # 새로운 행 시작
                    if (i + 1) % 5 == 0 and i < len(countries) - 1:
                        st.markdown("")  # 공간 추가
                        cols = st.columns(5)  # 새로운 컬럼 생성
        
    except Exception as e:
        st.warning(f"국가별 상세 메트릭 오류: {e}")

def render_country_detail_analysis(papers_df: pd.DataFrame, selected_countries: list):
    """선택 국가 상세 분석"""
    if not selected_countries or papers_df is None or papers_df.empty:
        st.warning("선택된 국가가 없거나 데이터가 없습니다.")
        return
    
    st.subheader("🔍 선택 국가 상세 분석")
    
    try:
        # 컬럼 찾기
        year_col = safe_get_column(papers_df, ['year', '연도'])
        country_col = safe_get_column(papers_df, ['country', '국가', 'nation'])
        paper_col = safe_get_numeric_column(papers_df, ['total', 'paper', '논문'])
        
        if not all([year_col, country_col]):
            st.warning("필요한 컬럼을 찾을 수 없습니다.")
            return
        
        # 필터링된 데이터
        filtered_papers = papers_df[papers_df[country_col].isin(selected_countries)]
        
        if filtered_papers.empty:
            st.warning("선택된 국가의 데이터가 없습니다.")
            return
        
        # 탭으로 구분된 분석
        tab1, tab2, tab3 = st.tabs(["📈 시계열 추이", "📊 국가별 비교", "🏆 순위 분석"])
        
        with tab1:
            render_selected_countries_timeseries(filtered_papers, year_col, country_col, paper_col)
        
        with tab2:
            render_selected_countries_comparison(filtered_papers, country_col, paper_col)
        
        with tab3:
            render_selected_countries_ranking(filtered_papers, country_col, paper_col, year_col)
            
    except Exception as e:
        st.error(f"선택 국가 상세 분석 오류: {e}")

def render_selected_countries_timeseries(df, year_col, country_col, paper_col):
    """선택 국가 시계열 분석"""
    try:
        # 연도별 추이
        if paper_col:
            country_yearly = df.groupby([year_col, country_col])[paper_col].sum().reset_index()
        else:
            country_yearly = df.groupby([year_col, country_col]).size().reset_index(name='Count')
            paper_col = 'Count'
        
        fig = px.line(
            country_yearly,
            x=year_col,
            y=paper_col,
            color=country_col,
            title='선택 국가 시계열 추이',
            markers=True
        )
        fig.update_traces(line_width=3, marker_size=8)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # 연도별 상세 테이블
        pivot_table = country_yearly.pivot(index=year_col, columns=country_col, values=paper_col).fillna(0)
        st.subheader("📋 연도별 상세 데이터")
        st.dataframe(pivot_table, use_container_width=True)
        
    except Exception as e:
        st.error(f"시계열 분석 오류: {e}")

def render_selected_countries_comparison(df, country_col, paper_col):
    """선택 국가 비교 분석"""
    try:
        # 국가별 총합 비교
        if paper_col:
            country_totals = df.groupby(country_col)[paper_col].sum().sort_values(ascending=True)
        else:
            country_totals = df[country_col].value_counts().sort_values(ascending=True)
        
        # 수평 막대 차트
        fig = px.bar(
            x=country_totals.values,
            y=country_totals.index,
            orientation='h',
            title='국가별 총 건수 비교',
            text=country_totals.values
        )
        fig.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # 파이 차트
        fig_pie = px.pie(
            values=country_totals.values,
            names=country_totals.index,
            title='국가별 비율'
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    except Exception as e:
        st.error(f"국가별 비교 분석 오류: {e}")

def render_selected_countries_ranking(df, country_col, paper_col, year_col):
    """선택 국가 순위 분석"""
    try:
        col1, col2 = st.columns(2)
        
        with col1:
            # 전체 순위
            if paper_col:
                country_ranking = df.groupby(country_col)[paper_col].sum().sort_values(ascending=False)
            else:
                country_ranking = df[country_col].value_counts()
            
            ranking_df = pd.DataFrame({
                '순위': range(1, len(country_ranking) + 1),
                '국가': country_ranking.index,
                '건수': country_ranking.values
            })
            
            st.subheader("📊 전체 순위")
            st.dataframe(ranking_df, use_container_width=True, hide_index=True)
        
        with col2:
            # 최근 연도 순위 (가장 최근 연도 기준)
            if year_col in df.columns:
                latest_year = df[year_col].max()
                latest_data = df[df[year_col] == latest_year]
                
                if paper_col:
                    latest_ranking = latest_data.groupby(country_col)[paper_col].sum().sort_values(ascending=False)
                else:
                    latest_ranking = latest_data[country_col].value_counts()
                
                latest_ranking_df = pd.DataFrame({
                    '순위': range(1, len(latest_ranking) + 1),
                    '국가': latest_ranking.index,
                    '건수': latest_ranking.values
                })
                
                st.subheader(f"📊 {latest_year}년 순위")
                st.dataframe(latest_ranking_df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"순위 분석 오류: {e}")

def render_country_comparison_matrix(papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """국가별 비교 매트릭스"""
    st.subheader("🎯 국가별 포지셔닝 매트릭스")
    
    if papers_df is None or papers_df.empty:
        st.warning("국가별 데이터가 없습니다.")
        return
    
    try:
        # 논문 데이터 분석
        country_col = safe_get_column(papers_df, ['country', '국가', 'nation'])
        paper_col = safe_get_numeric_column(papers_df, ['total', 'paper', '논문'])
        
        if not country_col:
            st.warning("국가 컬럼을 찾을 수 없습니다.")
            return
        
        # 논문 수 집계
        if paper_col:
            paper_counts = papers_df.groupby(country_col)[paper_col].sum()
        else:
            paper_counts = papers_df[country_col].value_counts()
        
        # 특허 수 집계 (있는 경우)
        patent_counts = pd.Series(dtype=int)
        if patents_df is not None and not patents_df.empty:
            patent_country_col = safe_get_column(patents_df, ['country', '국가', 'nation'])
            patent_col = safe_get_numeric_column(patents_df, ['patent', 'count', '특허'])
            
            if patent_country_col and patent_col:
                patent_counts = patents_df.groupby(patent_country_col)[patent_col].sum()
            elif patent_country_col:
                patent_counts = patents_df[patent_country_col].value_counts()
        
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
        
    except Exception as e:
        st.error(f"포지셔닝 매트릭스 오류: {e}")

def render_quadrant_analysis(comp_df: pd.DataFrame):
    """사분면 분석"""
    try:
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
        
        # 사분면별 파이 차트
        fig = px.pie(
            values=quadrant_counts.values,
            names=quadrant_counts.index,
            title="사분면별 국가 분포"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.warning(f"사분면 분석 오류: {e}")

def render_country_ranking(papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """국가별 순위"""
    st.subheader("🏆 국가별 순위")
    
    tab1, tab2, tab3 = st.tabs(["📄 논문 순위", "⚖️ 특허 순위", "🌟 종합 순위"])
    
    with tab1:
        render_paper_ranking(papers_df)
    
    with tab2:
        render_patent_ranking(patents_df)
    
    with tab3:
        render_combined_ranking(papers_df, patents_df)

def render_paper_ranking(papers_df):
    """논문 순위"""
    try:
        if papers_df is None or papers_df.empty:
            st.info("논문 데이터가 없습니다.")
            return
        
        country_col = safe_get_column(papers_df, ['country', '국가', 'nation'])
        paper_col = safe_get_numeric_column(papers_df, ['total', 'paper', '논문'])
        
        if not country_col:
            st.warning("국가 컬럼을 찾을 수 없습니다.")
            return
        
        if paper_col:
            paper_ranking = papers_df.groupby(country_col)[paper_col].sum().reset_index()
            paper_ranking.columns = ['국가', '논문 수']
        else:
            paper_ranking = papers_df[country_col].value_counts().reset_index()
            paper_ranking.columns = ['국가', '논문 수']
        
        paper_ranking = paper_ranking.sort_values('논문 수', ascending=False)
        paper_ranking['순위'] = range(1, len(paper_ranking) + 1)
        
        # 상위 20개국만 표시
        display_ranking = paper_ranking.head(20)[['순위', '국가', '논문 수']]
        st.dataframe(display_ranking, use_container_width=True, hide_index=True)
        
        # 시각화
        top_10 = paper_ranking.head(10)
        fig = px.bar(
            top_10,
            x='국가',
            y='논문 수',
            title='논문 수 상위 10개국',
            text='논문 수'
        )
        fig.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"논문 순위 분석 오류: {e}")

def render_patent_ranking(patents_df):
    """특허 순위"""
    try:
        if patents_df is None or patents_df.empty:
            st.info("특허 데이터가 없습니다.")
            return
        
        country_col = safe_get_column(patents_df, ['country', '국가', 'nation'])
        patent_col = safe_get_numeric_column(patents_df, ['patent', 'count', '특허'])
        
        if not country_col:
            st.warning("국가 컬럼을 찾을 수 없습니다.")
            return
        
        if patent_col:
            patent_ranking = patents_df.groupby(country_col)[patent_col].sum().reset_index()
            patent_ranking.columns = ['국가', '특허 수']
        else:
            patent_ranking = patents_df[country_col].value_counts().reset_index()
            patent_ranking.columns = ['국가', '특허 수']
        
        patent_ranking = patent_ranking.sort_values('특허 수', ascending=False)
        patent_ranking['순위'] = range(1, len(patent_ranking) + 1)
        
        # 상위 20개국만 표시
        display_ranking = patent_ranking.head(20)[['순위', '국가', '특허 수']]
        st.dataframe(display_ranking, use_container_width=True, hide_index=True)
        
        # 시각화
        top_10 = patent_ranking.head(10)
        fig = px.bar(
            top_10,
            x='국가',
            y='특허 수',
            title='특허 수 상위 10개국',
            text='특허 수',
            color_discrete_sequence=['#FF6B6B']
        )
        fig.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"특허 순위 분석 오류: {e}")

def render_combined_ranking(papers_df, patents_df):
    """종합 순위"""
    try:
        # 논문 데이터 처리
        paper_counts = pd.Series(dtype=int)
        if papers_df is not None and not papers_df.empty:
            country_col = safe_get_column(papers_df, ['country', '국가', 'nation'])
            paper_col = safe_get_numeric_column(papers_df, ['total', 'paper', '논문'])
            
            if country_col:
                if paper_col:
                    paper_counts = papers_df.groupby(country_col)[paper_col].sum()
                else:
                    paper_counts = papers_df[country_col].value_counts()
        
        # 특허 데이터 처리
        patent_counts = pd.Series(dtype=int)
        if patents_df is not None and not patents_df.empty:
            country_col = safe_get_column(patents_df, ['country', '국가', 'nation'])
            patent_col = safe_get_numeric_column(patents_df, ['patent', 'count', '특허'])
            
            if country_col:
                if patent_col:
                    patent_counts = patents_df.groupby(country_col)[patent_col].sum()
                else:
                    patent_counts = patents_df[country_col].value_counts()
        
        # 통합 순위 계산
        if not paper_counts.empty or not patent_counts.empty:
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
            
            # 상위 20개국 표시
            display_df = combined_df.head(20)[['순위', '국가', '논문 수', '특허 수', '총합']]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # 시각화 - 누적 막대 차트
            top_10 = combined_df.head(10)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='논문',
                x=top_10['국가'],
                y=top_10['논문 수'],
                marker_color='lightblue'
            ))
            fig.add_trace(go.Bar(
                name='특허',
                x=top_10['국가'],
                y=top_10['특허 수'],
                marker_color='lightcoral'
            ))
            
            fig.update_layout(
                title='종합 순위 상위 10개국 (논문 + 특허)',
                barmode='stack',
                xaxis_tickangle=-45,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("종합 순위를 계산할 데이터가 없습니다.")
        
    except Exception as e:
        st.error(f"종합 순위 분석 오류: {e}")

def render_country_growth_analysis(papers_df: pd.DataFrame):
    """국가별 성장 분석"""
    if papers_df is None or papers_df.empty:
        st.warning("국가별 성장 분석을 위한 데이터가 없습니다.")
        return
    
    st.subheader("📈 국가별 성장률 분석")
    
    try:
        # 컬럼 찾기
        year_col = safe_get_column(papers_df, ['year', '연도'])
        country_col = safe_get_column(papers_df, ['country', '국가', 'nation'])
        paper_col = safe_get_numeric_column(papers_df, ['total', 'paper', '논문'])
        
        if not all([year_col, country_col]):
            st.warning("성장률 분석에 필요한 컬럼(연도, 국가)을 찾을 수 없습니다.")
            return
        
        # 상위 10개국의 성장률 계산
        if paper_col:
            top_countries = papers_df.groupby(country_col)[paper_col].sum().nlargest(10).index.tolist()
        else:
            top_countries = papers_df[country_col].value_counts().head(10).index.tolist()
        
        growth_data = []
        for country in top_countries:
            country_data = papers_df[papers_df[country_col] == country]
            
            if paper_col:
                yearly_counts = country_data.groupby(year_col)[paper_col].sum()
            else:
                yearly_counts = country_data.groupby(year_col).size()
            
            if len(yearly_counts) > 1:
                # 연평균 성장률 계산 (CAGR)
                first_year_count = yearly_counts.iloc[0]
                last_year_count = yearly_counts.iloc[-1]
                years_span = len(yearly_counts) - 1
                
                if years_span > 0 and first_year_count > 0:
                    cagr = ((last_year_count / first_year_count) ** (1/years_span) - 1) * 100
                    
                    # 평균 성장률 (단순)
                    avg_growth = yearly_counts.pct_change().mean() * 100
                    
                    growth_data.append({
                        'Country': country,
                        'CAGR': cagr,
                        'Avg_Growth': avg_growth,
                        'First_Year': yearly_counts.index[0],
                        'Last_Year': yearly_counts.index[-1],
                        'Growth_Period': years_span,
                        'Total_Count': last_year_count
                    })
        
        if growth_data:
            growth_df = pd.DataFrame(growth_data)
            growth_df = growth_df.sort_values('CAGR', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # CAGR 차트
                fig = px.bar(
                    growth_df,
                    x='Country',
                    y='CAGR',
                    title='상위 10개국 연평균 성장률 (CAGR)',
                    color='CAGR',
                    color_continuous_scale='RdYlGn',
                    text='CAGR'
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 성장률 vs 총량 산점도
                fig = px.scatter(
                    growth_df,
                    x='Total_Count',
                    y='CAGR',
                    text='Country',
                    title='성장률 vs 총량',
                    size='Total_Count',
                    color='CAGR',
                    color_continuous_scale='RdYlGn'
                )
                fig.update_traces(textposition="top center")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # 성장률 테이블
            display_growth = growth_df.copy()
            display_growth['CAGR'] = display_growth['CAGR'].round(2)
            display_growth['Avg_Growth'] = display_growth['Avg_Growth'].round(2)
            display_growth.columns = [
                '국가', 'CAGR(%)', '평균성장률(%)', '시작연도', 
                '종료연도', '분석기간(년)', '최종건수'
            ]
            
            st.subheader("📊 성장률 상세 데이터")
            st.dataframe(display_growth, use_container_width=True, hide_index=True)
        else:
            st.info("성장률을 계산할 수 있는 데이터가 없습니다.")
        
    except Exception as e:
        st.error(f"국가별 성장 분석 오류: {e}")

def render_regional_analysis(papers_df: pd.DataFrame):
    """지역별 분석"""
    if papers_df is None or papers_df.empty:
        st.warning("지역별 분석을 위한 데이터가 없습니다.")
        return
    
    st.subheader("🌏 지역별 분석")
    
    try:
        country_col = safe_get_column(papers_df, ['country', '국가', 'nation'])
        
        if not country_col:
            st.warning("국가 컬럼을 찾을 수 없습니다.")
            return
        
        # 지역 분류 매핑 (확장된 버전)
        region_mapping = {
            # 북미
            '미국': '북미', 'United States': '북미', 'US': '북미', 'USA': '북미',
            '캐나다': '북미', 'Canada': '북미',
            '멕시코': '북미', 'Mexico': '북미',
            
            # 유럽
            '영국': '유럽', 'United Kingdom': '유럽', 'UK': '유럽', 'GB': '유럽',
            '독일': '유럽', 'Germany': '유럽', 'DE': '유럽',
            '프랑스': '유럽', 'France': '유럽', 'FR': '유럽',
            '이탈리아': '유럽', 'Italy': '유럽', 'IT': '유럽',
            '스페인': '유럽', 'Spain': '유럽', 'ES': '유럽',
            '네덜란드': '유럽', 'Netherlands': '유럽', 'NL': '유럽',
            '스위스': '유럽', 'Switzerland': '유럽', 'CH': '유럽',
            '스웨덴': '유럽', 'Sweden': '유럽', 'SE': '유럽',
            '노르웨이': '유럽', 'Norway': '유럽', 'NO': '유럽',
            'EU': '유럽', 'European Union': '유럽',
            
            # 아시아
            '중국': '아시아', 'China': '아시아', 'CN': '아시아',
            '일본': '아시아', 'Japan': '아시아', 'JP': '아시아',
            '한국': '아시아', 'Korea': '아시아', 'KR': '아시아', '대한민국': '아시아', 'South Korea': '아시아',
            '인도': '아시아', 'India': '아시아', 'IN': '아시아',
            '싱가포르': '아시아', 'Singapore': '아시아', 'SG': '아시아',
            '말레이시아': '아시아', 'Malaysia': '아시아', 'MY': '아시아',
            '태국': '아시아', 'Thailand': '아시아', 'TH': '아시아',
            '인도네시아': '아시아', 'Indonesia': '아시아', 'ID': '아시아',
            '필리핀': '아시아', 'Philippines': '아시아', 'PH': '아시아',
            '베트남': '아시아', 'Vietnam': '아시아', 'VN': '아시아',
            '대만': '아시아', 'Taiwan': '아시아', 'TW': '아시아',
            '홍콩': '아시아', 'Hong Kong': '아시아', 'HK': '아시아',
            
            # 오세아니아
            '호주': '오세아니아', 'Australia': '오세아니아', 'AU': '오세아니아',
            '뉴질랜드': '오세아니아', 'New Zealand': '오세아니아', 'NZ': '오세아니아',
            
            # 남미
            '브라질': '남미', 'Brazil': '남미', 'BR': '남미',
            '아르헨티나': '남미', 'Argentina': '남미', 'AR': '남미',
            '칠레': '남미', 'Chile': '남미', 'CL': '남미',
            
            # 중동
            '이스라엘': '중동', 'Israel': '중동', 'IL': '중동',
            '사우디아라비아': '중동', 'Saudi Arabia': '중동', 'SA': '중동',
            '아랍에미리트': '중동', 'UAE': '중동', 'United Arab Emirates': '중동',
            
            # 아프리카
            '남아프리카': '아프리카', 'South Africa': '아프리카', 'ZA': '아프리카',
            '이집트': '아프리카', 'Egypt': '아프리카', 'EG': '아프리카'
        }
        
        # 지역 분류 적용
        papers_df_region = papers_df.copy()
        papers_df_region['Region'] = papers_df_region[country_col].map(region_mapping).fillna('기타')
        
        # 지역별 집계
        paper_col = safe_get_numeric_column(papers_df, ['total', 'paper', '논문'])
        
        if paper_col:
            region_counts = papers_df_region.groupby('Region')[paper_col].sum().sort_values(ascending=False)
        else:
            region_counts = papers_df_region['Region'].value_counts()
        
        if len(region_counts) > 1:
            col1, col2 = st.columns(2)
            
            with col1:
                # 파이 차트
                fig = px.pie(
                    values=region_counts.values,
                    names=region_counts.index,
                    title='지역별 분포'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 막대 차트
                fig = px.bar(
                    x=region_counts.index,
                    y=region_counts.values,
                    title='지역별 건수',
                    text=region_counts.values
                )
                fig.update_traces(texttemplate='%{text:,}', textposition='outside')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # 지역별 통계 테이블
            st.subheader("📊 지역별 상세 통계")
            
            region_stats = []
            total_count = region_counts.sum()
            
            for region, count in region_counts.items():
                percentage = (count / total_count) * 100
                
                # 해당 지역 국가들
                region_countries = papers_df_region[papers_df_region['Region'] == region][country_col].unique()
                
                region_stats.append({
                    '지역': region,
                    '건수': f"{count:,}",
                    '비율': f"{percentage:.1f}%",
                    '국가 수': len(region_countries),
                    '주요 국가': ', '.join(region_countries[:3])  # 상위 3개국만 표시
                })
            
            region_stats_df = pd.DataFrame(region_stats)
            st.dataframe(region_stats_df, use_container_width=True, hide_index=True)
            
            # 시계열 분석 (연도 컬럼이 있는 경우)
            year_col = safe_get_column(papers_df, ['year', '연도'])
            if year_col:
                render_regional_timeseries(papers_df_region, year_col, paper_col)
        else:
            st.info("지역별 분석을 위한 충분한 데이터가 없습니다.")
        
    except Exception as e:
        st.error(f"지역별 분석 오류: {e}")

def render_regional_timeseries(df_region, year_col, paper_col):
    """지역별 시계열 분석"""
    try:
        st.subheader("📈 지역별 시계열 추이")
        
        if paper_col:
            regional_yearly = df_region.groupby([year_col, 'Region'])[paper_col].sum().reset_index()
        else:
            regional_yearly = df_region.groupby([year_col, 'Region']).size().reset_index(name='Count')
            paper_col = 'Count'
        
        # 상위 5개 지역만 표시
        top_regions = df_region.groupby('Region')[paper_col].sum().nlargest(5).index.tolist()
        regional_yearly_filtered = regional_yearly[regional_yearly['Region'].isin(top_regions)]
        
        fig = px.line(
            regional_yearly_filtered,
            x=year_col,
            y=paper_col,
            color='Region',
            title='주요 지역별 시계열 추이',
            markers=True
        )
        fig.update_traces(line_width=3, marker_size=8)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # 지역별 성장률
        growth_data = []
        for region in top_regions:
            region_data = regional_yearly_filtered[regional_yearly_filtered['Region'] == region]
            if len(region_data) > 1:
                region_data = region_data.sort_values(year_col)
                growth_rate = region_data[paper_col].pct_change().mean() * 100
                growth_data.append({'Region': region, 'Growth_Rate': growth_rate})
        
        if growth_data:
            growth_df = pd.DataFrame(growth_data).sort_values('Growth_Rate', ascending=False)
            
            st.subheader("📊 지역별 평균 성장률")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                fig = px.bar(
                    growth_df,
                    x='Region',
                    y='Growth_Rate',
                    title='지역별 평균 성장률 (%)',
                    color='Growth_Rate',
                    color_continuous_scale='RdYlGn',
                    text='Growth_Rate'
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.write("**성장률 순위:**")
                for i, row in growth_df.iterrows():
                    st.write(f"{growth_df.index.get_loc(i)+1}. {row['Region']}: {row['Growth_Rate']:.1f}%")
        
    except Exception as e:
        st.warning(f"지역별 시계열 분석 오류: {e}")