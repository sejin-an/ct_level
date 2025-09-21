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

def render_country_comparison_dashboard(papers_df: pd.DataFrame, patents_df: pd.DataFrame):
    """국가별 비교 대시보드"""
    st.subheader("🌍 국가별 종합 비교")
    
    # 연도 선택
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        available_years = sorted(set(papers_df['Year'].unique()) | set(patents_df['Year'].unique())) if not papers_df.empty or not patents_df.empty else []
        if available_years:
            selected_year = st.selectbox("분석 연도", available_years, index=len(available_years)-1)
        else:
            st.warning("연도 데이터가 없습니다.")
            return
    
    with col2:
        # 정렬 기준 선택
        sort_options = ["논문 수", "특허 수", "H-Index", "Triadic 비율"]
        sort_by = st.selectbox("정렬 기준", sort_options)
    
    # 선택된 연도 데이터 필터링
    papers_year = papers_df[papers_df['Year'] == selected_year] if not papers_df.empty else pd.DataFrame()
    patents_year = patents_df[patents_df['Year'] == selected_year] if not patents_df.empty else pd.DataFrame()
    
    # 국가별 통합 데이터 생성
    country_data = create_country_summary(papers_year, patents_year)
    
    if country_data.empty:
        st.warning("선택된 연도에 대한 데이터가 없습니다.")
        return
    
    # 정렬
    country_data = sort_country_data(country_data, sort_by)
    
    # 시각화
    render_country_charts(country_data, selected_year)
    
    # 상세 테이블
    render_country_table(country_data, selected_year)

def create_country_summary(papers_df: pd.DataFrame, patents_df: pd.DataFrame) -> pd.DataFrame:
    """국가별 요약 데이터 생성"""
    summary_data = {}
    
    # 논문 데이터 처리
    if not papers_df.empty:
        for _, row in papers_df.iterrows():
            country = row['Country']
            if country not in summary_data:
                summary_data[country] = {}
            
            summary_data[country].update({
                'Papers': row.get('Total_Papers', 0),
                'H_Index': row.get('H_Index', 0),
                'Q1_Ratio': row.get('Q1_Ratio(%)', 0),
                'Collaboration_Ratio': row.get('Collaboration_Ratio(%)', 0),
                'Avg_Citations': row.get('Avg_Citations', 0),
                'Avg_mrnif': row.get('Avg_mrnif', 0)
            })
    
    # 특허 데이터 처리
    if not patents_df.empty:
        patent_col = 'patent_count' if 'patent_count' in patents_df.columns else 'Total_Papers'
        
        for _, row in patents_df.iterrows():
            country = row['Country']
            if country not in summary_data:
                summary_data[country] = {}
            
            summary_data[country].update({
                'Patents': row.get(patent_col, 0),
                'Triadic_Ratio': row.get('triadic_ratio', 0) * 100 if 'triadic_ratio' in row else 0,
                'Claims_per_Patent': row.get('claims_per_patent', 0),
                'Foreign_Filing': row.get('foreign_filing_intensity', 0),
                'Patent_H_Index': row.get('h_index', 0)
            })
    
    # DataFrame으로 변환
    if summary_data:
        df = pd.DataFrame.from_dict(summary_data, orient='index').reset_index()
        df = df.rename(columns={'index': 'Country'})
        df = df.fillna(0)
        return df
    
    return pd.DataFrame()

def sort_country_data(df: pd.DataFrame, sort_by: str) -> pd.DataFrame:
    """국가 데이터 정렬"""
    sort_mapping = {
        "논문 수": "Papers",
        "특허 수": "Patents", 
        "H-Index": "H_Index",
        "Triadic 비율": "Triadic_Ratio"
    }
    
    sort_col = sort_mapping.get(sort_by, "Papers")
    if sort_col in df.columns:
        return df.sort_values(sort_col, ascending=False)
    return df

