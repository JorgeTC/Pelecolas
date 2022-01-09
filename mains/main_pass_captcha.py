import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent
sys.path.append(str(SCRIPT_DIR))

from src.safe_url import safe_get_url

def main():
    while True:
        safe_get_url('https://www.filmaffinity.com/es/main.html')

if __name__ == '__main__':
    main()