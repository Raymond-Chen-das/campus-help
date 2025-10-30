"""
配置檔案 - Campus Help
"""
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()


class Config:
    """應用配置"""
    
    # 應用資訊
    APP_NAME = "Campus Help"
    APP_SLOGAN = "有空幫一下，校園時間銀行"
    VERSION = "2.0 Streamlit"
    
    # 資料庫
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///campus_help.db')
    
    # Gemini API
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # 任務分類
    CATEGORIES = [
        "日常支援",
        "學習互助", 
        "校園協助",
        "技能交換",
        "情境陪伴"
    ]
    
    # 校區選項
    CAMPUSES = [
        "外雙溪校區",
        "城中校區",
        "線上"
    ]
    
    # 點數範圍
    POINTS_MIN = 10
    POINTS_MAX = 500
    POINTS_DEFAULT = 50
    
    # 媒合權重
    MATCHING_WEIGHTS = {
        'skill': 0.4,
        'time': 0.2,
        'rating': 0.2,
        'location': 0.2
    }
    
    # 安全關鍵字
    DANGER_KEYWORDS = [
        '代考', '代寫', '代購菸', '代購酒',
        '借錢', '貸款', '成人', '賭博', 
        '非法', '色情', '毒品'
    ]


# 測試用
if __name__ == '__main__':
    print("配置資訊:")
    print(f"應用名稱: {Config.APP_NAME}")
    print(f"版本: {Config.VERSION}")
    print(f"資料庫: {Config.DATABASE_URL}")
    print(f"Gemini API: {'已設定' if Config.GEMINI_API_KEY else '未設定'}")
