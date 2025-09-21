"""
데이터 로더 모듈
data_loader.py
"""

import pandas as pd
import streamlit as st

class DataLoader:
    """단순 데이터 로더"""
    
    def __init__(self, file_path='_통합평가자료.xlsx'):
        self.file_path = file_path
    
    def load_data(self, sample_size=None):
        """데이터 로드"""
        try:
            if sample_size and sample_size != "전체":
                df = pd.read_excel(self.file_path, nrows=sample_size)
            else:
                df = pd.read_excel(self.file_path)
            
            # 컬럼명 정리
            df.columns = df.columns.str.strip()
            
            return df
            
        except Exception as e:
            st.error(f"데이터 로드 오류: {e}")
            return pd.DataFrame()
    
    def preprocess_data(self, df):
        """단순 전처리"""
        if df.empty:
            return pd.DataFrame(), pd.DataFrame()
        
        # Year 컬럼 처리
        if 'Year' in df.columns:
            df_clean = df.copy()
            df_clean['Year'] = pd.to_numeric(df_clean['Year'], errors='coerce')
            df_clean = df_clean[(df_clean['Year'] >= 2000) & (df_clean['Year'] <= 2030)]
            
            # 논문/특허 구분
            if '구분' in df_clean.columns:
                papers = df_clean[df_clean['구분'].astype(str).str.contains('논문|1\\.', na=False)]
                patents = df_clean[df_clean['구분'].astype(str).str.contains('특허|2\\.', na=False)]
            else:
                papers = df_clean.copy()
                patents = pd.DataFrame()
            
            return papers, patents
        else:
            return pd.DataFrame(), pd.DataFrame()
    
    def get_summary(self, papers_df, patents_df):
        """요약 정보"""
        summary = {
            'paper_count': len(papers_df),
            'patent_count': len(patents_df),
            'total_count': len(papers_df) + len(patents_df),
            'year_range': None,
            'country_count': 0
        }
        
        if not papers_df.empty and 'Year' in papers_df.columns:
            summary['year_range'] = (papers_df['Year'].min(), papers_df['Year'].max())
        
        if not papers_df.empty and 'Country' in papers_df.columns:
            summary['country_count'] = papers_df['Country'].nunique()
        
        return summary