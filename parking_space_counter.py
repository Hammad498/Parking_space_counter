import cv2
import pickle
import os

# ---------- Configurations ----------
video_path = 'input/videoplayback.mp4'
positions_path = 'park_positions'
width, height = 40, 19  # Parking space size
empty_threshold = 0.22
font = cv2.FONT_HERSHEY_COMPLEX_SMALL

# ---------- File Checks ----------
if not os.path.exists(video_path):
    print(f"❌ Video file not found: {video_path}")
    exit()

if not os.path.exists(positions_path):
    print(f"❌ Parking positions file not found: {positions_path}")
    exit()

# ---------- Load Video and Positions ----------
cap = cv2.VideoCapture(video_path)

with open(positions_path, 'rb') as f:
    park_positions = pickle.load(f)

full_area = width * height


# ---------- Parking Space Counter ----------
def parking_space_counter(img_processed, overlay_img):
    counter = 0

    for position in park_positions:
        x, y = position
        img_crop = img_processed[y:y + height, x:x + width]
        count = cv2.countNonZero(img_crop)
        ratio = count / full_area

        if ratio < empty_threshold:
            color = (0, 255, 0)
            counter += 1
        else:
            color = (0, 0, 255)

        cv2.rectangle(overlay_img, position, (x + width, y + height), color, -1)
        cv2.putText(overlay_img, f"{ratio:.2f}", (x + 4, y + height - 4), font, 0.7, (255, 255, 255), 1)

    return counter


# ---------- Main Loop ----------
while True:
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    ret, frame = cap.read()

    if not ret or frame is None:
        print("⚠️ Frame could not be read. Exiting loop.")
        break

    overlay = frame.copy()

    # Image Processing
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 1)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 25, 16)

    # Count and draw
    counter = parking_space_counter(thresh, overlay)
    alpha = 0.7
    frame_new = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    # Display available count
    total_slots = len(park_positions)
    display_text = f"{counter}/{total_slots}"
    cv2.rectangle(frame_new, (0, 0), (220, 60), (255, 0, 255), -1)
    cv2.putText(frame_new, display_text, (20, 45), font, 2, (255, 255, 255), 2)

    # Show window
    cv2.imshow('Parking Space Counter', frame_new)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()
