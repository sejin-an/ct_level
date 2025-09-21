"""
데이터 로딩 및 전처리 유틸리티
utils/data_loader.py
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Tuple, List, Dict

class DataLoader:
    """데이터 로딩 및 전처리 클래스"""
    
    def __init__(self, file_path: str = '_통합평가자료.xlsx'):
        self.file_path = file_path
        self.raw_data = None
        self.papers_data = None
        self.patents_data = None
    
    @st.cache_data
    def load_excel_data(_self) -> pd.DataFrame:
        """엑셀 파일에서 데이터 로드"""
        try:
            df = pd.read_excel(_self.file_path, sheet_name='Sheet4')
            df.columns = df.columns.str.strip()
            df = df.dropna(subset=['Year'])
            return df
        except Exception as e:
            st.error(f"데이터 로드 오류: {e}")
            return pd.DataFrame()
    
    def preprocess_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """데이터 전처리"""
        df = df.copy()
        
        # 연도를 정수로 변환
        df['Year'] = df['Year'].astype(int)
        
        # 논문과 특허 데이터 분리
        papers_df = df[df['구분'] == '1. 논문'].copy()
        patents_df = df[df['구분'] == '2. 특허'].copy()
        
        # 논문 데이터 전처리
        papers_df = self._preprocess_papers(papers_df)
        
        # 특허 데이터 전처리
        patents_df = self._preprocess_patents(patents_df)
        
        return df, papers_df, patents_df
    
    def _preprocess_papers(self, papers_df: pd.DataFrame) -> pd.DataFrame:
        """논문 데이터 전처리"""
        if papers_df.empty:
            return papers_df
        
        # 결측값 처리
        numeric_columns = ['Total_Papers', 'H_Index', 'Q1_Ratio(%)', 
                          'Collaboration_Ratio(%)', 'Avg_Citations', 'Avg_mrnif']
        
        for col in numeric_columns:
            if col in papers_df.columns:
                papers_df[col] = pd.to_numeric(papers_df[col], errors='coerce').fillna(0)
        
        return papers_df
    
    def _preprocess_patents(self, patents_df: pd.DataFrame) -> pd.DataFrame:
        """특허 데이터 전처리"""
        if patents_df.empty:
            return patents_df
        
        # 특허 관련 컬럼명 매핑
        column_mapping = {
            'patent_count': 'patent_count',
            'triadic_ratio': 'triadic_ratio',
            'claims_per_patent': 'claims_per_patent',
            'foreign_filing_intensity': 'foreign_filing_intensity'
        }
        
        # 결측값 처리
        numeric_columns = list(column_mapping.values())
        
        for col in numeric_columns:
            if col in patents_df.columns:
                patents_df[col] = pd.to_numeric(patents_df[col], errors='coerce').fillna(0)
        
        return patents_df
    
    def filter_data(self, df: pd.DataFrame, year_range: Tuple[int, int], 
                   countries: List[str]) -> pd.DataFrame:
        """데이터 필터링"""
        filtered_df = df[
            (df['Year'] >= year_range[0]) & 
            (df['Year'] <= year_range[1]) & 
            (df['Country'].isin(countries))
        ]
        return filtered_df
    
    def get_summary_stats(self, df: pd.DataFrame) -> Dict:
        """요약 통계"""
        if df.empty:
            return {}
        
        return {
            'total_records': len(df),
            'years': sorted(df['Year'].unique()),
            'countries': sorted(df['Country'].unique()),
            'categories': sorted(df['구분'].unique()) if '구분' in df.columns else []
        }
    
    def get_yearly_summary(self, papers_df: pd.DataFrame, 
                          patents_df: pd.DataFrame) -> pd.DataFrame:
        """연도별 요약 데이터"""
        summary_data = []
        
        # 논문 데이터 요약
        if not papers_df.empty:
            papers_summary = papers_df.groupby(['Year', 'Country']).agg({
                'Total_Papers': 'sum',
                'H_Index': 'mean',
                'Q1_Ratio(%)': 'mean',
                'Collaboration_Ratio(%)': 'mean'
            }).reset_index()
            papers_summary['Type'] = 'Papers'
            summary_data.append(papers_summary)
        
        # 특허 데이터 요약
        if not patents_df.empty:
            patent_count_col = 'patent_count' if 'patent_count' in patents_df.columns else 'Total_Papers'
            
            agg_dict = {}
            if patent_count_col in patents_df.columns:
                agg_dict[patent_count_col] = 'sum'
            if 'triadic_ratio' in patents_df.columns:
                agg_dict['triadic_ratio'] = 'mean'
            if 'claims_per_patent' in patents_df.columns:
                agg_dict['claims_per_patent'] = 'mean'
            
            if agg_dict:
                patents_summary = patents_df.groupby(['Year', 'Country']).agg(agg_dict).reset_index()
                patents_summary['Type'] = 'Patents'
                summary_data.append(patents_summary)
        
        if summary_data:
            return pd.concat(summary_data, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def calculate_competitiveness_score(self, papers_df: pd.DataFrame, 
                                       patents_df: pd.DataFrame) -> pd.DataFrame:
        """경쟁력 점수 계산"""
        scores = []
        
        # 논문 기반 점수
        if not papers_df.empty:
            for _, row in papers_df.iterrows():
                paper_score = (
                    (row.get('Total_Papers', 0) * 0.3) +
                    (row.get('H_Index', 0) * 0.3) +
                    (row.get('Q1_Ratio(%)', 0) * 0.2) +
                    (row.get('Collaboration_Ratio(%)', 0) * 0.2)
                )
                
                scores.append({
                    'Year': row['Year'],
                    'Country': row['Country'],
                    'Type': 'Papers',
                    'Score': paper_score
                })
        
        # 특허 기반 점수
        if not patents_df.empty:
            patent_count_col = 'patent_count' if 'patent_count' in patents_df.columns else 'Total_Papers'
            
            for _, row in patents_df.iterrows():
                patent_score = (
                    (row.get(patent_count_col, 0) * 0.4) +
                    (row.get('triadic_ratio', 0) * 100 * 0.3) +
                    (row.get('claims_per_patent', 0) * 0.3)
                )
                
                scores.append({
                    'Year': row['Year'],
                    'Country': row['Country'],
                    'Type': 'Patents',
                    'Score': patent_score
                })
        
        return pd.DataFrame(scores) if scores else pd.DataFrame()

# 전역 데이터 로더 인스턴스
@st.cache_resource
def get_data_loader():
    """데이터 로더 싱글톤 인스턴스"""
    return DataLoader()

# 편의 함수들
def load_and_preprocess_data():
    """데이터 로드 및 전처리 (편의 함수)"""
    loader = get_data_loader()
    raw_data = loader.load_excel_data()
    
    if raw_data.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    return loader.preprocess_data(raw_data)

def get_available_filters(df: pd.DataFrame):
    """사용 가능한 필터 옵션 반환"""
    if df.empty:
        return [], (2020, 2024)
    
    countries = sorted(df['Country'].unique())
    year_min, year_max = int(df['Year'].min()), int(df['Year'].max())
    
    return countries, (year_min, year_max)