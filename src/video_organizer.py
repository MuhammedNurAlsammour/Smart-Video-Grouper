import os
import shutil
from datetime import datetime
import glob

def organize_videos(source_path, videos_per_folder=3):
    """
    تنظيم الفيديوهات في مجلدات كل 3 فيديوهات
    
    Args:
        source_path (str): مسار مجلد الفيديوهات المصدر
        videos_per_folder (int): عدد الفيديوهات في كل مجلد
    """
    # التحقق من وجود المسار
    if not os.path.exists(source_path):
        print(f"المسار غير موجود: {source_path}")
        return
    
    # الحصول على جميع ملفات الفيديو
    video_extensions = ['*.mp4', '*.avi', '*.mkv', '*.mov']
    video_files = []
    
    for ext in video_extensions:
        video_files.extend(glob.glob(os.path.join(source_path, ext)))
    
    # فرز الفيديوهات حسب تاريخ الإنشاء
    video_files.sort(key=lambda x: os.path.getctime(x))
    
    # إنشاء مجلدات وتنظيم الفيديوهات
    folder_count = 1
    for i in range(0, len(video_files), videos_per_folder):
        # إنشاء مجلد جديد
        folder_name = f"مجموعة_{folder_count}"
        folder_path = os.path.join(source_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        # نقل الفيديوهات إلى المجلد الجديد
        for video in video_files[i:i+videos_per_folder]:
            video_name = os.path.basename(video)
            new_path = os.path.join(folder_path, video_name)
            shutil.move(video, new_path)
            print(f"تم نقل {video_name} إلى {folder_name}")
        
        folder_count += 1
    
    print(f"تم تنظيم {len(video_files)} فيديو في {folder_count-1} مجلد")

if __name__ == "__main__":
    # المسار الافتراضي
    default_path = r"D:\ders\fikih\May 2022\video_files"
    
    # طلب المسار من المستخدم
    user_path = input(f"أدخل مسار مجلد الفيديوهات (اضغط Enter لاستخدام المسار الافتراضي {default_path}): ").strip()
    
    # استخدام المسار الافتراضي إذا لم يتم إدخال مسار
    source_path = user_path if user_path else default_path
    
    # تنظيم الفيديوهات
    organize_videos(source_path)