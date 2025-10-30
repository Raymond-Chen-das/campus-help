"""
資料庫模組 - Campus Help (增強版)
使用 SQLite + SQLAlchemy
新增：評價系統、任務狀態管理、點數轉換
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

# 建立引擎
engine = create_engine('sqlite:///campus_help.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# ========== 資料模型 ==========

class User(Base):
    """使用者模型"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    department = Column(String(100))
    grade = Column(String(20))
    campus = Column(String(50))
    skills = Column(Text)  # JSON 格式儲存技能列表
    
    # 統計資料
    points = Column(Integer, default=100)
    avg_rating = Column(Float, default=5.0)
    completed_tasks = Column(Integer, default=0)
    trust_score = Column(Float, default=1.0)
    
    # 設定
    willing_cross_campus = Column(Boolean, default=False)
    status = Column(String(20), default='active')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """轉換為字典"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'department': self.department,
            'grade': self.grade,
            'campus': self.campus,
            'skills': json.loads(self.skills) if self.skills else [],
            'points': self.points,
            'avg_rating': self.avg_rating,
            'completed_tasks': self.completed_tasks,
            'trust_score': self.trust_score,
            'willing_cross_campus': self.willing_cross_campus,
            'status': self.status
        }


class Task(Base):
    """任務模型"""
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    publisher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    accepted_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # 新增：被接受的幫助者
    
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    location = Column(String(200))
    campus = Column(String(50))
    
    points_offered = Column(Integer, nullable=False)
    is_urgent = Column(Boolean, default=False)
    status = Column(String(20), default='open')  # open, in_progress, completed, cancelled
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)  # 新增：完成時間
    
    # 關聯
    publisher = relationship('User', foreign_keys=[publisher_id])
    accepted_user = relationship('User', foreign_keys=[accepted_user_id])
    
    def to_dict(self):
        """轉換為字典"""
        session = Session()
        publisher = session.query(User).filter_by(id=self.publisher_id).first()
        accepted_user = session.query(User).filter_by(id=self.accepted_user_id).first() if self.accepted_user_id else None
        
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'location': self.location,
            'campus': self.campus,
            'points_offered': self.points_offered,
            'is_urgent': self.is_urgent,
            'status': self.status,
            'publisher_id': self.publisher_id,
            'publisher_name': publisher.name if publisher else '未知',
            'publisher_rating': publisher.avg_rating if publisher else 0,
            'accepted_user_id': self.accepted_user_id,
            'accepted_user_name': accepted_user.name if accepted_user else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M') if self.completed_at else None
        }


class TaskApplication(Base):
    """任務申請記錄"""
    __tablename__ = 'task_applications'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    applicant_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    status = Column(String(20), default='pending')  # pending, accepted, rejected
    applied_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    task = relationship('Task', foreign_keys=[task_id])
    applicant = relationship('User', foreign_keys=[applicant_id])
    
    def to_dict(self):
        """轉換為字典"""
        session = Session()
        applicant = session.query(User).filter_by(id=self.applicant_id).first()
        
        return {
            'id': self.id,
            'task_id': self.task_id,
            'applicant_id': self.applicant_id,
            'applicant_name': applicant.name if applicant else '未知',
            'applicant_rating': applicant.avg_rating if applicant else 0,
            'status': self.status,
            'applied_at': self.applied_at.strftime('%Y-%m-%d %H:%M') if self.applied_at else None
        }


class Review(Base):
    """評價記錄"""
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 評價者
    reviewee_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 被評價者
    
    rating = Column(Float, nullable=False)  # 1-5 星
    comment = Column(Text)  # 評價內容（可選）
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    task = relationship('Task', foreign_keys=[task_id])
    reviewer = relationship('User', foreign_keys=[reviewer_id])
    reviewee = relationship('User', foreign_keys=[reviewee_id])
    
    def to_dict(self):
        """轉換為字典"""
        session = Session()
        reviewer = session.query(User).filter_by(id=self.reviewer_id).first()
        reviewee = session.query(User).filter_by(id=self.reviewee_id).first()
        task = session.query(Task).filter_by(id=self.task_id).first()
        
        return {
            'id': self.id,
            'task_id': self.task_id,
            'task_title': task.title if task else '未知',
            'reviewer_id': self.reviewer_id,
            'reviewer_name': reviewer.name if reviewer else '未知',
            'reviewee_id': self.reviewee_id,
            'reviewee_name': reviewee.name if reviewee else '未知',
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }


# ========== 資料庫操作函數 ==========

def init_db():
    """初始化資料庫"""
    Base.metadata.create_all(engine)


def get_all_users():
    """取得所有使用者"""
    session = Session()
    users = session.query(User).filter_by(status='active').all()
    return [u.to_dict() for u in users]


def get_user_by_name(name):
    """根據名字取得使用者"""
    session = Session()
    user = session.query(User).filter_by(name=name, status='active').first()
    return user.to_dict() if user else None


def get_user_by_id(user_id):
    """根據 ID 取得使用者"""
    session = Session()
    user = session.query(User).filter_by(id=user_id).first()
    return user.to_dict() if user else None


def get_all_tasks(status=None):
    """取得所有任務"""
    session = Session()
    query = session.query(Task)
    
    if status:
        query = query.filter_by(status=status)
    
    tasks = query.order_by(Task.created_at.desc()).all()
    return [t.to_dict() for t in tasks]


def create_task(task_data):
    """建立任務（會扣除發起者點數）"""
    session = Session()
    
    try:
        publisher = session.query(User).filter_by(id=task_data['publisher_id']).first()
        
        # 檢查點數是否足夠
        if publisher.points < task_data['points_offered']:
            return None  # 點數不足
        
        # 扣除點數
        publisher.points -= task_data['points_offered']
        
        # 建立任務
        task = Task(
            publisher_id=task_data['publisher_id'],
            title=task_data['title'],
            description=task_data['description'],
            category=task_data['category'],
            location=task_data['location'],
            campus=task_data['campus'],
            points_offered=task_data['points_offered'],
            is_urgent=task_data.get('is_urgent', False)
        )
        
        session.add(task)
        session.commit()
        
        return task.id
    except Exception as e:
        session.rollback()
        print(f"建立任務失敗: {e}")
        return None
    finally:
        session.close()


def get_user_tasks(user_id, task_type='published'):
    """取得使用者的任務
    
    Args:
        user_id: 使用者 ID
        task_type: 'published' (發布的) 或 'applied' (申請的)
    """
    session = Session()
    
    if task_type == 'published':
        tasks = session.query(Task).filter_by(publisher_id=user_id).order_by(Task.created_at.desc()).all()
        return [t.to_dict() for t in tasks]
    
    elif task_type == 'applied':
        applications = session.query(TaskApplication).filter_by(applicant_id=user_id).all()
        result = []
        
        for app in applications:
            task = session.query(Task).filter_by(id=app.task_id).first()
            if task:
                task_dict = task.to_dict()
                task_dict['application_status'] = app.status
                task_dict['applied_at'] = app.applied_at.strftime('%Y-%m-%d %H:%M')
                result.append(task_dict)
        
        return result
    
    return []


def apply_for_task(task_id, applicant_id):
    """申請任務"""
    session = Session()
    
    try:
        # 檢查是否已申請
        existing = session.query(TaskApplication).filter_by(
            task_id=task_id,
            applicant_id=applicant_id
        ).first()
        
        if existing:
            return False  # 已經申請過
        
        # 建立申請記錄
        application = TaskApplication(
            task_id=task_id,
            applicant_id=applicant_id
        )
        
        session.add(application)
        session.commit()
        
        return True
    except Exception as e:
        session.rollback()
        print(f"申請任務失敗: {e}")
        return False
    finally:
        session.close()


def get_task_applications(task_id):
    """取得任務的所有申請"""
    session = Session()
    applications = session.query(TaskApplication).filter_by(task_id=task_id).all()
    return [a.to_dict() for a in applications]


# ========== 新增：任務狀態管理 ==========

def accept_application(task_id, applicant_id, publisher_id):
    """
    接受申請（發起者操作）
    
    Args:
        task_id: 任務 ID
        applicant_id: 被接受的申請者 ID
        publisher_id: 發起者 ID（用於驗證）
    
    Returns:
        bool: 是否成功
    """
    session = Session()
    
    try:
        # 驗證任務所有權
        task = session.query(Task).filter_by(id=task_id, publisher_id=publisher_id).first()
        if not task:
            return False
        
        # 確認任務狀態為 open
        if task.status != 'open':
            return False
        
        # 更新任務狀態
        task.status = 'in_progress'
        task.accepted_user_id = applicant_id
        
        # 更新申請狀態
        applications = session.query(TaskApplication).filter_by(task_id=task_id).all()
        for app in applications:
            if app.applicant_id == applicant_id:
                app.status = 'accepted'
            else:
                app.status = 'rejected'
        
        session.commit()
        return True
    
    except Exception as e:
        session.rollback()
        print(f"接受申請失敗: {e}")
        return False
    finally:
        session.close()


def complete_task(task_id, user_id):
    """
    完成任務（雙方都可以標記，需要雙方確認）
    
    Args:
        task_id: 任務 ID
        user_id: 操作者 ID（發起者或幫助者）
    
    Returns:
        bool: 是否成功
    """
    session = Session()
    
    try:
        task = session.query(Task).filter_by(id=task_id).first()
        if not task:
            return False
        
        # 確認任務狀態為 in_progress
        if task.status != 'in_progress':
            return False
        
        # 驗證操作權限（發起者或被接受的幫助者）
        if user_id not in [task.publisher_id, task.accepted_user_id]:
            return False
        
        # 更新任務狀態為完成
        task.status = 'completed'
        task.completed_at = datetime.utcnow()
        
        # 轉移點數：從發起者到幫助者
        publisher = session.query(User).filter_by(id=task.publisher_id).first()
        helper = session.query(User).filter_by(id=task.accepted_user_id).first()
        
        if helper:
            # 幫助者獲得點數
            helper.points += task.points_offered
            
            # 更新完成任務數
            helper.completed_tasks += 1
            publisher.completed_tasks += 1
        
        session.commit()
        return True
    
    except Exception as e:
        session.rollback()
        print(f"完成任務失敗: {e}")
        return False
    finally:
        session.close()


# ========== 新增：評價系統 ==========

def submit_review(task_id, reviewer_id, reviewee_id, rating, comment=''):
    """
    提交評價
    
    Args:
        task_id: 任務 ID
        reviewer_id: 評價者 ID
        reviewee_id: 被評價者 ID
        rating: 評分 (1-5)
        comment: 評價內容
    
    Returns:
        bool: 是否成功
    """
    session = Session()
    
    try:
        # 驗證任務已完成
        task = session.query(Task).filter_by(id=task_id, status='completed').first()
        if not task:
            return False
        
        # 驗證評價權限（只能評價對方）
        if not ((reviewer_id == task.publisher_id and reviewee_id == task.accepted_user_id) or
                (reviewer_id == task.accepted_user_id and reviewee_id == task.publisher_id)):
            return False
        
        # 檢查是否已評價
        existing = session.query(Review).filter_by(
            task_id=task_id,
            reviewer_id=reviewer_id,
            reviewee_id=reviewee_id
        ).first()
        
        if existing:
            return False  # 已經評價過
        
        # 建立評價記錄
        review = Review(
            task_id=task_id,
            reviewer_id=reviewer_id,
            reviewee_id=reviewee_id,
            rating=rating,
            comment=comment
        )
        
        session.add(review)
        
        # 更新被評價者的平均評分
        update_user_rating(session, reviewee_id)
        
        session.commit()
        return True
    
    except Exception as e:
        session.rollback()
        print(f"提交評價失敗: {e}")
        return False
    finally:
        session.close()


def update_user_rating(session, user_id):
    """
    更新使用者的平均評分和信任值
    
    Args:
        session: 資料庫 session
        user_id: 使用者 ID
    """
    # 取得該使用者的所有評價
    reviews = session.query(Review).filter_by(reviewee_id=user_id).all()
    
    if reviews:
        # 計算平均評分
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        
        # 取得使用者
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.avg_rating = round(avg_rating, 2)
            
            # 更新信任值 = (平均評分 × 0.7) + (完成率 × 0.3)
            # 完成率基於完成任務數（假設最多50個為滿分）
            completion_rate = min(1.0, user.completed_tasks / 50)
            user.trust_score = round((avg_rating / 5.0 * 0.7) + (completion_rate * 0.3), 2)


def get_reviews_for_user(user_id):
    """
    取得使用者收到的評價
    
    Args:
        user_id: 使用者 ID
    
    Returns:
        list: 評價列表
    """
    session = Session()
    reviews = session.query(Review).filter_by(reviewee_id=user_id).order_by(Review.created_at.desc()).all()
    return [r.to_dict() for r in reviews]


def check_review_status(task_id, user_id):
    """
    檢查用戶是否已對任務進行評價
    
    Args:
        task_id: 任務 ID
        user_id: 使用者 ID
    
    Returns:
        dict: {'can_review': bool, 'reviewee_id': int, 'has_reviewed': bool}
    """
    session = Session()
    
    task = session.query(Task).filter_by(id=task_id, status='completed').first()
    if not task:
        return {'can_review': False, 'reviewee_id': None, 'has_reviewed': False}
    
    # 確定被評價者
    if user_id == task.publisher_id:
        reviewee_id = task.accepted_user_id
    elif user_id == task.accepted_user_id:
        reviewee_id = task.publisher_id
    else:
        return {'can_review': False, 'reviewee_id': None, 'has_reviewed': False}
    
    # 檢查是否已評價
    existing = session.query(Review).filter_by(
        task_id=task_id,
        reviewer_id=user_id,
        reviewee_id=reviewee_id
    ).first()
    
    return {
        'can_review': True,
        'reviewee_id': reviewee_id,
        'has_reviewed': existing is not None
    }


# ========== 測試資料 ==========

def seed_test_data():
    """填充測試資料"""
    session = Session()
    
    # 清空現有資料
    session.query(Review).delete()
    session.query(TaskApplication).delete()
    session.query(Task).delete()
    session.query(User).delete()
    session.commit()
    
    # 建立測試使用者
    users_data = [
        {
            'email': 'alice@scu.edu.tw',
            'name': '王小美',
            'department': '資訊管理學系',
            'grade': '大二',
            'campus': '外雙溪校區',
            'skills': json.dumps(['攝影', '影片剪輯', '平面設計', 'Photoshop']),
            'points': 200,
            'avg_rating': 4.8,
            'completed_tasks': 15,
            'trust_score': 0.95
        },
        {
            'email': 'bob@scu.edu.tw',
            'name': '李大明',
            'department': '企業管理學系',
            'grade': '大三',
            'campus': '城中校區',
            'skills': json.dumps(['搬運', '組裝家具', '修理電腦', '跑腿']),
            'points': 350,
            'avg_rating': 4.5,
            'completed_tasks': 28,
            'trust_score': 0.92,
            'willing_cross_campus': True
        },
        {
            'email': 'carol@scu.edu.tw',
            'name': '陳小華',
            'department': '英文學系',
            'grade': '大一',
            'campus': '外雙溪校區',
            'skills': json.dumps(['英文教學', '簡報製作', '文書處理', '翻譯']),
            'points': 150,
            'avg_rating': 4.9,
            'completed_tasks': 10,
            'trust_score': 0.98
        },
        {
            'email': 'david@scu.edu.tw',
            'name': '張志明',
            'department': '數學系',
            'grade': '大四',
            'campus': '外雙溪校區',
            'skills': json.dumps(['數學教學', '程式設計', '資料分析', 'Python']),
            'points': 500,
            'avg_rating': 4.7,
            'completed_tasks': 45,
            'trust_score': 0.94
        }
    ]
    
    users = []
    for user_data in users_data:
        user = User(**user_data)
        session.add(user)
        users.append(user)
    
    session.commit()
    
    # 建立測試任務
    tasks_data = [
        {
            'publisher_id': users[0].id,
            'title': '幫忙搬宿舍行李',
            'description': '需要幫忙搬一些行李箱和紙箱，從柚芳樓到楓雅樓，大約20分鐘內可完成。東西不多，主要是幾個紙箱和一個行李箱。',
            'category': '日常支援',
            'location': '柚芳樓 → 楓雅樓',
            'campus': '外雙溪校區',
            'points_offered': 50,
            'is_urgent': True
        },
        {
            'publisher_id': users[1].id,
            'title': '協助活動攝影',
            'description': '系學會舉辦迎新晚會，需要攝影記錄約2小時。希望有攝影經驗，能拍出活動氣氛。晚會在望星廣場舉行。',
            'category': '校園協助',
            'location': '望星廣場',
            'campus': '外雙溪校區',
            'points_offered': 80
        },
        {
            'publisher_id': users[2].id,
            'title': '教微積分解題',
            'description': '期中考前想請教幾題微積分題目，約1小時。主要是導數和積分的應用題，希望能夠耐心講解解題技巧。',
            'category': '學習互助',
            'location': '圖書館 7F會議室',
            'campus': '城中校區',
            'points_offered': 60
        },
        {
            'publisher_id': users[3].id,
            'title': '幫忙修電腦',
            'description': '電腦無法開機，需要懂電腦的人幫忙檢查。可能是硬體或軟體問題，希望能診斷並修復。',
            'category': '日常支援',
            'location': '松勁樓',
            'campus': '外雙溪校區',
            'points_offered': 70
        },
        {
            'publisher_id': users[0].id,
            'title': '代購午餐',
            'description': '課太多走不開，幫忙在商學院附近買便當。可以用 LINE Pay 或現金付款，會多給跑腿費。',
            'category': '日常支援',
            'location': '商學院',
            'campus': '城中校區',
            'points_offered': 30,
            'is_urgent': True
        },
        {
            'publisher_id': users[1].id,
            'title': '英文簡報修改',
            'description': '需要英文母語者或英文很好的人幫忙修改英文簡報，約10頁，主要是文法和用詞優化。',
            'category': '學習互助',
            'location': '線上',
            'campus': '線上',
            'points_offered': 100
        }
    ]
    
    for task_data in tasks_data:
        task = Task(**task_data)
        session.add(task)
    
    session.commit()
    session.close()
    
    print("✅ 測試資料建立完成！")
    print(f"   - 使用者: {len(users_data)} 位")
    print(f"   - 任務: {len(tasks_data)} 個")


if __name__ == '__main__':
    # 測試用
    init_db()
    seed_test_data()