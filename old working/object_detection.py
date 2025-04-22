import cv2
import numpy as np
import os
from ultralytics import YOLO

# Load Pretrained YOLO Model
model = YOLO("yolov8n.pt")

def preprocess_image(image_path):
    """Enhance contrast and apply edge detection for blueprint images."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Load in grayscale
    blurred = cv2.GaussianBlur(image, (5, 5), 0)  # Reduce noise
    edges = cv2.Canny(blurred, 50, 150)  # Edge detection
    return edges

def detect_objects(image_path, output_path):
    """Detect objects (doors, windows, walls) in a blueprint image."""
    processed_image = preprocess_image(image_path)
    
    # Save the preprocessed image for debugging
    preprocessed_output = os.path.join("extracted_data", "preprocessed_sample.jpg")
    cv2.imwrite(preprocessed_output, processed_image)
    print(f"✅ Preprocessed image saved: {preprocessed_output}")

    # Convert back to 3-channel image for YOLO
    processed_image = cv2.cvtColor(processed_image, cv2.COLOR_GRAY2BGR)

    results = model(processed_image, conf=0.2)  # Lower confidence threshold

    # Draw bounding boxes if detections are found
    detected = False
    for result in results:
        for box in result.boxes.xyxy:
            x1, y1, x2, y2 = map(int, box)
            label = result.names[result.boxes.cls[0].item()]
            confidence = result.boxes.conf[0].item()

            cv2.rectangle(processed_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(processed_image, f"{label} {confidence:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            detected = True

    # Save output image
    cv2.imwrite(output_path, processed_image)
    
    if detected:
        print(f"✅ Object detection completed: {output_path}")
    else:
        print("⚠️ No objects detected. Try custom YOLO training.")

if __name__ == "__main__":
    input_folder = "data"
    output_folder = "extracted_data"

    os.makedirs(output_folder, exist_ok=True)

    for image_file in os.listdir(input_folder):
        if image_file.endswith(".jpg") or image_file.endswith(".png"):
            image_path = os.path.join(input_folder, image_file)
            output_path = os.path.join(output_folder, f"detected_{image_file}")
            detect_objects(image_path, output_path)
