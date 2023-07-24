import cv2
import mediapipe as mp
from pymunk.vec2d import Vec2d
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

def fingers_make():
  for i in range(21):
    fingers.append(results.multi_hand_landmarks[0].landmark[i])

def numbering():
  for i in range(21):
    cv2.putText(image, str(i), org=(int((1-fingers[i].x) * image.shape[1]), int (fingers[i].y * image.shape[0] + 20)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 0), thickness=1)

def facing_sign():
  if abs(fingers[5].x - fingers[17].x) <= 0.04:
    cv2.putText(image, "side", org=(int((1-fingers[0].x) * image.shape[1]), int (fingers[0].y * image.shape[0] + 40)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 0, 0), thickness=1)
  elif fingers[5].x > fingers[17].x:
    cv2.putText(image, "inside", org=(int((1-fingers[0].x) * image.shape[1]), int (fingers[0].y * image.shape[0] + 40)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 0, 0), thickness=1)
  elif fingers[5].x <= fingers[17].x:
    cv2.putText(image, "outside", org=(int((1-fingers[0].x) * image.shape[1]), int (fingers[0].y * image.shape[0] + 40)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 0, 0), thickness=1)

def smoothing(weight):
  if old_fingers != []:
    for i in range(21):
      fingers[i] = old_fingers[i] + (fingers[i] - old_fingers[i]) * weight

# 웹캠, 영상 파일의 경우 이것을 사용하세요.:
cap = cv2.VideoCapture(1)
with mp_hands.Hands(
    model_complexity=1,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("카메라를 찾을 수 없습니다.")
      # 동영상을 불러올 경우는 'continue' 대신 'break'를 사용합니다.
      continue

    # 필요에 따라 성능 향상을 위해 이미지 작성을 불가능함으로 기본 설정합니다.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    fingers = []
    old_fingers = []

    # 이미지에 손 주석을 그립니다.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())

    # 보기 편하게 이미지를 좌우 반전합니다.
    image = cv2.flip(image, 1)

    if fingers != []:
      old_fingers = fingers

    if results.multi_hand_landmarks:
      fingers_make()

      numbering()
      facing_sign()



    cv2.imshow('MediaPipe Hands', image)

    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()

