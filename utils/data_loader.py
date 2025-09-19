# utils/data_loader.py
import streamlit as st
import pandas as pd
import numpy as np
import os

@st.cache_data
def load_data(file_path):
    """엑셀 파일에서 데이터 로드"""
    try:
        # 파일 존재 확인
        if not os.path.exists(file_path):
            st.error(f"파일이 존재하지 않습니다: {file_path}")
            return None
            
        # 엑셀 파일 로드
        df = pd.read_excel(file_path)
        st.success(f"파일 로드 성공: {file_path}, 데이터 크기: {df.shape}")
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        import traceback
        st.error(f"상세 오류: {traceback.format_exc()}")
        return None

def create_sample_data():
    """샘플 데이터 생성"""
    # 국가 목록
    countries = ['US', 'CN', 'JP', 'KR', 'DE', 'FR', 'GB', 'IN', 'CA', 'IT', 
                'AU', 'ES', 'BR', 'RU', 'NL', 'CH', 'SE', 'SG', 'TR', 'PL']
    
    # 기본 데이터 생성
    data = []
    
    # 논문 데이터
    for country in countries:
        papers = int(np.random.exponential(1000) * (1 + countries.index(country) * 0.1))
        citations = int(papers * np.random.uniform(5, 15))
        h_index = int(np.sqrt(citations) * np.random.uniform(0.8, 1.2))
        
        data.append({
            "구분": "1. 논문",
            "Country": country,
            "논문 건수": papers,
            "Total_Citations": citations,
            "Avg_Citations": citations / papers if papers > 0 else 0,
            "H_Index": h_index,
            "Top10_Ratio(%)": np.random.uniform(5, 20),
            "Q1_Ratio(%)": np.random.uniform(30, 60),
            "Collaboration_Ratio(%)": np.random.uniform(40, 80),
            "label_m": np.random.randint(1, 39),  # 38대 분류
            "label_s": np.random.randint(1, 83),  # 82대 분류
            "label_m_title": f"기술분류_38_{np.random.randint(1, 39)}",
            "label_s_title": f"기술분류_82_{np.random.randint(1, 83)}"
        })
    
    # 특허 데이터
    for country in countries:
        patents = int(np.random.exponential(800) * (1 + countries.index(country) * 0.08))
        citations = int(patents * np.random.uniform(3, 10))
        h_index = int(np.sqrt(citations) * np.random.uniform(0.7, 1.1))
        
        data.append({
            "구분": "2. 특허",
            "Country": country,
            "total_papers_granted": patents,
            "total_citations": citations,
            "avg_citations": citations / patents if patents > 0 else 0,
            "h_index": h_index,
            "triadic_ratio": np.random.uniform(0.05, 0.3),
            "foreign_filing_intensity": np.random.uniform(2, 8),
            "patent_impact": np.random.uniform(0.5, 2),
            "label_m": np.random.randint(1, 39),  # 38대 분류
            "label_s": np.random.randint(1, 83),  # 82대 분류
            "label_m_title": f"기술분류_38_{np.random.randint(1, 39)}",
            "label_s_title": f"기술분류_82_{np.random.randint(1, 83)}"
        })
    
    return pd.DataFrame(data)

def preprocess_data(df):
    """데이터 전처리"""
    if df is None:
        return None, None
    
    # 논문/특허 구분
    if '구분' in df.columns:
        paper_df = df[df['구분'] == '1. 논문'].copy()
        patent_df = df[df['구분'] == '2. 특허'].copy()
    else:
        st.error("데이터에 '구분' 컬럼이 없습니다.")
        return None, None
    
    # 국가 컬럼 확인
    country_col = None
    for col_name in ['Country', 'country']:
        if col_name in paper_df.columns:
            country_col = col_name
            break
    
    if country_col is None:
        st.warning("국가 컬럼을 찾을 수 없습니다.")
    else:
        # 국가 컬럼 이름 표준화
        if country_col != 'Country':
            paper_df['Country'] = paper_df[country_col]
            patent_df['Country'] = patent_df[country_col]
    
    # 기술 분류 정보 추가
    for data_df in [paper_df, patent_df]:
        if 'label_m' in data_df.columns and 'label_m_title' in data_df.columns:
            data_df['기술분류_38'] = data_df['label_m_title']
        
        if 'label_s' in data_df.columns and 'label_s_title' in data_df.columns:
            data_df['기술분류_82'] = data_df['label_s_title']
    
    return paper_df, patent_df

def get_top20_countries(paper_df, patent_df):
    """논문과 특허 데이터에서 상위 20개국 필터링"""
    # 논문 기준 상위 국가
    paper_top = []
    if paper_df is not None and 'Country' in paper_df.columns:
        # 논문 지표 후보들
        paper_metrics = ['논문 건수', 'Total_Papers', '논문 점유율(%)', 'H_Index']
        
        for metric in paper_metrics:
            if metric in paper_df.columns:
                paper_top = paper_df.groupby('Country')[metric].sum().nlargest(20).index.tolist()
                st.info(f"논문 기준 상위 20개국: {', '.join(paper_top[:5])}...")
                break
    
    # 특허 기준 상위 국가
    patent_top = []
    if patent_df is not None and 'Country' in patent_df.columns:
        # 특허 지표 후보들
        patent_metrics = ['total_papers_granted', 'patent_share', 'h_index', 'total_citations']
        
        for metric in patent_metrics:
            if metric in patent_df.columns:
                patent_top = patent_df.groupby('Country')[metric].sum().nlargest(20).index.tolist()
                st.info(f"특허 기준 상위 20개국: {', '.join(patent_top[:5])}...")
                break
    
    # 우선순위: 논문 top10 + 특허 top10 (중복 제거)
    combined = list(dict.fromkeys(paper_top[:10] + patent_top[:10]))
    
    # 남은 자리는 논문, 특허 순위로 채움
    if len(combined) < 20:
        remaining = 20 - len(combined)
        extra_countries = [c for c in paper_top[10:] + patent_top[10:] if c not in combined]
        combined.extend(extra_countries[:remaining])
    
    # 최대 20개로 제한
    top_countries = combined[:20]
    
    st.success(f"분석 대상 상위 20개국 선정 완료: {', '.join(top_countries)}")
    
    return top_countries
    
def show_debug_info(df, paper_df, patent_df):
    """디버깅 정보 표시"""
    with st.expander("데이터 디버깅 정보", expanded=False):
        st.write("### 원본 데이터")
        st.write(f"크기: {df.shape}")
        st.write(f"컬럼: {', '.join(df.columns)}")
        st.write("첫 5개 행:")
        st.dataframe(df.head())
        
        st.write("### 논문 데이터")
        if paper_df is not None:
            st.write(f"크기: {paper_df.shape}")
            st.write("사용 가능한 지표 컬럼:")
            for col in paper_df.columns:
                if paper_df[col].dtype in ['int64', 'float64']:
                    st.write(f"- {col} ({paper_df[col].dtype})")
            st.write("첫 5개 행:")
            st.dataframe(paper_df.head())
        else:
            st.write("논문 데이터 없음")
        
        st.write("### 특허 데이터")
        if patent_df is not None:
            st.write(f"크기: {patent_df.shape}")
            st.write("사용 가능한 지표 컬럼:")
            for col in patent_df.columns:
                if patent_df[col].dtype in ['int64', 'float64']:
                    st.write(f"- {col} ({patent_df[col].dtype})")
            st.write("첫 5개 행:")
            st.dataframe(patent_df.head())
        else:
            st.write("특허 데이터 없음")