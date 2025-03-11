import os
from PIL import Image, ImageDraw, ImageFont

def setup_directories():
    # Define base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create required directories
    directories = [
        os.path.join(base_dir, 'static', 'images'),
        os.path.join(base_dir, 'static', 'uploads', 'books'),
        os.path.join(base_dir, 'static', 'uploads', 'covers')
    ]
    
    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

    # Create default cover image if it doesn't exist
    default_cover_path = os.path.join(base_dir, 'static', 'images', 'default-cover.png')
    if not os.path.exists(default_cover_path):
        # Create a simple default cover
        img = Image.new('RGB', (200, 300), color='#f0f0f0')
        d = ImageDraw.Draw(img)
        try:
            # Try to add text (even without custom font)
            d.text((100, 150), "No Cover", fill='#666666', anchor="mm")
        except Exception as e:
            print(f"Error adding text to default cover: {e}")
        img.save(default_cover_path)
        print(f"Created default cover image: {default_cover_path}")

if __name__ == "__main__":
    setup_directories() 