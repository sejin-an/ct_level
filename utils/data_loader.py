"""
데이터 로더 및 전처리 유틸리티
utils/data_loader.py
"""

import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data():
    """엑셀 파일에서 데이터 로드"""
    excel_file = '_통합평가자료.xlsx'
    
    papers_df = None
    patents_df = None
    
    if os.path.exists(excel_file):
        try:
            # 엑셀 파일의 모든 시트 확인
            excel_sheets = pd.ExcelFile(excel_file).sheet_names
            st.sidebar.info(f"발견된 시트: {', '.join(excel_sheets)}")
            
            # 첫 번째 시트를 논문 데이터로 사용
            papers_df = pd.read_excel(excel_file, sheet_name=0)
            st.sidebar.success(f"논문 데이터 로드 완료: {len(papers_df):,} 행, {len(papers_df.columns)} 열")
            
            # 두 번째 시트가 있으면 특허 데이터로 사용
            if len(excel_sheets) > 1:
                patents_df = pd.read_excel(excel_file, sheet_name=1)
                st.sidebar.success(f"특허 데이터 로드 완료: {len(patents_df):,} 행, {len(patents_df.columns)} 열")
            else:
                # 특허 관련 컬럼이 있는지 확인하여 분리
                patent_cols = [col for col in papers_df.columns if any(keyword in col.lower() 
                             for keyword in ['patent', 'triadic', 'claims', '특허'])]
                if patent_cols:
                    patents_df = papers_df[['Year', 'Country'] + patent_cols].copy()
                    st.sidebar.info("논문 데이터에서 특허 관련 컬럼을 분리했습니다.")
            
        except Exception as e:
            st.sidebar.error(f"엑셀 파일 로드 실패: {e}")
    else:
        st.sidebar.warning(f"엑셀 파일을 찾을 수 없습니다: {excel_file}")
    
    return papers_df, patents_df

def filter_data(papers_df, patents_df, sidebar):
    """사이드바 필터 적용"""
    
    # 연도 범위 설정
    min_year, max_year = get_year_range(papers_df, patents_df)
    
    year_range = sidebar.slider(
        "연도 범위",
        min_value=int(min_year),
        max_value=int(max_year),
        value=(int(min_year), int(max_year))
    )
    
    # 국가 필터
    available_countries = get_all_countries(papers_df, patents_df)
    
    if available_countries:
        selected_countries = sidebar.multiselect(
            "국가 선택",
            options=['전체'] + available_countries,
            default=['전체']
        )
    else:
        selected_countries = ['전체']
    
    # 필터링 적용
    filtered_papers = apply_year_filter(papers_df, year_range)
    filtered_patents = apply_year_filter(patents_df, year_range)
    
    if '전체' not in selected_countries:
        filtered_papers = apply_country_filter(filtered_papers, selected_countries)
        filtered_patents = apply_country_filter(filtered_patents, selected_countries)
    
    return filtered_papers, filtered_patents

def get_year_range(papers_df, patents_df):
    """데이터에서 연도 범위 추출"""
    min_year, max_year = 2015, 2024
    
    for df in [papers_df, patents_df]:
        if df is not None and not df.empty:
            year_col = find_year_column(df)
            if year_col and year_col in df.columns:
                try:
                    # 숫자형 연도만 추출
                    years = pd.to_numeric(df[year_col], errors='coerce').dropna()
                    if not years.empty:
                        df_min = int(years.min())
                        df_max = int(years.max())
                        min_year = min(min_year, df_min)
                        max_year = max(max_year, df_max)
                except (ValueError, TypeError):
                    continue
    
    return min_year, max_year

def get_all_countries(papers_df, patents_df):
    """모든 데이터에서 국가 목록 추출"""
    countries = set()
    
    for df in [papers_df, patents_df]:
        if df is not None:
            country_col = find_country_column(df)
            if country_col:
                countries.update(df[country_col].dropna().unique())
    
    return sorted(list(countries))

def find_year_column(df):
    """연도 컬럼 찾기"""
    if df is None:
        return None
    
    for col in df.columns:
        if col.lower() in ['year', '연도', 'yr']:
            return col
    return None

def find_country_column(df):
    """국가 컬럼 찾기"""
    if df is None:
        return None
    
    for col in df.columns:
        if col.lower() in ['country', '국가', 'nation', 'countries']:
            return col
    return None

def apply_year_filter(df, year_range):
    """연도 필터 적용"""
    if df is None or df.empty:
        return df
    
    year_col = find_year_column(df)
    if year_col and year_col in df.columns:
        try:
            # 연도를 숫자로 변환
            years = pd.to_numeric(df[year_col], errors='coerce')
            mask = (years >= year_range[0]) & (years <= year_range[1])
            return df[mask]
        except Exception:
            return df
    
    return df

def apply_country_filter(df, selected_countries):
    """국가 필터 적용"""
    if df is None or df.empty:
        return df
    
    country_col = find_country_column(df)
    if country_col and country_col in df.columns:
        try:
            return df[df[country_col].isin(selected_countries)]
        except Exception:
            return df
    
    return df

