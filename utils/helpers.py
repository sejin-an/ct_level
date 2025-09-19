# utils/helpers.py
import streamlit as st

def get_available_metrics(df, preferred_metrics):
    """데이터프레임에서 사용 가능한 지표 목록 반환"""
    available_metrics = []
    
    for metric, name in preferred_metrics:
        if metric in df.columns:
            available_metrics.append((metric, name))
    
    return available_metrics