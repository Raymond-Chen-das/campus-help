"""
智慧媒合引擎 - Campus Help
多因子加權模型計算媒合分數
"""
from datetime import datetime

class MatchingEngine:
    """任務媒合引擎"""
    
    # 權重配置
    WEIGHTS = {
        'skill': 0.4,      # 技能匹配度
        'time': 0.2,       # 時間重疊度
        'rating': 0.2,     # 評價信任值
        'location': 0.2    # 地點相符度
    }
    
    def calculate_match_score(self, user, task):
        """
        計算使用者與任務的媒合分數
        
        Args:
            user (dict): 使用者資料
            task (dict): 任務資料
        
        Returns:
            dict: 包含各項分數和總分的字典
        """
        # 1. 技能匹配度
        skill_score = self._calculate_skill_score(user, task)
        
        # 2. 時間重疊度 (簡化版：假設都有空)
        time_score = self._calculate_time_score(user, task)
        
        # 3. 評價信任值
        rating_score = self._calculate_rating_score(user)
        
        # 4. 地點相符度
        location_score = self._calculate_location_score(user, task)
        
        # 計算總分
        total_score = (
            skill_score * self.WEIGHTS['skill'] +
            time_score * self.WEIGHTS['time'] +
            rating_score * self.WEIGHTS['rating'] +
            location_score * self.WEIGHTS['location']
        )
        
        return {
            'total_score': total_score,
            'skill_score': skill_score,
            'time_score': time_score,
            'rating_score': rating_score,
            'location_score': location_score,
            'breakdown': {
                '技能匹配': f"{skill_score:.0%}",
                '時間相符': f"{time_score:.0%}",
                '評價信任': f"{rating_score:.0%}",
                '地點相符': f"{location_score:.0%}"
            }
        }
    
    def _calculate_skill_score(self, user, task):
        """
        計算技能匹配度
        
        邏輯：
        - 根據任務分類推斷所需技能
        - 計算使用者技能與任務需求的重疊度
        """
        user_skills = set([s.lower() for s in user.get('skills', [])])
        
        # 根據任務分類推斷所需技能
        category = task.get('category', '')
        required_skills = self._infer_skills_from_category(category, task)
        
        if not required_skills:
            return 0.5  # 無法判斷時給中等分數
        
        # 計算重疊度
        overlap = len(user_skills.intersection(required_skills))
        
        if overlap == 0:
            return 0.3  # 基礎分數（願意嘗試）
        
        # 有重疊技能
        score = min(1.0, 0.5 + (overlap * 0.2))  # 每個匹配技能加 20%
        return score
    
    def _infer_skills_from_category(self, category, task):
        """根據任務分類和描述推斷所需技能"""
        description = task.get('description', '').lower()
        title = task.get('title', '').lower()
        combined = description + ' ' + title
        
        # 技能關鍵字映射
        skill_keywords = {
            '搬運': ['搬', '搬運', '行李', '家具'],
            '修理電腦': ['電腦', '修理', '維修', '重灌'],
            '攝影': ['攝影', '拍照', '相機', '照片'],
            '設計': ['設計', 'photoshop', 'ps', '美編', '排版'],
            '教學': ['教', '解題', '輔導', '家教'],
            '程式設計': ['程式', 'python', 'coding', '寫程式'],
            '翻譯': ['翻譯', '英文', '日文'],
            '跑腿': ['代購', '買', '送']
        }
        
        inferred_skills = set()
        for skill, keywords in skill_keywords.items():
            if any(keyword in combined for keyword in keywords):
                inferred_skills.add(skill.lower())
        
        # 根據分類加入通用技能
        category_skills = {
            '日常支援': {'搬運', '跑腿'},
            '學習互助': {'教學'},
            '校園協助': {'攝影', '活動協助'},
            '技能交換': {'設計', '程式設計'}
        }
        
        if category in category_skills:
            inferred_skills.update([s.lower() for s in category_skills[category]])
        
        return inferred_skills
    
    def _calculate_time_score(self, user, task):
        """
        計算時間重疊度
        
        簡化版：假設使用者都有空（黑客松展示用）
        實際版本需要比對時間表
        """
        # 如果是急件，降低分數（除非使用者明確表示有空）
        if task.get('is_urgent'):
            return 0.8
        
        return 1.0  # 簡化版：假設時間都合適
    
    def _calculate_rating_score(self, user):
        """
        計算評價信任值
        
        基於：
        - 平均評分
        - 完成率（用完成任務數估算）
        - 信任值
        """
        avg_rating = user.get('avg_rating', 3.0)
        trust_score = user.get('trust_score', 0.5)
        completed = user.get('completed_tasks', 0)
        
        # 歸一化評分 (1-5 → 0-1)
        rating_normalized = (avg_rating - 1) / 4
        
        # 完成率評估（完成越多，越可靠）
        completion_factor = min(1.0, completed / 20)  # 20個任務為滿分
        
        # 綜合計算
        score = (
            rating_normalized * 0.5 +
            trust_score * 0.3 +
            completion_factor * 0.2
        )
        
        return max(0.0, min(1.0, score))
    
    def _calculate_location_score(self, user, task):
        """
        計算地點相符度
        
        邏輯：
        - 同校區：1.0
        - 跨校區但願意：0.6
        - 線上任務：1.0
        - 不願跨校區：0.0
        """
        user_campus = user.get('campus', '')
        task_campus = task.get('campus', '')
        willing_cross = user.get('willing_cross_campus', False)
        
        # 線上任務
        if '線上' in task_campus:
            return 1.0
        
        # 同校區
        if user_campus == task_campus:
            return 1.0
        
        # 跨校區
        if user_campus != task_campus:
            if willing_cross:
                return 0.6
            else:
                return 0.2  # 給一點分數（可能會考慮）
        
        return 0.5  # 預設中等分數
    
    def get_top_recommendations(self, user, tasks, top_n=5):
        """
        取得 Top N 推薦任務
        
        Args:
            user (dict): 使用者資料
            tasks (list): 任務列表
            top_n (int): 返回數量
        
        Returns:
            list: 排序後的推薦列表
        """
        recommendations = []
        
        for task in tasks:
            # 不推薦自己發布的任務
            if task.get('publisher_id') == user.get('id'):
                continue
            
            # 計算分數
            score_data = self.calculate_match_score(user, task)
            
            recommendations.append({
                'task': task,
                'score': score_data['total_score'],
                'details': score_data
            })
        
        # 排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:top_n]


# 測試用
if __name__ == '__main__':
    # 測試資料
    user = {
        'id': 1,
        'name': '王小美',
        'campus': '外雙溪校區',
        'skills': ['攝影', '影片剪輯', '平面設計'],
        'avg_rating': 4.8,
        'completed_tasks': 15,
        'trust_score': 0.95,
        'willing_cross_campus': False
    }
    
    task = {
        'id': 1,
        'title': '協助活動攝影',
        'description': '系學會舉辦迎新晚會，需要攝影記錄約2小時',
        'category': '校園協助',
        'campus': '外雙溪校區',
        'is_urgent': False
    }
    
    engine = MatchingEngine()
    result = engine.calculate_match_score(user, task)
    
    print("媒合分數測試:")
    print(f"總分: {result['total_score']:.2%}")
    print(f"技能: {result['skill_score']:.2%}")
    print(f"時間: {result['time_score']:.2%}")
    print(f"評價: {result['rating_score']:.2%}")
    print(f"地點: {result['location_score']:.2%}")
