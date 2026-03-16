# run.py
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.db.__main__ import main

if __name__ == "__main__":
    main()