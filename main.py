"""
기술수준조사 서지분석 대시보드
연도별 데이터 반영 버전
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
    page_title="기술수준조사 서지분석 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 데이터 로드 함수
@st.cache_data
def load_data():
    """엑셀 파일에서 데이터 로드"""
    try:
        # 실제 파일명에 맞게 수정
        df = pd.read_excel('_통합평가자료.xlsx', sheet_name='Sheet4')
        
        # 컬럼명 정리
        df.columns = df.columns.str.strip()
        
        # Year가 null인 행 제거
        df = df.dropna(subset=['Year'])
        
        return df
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return pd.DataFrame()

# 데이터 전처리 함수
def preprocess_data(df):
    """데이터 전처리"""
    df = df.copy()
    
    # Year가 있는 데이터와 없는 데이터 분리
    yearly_data = df[df['Year'].notna()].copy()
    summary_data = df[df['Year'].isna()].copy()
    
    # 연도 데이터의 Year를 정수로 변환
    if not yearly_data.empty:
        yearly_data['Year'] = yearly_data['Year'].astype(int)
    
    # 논문과 특허 데이터 분리
    yearly_papers = yearly_data[yearly_data['구분'] == '1. 논문'].copy() if not yearly_data.empty else pd.DataFrame()
    yearly_patents = yearly_data[yearly_data['구분'] == '2. 특허'].copy() if not yearly_data.empty else pd.DataFrame()
    
    summary_papers = summary_data[summary_data['구분'] == '1. 논문'].copy() if not summary_data.empty else pd.DataFrame()
    summary_patents = summary_data[summary_data['구분'] == '2. 특허'].copy() if not summary_data.empty else pd.DataFrame()
    
    return {
        'yearly_data': yearly_data,
        'summary_data': summary_data,
        'yearly_papers': yearly_papers,
        'yearly_patents': yearly_patents,
        'summary_papers': summary_papers,
        'summary_patents': summary_patents
    }

# KPI 메트릭 함수
def render_kpi_metrics(data_dict):
    """주요 지표 카드 - 연도별 데이터와 통합 지표 구분"""
    st.subheader("📊 주요 지표")
    
    col1, col2, col3, col4 = st.columns(4)
    
    yearly_papers = data_dict['yearly_papers']
    yearly_patents = data_dict['yearly_patents']
    summary_papers = data_dict['summary_papers']
    summary_patents = data_dict['summary_patents']
    
    with col1:
        # 연도별 논문 수 (가장 최근 데이터)
        if not yearly_papers.empty:
            latest_year = yearly_papers['Year'].max()
            total_papers = yearly_papers[yearly_papers['Year'] == latest_year]['Total_Papers'].sum()
            st.metric(
                label="📄 최근 논문 수",
                value=f"{total_papers:,}",
                delta=f"{latest_year}년 기준"
            )
        else:
            st.metric(label="📄 논문 수", value="0", delta="데이터 없음")
    
    with col2:
        # 연도별 특허 수
        if not yearly_patents.empty:
            latest_year = yearly_patents['Year'].max()
            patent_col = 'patent_count' if 'patent_count' in yearly_patents.columns else 'Total_Papers'
            total_patents = yearly_patents[yearly_patents['Year'] == latest_year][patent_col].sum() if patent_col in yearly_patents.columns else 0
            st.metric(
                label="⚖️ 최근 특허 수",
                value=f"{total_patents:,}",
                delta=f"{latest_year}년 기준"
            )
        else:
            st.metric(label="⚖️ 특허 수", value="0", delta="데이터 없음")
    
    with col3:
        # 통합 지표: 전체 논문 점유율
        if not summary_papers.empty and '논문 점유율(%)' in summary_papers.columns:
            total_share = summary_papers['논문 점유율(%)'].sum()
            st.metric(
                label="📊 논문 점유율",
                value=f"{total_share:.1f}%",
                delta="전체 기간"
            )
        else:
            # 연도별 평균 H-Index로 대체
            if not yearly_papers.empty and 'H_Index' in yearly_papers.columns:
                avg_h_index = yearly_papers['H_Index'].mean()
                st.metric(
                    label="📈 평균 H-Index",
                    value=f"{avg_h_index:.1f}",
                    delta="연도별 평균"
                )
    
    with col4:
        # 분석 범위
        years_count = len(data_dict['yearly_data']['Year'].unique()) if not data_dict['yearly_data'].empty else 0
        countries_count = len(set(
            list(data_dict['yearly_data']['Country'].unique() if not data_dict['yearly_data'].empty else []) +
            list(data_dict['summary_data']['Country'].unique() if not data_dict['summary_data'].empty else [])
        ))
        st.metric(
            label="🌍 분석 범위",
            value=f"{countries_count} 국가",
            delta=f"{years_count}년간 + 통합지표"
        )

# 연도별 트렌드 분석 (연도 데이터만 사용)
def render_yearly_trends(data_dict):
    """연도별 트렌드 분석 - 연도가 있는 데이터만 사용"""
    st.subheader("📈 연도별 트렌드 (2011-2012)")
    
    yearly_papers = data_dict['yearly_papers']
    yearly_patents = data_dict['yearly_patents']
    
    if yearly_papers.empty and yearly_patents.empty:
        st.warning("연도별 트렌드를 위한 데이터가 없습니다.")
        return
    
    # 2x2 서브플롯 생성
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('논문 출간 수', '특허 출원 수', '논문 H-Index', '특허 관련 지표'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    
    # 1. 논문 출간 수 (연도별)
    if not yearly_papers.empty and 'Total_Papers' in yearly_papers.columns:
        for i, country in enumerate(yearly_papers['Country'].unique()):
            country_data = yearly_papers[yearly_papers['Country'] == country]
            fig.add_trace(
                go.Scatter(
                    x=country_data['Year'],
                    y=country_data['Total_Papers'],
                    mode='lines+markers',
                    name=f"{country}",
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=8)
                ),
                row=1, col=1
            )
    
    # 2. 특허 출원 수 (연도별)
    if not yearly_patents.empty:
        patent_col = 'patent_count' if 'patent_count' in yearly_patents.columns else 'Total_Papers'
        if patent_col in yearly_patents.columns:
            for i, country in enumerate(yearly_patents['Country'].unique()):
                country_data = yearly_patents[yearly_patents['Country'] == country]
                fig.add_trace(
                    go.Scatter(
                        x=country_data['Year'],
                        y=country_data[patent_col],
                        mode='lines+markers',
                        name=f"{country} (특허)",
                        line=dict(color=colors[i % len(colors)], width=3, dash='dash'),
                        marker=dict(size=8),
                        showlegend=False
                    ),
                    row=1, col=2
                )
    
    # 3. H-Index 트렌드
    if not yearly_papers.empty and 'H_Index' in yearly_papers.columns:
        for i, country in enumerate(yearly_papers['Country'].unique()):
            country_data = yearly_papers[yearly_papers['Country'] == country]
            fig.add_trace(
                go.Scatter(
                    x=country_data['Year'],
                    y=country_data['H_Index'],
                    mode='lines+markers',
                    name=f"{country} (H-Index)",
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=8),
                    showlegend=False
                ),
                row=2, col=1
            )
    
    # 4. 논문 품질 지표 (Q1 비율)
    if not yearly_papers.empty and 'Q1_Ratio(%)' in yearly_papers.columns:
        for i, country in enumerate(yearly_papers['Country'].unique()):
            country_data = yearly_papers[yearly_papers['Country'] == country]
            fig.add_trace(
                go.Scatter(
                    x=country_data['Year'],
                    y=country_data['Q1_Ratio(%)'],
                    mode='lines+markers',
                    name=f"{country} (Q1%)",
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=8),
                    showlegend=False
                ),
                row=2, col=2
            )
    
    # 레이아웃 업데이트
    fig.update_layout(
        height=600,
        title_text="연도별 주요 지표 트렌드 (실제 연도 데이터)",
        showlegend=True
    )
    
    # 축 제목 설정
    fig.update_xaxes(title_text="연도", row=2, col=1)
    fig.update_xaxes(title_text="연도", row=2, col=2)
    fig.update_yaxes(title_text="논문 수", row=1, col=1)
    fig.update_yaxes(title_text="특허 수", row=1, col=2)
    fig.update_yaxes(title_text="H-Index", row=2, col=1)
    fig.update_yaxes(title_text="Q1 비율 (%)", row=2, col=2)
    
    st.plotly_chart(fig, use_container_width=True)

# 국가별 비교 분석
def render_country_comparison(papers_df, patents_df):
    """국가별 비교 분석"""
    st.subheader("🌍 국가별 비교")
    
    # 연도 선택 위젯
    col1, col2 = st.columns([1, 3])
    
    with col1:
        available_years = sorted(papers_df['Year'].unique()) if not papers_df.empty else []
        if available_years:
            selected_year = st.selectbox("분석 연도", available_years, index=len(available_years)-1)
        else:
            st.warning("연도 데이터가 없습니다.")
            return
    
    # 선택된 연도 데이터 필터링
    papers_year = papers_df[papers_df['Year'] == selected_year] if not papers_df.empty else pd.DataFrame()
    patents_year = patents_df[patents_df['Year'] == selected_year] if not patents_df.empty else pd.DataFrame()
    
    # 국가별 종합 데이터 생성
    country_summary = []
    
    if not papers_year.empty:
        for _, row in papers_year.iterrows():
            country_summary.append({
                'Country': row['Country'],
                'Papers': row.get('Total_Papers', 0),
                'H_Index': row.get('H_Index', 0),
                'Q1_Ratio': row.get('Q1_Ratio(%)', 0),
                'Collaboration_Ratio': row.get('Collaboration_Ratio(%)', 0),
                'Type': 'Papers'
            })
    
    if not patents_year.empty:
        patent_col = 'patent_count' if 'patent_count' in patents_year.columns else 'Total_Papers'
        for _, row in patents_year.iterrows():
            country_summary.append({
                'Country': row['Country'],
                'Patents': row.get(patent_col, 0),
                'Triadic_Ratio': row.get('triadic_ratio', 0) * 100 if 'triadic_ratio' in row else 0,
                'Claims_per_Patent': row.get('claims_per_patent', 0),
                'Foreign_Filing': row.get('foreign_filing_intensity', 0),
                'Type': 'Patents'
            })
    
    if country_summary:
        summary_df = pd.DataFrame(country_summary)
        
        # 논문 vs 특허 비교 차트
        col1, col2 = st.columns(2)
        
        with col1:
            # 논문 데이터 차트
            papers_data = summary_df[summary_df['Type'] == 'Papers']
            if not papers_data.empty:
                fig = px.bar(
                    papers_data,
                    x='Country',
                    y='Papers',
                    color='H_Index',
                    title=f"{selected_year}년 국가별 논문 수",
                    color_continuous_scale='Blues'
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 특허 데이터 차트
            patents_data = summary_df[summary_df['Type'] == 'Patents']
            if not patents_data.empty:
                fig = px.bar(
                    patents_data,
                    x='Country',
                    y='Patents',
                    color='Triadic_Ratio',
                    title=f"{selected_year}년 국가별 특허 수",
                    color_continuous_scale='Reds'
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

# 레이더 차트 분석
def render_radar_analysis(papers_df, patents_df):
    """레이더 차트 다차원 분석"""
    st.subheader("🎯 다차원 성과 분석")
    
    if papers_df.empty:
        st.warning("논문 데이터가 없습니다.")
        return
    
    # 최신 연도 데이터 사용
    latest_year = papers_df['Year'].max()
    papers_latest = papers_df[papers_df['Year'] == latest_year]
    
    # 상위 5개국 선택 (논문 수 기준)
    top_countries = papers_latest.nlargest(5, 'Total_Papers')['Country'].tolist()
    
    # 레이더 차트 데이터 준비
    fig = go.Figure()
    
    metrics = ['Total_Papers', 'H_Index', 'Q1_Ratio(%)', 'Collaboration_Ratio(%)', 'Avg_Citations']
    metric_labels = ['논문 수', 'H-Index', 'Q1 비율', '국제협력 비율', '평균 인용']
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    
    for i, country in enumerate(top_countries):
        country_data = papers_latest[papers_latest['Country'] == country].iloc[0]
        
        # 정규화된 값 계산 (0-100 스케일)
        values = []
        for metric in metrics:
            if metric in country_data:
                max_val = papers_latest[metric].max()
                min_val = papers_latest[metric].min()
                if max_val != min_val:
                    normalized_val = ((country_data[metric] - min_val) / (max_val - min_val)) * 100
                else:
                    normalized_val = 50
                values.append(normalized_val)
            else:
                values.append(0)
        
        # 레이더 차트에 추가
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],  # 첫 번째 값을 마지막에 추가하여 닫힌 형태 만들기
            theta=metric_labels + [metric_labels[0]],
            fill='toself',
            name=country,
            line_color=colors[i % len(colors)],
            fillcolor=colors[i % len(colors)],
            opacity=0.3
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title=f"{latest_year}년 상위 5개국 다차원 성과 비교",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

# 상세 데이터 테이블
def render_detailed_table(df, papers_df, patents_df):
    """상세 데이터 테이블"""
    st.subheader("📋 상세 데이터")
    
    tab1, tab2, tab3 = st.tabs(["📄 논문 데이터", "⚖️ 특허 데이터", "📊 통합 요약"])
    
    with tab1:
        if not papers_df.empty:
            # 주요 컬럼만 선택하여 표시
            display_cols = ['Year', 'Country', 'Total_Papers', 'H_Index', 'Q1_Ratio(%)', 
                          'Collaboration_Ratio(%)', 'Avg_Citations', 'Avg_mrnif']
            available_cols = [col for col in display_cols if col in papers_df.columns]
            st.dataframe(papers_df[available_cols], use_container_width=True)
        else:
            st.info("논문 데이터가 없습니다.")
    
    with tab2:
        if not patents_df.empty:
            # 특허 관련 주요 컬럼
            patent_cols = ['Year', 'Country', 'patent_count', 'triadic_ratio', 
                          'claims_per_patent', 'foreign_filing_intensity', 'h_index']
            available_patent_cols = [col for col in patent_cols if col in patents_df.columns]
            if available_patent_cols:
                st.dataframe(patents_df[available_patent_cols], use_container_width=True)
            else:
                st.dataframe(patents_df, use_container_width=True)
        else:
            st.info("특허 데이터가 없습니다.")
    
    with tab3:
        # 연도별 국가별 요약
        if not df.empty:
            summary = df.groupby(['Year', 'Country', '구분']).size().reset_index(name='Count')
            summary_pivot = summary.pivot_table(
                index=['Year', 'Country'], 
                columns='구분', 
                values='Count', 
                fill_value=0
            )
            st.dataframe(summary_pivot, use_container_width=True)

# 메인 애플리케이션
def main():
    # 제목
    st.title("📊 기술수준조사 서지분석 대시보드")
    st.caption("연도별 논문 및 특허 데이터 종합 분석")
    st.markdown("---")
    
    # 데이터 로드
    df = load_data()
    
    if df.empty:
        st.error("데이터를 로드할 수 없습니다. 엑셀 파일을 확인해주세요.")
        return
    
    # 데이터 전처리
    df, papers_df, patents_df = preprocess_data(df)
    
    # 사이드바 필터
    st.sidebar.title("🔍 필터 설정")
    st.sidebar.markdown("---")
    
    # 연도 범위 선택
    if not df.empty:
        year_range = st.sidebar.slider(
            "분석 연도 범위",
            min_value=int(df['Year'].min()),
            max_value=int(df['Year'].max()),
            value=(int(df['Year'].min()), int(df['Year'].max()))
        )
        
        # 국가 선택
        countries = df['Country'].unique().tolist()
        selected_countries = st.sidebar.multiselect(
            "분석 대상 국가",
            countries,
            default=countries
        )
        
        # 데이터 필터링
        filtered_df = df[
            (df['Year'] >= year_range[0]) & 
            (df['Year'] <= year_range[1]) & 
            (df['Country'].isin(selected_countries))
        ]
        
        filtered_papers = papers_df[
            (papers_df['Year'] >= year_range[0]) & 
            (papers_df['Year'] <= year_range[1]) & 
            (papers_df['Country'].isin(selected_countries))
        ]
        
        filtered_patents = patents_df[
            (patents_df['Year'] >= year_range[0]) & 
            (patents_df['Year'] <= year_range[1]) & 
            (patents_df['Country'].isin(selected_countries))
        ]
    else:
        filtered_df = df
        filtered_papers = papers_df
        filtered_patents = patents_df
    
    # 1. KPI 메트릭
    render_kpi_metrics(filtered_df, filtered_papers, filtered_patents)
    st.markdown("---")
    
    # 2. 연도별 트렌드
    render_yearly_trends(filtered_papers, filtered_patents)
    st.markdown("---")
    
    # 3. 국가별 비교
    render_country_comparison(filtered_papers, filtered_patents)
    st.markdown("---")
    
    # 4. 레이더 차트 분석
    render_radar_analysis(filtered_papers, filtered_patents)
    st.markdown("---")
    
# 통합 지표 분석 (Year가 null인 데이터 활용)
def render_summary_analysis(data_dict):
    """통합 지표 분석 - 전체 기간 재산출 지표들"""
    st.subheader("📊 전체 기간 통합 지표")
    
    summary_papers = data_dict['summary_papers']
    summary_patents = data_dict['summary_patents']
    
    if summary_papers.empty and summary_patents.empty:
        st.warning("통합 지표 데이터가 없습니다.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📄 논문 통합 지표**")
        if not summary_papers.empty:
            # 한글 컬럼들 표시
            display_cols = ['Country']
            korean_cols = ['논문 점유율(%)', '논문 증가율(%)', '논문 영향력', 
                          '중요 논문 건수', '중요 논문 비율(%)', 'Top 10% 논문 수', 
                          'Top 10% 비율(%)', 'Q1 논문 수', 'Q1 논문 비율(%)', 
                          'MRNIF 평균', 'H-index', '국제협력 논문 수', '국제협력 비율(%)']
            
            available_korean_cols = [col for col in korean_cols if col in summary_papers.columns]
            display_cols.extend(available_korean_cols)
            
            if len(display_cols) > 1:
                papers_display = summary_papers[display_cols].copy()
                
                # 숫자 컬럼 포맷팅
                for col in available_korean_cols:
                    if papers_display[col].dtype in ['float64', 'int64']:
                        if '비율' in col or '%' in col:
                            papers_display[col] = papers_display[col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "")
                        elif '건수' in col or '수' in col:
                            papers_display[col] = papers_display[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "")
                        else:
                            papers_display[col] = papers_display[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
                
                st.dataframe(papers_display, use_container_width=True, hide_index=True)
    
    with col2:
        st.write("**⚖️ 특허 통합 지표**")
        if not summary_patents.empty:
            # 특허 관련 컬럼 확인
            patent_korean_cols = [col for col in summary_patents.columns if isinstance(col, str) and any(
                keyword in col for keyword in ['특허', '청구항', '패밀리', '인용', '출원']
            )]
            
            if patent_korean_cols:
                display_cols = ['Country'] + patent_korean_cols
                patents_display = summary_patents[display_cols].copy()
                st.dataframe(patents_display, use_container_width=True, hide_index=True)
            else:
                st.info("특허 통합 지표가 없습니다.")
    
    # 통합 지표 시각화
    if not summary_papers.empty:
        st.markdown("---")
        render_summary_charts(summary_papers, summary_patents)

def render_summary_charts(summary_papers, summary_patents):
    """통합 지표 차트"""
    col1, col2 = st.columns(2)
    
    with col1:
        # 논문 점유율 차트
        if '논문 점유율(%)' in summary_papers.columns:
            fig = px.bar(
                summary_papers,
                x='Country',
                y='논문 점유율(%)',
                title='국가별 논문 점유율',
                color='논문 점유율(%)',
                color_continuous_scale='Blues'
            )
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 논문 영향력 vs 중요 논문 비율
        if all(col in summary_papers.columns for col in ['논문 영향력', '중요 논문 비율(%)']):
            fig = px.scatter(
                summary_papers,
                x='논문 영향력',
                y='중요 논문 비율(%)',
                color='Country',
                size='Q1 논문 비율(%)' if 'Q1 논문 비율(%)' in summary_papers.columns else None,
                title='논문 영향력 vs 중요 논문 비율',
                hover_data=['Country']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # 사이드바 정보
    st.sidebar.markdown("---")
    st.sidebar.info(f"""
    **데이터 현황**
    - 총 레코드: {len(filtered_df):,}개
    - 논문 데이터: {len(filtered_papers):,}개
    - 특허 데이터: {len(filtered_patents):,}개
    - 분석 국가: {len(selected_countries if 'selected_countries' in locals() else [])}개
    """)

if __name__ == "__main__":
    main()