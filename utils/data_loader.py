"""
수정된 데이터 로딩 및 전처리 유틸리티
utils/data_loader.py
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Tuple, List, Dict

class DataLoader:
    """데이터 로딩 및 전처리 클래스 - 연도별/재산출 지표 구분"""
    
    def __init__(self, file_path: str = '_통합평가자료.xlsx'):
        self.file_path = file_path
        self.raw_data = None
        self.yearly_data = None  # Year가 있는 원시 데이터
        self.summary_data = None  # Year가 없는 재산출 지표
    
    @st.cache_data
    def load_excel_data(_self) -> pd.DataFrame:
        """엑셀 파일에서 데이터 로드"""
        try:
            df = pd.read_excel(_self.file_path, sheet_name='Sheet4')
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            st.error(f"데이터 로드 오류: {e}")
            return pd.DataFrame()
    
    def separate_data_types(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """연도별 데이터와 재산출 지표 분리"""
        # Year가 있는 데이터 (원시 측정값)
        yearly_data = df[df['Year'].notna()].copy()
        
        # Year가 없는 데이터 (재산출 지표)
        summary_data = df[df['Year'].isna()].copy()
        
        return yearly_data, summary_data
    
    def preprocess_yearly_data(self, yearly_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """연도별 원시 데이터 전처리"""
        if yearly_df.empty:
            return pd.DataFrame(), pd.DataFrame()
        
        # 연도를 정수로 변환
        yearly_df['Year'] = yearly_df['Year'].astype(int)
        
        # 논문과 특허 데이터 분리
        papers_yearly = yearly_df[yearly_df['구분'] == '1. 논문'].copy()
        patents_yearly = yearly_df[yearly_df['구분'] == '2. 특허'].copy()
        
        # 논문 데이터 전처리
        if not papers_yearly.empty:
            paper_columns = ['Total_Papers', 'H_Index', 'Q1_Ratio(%)', 
                           'Collaboration_Ratio(%)', 'Avg_Citations', 'Avg_mrnif']
            for col in paper_columns:
                if col in papers_yearly.columns:
                    papers_yearly[col] = pd.to_numeric(papers_yearly[col], errors='coerce').fillna(0)
        
        # 특허 데이터 전처리  
        if not patents_yearly.empty:
            # 원시 특허 데이터는 Total_Papers 컬럼을 특허 수로 사용
            if 'Total_Papers' in patents_yearly.columns:
                patents_yearly['Patent_Count'] = patents_yearly['Total_Papers']
        
        return papers_yearly, patents_yearly
    
    def preprocess_summary_data(self, summary_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """재산출 지표 데이터 전처리"""
        if summary_df.empty:
            return pd.DataFrame(), pd.DataFrame()
        
        # 논문과 특허 재산출 지표 분리
        papers_summary = summary_df[summary_df['구분'] == '1. 논문'].copy()
        patents_summary = summary_df[summary_df['구분'] == '2. 특허'].copy()
        
        # 논문 재산출 지표 전처리
        if not papers_summary.empty:
            paper_summary_columns = [
                '논문 건수', '논문 점유율(%)', '논문 증가율(%)', '논문 영향력',
                '중요 논문 건수', '중요 논문 비율(%)', 'Top 10% 논문 수', 'Top 10% 비율(%)',
                'Q1 논문 수', 'Q1 논문 비율(%)', 'MRNIF 평균', 'H-index',
                '국제협력 논문 수', '국제협력 비율(%)'
            ]
            
            for col in paper_summary_columns:
                if col in papers_summary.columns:
                    papers_summary[col] = pd.to_numeric(papers_summary[col], errors='coerce').fillna(0)
        
        # 특허 재산출 지표 전처리
        if not patents_summary.empty:
            patent_summary_columns = [
                'patent_count', 'patent_share', 'growth_rate', 'foreign_filing_intensity',
                'patent_impact', 'important_patent_share', 'ip4_share', 'claims_per_patent',
                'total_citations', 'avg_citations', 'triadic_ratio', 'granted_ratio'
            ]
            
            for col in patent_summary_columns:
                if col in patents_summary.columns:
                    patents_summary[col] = pd.to_numeric(patents_summary[col], errors='coerce').fillna(0)
        
        return papers_summary, patents_summary
    
    def load_and_preprocess_all(self) -> Dict[str, pd.DataFrame]:
        """모든 데이터 로드 및 전처리"""
        # 원본 데이터 로드
        raw_df = self.load_excel_data()
        
        if raw_df.empty:
            return {
                'raw': pd.DataFrame(),
                'yearly': pd.DataFrame(),
                'summary': pd.DataFrame(),
                'papers_yearly': pd.DataFrame(),
                'patents_yearly': pd.DataFrame(),
                'papers_summary': pd.DataFrame(),
                'patents_summary': pd.DataFrame()
            }
        
        # 연도별/재산출 데이터 분리
        yearly_data, summary_data = self.separate_data_types(raw_df)
        
        # 연도별 데이터 전처리
        papers_yearly, patents_yearly = self.preprocess_yearly_data(yearly_data)
        
        # 재산출 지표 전처리
        papers_summary, patents_summary = self.preprocess_summary_data(summary_data)
        
        return {
            'raw': raw_df,
            'yearly': yearly_data,
            'summary': summary_data,
            'papers_yearly': papers_yearly,
            'patents_yearly': patents_yearly,
            'papers_summary': papers_summary,
            'patents_summary': patents_summary
        }
    
    def get_available_years(self, yearly_df: pd.DataFrame) -> List[int]:
        """사용 가능한 연도 목록"""
        if yearly_df.empty or 'Year' not in yearly_df.columns:
            return []
        return sorted(yearly_df['Year'].unique())
    
    def get_available_countries(self, df: pd.DataFrame) -> List[str]:
        """사용 가능한 국가 목록"""
        if df.empty or 'Country' not in df.columns:
            return []
        return sorted(df['Country'].unique())
    
    def create_combined_summary(self, papers_yearly: pd.DataFrame, patents_yearly: pd.DataFrame,
                               papers_summary: pd.DataFrame, patents_summary: pd.DataFrame) -> pd.DataFrame:
        """연도별 데이터와 재산출 지표를 결합한 종합 요약"""
        combined_data = []
        
        # 모든 국가 목록 수집
        all_countries = set()
        
        for df in [papers_yearly, patents_yearly, papers_summary, patents_summary]:
            if not df.empty and 'Country' in df.columns:
                all_countries.update(df['Country'].unique())
        
        # 국가별 데이터 통합
        for country in all_countries:
            country_data = {'Country': country}
            
            # 연도별 논문 데이터 (최신 연도)
            country_papers_yearly = papers_yearly[papers_yearly['Country'] == country]
            if not country_papers_yearly.empty:
                latest_paper = country_papers_yearly.iloc[-1]  # 최신 연도
                country_data.update({
                    'Year_Papers': latest_paper.get('Total_Papers', 0),
                    'Year_H_Index': latest_paper.get('H_Index', 0),
                    'Year_Q1_Ratio': latest_paper.get('Q1_Ratio(%)', 0),
                    'Year': latest_paper.get('Year', 0)
                })
            
            # 연도별 특허 데이터 (최신 연도)
            country_patents_yearly = patents_yearly[patents_yearly['Country'] == country]
            if not country_patents_yearly.empty:
                latest_patent = country_patents_yearly.iloc[-1]  # 최신 연도
                country_data.update({
                    'Year_Patents': latest_patent.get('Patent_Count', 0),
                })
            
            # 재산출 논문 지표
            country_papers_summary = papers_summary[papers_summary['Country'] == country]
            if not country_papers_summary.empty:
                paper_summary = country_papers_summary.iloc[0]
                country_data.update({
                    'Total_Papers': paper_summary.get('논문 건수', 0),
                    'Paper_Share': paper_summary.get('논문 점유율(%)', 0),
                    'Paper_Growth': paper_summary.get('논문 증가율(%)', 0),
                    'Paper_Impact': paper_summary.get('논문 영향력', 0),
                    'Important_Papers': paper_summary.get('중요 논문 건수', 0),
                    'Q1_Papers': paper_summary.get('Q1 논문 수', 0),
                    'Q1_Paper_Ratio': paper_summary.get('Q1 논문 비율(%)', 0),
                    'Collaboration_Papers': paper_summary.get('국제협력 논문 수', 0),
                    'Collaboration_Ratio': paper_summary.get('국제협력 비율(%)', 0),
                    'Summary_H_Index': paper_summary.get('H-index', 0)
                })
            
            # 재산출 특허 지표
            country_patents_summary = patents_summary[patents_summary['Country'] == country]
            if not country_patents_summary.empty:
                patent_summary = country_patents_summary.iloc[0]
                country_data.update({
                    'Total_Patents': patent_summary.get('patent_count', 0),
                    'Patent_Share': patent_summary.get('patent_share', 0) * 100,
                    'Patent_Growth': patent_summary.get('growth_rate', 0) * 100,
                    'Patent_Impact': patent_summary.get('patent_impact', 0),
                    'Important_Patent_Share': patent_summary.get('important_patent_share', 0) * 100,
                    'Foreign_Filing': patent_summary.get('foreign_filing_intensity', 0),
                    'Claims_per_Patent': patent_summary.get('claims_per_patent', 0),
                    'Triadic_Ratio': patent_summary.get('triadic_ratio', 0) * 100 if patent_summary.get('triadic_ratio', 0) < 1 else patent_summary.get('triadic_ratio', 0),
                    'Patent_Citations': patent_summary.get('avg_citations', 0)
                })
            
            combined_data.append(country_data)
        
        return pd.DataFrame(combined_data)

# 전역 함수들
@st.cache_resource
def get_data_loader():
    """데이터 로더 싱글톤 인스턴스"""
    return DataLoader()

def load_all_data():
    """모든 데이터 로드 (편의 함수)"""
    loader = get_data_loader()
    return loader.load_and_preprocess_all()

def get_data_info(data_dict: Dict[str, pd.DataFrame]) -> Dict:
    """데이터 정보 요약"""
    info = {}
    
    for key, df in data_dict.items():
        if not df.empty:
            info[key] = {
                'rows': len(df),
                'columns': len(df.columns),
                'countries': df['Country'].nunique() if 'Country' in df.columns else 0,
                'years': sorted(df['Year'].unique()) if 'Year' in df.columns and df['Year'].notna().any() else []
            }
        else:
            info[key] = {'rows': 0, 'columns': 0, 'countries': 0, 'years': []}
    
    return info