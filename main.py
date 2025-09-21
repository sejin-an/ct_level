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
    """엑셀 파일에서 데이터 로드 - 대용량 최적화"""
    try:
        # 여러 가지 방법으로 시도
        try:
            # 방법 1: 기본 pandas 읽기 (첫 1000행으로 구조 확인)
            df_sample = pd.read_excel('_통합평가자료.xlsx', nrows=1000)
            st.info(f"📊 샘플 로드 완료: {len(df_sample)}행, {len(df_sample.columns)}열")
            
            # 전체 데이터 로드 여부 확인
            load_full = st.sidebar.checkbox("🔄 전체 데이터 로드", value=False, 
                                          help="체크하면 전체 16만행을 로드합니다 (시간이 오래 걸릴 수 있음)")
            
            if load_full:
                df = pd.read_excel('_통합평가자료.xlsx')
                st.success(f"✅ 전체 데이터 로드 성공: {len(df)}행, {len(df.columns)}열")
            else:
                # 샘플 데이터 사용 (분석용)
                df = df_sample.copy()
                st.warning("⚠️ 샘플 데이터 사용 중 (1000행). 전체 분석을 원하면 사이드바에서 '전체 데이터 로드'를 체크하세요.")
                
        except Exception as e1:
            try:
                # 방법 2: 시트명 지정
                df = pd.read_excel('_통합평가자료.xlsx', sheet_name='Sheet4', nrows=5000)
                st.success("✅ 시트명 지정으로 데이터 로드 성공 (5000행 제한)")
            except Exception as e2:
                try:
                    # 방법 3: 엔진 지정
                    df = pd.read_excel('_통합평가자료.xlsx', sheet_name=0, engine='openpyxl', nrows=5000)
                    st.success("✅ openpyxl 엔진으로 데이터 로드 성공 (5000행 제한)")
                except Exception as e3:
                    st.error(f"모든 방법 실패:")
                    st.error(f"방법1: {e1}")
                    st.error(f"방법2: {e2}")
                    st.error(f"방법3: {e3}")
                    return pd.DataFrame()
        
        # 컬럼명 정리
        df.columns = df.columns.str.strip()
        
        # 메모리 사용량 최적화
        memory_usage = df.memory_usage(deep=True).sum() / 1024**2  # MB
        st.info(f"💾 메모리 사용량: {memory_usage:.1f} MB")
        
        # 기본 정보 표시
        st.info(f"📊 데이터 로드 완료: {len(df):,}행, {len(df.columns)}열")
        
        return df
        
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        st.info("파일 경로를 확인하고 다음을 시도해보세요:")
        st.code("""
        # 현재 디렉토리 확인
        import os
        print("현재 디렉토리:", os.getcwd())
        print("파일 목록:", os.listdir('.'))
        """)
        return pd.DataFrame()

