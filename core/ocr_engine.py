# core/ocr_engine.py

import pytesseract
import cv2
import numpy as np

def detect_text(image):
    cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    gray = cv2.convertScaleAbs(gray, alpha=1.3, beta=5) # Giữ logic tăng contrast cũ
    
    data = pytesseract.image_to_data(gray, lang='eng', output_type=pytesseract.Output.DICT)
    lines = [data['text'][i].strip() for i in range(len(data['text'])) 
             if int(data['conf'][i]) > 60 and data['text'][i].strip()]
    return " ".join(lines)