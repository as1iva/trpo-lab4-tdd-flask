"""Run the suite on each saved source/test change. Ctrl+C stops the watcher."""
from pathlib import Path
import subprocess
import sys
import time


def snapshot():
    return {str(p): p.stat().st_mtime_ns for folder in ("todo", "tests")
            for p in Path(folder).rglob("*") if p.is_file() and "__pycache__" not in p.parts}


def main():
    previous = None
    try:
        while True:
            current = snapshot()
            if current != previous:
                print("\nИзменение файлов: запуск pytest", flush=True)
                subprocess.run([sys.executable, "-m", "pytest", "-q"], check=False)
                previous = current
            time.sleep(1)
    except KeyboardInterrupt:
        print("Наблюдение завершено")


if __name__ == "__main__":
    main()
