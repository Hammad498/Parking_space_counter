import cv2
import pickle
import os

video_path = 'input/videoplayback.mp4'
positions_file = 'park_positions'
width, height = 40, 19

# List to store parking spot positions
positions = []

# Load video
if not os.path.exists(video_path):
    print(f"❌ Video file not found: {video_path}")
    exit()

cap = cv2.VideoCapture(video_path)

def mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        positions.append((x, y))
    elif event == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(positions):
            if pos[0] < x < pos[0] + width and pos[1] < y < pos[1] + height:
                positions.pop(i)
                break

while True:
    ret, frame = cap.read()
    if not ret:
        break

    for pos in positions:
        cv2.rectangle(frame, pos, (pos[0]+width, pos[1]+height), (255, 0, 255), 2)

    cv2.imshow("Mark Parking Spaces", frame)
    cv2.setMouseCallback("Mark Parking Spaces", mouse_click)

    key = cv2.waitKey(1)
    if key == ord('s'):  # Press 's' to save
        with open(positions_file, 'wb') as f:
            pickle.dump(positions, f)
        print(f"✅ Saved {len(positions)} parking spots.")
        break
    elif key == 27:  # ESC to exit without saving
        break

cap.release()
cv2.destroyAllWindows()