# 호환성을 위한 추가 함수들
def get_available_countries(papers_df, patents_df=None):
    """사용 가능한 국가 목록 반환 (호환성)"""
    return get_all_countries(papers_df, patents_df)

def get_available_years(papers_df, patents_df=None):
    """사용 가능한 연도 범위 반환 (호환성)"""
    min_year, max_year = get_year_range(papers_df, patents_df)
    return int(min_year), int(max_year)

class DataLoader:
    """데이터 로더 클래스 (호환성)"""
    
    def __init__(self):
        self.papers_df = None
        self.patents_df = None
    
    def load_data(self, sample_size="전체"):
        """데이터 로드"""
        excel_file = '_통합평가자료.xlsx'
        
        if os.path.exists(excel_file):
            try:
                # 전체 데이터 로드
                df = pd.read_excel(excel_file, sheet_name=0)
                
                # 샘플링
                if sample_size != "전체" and isinstance(sample_size, int):
                    if len(df) > sample_size:
                        df = df.sample(n=sample_size, random_state=42)
                
                return df
            except Exception as e:
                st.error(f"데이터 로드 실패: {e}")
                return pd.DataFrame()
        else:
            st.warning("엑셀 파일을 찾을 수 없습니다.")
            return pd.DataFrame()
    
    def preprocess_data(self, df):
        """데이터 전처리"""
        if df.empty:
            return pd.DataFrame(), pd.DataFrame()
        
        # 논문 관련 컬럼 확인
        paper_cols = ['Year', 'Country']
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['paper', 'h_index', 'citation', 'q1', 'collaboration']):
                paper_cols.append(col)
        
        # 특허 관련 컬럼 확인
        patent_cols = ['Year', 'Country']
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['patent', 'triadic', 'claims']):
                patent_cols.append(col)
        
        # 중복 제거
        paper_cols = list(set(paper_cols))
        patent_cols = list(set(patent_cols))
        
        # 실제 존재하는 컬럼만 선택
        paper_cols = [col for col in paper_cols if col in df.columns]
        patent_cols = [col for col in patent_cols if col in df.columns]
        
        papers_df = df[paper_cols].copy() if paper_cols else pd.DataFrame()
        patents_df = df[patent_cols].copy() if patent_cols else pd.DataFrame()
        
        return papers_df, patents_df
    
    def get_summary_stats(self, papers_df, patents_df):
        """요약 통계 생성"""
        paper_count = len(papers_df) if papers_df is not None and not papers_df.empty else 0
        patent_count = len(patents_df) if patents_df is not None and not patents_df.empty else 0
        
        year_range = None
        country_count = 0
        
        # 연도 범위 계산
        all_years = []
        if papers_df is not None and not papers_df.empty:
            year_col = find_year_column(papers_df)
            if year_col and year_col in papers_df.columns:
                # 숫자형 연도만 추출
                years = papers_df[year_col].dropna()
                years = pd.to_numeric(years, errors='coerce').dropna()
                if not years.empty:
                    all_years.extend(years.tolist())
        
        if patents_df is not None and not patents_df.empty:
            year_col = find_year_column(patents_df)
            if year_col and year_col in patents_df.columns:
                # 숫자형 연도만 추출
                years = patents_df[year_col].dropna()
                years = pd.to_numeric(years, errors='coerce').dropna()
                if not years.empty:
                    all_years.extend(years.tolist())
        
        if all_years:
            try:
                min_year = int(min(all_years))
                max_year = int(max(all_years))
                year_range = (min_year, max_year)
            except (ValueError, TypeError):
                year_range = None
        # 국가 수 계산
        all_countries = set()
        if papers_df is not None and not papers_df.empty:
            country_col = find_country_column(papers_df)
            if country_col and country_col in papers_df.columns:
                try:
                    countries = papers_df[country_col].dropna().unique()
                    all_countries.update(countries)
                except Exception:
                    pass
        
        if patents_df is not None and not patents_df.empty:
            country_col = find_country_column(patents_df)
            if country_col and country_col in patents_df.columns:
                try:
                    countries = patents_df[country_col].dropna().unique()
                    all_countries.update(countries)
                except Exception:
                    pass
        
        country_count = len(all_countries)
        
        return {
            'paper_count': paper_count,
            'patent_count': patent_count,
            'total_count': paper_count + patent_count,
            'year_range': year_range,
            'country_count': country_count
        }
    
    def filter_data_by_years(self, papers_df, patents_df, year_range):
        """연도별 필터링"""
        filtered_papers = apply_year_filter(papers_df, year_range)
        filtered_patents = apply_year_filter(patents_df, year_range)
        return filtered_papers, filtered_patents
    
    def filter_data_by_countries(self, papers_df, patents_df, countries):
        """국가별 필터링"""
        filtered_papers = apply_country_filter(papers_df, countries)
        filtered_patents = apply_country_filter(patents_df, countries)
        return filtered_papers, filtered_patents