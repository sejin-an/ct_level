"""
KPI 메트릭 컴포넌트
"""
import streamlit as st

def render_kpi_metrics(df, col_mapping, is_patent=False):
    """KPI 메트릭 카드 렌더링"""
    
    if is_patent:
        # 특허 KPI
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total = df[col_mapping.get('total_papers', 'total_papers')].sum()
            st.metric("🔬 총 특허수", f"{total:,}")
        
        with col2:
            if 'triadic_count' in col_mapping:
                triadic = df[col_mapping['triadic_count']].sum()
                st.metric("🌐 Triadic 특허", f"{triadic:,}")
        
        with col3:
            if 'h_index' in col_mapping:
                h_index = df[col_mapping['h_index']].mean()
                st.metric("📊 평균 H-Index", f"{h_index:.1f}")
        
        with col4:
            if 'avg_family_countries' in col_mapping:
                family = df[col_mapping['avg_family_countries']].mean()
                st.metric("🌍 평균 패밀리 국가", f"{family:.1f}")
        
        with col5:
            if 'citations_per_claim' in col_mapping:
                citations = df[col_mapping['citations_per_claim']].mean()
                st.metric("📈 청구항당 인용", f"{citations:.2f}")
    
    else:
        # 논문 KPI
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total = df[col_mapping.get('total_papers', 'totalpapers')].sum()
            st.metric("📄 총 논문수", f"{total:,}")
        
        with col2:
            if 'h_index' in col_mapping:
                h_index = df[col_mapping['h_index']].mean()
                st.metric("📊 평균 H-Index", f"{h_index:.1f}")
        
        with col3:
            if 'top10_ratio' in col_mapping:
                top10 = df[col_mapping['top10_ratio']].mean()
                st.metric("🎯 Top10%", f"{top10:.1f}%")
        
        with col4:
            if 'q1_ratio' in col_mapping:
                q1 = df[col_mapping['q1_ratio']].mean()
                st.metric("⭐ Q1 저널", f"{q1:.1f}%")
        
        with col5:
            if 'collaboration_ratio' in col_mapping:
                collab = df[col_mapping['collaboration_ratio']].mean()
                st.metric("🤝 국제협력", f"{collab:.1f}%")