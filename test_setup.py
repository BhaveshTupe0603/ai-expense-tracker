import cv2
import pytesseract
from PIL import Image, ImageDraw

# --- CONFIGURATION ---
# If you didn't add Tesseract to your System PATH, uncomment the line below 
# and ensure the path matches your installation:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def run_test():
    print("1. Testing Library Imports...")
    try:
        import numpy
        import flask
        print("   ✅ Libraries imported successfully.")
    except ImportError as e:
        print(f"   ❌ Library Error: {e}")
        return

    print("\n2. Creating a dummy image for testing...")
    try:
        # Create a simple white image with black text using PIL
        img = Image.new('RGB', (400, 100), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        # We draw text. Note: Default font is used, which is very small, 
        # but Tesseract is good enough to read it usually.
        d.text((10, 40), "System Check Passed 123", fill=(0, 0, 0))
        
        img_path = "test_image.png"
        img.save(img_path)
        print(f"   ✅ Image created: {img_path}")
    except Exception as e:
        print(f"   ❌ Image Creation Error: {e}")
        return

    print("\n3. Testing OpenCV (Image Loading)...")
    try:
        cv_img = cv2.imread(img_path)
        if cv_img is None:
            raise ValueError("OpenCV could not read the file.")
        print(f"   ✅ OpenCV loaded image (Size: {cv_img.shape})")
    except Exception as e:
        print(f"   ❌ OpenCV Error: {e}")
        return

    print("\n4. Testing Tesseract OCR...")
    try:
        # Convert to RGB for Tesseract (OpenCV loads as BGR)
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        
        # Run OCR
        text = pytesseract.image_to_string(rgb_img)
        clean_text = text.strip()
        
        print(f"   ---------------------------")
        print(f"   OCR Output: '{clean_text}'")
        print(f"   ---------------------------")
        
        if "System Check" in clean_text:
            print("   ✅ SUCCESS! Tesseract read the text correctly.")
        else:
            print("   ⚠️  WARNING: Tesseract ran, but didn't read the text perfectly.")
            print("   (This might be due to font size in the dummy image, but the connection works.)")
            
    except FileNotFoundError:
        print("   ❌ Tesseract Not Found!")
        print("   Solution: Uncomment the 'tesseract_cmd' line at the top of this script.")
    except Exception as e:
        print(f"   ❌ OCR Error: {e}")

if __name__ == "__main__":
    run_test()