# 데이터 전처리 함수
def preprocess_data(df):
    """데이터 전처리 - 대용량 데이터 안전 처리"""
    if df.empty:
        return {
            'yearly_data': pd.DataFrame(),
            'summary_data': pd.DataFrame(),
            'yearly_papers': pd.DataFrame(),
            'yearly_patents': pd.DataFrame(),
            'summary_papers': pd.DataFrame(),
            'summary_patents': pd.DataFrame()
        }
    
    st.info(f"🔄 데이터 전처리 시작... ({len(df):,}행)")
    
    df = df.copy()
    
    # Year 컬럼이 존재하는지 확인
    if 'Year' not in df.columns:
        st.warning("'Year' 컬럼을 찾을 수 없습니다.")
        # 대안으로 연도 같은 컬럼 찾기
        possible_year_cols = [col for col in df.columns if 'year' in str(col).lower() or 'yr' in str(col).lower()]
        if possible_year_cols:
            df['Year'] = df[possible_year_cols[0]]
            st.info(f"'{possible_year_cols[0]}' 컬럼을 Year로 사용합니다.")
        else:
            df['Year'] = np.nan
    
    # Year 컬럼 안전하게 처리
    try:
        # Year 컬럼의 고유값 확인
        year_values = df['Year'].dropna().unique()
        st.write(f"**Year 컬럼 고유값 (처음 10개):** {sorted(year_values)[:10]}")
        
        # 연도처럼 보이는 값들만 필터링 (1990-2030)
        valid_years = []
        for val in year_values:
            try:
                year_int = int(float(val))
                if 1990 <= year_int <= 2030:
                    valid_years.append(year_int)
            except (ValueError, TypeError):
                continue
        
        st.info(f"유효한 연도 값: {sorted(valid_years)}")
        
        # Year가 있는 데이터와 없는 데이터 분리 (안전하게)
        def is_valid_year(val):
            if pd.isna(val):
                return False
            try:
                year_int = int(float(val))
                return 1990 <= year_int <= 2030
            except (ValueError, TypeError):
                return False
        
        df['is_valid_year'] = df['Year'].apply(is_valid_year)
        yearly_data = df[df['is_valid_year']].copy()
        summary_data = df[~df['is_valid_year']].copy()
        
        # 유효한 연도 데이터의 Year를 정수로 변환
        if not yearly_data.empty:
            yearly_data['Year'] = yearly_data['Year'].apply(lambda x: int(float(x)) if pd.notna(x) else x)
        
        st.success(f"✅ 연도별 데이터: {len(yearly_data):,}행, 통합 데이터: {len(summary_data):,}행")
        
    except Exception as e:
        st.error(f"Year 컬럼 처리 중 오류: {e}")
        # 안전 모드: 모든 데이터를 summary로 처리
        yearly_data = pd.DataFrame()
        summary_data = df.copy()
        st.warning("⚠️ 모든 데이터를 통합 지표로 처리합니다.")
    
    # 구분 컬럼 확인 및 처리
    category_col = None
    for col in ['구분', '분류', 'Category', 'Type', 'category', 'type']:
        if col in df.columns:
            category_col = col
            break
    
    if category_col is None:
        st.warning("구분 컬럼을 찾을 수 없습니다. 데이터를 샘플링하여 확인합니다.")
        # 샘플 데이터로 구분 컬럼 추정
        sample_df = df.head(1000)  # 처음 1000행만 확인
        for col in sample_df.columns:
            unique_vals = sample_df[col].dropna().astype(str).unique()
            if any('논문' in str(val) or 'paper' in str(val).lower() for val in unique_vals):
                category_col = col
                st.info(f"'{col}' 컬럼을 구분 컬럼으로 사용합니다.")
                break
    
    # 논문/특허 분리
    if category_col is None:
        st.info("구분 컬럼이 없어 모든 데이터를 논문으로 처리합니다.")
        yearly_papers = yearly_data.copy()
        yearly_patents = pd.DataFrame()
        summary_papers = summary_data.copy()
        summary_patents = pd.DataFrame()
    else:
        try:
            # 안전한 문자열 매칭
            def is_paper(val):
                if pd.isna(val):
                    return False
                val_str = str(val).lower()
                return any(keyword in val_str for keyword in ['논문', 'paper', '1.'])
            
            def is_patent(val):
                if pd.isna(val):
                    return False
                val_str = str(val).lower()
                return any(keyword in val_str for keyword in ['특허', 'patent', '2.'])
            
            # 논문과 특허 데이터 분리
            yearly_papers = yearly_data[yearly_data[category_col].apply(is_paper)].copy()
            yearly_patents = yearly_data[yearly_data[category_col].apply(is_patent)].copy()
            
            summary_papers = summary_data[summary_data[category_col].apply(is_paper)].copy()
            summary_patents = summary_data[summary_data[category_col].apply(is_patent)].copy()
            
            st.info(f"""
            📊 **데이터 분류 완료:**
            - 연도별 논문: {len(yearly_papers):,}행
            - 연도별 특허: {len(yearly_patents):,}행  
            - 통합 논문: {len(summary_papers):,}행
            - 통합 특허: {len(summary_patents):,}행
            """)
            
        except Exception as e:
            st.error(f"데이터 분류 중 오류: {e}")
            # 안전 모드
            yearly_papers = yearly_data.copy()
            yearly_patents = pd.DataFrame()
            summary_papers = summary_data.copy()
            summary_patents = pd.DataFrame()
    
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
    """주요 지표 카드 - 대용량 데이터 안전 처리"""
    st.subheader("📊 주요 지표")
    
    col1, col2, col3, col4 = st.columns(4)
    
    yearly_papers = data_dict['yearly_papers']
    yearly_patents = data_dict['yearly_patents']
    summary_papers = data_dict['summary_papers']
    summary_patents = data_dict['summary_patents']
    
    with col1:
        # 논문 수 계산
        try:
            if not yearly_papers.empty and 'Total_Papers' in yearly_papers.columns:
                total_papers = yearly_papers['Total_Papers'].sum()
                year_info = f"연도별 합계"
            elif not summary_papers.empty:
                # 통합 데이터에서 논문 관련 숫자 컬럼 찾기
                numeric_cols = summary_papers.select_dtypes(include=[np.number]).columns
                paper_cols = [col for col in numeric_cols if any(keyword in str(col).lower() for keyword in ['논문', 'paper', 'count'])]
                if paper_cols:
                    total_papers = summary_papers[paper_cols[0]].sum()
                    year_info = "통합 지표"
                else:
                    total_papers = len(summary_papers)
                    year_info = "레코드 수"
            else:
                total_papers = 0
                year_info = "데이터 없음"
            
            st.metric(
                label="📄 논문 수",
                value=f"{total_papers:,.0f}",
                delta=year_info
            )
        except Exception as e:
            st.metric(label="📄 논문 수", value="오류", delta=str(e)[:20])
    
    with col2:
        # 특허 수 계산
        try:
            if not yearly_patents.empty:
                patent_cols = [col for col in yearly_patents.columns if any(keyword in str(col).lower() for keyword in ['patent', 'count', 'total'])]
                if patent_cols:
                    total_patents = yearly_patents[patent_cols[0]].sum()
                else:
                    total_patents = len(yearly_patents)
                year_info = "연도별"
            elif not summary_patents.empty:
                numeric_cols = summary_patents.select_dtypes(include=[np.number]).columns
                patent_cols = [col for col in numeric_cols if any(keyword in str(col).lower() for keyword in ['특허', 'patent', 'count'])]
                if patent_cols:
                    total_patents = summary_patents[patent_cols[0]].sum()
                else:
                    total_patents = len(summary_patents)
                year_info = "통합 지표"
            else:
                total_patents = 0
                year_info = "데이터 없음"
            
            st.metric(
                label="⚖️ 특허 수",
                value=f"{total_patents:,.0f}",
                delta=year_info
            )
        except Exception as e:
            st.metric(label="⚖️ 특허 수", value="오류", delta=str(e)[:20])
    
    with col3:
        # H-Index 또는 영향력 지표
        try:
            h_index_val = 0
            source = "데이터 없음"
            
            # 순서대로 시도
            if not yearly_papers.empty and 'H_Index' in yearly_papers.columns:
                h_index_val = yearly_papers['H_Index'].mean()
                source = "연도별 평균"
            elif not summary_papers.empty:
                # 영향력 관련 컬럼 찾기
                impact_cols = [col for col in summary_papers.columns if any(
                    keyword in str(col).lower() for keyword in ['h-index', 'hindex', '영향력', 'impact', 'index']
                )]
                if impact_cols:
                    h_index_val = summary_papers[impact_cols[0]].mean()
                    source = f"{impact_cols[0][:10]}..."
            
            st.metric(
                label="📈 영향력 지수",
                value=f"{h_index_val:.1f}",
                delta=source
            )
        except Exception as e:
            st.metric(label="📈 영향력 지수", value="오류", delta=str(e)[:20])
    
    with col4:
        # 분석 범위
        try:
            total_countries = set()
            total_years = set()
            
            for key in ['yearly_data', 'summary_data']:
                if not data_dict[key].empty and 'Country' in data_dict[key].columns:
                    total_countries.update(data_dict[key]['Country'].dropna().unique())
            
            if not data_dict['yearly_data'].empty and 'Year' in data_dict['yearly_data'].columns:
                total_years.update(data_dict['yearly_data']['Year'].dropna().unique())
            
            st.metric(
                label="🌍 분석 범위",
                value=f"{len(total_countries)} 국가",
                delta=f"{len(total_years)}년" if total_years else "통합지표"
            )
        except Exception as e:
            st.metric(label="🌍 분석 범위", value="오류", delta=str(e)[:20])

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