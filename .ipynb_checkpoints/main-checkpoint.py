"""
연구 논문 분석 대시보드
Main Application
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 페이지 설정
st.set_page_config(
    page_title="연구 논문 분석 대시보드",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바 헤더
st.sidebar.title("📚 연구 논문 분석 대시보드")
st.sidebar.markdown("---")

# 메뉴 선택
menu = st.sidebar.selectbox(
    "📍 분석 메뉴",
    ["📊 종합 현황", "🌍 국가별 분석", "🏷️ 기술 분야별", "📈 시계열 분석", "🎯 영향력 분석", "📋 상세 데이터"]
)

st.sidebar.markdown("---")

# 데이터 로드 함수
@st.cache_data
def load_paper_data():
    """pkl 파일에서 논문 데이터 로드"""
    import os
    import pickle
    
    data_path = 'data/papers_data.pkl'
    
    # pkl 파일이 존재하면 로드
    if os.path.exists(data_path):
        with open(data_path, 'rb') as f:
            return pickle.load(f)
    
    # 파일이 없으면 샘플 데이터 생성 (초기 세팅용)
    else:
        countries = ['한국', '미국', '중국', '일본', '독일', '영국', '프랑스', '캐나다']
        tech_labels = ['AI/ML', '재생에너지', '바이오테크', '나노기술', '양자컴퓨팅', '로봇공학', '블록체인', '기후기술']
        years = list(range(2020, 2025))
        
        data = []
        for country in countries:
            for tech in tech_labels:
                for year in years:
                    data.append({
                        '국가': country,
                        '기술라벨': tech,
                        '연도': year,
                        '총_논문수': np.random.randint(50, 500),
                        '평균_영향력': np.random.uniform(0.5, 5.0),
                        '평균_H_index': np.random.uniform(10, 50),
                        '중요논문_총수': np.random.randint(5, 100),
                        '평균_생산성점수': np.random.uniform(60, 100),
                        '평균_영향력점수': np.random.uniform(40, 95)
                    })
        
        df = pd.DataFrame(data)
        
        # data 폴더가 없으면 생성
        os.makedirs('data', exist_ok=True)
        
        # pkl 파일로 저장
        with open(data_path, 'wb') as f:
            pickle.dump(df, f)
        
        return df

# 데이터 로드
df = load_paper_data()

# 필터 섹션 - 사이드바
st.sidebar.markdown("### 🔍 데이터 필터")

# 연도 필터
st.sidebar.markdown("**📅 연도 선택**")
year_min, year_max = int(df['연도'].min()), int(df['연도'].max())
selected_years = st.sidebar.slider(
    "연도 범위",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
    step=1
)

# 국가 필터
st.sidebar.markdown("**🌍 국가 선택**")
all_countries = df['국가'].unique().tolist()
select_all_countries = st.sidebar.checkbox("모든 국가 선택", value=True)
if select_all_countries:
    selected_countries = all_countries
else:
    selected_countries = st.sidebar.multiselect(
        "국가를 선택하세요",
        options=all_countries,
        default=all_countries[:3]
    )

# 기술 분야 필터
st.sidebar.markdown("**🏷️ 기술 분야 선택**")
all_tech = df['기술라벨'].unique().tolist()
select_all_tech = st.sidebar.checkbox("모든 기술 선택", value=True)
if select_all_tech:
    selected_tech = all_tech
else:
    selected_tech = st.sidebar.multiselect(
        "기술 분야를 선택하세요",
        options=all_tech,
        default=all_tech[:3]
    )

# 논문 수 필터
st.sidebar.markdown("**📚 논문 수 범위**")
paper_min, paper_max = int(df['총_논문수'].min()), int(df['총_논문수'].max())
paper_range = st.sidebar.slider(
    "최소 논문 수",
    min_value=paper_min,
    max_value=paper_max,
    value=(paper_min, paper_max)
)

# 영향력 점수 필터
st.sidebar.markdown("**⭐ 영향력 점수**")
impact_threshold = st.sidebar.number_input(
    "최소 영향력 점수",
    min_value=float(df['평균_영향력점수'].min()),
    max_value=float(df['평균_영향력점수'].max()),
    value=float(df['평균_영향력점수'].min()),
    step=5.0
)

# 필터 적용
filtered_df = df[
    (df['연도'] >= selected_years[0]) & 
    (df['연도'] <= selected_years[1]) &
    (df['국가'].isin(selected_countries)) &
    (df['기술라벨'].isin(selected_tech)) &
    (df['총_논문수'] >= paper_range[0]) &
    (df['총_논문수'] <= paper_range[1]) &
    (df['평균_영향력점수'] >= impact_threshold)
].copy()

# 필터 결과 통계
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 필터 결과")
st.sidebar.info(f"""
- **총 데이터**: {len(filtered_df):,} 건
- **선택 국가**: {len(selected_countries)} 개
- **선택 기술**: {len(selected_tech)} 개
- **연도 범위**: {selected_years[0]}-{selected_years[1]}
""")

# 필터 리셋 버튼
if st.sidebar.button("🔄 필터 초기화"):
    st.rerun()

# 메인 컨텐츠
if menu == "📊 종합 현황":
    st.title("📊 연구 논문 종합 현황")
    st.markdown("---")
    
    # KPI 카드
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        total_papers = filtered_df['총_논문수'].sum()
        st.metric("총 논문 수", f"{total_papers:,}")
    
    with col2:
        avg_impact = filtered_df['평균_영향력'].mean()
        st.metric("평균 영향력", f"{avg_impact:.2f}")
    
    with col3:
        avg_h_index = filtered_df['평균_H_index'].mean()
        st.metric("평균 H-index", f"{avg_h_index:.1f}")
    
    with col4:
        important_papers = filtered_df['중요논문_총수'].sum()
        st.metric("중요 논문 총수", f"{important_papers:,}")
    
    with col5:
        avg_productivity = filtered_df['평균_생산성점수'].mean()
        st.metric("평균 생산성", f"{avg_productivity:.1f}")
    
    with col6:
        avg_impact_score = filtered_df['평균_영향력점수'].mean()
        st.metric("영향력 점수", f"{avg_impact_score:.1f}")
    
    st.markdown("---")
    
    # 차트
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("국가별 총 논문 수")
        country_papers = filtered_df.groupby('국가')['총_논문수'].sum().sort_values(ascending=True)
        fig = px.bar(country_papers, orientation='h',
                    labels={'value': '논문 수', 'index': '국가'},
                    color=country_papers.values,
                    color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("기술 분야별 평균 영향력")
        tech_impact = filtered_df.groupby('기술라벨')['평균_영향력'].mean().sort_values(ascending=False)
        fig = px.bar(tech_impact,
                    labels={'value': '평균 영향력', 'index': '기술 분야'},
                    color=tech_impact.values,
                    color_continuous_scale='RdYlBu')
        st.plotly_chart(fig, use_container_width=True)

elif menu == "🌍 국가별 분석":
    st.title("🌍 국가별 연구 성과 분석")
    st.markdown("---")
    
    # 국가별 종합 지표
    country_metrics = filtered_df.groupby('국가').agg({
        '총_논문수': 'sum',
        '평균_영향력': 'mean',
        '평균_H_index': 'mean',
        '중요논문_총수': 'sum',
        '평균_생산성점수': 'mean',
        '평균_영향력점수': 'mean'
    }).round(2)
    
    # 레이더 차트를 위한 데이터 준비
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_country = st.selectbox("국가 선택", country_metrics.index)
        
        st.subheader(f"{selected_country} 주요 지표")
        country_data = country_metrics.loc[selected_country]
        
        st.metric("총 논문 수", f"{int(country_data['총_논문수']):,}")
        st.metric("평균 영향력", f"{country_data['평균_영향력']:.2f}")
        st.metric("평균 H-index", f"{country_data['평균_H_index']:.1f}")
        st.metric("중요 논문 수", f"{int(country_data['중요논문_총수']):,}")
    
    with col2:
        # 국가 비교 레이더 차트
        st.subheader("국가별 연구 역량 비교")
        
        # 정규화된 값으로 레이더 차트 생성
        normalized_metrics = country_metrics.copy()
        for col in normalized_metrics.columns:
            normalized_metrics[col] = (normalized_metrics[col] - normalized_metrics[col].min()) / (normalized_metrics[col].max() - normalized_metrics[col].min()) * 100
        
        fig = go.Figure()
        
        for country in normalized_metrics.index[:5]:  # 상위 5개국
            fig.add_trace(go.Scatterpolar(
                r=normalized_metrics.loc[country].values,
                theta=['논문수', '영향력', 'H-index', '중요논문', '생산성', '영향력점수'],
                fill='toself',
                name=country
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 국가별 기술 분야 히트맵
    st.subheader("국가-기술 분야 논문 분포 히트맵")
    heatmap_data = filtered_df.pivot_table(
        values='총_논문수',
        index='국가',
        columns='기술라벨',
        aggfunc='sum'
    )
    
    fig = px.imshow(heatmap_data,
                    labels=dict(x="기술 분야", y="국가", color="논문 수"),
                    color_continuous_scale="YlOrRd",
                    aspect="auto")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "🏷️ 기술 분야별":
    st.title("🏷️ 기술 분야별 분석")
    st.markdown("---")
    
    # 기술 선택
    selected_tech_detail = st.selectbox("분석할 기술 분야", filtered_df['기술라벨'].unique())
    tech_df = filtered_df[filtered_df['기술라벨'] == selected_tech_detail]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("총 논문 수", f"{tech_df['총_논문수'].sum():,}")
        st.metric("평균 영향력", f"{tech_df['평균_영향력'].mean():.2f}")
    
    with col2:
        st.metric("평균 H-index", f"{tech_df['평균_H_index'].mean():.1f}")
        st.metric("중요 논문 수", f"{tech_df['중요논문_총수'].sum():,}")
    
    with col3:
        st.metric("평균 생산성", f"{tech_df['평균_생산성점수'].mean():.1f}")
        st.metric("평균 영향력 점수", f"{tech_df['평균_영향력점수'].mean():.1f}")
    
    st.markdown("---")
    
    # 기술별 국가 순위
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"{selected_tech_detail} - 국가별 논문 수")
        country_tech_papers = tech_df.groupby('국가')['총_논문수'].sum().sort_values(ascending=False)
        fig = px.pie(country_tech_papers, values=country_tech_papers.values, 
                    names=country_tech_papers.index, hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader(f"{selected_tech_detail} - 연도별 추이")
        yearly_tech = tech_df.groupby('연도').agg({
            '총_논문수': 'sum',
            '평균_영향력': 'mean'
        })
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(x=yearly_tech.index, y=yearly_tech['총_논문수'], name="논문 수"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=yearly_tech.index, y=yearly_tech['평균_영향력'], 
                      name="평균 영향력", mode='lines+markers'),
            secondary_y=True,
        )
        fig.update_xaxis(title_text="연도")
        fig.update_yaxis(title_text="논문 수", secondary_y=False)
        fig.update_yaxis(title_text="평균 영향력", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)
    
    # 기술 분야 간 비교
    st.subheader("기술 분야 간 성과 비교")
    tech_comparison = filtered_df.groupby('기술라벨').agg({
        '평균_영향력': 'mean',
        '평균_H_index': 'mean',
        '평균_생산성점수': 'mean',
        '평균_영향력점수': 'mean'
    }).round(2)
    
    fig = px.scatter(tech_comparison, 
                    x='평균_생산성점수', 
                    y='평균_영향력점수',
                    size='평균_H_index',
                    color='평균_영향력',
                    hover_name=tech_comparison.index,
                    labels={'평균_생산성점수': '생산성 점수', '평균_영향력점수': '영향력 점수'},
                    color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

elif menu == "📈 시계열 분석":
    st.title("📈 시계열 분석")
    st.markdown("---")
    
    # 연도별 추이
    yearly_metrics = filtered_df.groupby('연도').agg({
        '총_논문수': 'sum',
        '평균_영향력': 'mean',
        '평균_H_index': 'mean',
        '중요논문_총수': 'sum',
        '평균_생산성점수': 'mean',
        '평균_영향력점수': 'mean'
    })
    
    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["📝 논문 수 추이", "📊 영향력 지표", "🎯 생산성 분석"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("연도별 총 논문 수")
            fig = px.line(yearly_metrics, y='총_논문수', 
                         markers=True, line_shape='spline')
            fig.update_traces(line_color='#2E86AB', line_width=3)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("국가별 논문 수 변화")
            country_yearly = filtered_df.groupby(['연도', '국가'])['총_논문수'].sum().reset_index()
            fig = px.line(country_yearly, x='연도', y='총_논문수', 
                         color='국가', markers=True)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("평균 영향력 & H-index 추이")
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                go.Scatter(x=yearly_metrics.index, y=yearly_metrics['평균_영향력'],
                          name="평균 영향력", mode='lines+markers', line=dict(color='#E63946')),
                secondary_y=False,
            )
            fig.add_trace(
                go.Scatter(x=yearly_metrics.index, y=yearly_metrics['평균_H_index'],
                          name="평균 H-index", mode='lines+markers', line=dict(color='#457B9D')),
                secondary_y=True,
            )
            fig.update_xaxis(title_text="연도")
            fig.update_yaxis(title_text="평균 영향력", secondary_y=False)
            fig.update_yaxis(title_text="평균 H-index", secondary_y=True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("중요 논문 비율 추이")
            yearly_metrics['중요논문_비율'] = (yearly_metrics['중요논문_총수'] / yearly_metrics['총_논문수'] * 100).round(2)
            fig = px.area(yearly_metrics, y='중요논문_비율',
                         labels={'중요논문_비율': '중요 논문 비율 (%)'},
                         color_discrete_sequence=['#06FFA5'])
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("생산성 vs 영향력 점수 변화")
        fig = px.scatter(yearly_metrics, 
                        x='평균_생산성점수', 
                        y='평균_영향력점수',
                        size='총_논문수',
                        color=yearly_metrics.index,
                        labels={'평균_생산성점수': '생산성 점수', '평균_영향력점수': '영향력 점수'},
                        color_continuous_scale='Turbo')
        
        # 추세선 추가
        fig.add_trace(go.Scatter(
            x=yearly_metrics['평균_생산성점수'],
            y=yearly_metrics['평균_영향력점수'],
            mode='lines',
            line=dict(dash='dash', color='gray'),
            showlegend=False
        ))
        st.plotly_chart(fig, use_container_width=True)
        
        # 연도별 성장률
        st.subheader("전년 대비 성장률 (%)")
        growth_metrics = yearly_metrics.pct_change() * 100
        growth_metrics = growth_metrics.dropna()
        
        fig = px.bar(growth_metrics[['총_논문수', '평균_영향력', '평균_H_index']],
                    barmode='group',
                    labels={'value': '성장률 (%)', 'index': '연도'},
                    color_discrete_map={'총_논문수': '#FF6B6B', 
                                       '평균_영향력': '#4ECDC4',
                                       '평균_H_index': '#45B7D1'})
        st.plotly_chart(fig, use_container_width=True)

elif menu == "🎯 영향력 분석":
    st.title("🎯 연구 영향력 상세 분석")
    st.markdown("---")
    
    # 영향력 분포
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("영향력 점수 분포")
        fig = px.histogram(filtered_df, x='평균_영향력점수', nbins=30,
                          labels={'평균_영향력점수': '영향력 점수', 'count': '빈도'},
                          color_discrete_sequence=['#9B59B6'])
        fig.add_vline(x=filtered_df['평균_영향력점수'].mean(), 
                     line_dash="dash", line_color="red",
                     annotation_text="평균")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("H-index 분포")
        fig = px.box(filtered_df, y='평균_H_index', x='기술라벨',
                    labels={'평균_H_index': 'H-index', '기술라벨': '기술 분야'},
                    color='기술라벨')
        st.plotly_chart(fig, use_container_width=True)
    
    # 상관관계 분석
    st.subheader("지표 간 상관관계")
    
    correlation_cols = ['총_논문수', '평균_영향력', '평균_H_index', '중요논문_총수', '평균_생산성점수', '평균_영향력점수']
    correlation_matrix = filtered_df[correlation_cols].corr()
    
    fig = px.imshow(correlation_matrix,
                   labels=dict(color="상관계수"),
                   color_continuous_scale='RdBu',
                   zmin=-1, zmax=1)
    st.plotly_chart(fig, use_container_width=True)
    
    # Top 연구 그룹
    st.subheader("🏆 Top 연구 그룹 (국가-기술)")
    
    top_groups = filtered_df.nlargest(10, '평균_영향력점수')[['국가', '기술라벨', '연도', '평균_영향력점수', '평균_H_index', '총_논문수']]
    
    fig = px.scatter(top_groups, x='평균_영향력점수', y='평균_H_index',
                    size='총_논문수', color='국가',
                    hover_data=['기술라벨', '연도'],
                    labels={'평균_영향력점수': '영향력 점수', '평균_H_index': 'H-index'})
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(top_groups, use_container_width=True, hide_index=True)

elif menu == "📋 상세 데이터":
    st.title("📋 상세 데이터 조회")
    st.markdown("---")
    
    # 데이터 필터링 옵션
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sort_by = st.selectbox("정렬 기준", correlation_cols)
    with col2:
        sort_order = st.radio("정렬 순서", ["내림차순", "오름차순"], horizontal=True)
    with col3:
        top_n = st.number_input("표시 개수", min_value=10, max_value=100, value=20, step=10)
    
    # 정렬
    sorted_df = filtered_df.sort_values(by=sort_by, ascending=(sort_order == "오름차순")).head(top_n)
    
    # 요약 통계
    st.subheader("📊 요약 통계")
    summary_stats = filtered_df[correlation_cols].describe().round(2)
    st.dataframe(summary_stats, use_container_width=True)
    
    # 상세 데이터 테이블
    st.subheader("🔍 상세 데이터")
    st.dataframe(sorted_df, use_container_width=True, hide_index=True)
    
    # 데이터 다운로드
    csv = sorted_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 CSV 다운로드",
        data=csv,
        file_name=f'research_papers_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv'
    )
    
    # SQL 쿼리 예시
    with st.expander("pkl 파일 생성/업데이트 코드"):
        st.code("""
import pandas as pd
import pickle

# 데이터 준비
df = pd.DataFrame({
    '국가': ['한국', '미국', ...],
    '기술라벨': ['AI/ML', '재생에너지', ...],
    '연도': [2020, 2021, ...],
    '총_논문수': [150, 200, ...],
    '평균_영향력': [3.5, 4.2, ...],
    '평균_H_index': [25, 30, ...],
    '중요논문_총수': [15, 25, ...],
    '평균_생산성점수': [75, 82, ...],
    '평균_영향력점수': [68, 75, ...]
})

# pkl 파일로 저장
with open('data/papers_data.pkl', 'wb') as f:
    pickle.dump(df, f)

# pkl 파일 읽기
with open('data/papers_data.pkl', 'rb') as f:
    df = pickle.load(f)
        """, language='python')

# 푸터
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **데이터 소스**: data/papers_data.pkl  
    **마지막 업데이트**: 데이터 파일 참조  
    """
)