"""
Check if all required dependencies are installed
"""

import sys

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"[OK] {package_name:25} - INSTALLED")
        return True
    except ImportError:
        print(f"[NO] {package_name:25} - NOT INSTALLED")
        return False

def main():
    print("=" * 60)
    print("  Medi-Flow Systems - Dependency Check")
    print("  Smart Management. Better Health.")
    print("=" * 60)
    print()
    
    required_packages = [
        ("Flask", "flask"),
        ("Flask-SQLAlchemy", "flask_sqlalchemy"),
        ("Flask-CORS", "flask_cors"),
        ("psycopg2-binary", "psycopg2"),
        ("bcrypt", "bcrypt"),
        ("PyJWT", "jwt"),
        ("reportlab", "reportlab"),
        ("pandas", "pandas"),
        ("spacy", "spacy"),
        ("scikit-learn", "sklearn"),
        ("fuzzywuzzy", "fuzzywuzzy"),
        ("python-Levenshtein", "Levenshtein"),
        ("nltk", "nltk"),
    ]
    
    installed_count = 0
    total_count = len(required_packages)
    
    print("Checking required packages:\n")
    
    for package_name, import_name in required_packages:
        if check_package(package_name, import_name):
            installed_count += 1
    
    print()
    print("=" * 60)
    print(f"Status: {installed_count}/{total_count} packages installed")
    print("=" * 60)
    print()
    
    if installed_count == total_count:
        print("[SUCCESS] All dependencies are installed!")
        print("[SUCCESS] You can now run: python app.py")
        print()
        print("Next steps:")
        print("1. Download spaCy model: python -m spacy download en_core_web_sm")
        print("2. Initialize database: python init_db.py")
        print("3. Load chatbot KB: python chatbot/loader.py")
        print("4. Start server: python app.py")
        return 0
    else:
        missing = total_count - installed_count
        print(f"[WARNING] {missing} package(s) still need to be installed")
        print()
        print("To install missing packages:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
