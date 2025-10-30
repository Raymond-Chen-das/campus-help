"""
AI 服務模組 - Campus Help
使用 Google Gemini API 提供 AI 增強功能
"""
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 嘗試導入 Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  警告: google-generativeai 未安裝，AI 功能將使用模擬模式")


class AIService:
    """AI 服務類別"""
    
    def __init__(self):
        """初始化 AI 服務"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                print("✅ Gemini AI 已啟用")
            except Exception as e:
                print(f"⚠️  Gemini 初始化失敗: {e}")
                self.model = None
        else:
            print("⚠️  Gemini API Key 未設定，使用模擬模式")
    
    @staticmethod
    def optimize_task_description(description):
        """
        優化任務描述
        
        Args:
            description (str): 原始任務描述
        
        Returns:
            dict: {'success': bool, 'optimized_description': str}
        """
        service = AIService()
        
        if not service.model:
            # 模擬模式
            return {
                'success': True,
                'optimized_description': f"{description}\n\n[AI 優化建議] 建議加入具體時間、地點和所需時長，讓幫助者更容易評估是否適合。"
            }
        
        try:
            prompt = f"""
你是一個任務描述優化專家。請幫忙優化以下任務描述，使其更清楚、具體、吸引人。

原始描述：
{description}

優化要求：
1. 保持原意，但更清楚具體
2. 加入時間、地點、所需技能等細節（如果缺少）
3. 讓描述更有吸引力
4. 保持簡潔（不超過原文的1.5倍長度）
5. 使用繁體中文

請直接輸出優化後的描述，不要加任何前綴或說明。
"""
            
            response = service.model.generate_content(prompt)
            optimized = response.text.strip()
            
            return {
                'success': True,
                'optimized_description': optimized
            }
        
        except Exception as e:
            print(f"AI 優化失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def risk_assessment(description, category):
        """
        任務風險審查
        
        Args:
            description (str): 任務描述
            category (str): 任務分類
        
        Returns:
            dict: {'success': bool, 'data': {...}}
        """
        service = AIService()
        
        # 關鍵字檢測（快速篩選）
        danger_keywords = [
            '代考', '代寫', '代購菸', '代購酒', '借錢', '貸款',
            '成人', '賭博', '非法', '色情', '毒品'
        ]
        
        flags = []
        for keyword in danger_keywords:
            if keyword in description:
                flags.append(keyword)
        
        if flags:
            return {
                'success': True,
                'data': {
                    'risk_level': 'critical',
                    'risk_score': 1.0,
                    'recommendation': '自動拒絕',
                    'reason': '包含禁止關鍵字',
                    'flags': flags
                }
            }
        
        if not service.model:
            # 模擬模式：通過安全檢查
            return {
                'success': True,
                'data': {
                    'risk_level': 'low',
                    'risk_score': 0.1,
                    'recommendation': '允許發布',
                    'reason': '未發現明顯風險',
                    'flags': []
                }
            }
        
        try:
            prompt = f"""
你是一個內容安全審查專家。請評估以下任務是否違反平台規範。

任務分類：{category}
任務描述：
{description}

平台禁止事項：
1. 代考、代寫報告（違反學術誠信）
2. 代購菸酒、成人內容（法律限制）
3. 金錢借貸相關（超出服務範圍）
4. 危險或違規活動（安全考量）

請以 JSON 格式回應：
{{
  "risk_level": "low/medium/high/critical",
  "risk_score": 0.0-1.0,
  "recommendation": "允許發布/需人工審核/自動拒絕",
  "reason": "簡短說明",
  "flags": ["風險標記列表"]
}}

只輸出 JSON，不要其他文字。
"""
            
            response = service.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # 移除可能的 markdown 標記
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            import json
            data = json.loads(result_text)
            
            return {
                'success': True,
                'data': data
            }
        
        except Exception as e:
            print(f"AI 風險審查失敗: {e}")
            # 失敗時預設允許（需人工審核）
            return {
                'success': True,
                'data': {
                    'risk_level': 'medium',
                    'risk_score': 0.5,
                    'recommendation': '需人工審核',
                    'reason': 'AI 審查失敗，建議人工檢查',
                    'flags': ['AI審查失敗']
                }
            }
    
    @staticmethod
    def parse_task_description(description):
        """
        解析任務描述，提取關鍵資訊
        
        Args:
            description (str): 任務描述
        
        Returns:
            dict: {'success': bool, 'data': {...}}
        """
        service = AIService()
        
        if not service.model:
            # 模擬模式
            return {
                'success': True,
                'data': {
                    'required_skills': ['通用技能'],
                    'estimated_time': '未指定',
                    'location_type': '實體',
                    'urgency': 'normal'
                }
            }
        
        try:
            prompt = f"""
請分析以下任務描述，提取關鍵資訊。

任務描述：
{description}

請以 JSON 格式回應：
{{
  "required_skills": ["所需技能列表"],
  "estimated_time": "預估時長",
  "location_type": "實體/線上/混合",
  "urgency": "low/normal/high",
  "key_points": ["關鍵要點列表"]
}}

只輸出 JSON，不要其他文字。
"""
            
            response = service.model.generate_content(prompt)
            result_text = response.text.strip()
            
            if result_text.startswith('```json'):
                result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            import json
            data = json.loads(result_text)
            
            return {
                'success': True,
                'data': data
            }
        
        except Exception as e:
            print(f"AI 解析失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# 測試用
if __name__ == '__main__':
    print("測試 AI 服務...")
    
    # 測試優化描述
    print("\n1. 測試任務描述優化:")
    result = AIService.optimize_task_description("幫忙搬東西")
    if result['success']:
        print(f"✅ 優化成功:\n{result['optimized_description']}")
    
    # 測試風險審查
    print("\n2. 測試風險審查:")
    result = AIService.risk_assessment("幫忙搬宿舍行李，約20分鐘", "日常支援")
    if result['success']:
        print(f"✅ 風險等級: {result['data']['risk_level']}")
        print(f"   建議: {result['data']['recommendation']}")
    
    # 測試解析
    print("\n3. 測試任務解析:")
    result = AIService.parse_task_description("需要會攝影的人幫忙拍活動照片，大約2小時")
    if result['success']:
        print(f"✅ 解析結果:")
        print(f"   技能: {result['data'].get('required_skills')}")
        print(f"   時長: {result['data'].get('estimated_time')}")
