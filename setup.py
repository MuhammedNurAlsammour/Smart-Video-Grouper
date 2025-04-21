from setuptools import setup
import sys
import os

# المسار إلى الأيقونة
icon_path = os.path.join('assets', 'icons', 'SmartTransfer.ico')

setup(
    name="SmartVideoGrouper",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Smart Video Grouper Application",
    packages=['src'],
    include_package_data=True,
    install_requires=[
        'tkinter',
        'pillow',
    ],
    options={
        'build_exe': {
            'include_files': [
                icon_path,
            ],
            'icon': icon_path,
        },
    },
    windows=[{
        'script': 'src/main_qt.py',
        'icon_resources': [(1, icon_path)],
        'dest_dir': 'dist',
    }],
) 