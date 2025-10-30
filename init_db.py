"""
資料庫初始化腳本
執行此腳本以建立資料庫和填充測試資料
"""
from database import init_db, seed_test_data

if __name__ == '__main__':
    print("=" * 50)
    print("  Campus Help 資料庫初始化")
    print("=" * 50)
    
    print("\n📦 建立資料庫結構...")
    init_db()
    print("✅ 資料庫結構建立完成")
    
    print("\n📊 填充測試資料...")
    seed_test_data()
    
    print("\n" + "=" * 50)
    print("  初始化完成！")
    print("=" * 50)
    print("\n🚀 執行以下指令啟動應用：")
    print("   streamlit run app.py")
    print("\n📝 測試帳號：")
    print("   - 王小美 (資訊管理學系)")
    print("   - 李大明 (企業管理學系)")
    print("   - 陳小華 (英文學系)")
    print("   - 張志明 (數學系)")
