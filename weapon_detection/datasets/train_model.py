from ultralytics import YOLO

# Load base model
model = YOLO("yolov8n.pt")

# Train on your dataset
model.train(
    data="weapon_detection_yolo/data.yaml",
    epochs=50,
    imgsz=640
)