def render_country_charts(country_data: pd.DataFrame, selected_year: int):
    """국가별 차트 렌더링"""
    col1, col2 = st.columns(2)
    
    with col1:
        # 논문 수 vs H-Index
        if 'Papers' in country_data.columns and 'H_Index' in country_data.columns:
            fig = px.scatter(
                country_data,
                x='Papers',
                y='H_Index',
                color='Q1_Ratio' if 'Q1_Ratio' in country_data.columns else None,
                size='Collaboration_Ratio' if 'Collaboration_Ratio' in country_data.columns else None,
                hover_name='Country',
                title=f'{selected_year}년 논문 수 vs H-Index',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 특허 수 vs Triadic 비율
        if 'Patents' in country_data.columns and 'Triadic_Ratio' in country_data.columns:
            fig = px.scatter(
                country_data,
                x='Patents',
                y='Triadic_Ratio',
                color='Claims_per_Patent' if 'Claims_per_Patent' in country_data.columns else None,
                size='Foreign_Filing' if 'Foreign_Filing' in country_data.columns else None,
                hover_name='Country',
                title=f'{selected_year}년 특허 수 vs Triadic 비율',
                color_continuous_scale='Plasma'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

def render_country_rankings(country_data: pd.DataFrame, top_n: int = 10):
    """국가별 순위 차트"""
    st.subheader(f"🏆 상위 {top_n}개국 순위")
    
    # 4개 지표별 상위 국가
    metrics = [
        ('Papers', '논문 수', '#1f77b4'),
        ('Patents', '특허 수', '#ff7f0e'), 
        ('H_Index', 'H-Index', '#2ca02c'),
        ('Triadic_Ratio', 'Triadic 비율', '#d62728')
    ]
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[metric[1] for metric in metrics]
    )
    
    for i, (col, title, color) in enumerate(metrics):
        if col in country_data.columns:
            top_countries = country_data.nlargest(top_n, col)
            
            row = (i // 2) + 1
            col_num = (i % 2) + 1
            
            fig.add_trace(
                go.Bar(
                    x=top_countries['Country'],
                    y=top_countries[col],
                    name=title,
                    marker_color=color,
                    showlegend=False
                ),
                row=row, col=col_num
            )
            
            # 축 라벨 업데이트
            fig.update_xaxes(tickangle=-45, row=row, col=col_num)
    
    fig.update_layout(height=500, title_text="주요 지표별 국가 순위")
    st.plotly_chart(fig, use_container_width=True)

def render_radar_comparison(country_data: pd.DataFrame, max_countries: int = 5):
    """레이더 차트 국가 비교"""
    st.subheader("🎯 다차원 성과 비교")
    
    # 상위 국가 선택 (논문 수 기준)
    if 'Papers' in country_data.columns:
        top_countries = country_data.nlargest(max_countries, 'Papers')
    else:
        top_countries = country_data.head(max_countries)
    
    # 레이더 차트 메트릭 정의
    radar_metrics = [
        ('Papers', '논문 수'),
        ('Patents', '특허 수'),
        ('H_Index', 'H-Index'),
        ('Q1_Ratio', 'Q1 비율'),
        ('Triadic_Ratio', 'Triadic 비율')
    ]
    
    fig = go.Figure()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    
    for i, (_, country_row) in enumerate(top_countries.iterrows()):
        values = []
        labels = []
        
        for col, label in radar_metrics:
            if col in country_data.columns:
                # 정규화 (0-100 스케일)
                max_val = country_data[col].max()
                min_val = country_data[col].min()
                
                if max_val != min_val:
                    normalized_val = ((country_row[col] - min_val) / (max_val - min_val)) * 100
                else:
                    normalized_val = 50
                
                values.append(normalized_val)
                labels.append(label)
        
        if values:
            # 닫힌 형태를 위해 첫 번째 값을 마지막에 추가
            values.append(values[0])
            labels.append(labels[0])
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=labels,
                fill='toself',
                name=country_row['Country'],
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
        title="상위 국가 다차원 성과 비교",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_country_table(country_data: pd.DataFrame, selected_year: int):
    """국가별 상세 테이블"""
    st.subheader("📋 국가별 상세 데이터")
    
    # 컬럼명 한글화
    display_columns = {
        'Country': '국가',
        'Papers': '논문 수',
        'Patents': '특허 수',
        'H_Index': 'H-Index',
        'Q1_Ratio': 'Q1 비율 (%)',
        'Collaboration_Ratio': '국제협력 비율 (%)',
        'Triadic_Ratio': 'Triadic 비율 (%)',
        'Claims_per_Patent': '특허당 청구항',
        'Foreign_Filing': '해외출원 강도',
        'Avg_Citations': '평균 인용수',
        'Avg_mrnif': '평균 MRNIF'
    }
    
    # 사용 가능한 컬럼만 선택
    available_cols = [col for col in display_columns.keys() if col in country_data.columns]
    
    if available_cols:
        display_df = country_data[available_cols].copy()
        
        # 컬럼명 변경
        rename_dict = {col: display_columns[col] for col in available_cols}
        display_df = display_df.rename(columns=rename_dict)
        
        # 숫자 포맷팅
        numeric_cols = display_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if '비율' in col or '%' in col:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}%")
            elif 'Index' in col or '인용수' in col or '청구항' in col:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}")
            else:
                display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}" if x >= 1 else f"{x:.2f}")
        
        # 테이블 표시
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # 다운로드 버튼
        csv = display_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 CSV 다운로드",
            data=csv,
            file_name=f'country_comparison_{selected_year}.csv',
            mime='text/csv'
        )

