"""
서지분석 대시보드 - 국가 비교 중심
"""
import streamlit as st
from utils.data_loader import load_data, filter_data

# 컴포넌트 임포트
from components.country_comparison import render_country_comparison
from components.country_trends import render_country_trends
from components.country_citation import render_country_citation
from components.country_collaboration import render_country_collaboration
from components.country_technology import render_country_technology
from components.country_patent import render_country_patent

st.set_page_config(page_title="서지분석 대시보드", page_icon="📊", layout="wide")

# 데이터 로드
paper_df, patent_df = load_data()

# 사이드바
st.sidebar.title("🔍 필터 설정")
st.sidebar.markdown("---")
paper_filtered, patent_filtered = filter_data(paper_df, patent_df, st.sidebar)

# 메인
st.title("📊 국가별 서지분석 대시보드")
st.markdown("---")

# 1. 국가별 종합 비교
render_country_comparison(paper_filtered, patent_filtered)
st.markdown("---")

# 2. 국가별 시계열 추이
render_country_trends(paper_filtered, patent_filtered)
st.markdown("---")

# 3. 국가별 인용 영향력
render_country_citation(paper_filtered)
st.markdown("---")

# 4. 국가별 협력 네트워크
render_country_collaboration(paper_filtered)
st.markdown("---")

# 5. 국가별 기술 포트폴리오
render_country_technology(paper_filtered, patent_filtered)
st.markdown("---")

# 6. 국가별 특허 경쟁력
render_country_patent(patent_filtered)

st.markdown("---")
st.caption("📊 Country-level Bibliometric Analysis")