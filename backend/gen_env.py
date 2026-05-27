import json
import os
import sys

def main():
    # Define potential paths for the service account JSON file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(script_dir, "service-account.json"),
        os.path.join(os.getcwd(), "service-account.json"),
        os.path.join(os.getcwd(), "backend", "service-account.json")
    ]
    
    json_path = None
    for path in possible_paths:
        if os.path.exists(path):
            json_path = path
            break
            
    if not json_path:
        print("=" * 60)
        print("שגיאה: קובץ service-account.json לא נמצא!")
        print("=" * 60)
        print("כיצד להמשיך:")
        print("1. הורד את קובץ המפתח (JSON) החדש מהקונסול של Google Cloud / Firebase.")
        print(f"2. שמור את הקובץ בשם 'service-account.json' בתיקייה:")
        print(f"   {script_dir}")
        print("3. הרץ מחדש את הסקריפט הזה.")
        print("=" * 60)
        sys.exit(1)
        
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"שגיאה בקריאת קובץ ה-JSON: {e}")
        sys.exit(1)
        
    # Convert to a single-line JSON string
    json_string = json.dumps(data)
    print("\nהעתק את השורה הבאה והדבק אותה בקובץ ה-.env שלך:")
    print("-" * 60)
    print(f"FIREBASE_SERVICE_ACCOUNT='{json_string}'")
    print("-" * 60)

if __name__ == "__main__":
    main()
