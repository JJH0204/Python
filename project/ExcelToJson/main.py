import pandas as pd
import json
import os
from typing import Union, Dict, List

class ExcelToJsonConverter:
    def __init__(self, excel_path: str):
        """
        엑셀 파일을 JSON으로 변환하는 클래스
        Args:
            excel_path (str): 엑셀 파일 경로
        """
        self.excel_path = excel_path
        
    def read_excel(self, sheet_name: Union[str, int, None] = 0) -> pd.DataFrame:
        """
        엑셀 파일을 읽어오는 메서드
        Args:
            sheet_name: 시트 이름 또는 인덱스 (기본값: 0)
        Returns:
            pd.DataFrame: 읽어온 엑셀 데이터
        """
        try:
            return pd.read_excel(self.excel_path, sheet_name=sheet_name)
        except Exception as e:
            raise Exception(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {str(e)}")

    def convert_to_json(self, output_path: str, sheet_name: Union[str, int, None] = 0,
                       orient: str = 'records', indent: int = 2) -> None:
        """
        엑셀 데이터를 JSON 파일로 변환하는 메서드
        Args:
            output_path (str): 저장할 JSON 파일 경로
            sheet_name: 시트 이름 또는 인덱스 (기본값: 0)
            orient (str): JSON 변환 방식 (기본값: 'records')
            indent (int): JSON 들여쓰기 칸 수 (기본값: 2)
        """
        try:
            # 엑셀 파일 읽기
            df = self.read_excel(sheet_name)
            
            # DataFrame을 JSON으로 변환
            json_data = df.to_json(orient=orient, force_ascii=False, indent=indent)
            
            # JSON 파일 저장
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_data)
                
            print(f"변환이 완료되었습니다. 저장 경로: {output_path}")
            
        except Exception as e:
            raise Exception(f"JSON 변환 중 오류가 발생했습니다: {str(e)}")

def main():
    # 테스트용 엑셀 파일 경로
    excel_path = "student_data.xlsx"
    output_path = "student_data.json"
    
    converter = ExcelToJsonConverter(excel_path)
    converter.convert_to_json(output_path)

if __name__ == "__main__":
    main()
