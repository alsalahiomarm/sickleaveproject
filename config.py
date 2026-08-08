import os

class Config:
    # كلمة المرور الخاصة بلوحة التحكم (يمكنك تغييرها من هنا متى أردت)
    ADMIN_PASSWORD = "mmm774244614"
    
    # مفتاح تشفير الجلسات
    SECRET_KEY = os.urandom(24)
    
    # اسم قاعدة البيانات
    DB_NAME = "sick_leaves.db"