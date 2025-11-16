#!/usr/bin/env python3
"""
Create realistic Tunisian plate images for testing
"""
import cv2
import numpy as np

def create_realistic_tunisian_plate(plate_number, output_file):
    """
    Create a realistic Tunisian license plate image
    
    Tunisian plates have:
    - White background
    - Blue band on the left with EU flag colors and "TN"
    - Black or dark text
    - Reflective appearance
    """
    
    # Create base white plate (typical size ratio)
    plate = np.ones((150, 520, 3), dtype=np.uint8) * 240  # Off-white
    
    # Add slight texture/noise for realism
    noise = np.random.normal(0, 2, plate.shape).astype(np.uint8)
    plate = cv2.add(plate, noise)
    
    # Blue EU band on left (50mm width proportion)
    # EU color: Blue with gold stars
    plate[10:140, 10:70] = [180, 30, 30]  # Dark blue (BGR)
    
    # Add EU-style marking
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(plate, "TN", (15, 70), font, 1, (255, 255, 255), 2)
    
    # Add yellow band on bottom
    plate[130:140, :] = [0, 255, 255]  # Yellow
    
    # Main plate number - large, bold, black
    # Add shadow effect first
    cv2.putText(plate, plate_number, (85, 100), cv2.FONT_HERSHEY_DUPLEX, 
                3.5, (40, 40, 40), 5)  # Shadow
    cv2.putText(plate, plate_number, (80, 95), cv2.FONT_HERSHEY_DUPLEX, 
                3.5, (0, 0, 0), 4)  # Main text
    
    # Add some reflections for realism
    for i in range(0, 520, 30):
        cv2.line(plate, (i, 0), (i+20, 150), (255, 255, 255), 1)
    
    # Save image
    cv2.imwrite(output_file, plate)
    print(f"[+] Created: {output_file}")
    return plate

# Create test images with different Tunisian plate numbers
if __name__ == '__main__':
    plates = [
        "199TN0199",
        "123TN4567",
        "456TN8901",
        "789TN2345",
    ]
    
    for i, plate_num in enumerate(plates):
        create_realistic_tunisian_plate(plate_num, f"data/test_images/plate_{i+1}.jpg")
    
    print(f"\n[OK] Created {len(plates)} test plate images")
