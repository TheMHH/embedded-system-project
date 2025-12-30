#!/usr/bin/env python3
"""
OpenCV Test - Tests extract_position function with an image file.
"""

import cv2
import numpy as np
from typing import Optional


def extract_position(image_data: bytes) -> Optional[int]:
    """
    Extract position from image data by detecting face and mapping x position to 0-180.
    
    Args:
        image_data: JPEG image bytes
        
    Returns:
        Position value (0-180) or None if no face detected
    """
    try:
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            print("Failed to decode image")
            return None
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            print("No face detected")
            return None
        
        x, y, w, h = faces[0]
        
        face_center_x = x + (w / 2)
        
        image_width = img.shape[1]
        
        position = int(np.interp(face_center_x, [0, image_width], [0, 180]))
        
        print(f"Face detected at x={x}, y={y}, width={w}, height={h}")
        print(f"Face center x: {face_center_x:.1f}, Image width: {image_width}, Position: {position}")
        
        return position
        
    except Exception as e:
        print(f"Error in extract_position: {e}")
        return None

if __name__ == "__main__":    
    test_image = "test_image.jpg"
    
    with open(test_image, 'rb') as f:
        image_data = f.read()
    
    print(f"Image file size: {len(image_data)} bytes")
    
    # Test extract_position
    position = extract_position(image_data)
    
    if position is not None:
        print(f"\n✓ SUCCESS: Position extracted = {position} (0-180 range)")
        print(f"  This means the servo should move to position {position} degrees")
    else:
        print("\n✗ FAILED: No position extracted (no face detected or error occurred)")
    
    print("=" * 60)

