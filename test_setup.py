import os

def test_directory_structure():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    required_paths = [
        os.path.join(base_dir, 'static', 'images', 'default-cover.png'),
        os.path.join(base_dir, 'static', 'uploads', 'books'),
        os.path.join(base_dir, 'static', 'uploads', 'covers')
    ]
    
    for path in required_paths:
        if os.path.exists(path):
            print(f"✓ Found: {path}")
        else:
            print(f"✗ Missing: {path}")

if __name__ == "__main__":
    test_directory_structure() 