r"""
One-time fix: adds the missing `views` column to the `blogs` table (SQLite).
Run from the project root (E:\PrimeKeyEstates):   python add_blog_views.py
Stop the Flask server first, then start it again after this finishes.
"""
import os
import sqlite3

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP = {"venv", ".venv", "env", "node_modules", ".git", "__pycache__"}

found = []
for folder, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for name in files:
        if name.lower().endswith((".db", ".sqlite", ".sqlite3")):
            found.append(os.path.join(folder, name))

done = False
for path in found:
    try:
        con = sqlite3.connect(path)
        tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "blogs" not in tables:
            con.close()
            continue
        cols = {r[1] for r in con.execute("PRAGMA table_info(blogs)")}
        if "views" in cols:
            print(f"[OK] 'views' column already exists in: {path}")
        else:
            con.execute("ALTER TABLE blogs ADD COLUMN views INTEGER DEFAULT 0")
            con.execute("UPDATE blogs SET views = 0 WHERE views IS NULL")
            con.commit()
            print(f"[DONE] Added 'views' column to blogs in: {path}")
        con.close()
        done = True
    except sqlite3.Error as e:
        print(f"[SKIP] {path}: {e}")

if not done:
    print("No SQLite database with a 'blogs' table found under:", ROOT)
    print("Check SQLALCHEMY_DATABASE_URI in config.py for the database path.")
