import pandas as pd

# 샘플 데이터 생성
data = {
    '학번': ['2023001', '2023002', '2023003', '2023004', '2023005'],
    '이름': ['김철수', '이영희', '박민수', '정지원', '최유진'],
    '나이': [20, 21, 19, 22, 20],
    '학과': ['컴퓨터공학과', '전자공학과', '소프트웨어학과', '정보통신공학과', '인공지능학과'],
    '평균성적': [85.5, 92.3, 88.7, 90.1, 87.9]
}

# DataFrame 생성
df = pd.DataFrame(data)

# 엑셀 파일로 저장
excel_path = 'student_data.xlsx'
df.to_excel(excel_path, index=False)
print(f"샘플 엑셀 파일이 생성되었습니다: {excel_path}")