def render_competitive_positioning(country_data: pd.DataFrame):
    """경쟁력 포지셔닝 매트릭스"""
    st.subheader("🎯 경쟁력 포지셔닝")
    
    if 'Papers' not in country_data.columns or 'Patents' not in country_data.columns:
        st.warning("논문과 특허 데이터가 모두 필요합니다.")
        return
    
    # 사분면 분석
    papers_median = country_data['Papers'].median()
    patents_median = country_data['Patents'].median()
    
    # 사분면 라벨링
    def get_quadrant(row):
        if row['Papers'] >= papers_median and row['Patents'] >= patents_median:
            return "리더 (High-High)"
        elif row['Papers'] >= papers_median and row['Patents'] < patents_median:
            return "연구 중심 (High-Low)"
        elif row['Papers'] < papers_median and row['Patents'] >= patents_median:
            return "상용화 중심 (Low-High)"
        else:
            return "신흥 국가 (Low-Low)"
    
    country_data['Quadrant'] = country_data.apply(get_quadrant, axis=1)
    
    # 산점도 생성
    fig = px.scatter(
        country_data,
        x='Papers',
        y='Patents',
        color='Quadrant',
        size='H_Index' if 'H_Index' in country_data.columns else None,
        hover_name='Country',
        title='국가별 경쟁력 포지셔닝 매트릭스',
        color_discrete_map={
            "리더 (High-High)": "#2E8B57",
            "연구 중심 (High-Low)": "#4169E1", 
            "상용화 중심 (Low-High)": "#FF8C00",
            "신흥 국가 (Low-Low)": "#DC143C"
        }
    )
    
    # 중앙선 추가
    fig.add_hline(y=patents_median, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=papers_median, line_dash="dash", line_color="gray", opacity=0.5)
    
    # 사분면 라벨 추가
    fig.add_annotation(x=papers_median*1.5, y=patents_median*1.5, text="리더", showarrow=False, font_size=12, opacity=0.7)
    fig.add_annotation(x=papers_median*1.5, y=patents_median*0.5, text="연구중심", showarrow=False, font_size=12, opacity=0.7)
    fig.add_annotation(x=papers_median*0.5, y=patents_median*1.5, text="상용화중심", showarrow=False, font_size=12, opacity=0.7)
    fig.add_annotation(x=papers_median*0.5, y=patents_median*0.5, text="신흥국가", showarrow=False, font_size=12, opacity=0.7)
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # 사분면별 국가 수
    quadrant_counts = country_data['Quadrant'].value_counts()
    st.write("**사분면별 국가 분포:**")
    for quadrant, count in quadrant_counts.items():
        st.write(f"- {quadrant}: {count}개국")

def render_country_filters():
    """국가 선택 필터"""
    return st.multiselect(
        "비교할 국가 선택",
        options=[],  # 실제 구현시 국가 리스트 제공
        default=[],
        help="분석할 국가를 선택하세요 (최대 10개)"
    )