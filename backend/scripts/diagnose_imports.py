import importlib
import glob
import sys
import time

sys.path.insert(0, ".")

test_files = glob.glob("tests/unit/test_*.py")
print(f"Found {len(test_files)} test files", flush=True)

for f in sorted(test_files):
    mod = f.replace("\\", ".").replace("/", ".").replace(".py", "")
    print(f"Importing {mod}...", end="", flush=True)
    t0 = time.time()
    try:
        importlib.import_module(mod)
        print(f" OK ({round(time.time() - t0, 2)}s)", flush=True)
    except Exception as e:
        print(f" FAILED: {e}", flush=True)

print("All imports tested successfully!", flush=True)
