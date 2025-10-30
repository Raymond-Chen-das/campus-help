"""
功能測試腳本
驗證所有模組是否正常運作
"""
import sys

def test_imports():
    """測試所有模組是否可以匯入"""
    print("🔍 測試 1: 檢查模組匯入...")
    
    try:
        import streamlit
        print("   ✅ Streamlit")
    except ImportError:
        print("   ❌ Streamlit 未安裝")
        return False
    
    try:
        import sqlalchemy
        print("   ✅ SQLAlchemy")
    except ImportError:
        print("   ❌ SQLAlchemy 未安裝")
        return False
    
    try:
        import pandas
        print("   ✅ Pandas")
    except ImportError:
        print("   ❌ Pandas 未安裝")
        return False
    
    try:
        import plotly
        print("   ✅ Plotly")
    except ImportError:
        print("   ❌ Plotly 未安裝")
        return False
    
    try:
        from database import init_db, get_all_users
        print("   ✅ database.py")
    except ImportError as e:
        print(f"   ❌ database.py 匯入失敗: {e}")
        return False
    
    try:
        from matching_engine import MatchingEngine
        print("   ✅ matching_engine.py")
    except ImportError as e:
        print(f"   ❌ matching_engine.py 匯入失敗: {e}")
        return False
    
    try:
        from ai_service import AIService
        print("   ✅ ai_service.py")
    except ImportError as e:
        print(f"   ❌ ai_service.py 匯入失敗: {e}")
        return False
    
    return True

def test_database():
    """測試資料庫功能"""
    print("\n🔍 測試 2: 資料庫功能...")
    
    try:
        from database import init_db, seed_test_data, get_all_users, get_all_tasks
        
        # 初始化
        init_db()
        print("   ✅ 資料庫初始化")
        
        # 填充資料
        seed_test_data()
        print("   ✅ 測試資料填充")
        
        # 查詢
        users = get_all_users()
        print(f"   ✅ 取得使用者: {len(users)} 位")
        
        tasks = get_all_tasks()
        print(f"   ✅ 取得任務: {len(tasks)} 個")
        
        return True
    except Exception as e:
        print(f"   ❌ 資料庫測試失敗: {e}")
        return False

def test_matching_engine():
    """測試媒合引擎"""
    print("\n🔍 測試 3: 媒合引擎...")
    
    try:
        from matching_engine import MatchingEngine
        
        # 測試資料
        user = {
            'id': 1,
            'name': '測試使用者',
            'campus': '外雙溪校區',
            'skills': ['攝影', '設計'],
            'avg_rating': 4.5,
            'completed_tasks': 10,
            'trust_score': 0.9,
            'willing_cross_campus': False
        }
        
        task = {
            'id': 1,
            'title': '測試任務',
            'description': '需要攝影協助',
            'category': '校園協助',
            'campus': '外雙溪校區',
            'is_urgent': False
        }
        
        engine = MatchingEngine()
        result = engine.calculate_match_score(user, task)
        
        print(f"   ✅ 媒合分數計算: {result['total_score']:.2%}")
        print(f"      - 技能: {result['skill_score']:.2%}")
        print(f"      - 時間: {result['time_score']:.2%}")
        print(f"      - 評價: {result['rating_score']:.2%}")
        print(f"      - 地點: {result['location_score']:.2%}")
        
        return True
    except Exception as e:
        print(f"   ❌ 媒合引擎測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_service():
    """測試 AI 服務"""
    print("\n🔍 測試 4: AI 服務...")
    
    try:
        from ai_service import AIService
        
        # 測試風險審查
        result = AIService.risk_assessment("幫忙搬東西", "日常支援")
        if result['success']:
            print(f"   ✅ 風險審查: {result['data']['recommendation']}")
        else:
            print(f"   ⚠️  風險審查: 使用模擬模式")
        
        # 測試描述優化
        result = AIService.optimize_task_description("幫忙搬東西")
        if result['success']:
            print(f"   ✅ 描述優化: 功能正常")
        else:
            print(f"   ⚠️  描述優化: 使用模擬模式")
        
        print("   ℹ️  如果顯示模擬模式，請設定 GEMINI_API_KEY")
        
        return True
    except Exception as e:
        print(f"   ❌ AI 服務測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("=" * 50)
    print("  Campus Help 功能測試")
    print("=" * 50)
    print()
    
    tests = [
        ("模組匯入", test_imports),
        ("資料庫功能", test_database),
        ("媒合引擎", test_matching_engine),
        ("AI 服務", test_ai_service),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ {name} 測試異常: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print("  測試結果")
    print("=" * 50)
    print(f"✅ 通過: {passed}/{len(tests)}")
    print(f"❌ 失敗: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 所有測試通過！可以啟動應用了！")
        print("\n執行以下指令啟動:")
        print("   streamlit run app.py")
        print("\n或直接執行:")
        print("   start.bat")
        return 0
    else:
        print("\n⚠️  部分測試失敗，請檢查錯誤訊息")
        return 1

if __name__ == '__main__':
    sys.exit(main())
