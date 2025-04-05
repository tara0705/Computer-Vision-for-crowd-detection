import os
import cv2
import torch
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import numpy as np
import torchvision.transforms as transforms
from ultralytics import YOLO
from twilio.rest import Client

device = "cuda" if torch.cuda.is_available() else "cpu"
model = YOLO('yolov8s.pt').to(device)


cap = cv2.VideoCapture(0)


midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small").to(device).eval()
midas_transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])


output_dir = "theft_frames"
os.makedirs(output_dir, exist_ok=True)

#mail api
SENDER_EMAIL = "your email"
RECEIVER_EMAIL = "sender email"
SENDER_PASSWORD = "obtain app password from your gmail api"

# call api
TWILIO_ACCOUNT_SID = "your account"
TWILIO_AUTH_TOKEN = "add your token"
TWILIO_PHONE = "your phone number"
ALERT_PHONE = "add twilio phone number"

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def estimate_depth(frame):
    img = midas_transform(frame).unsqueeze(0).to(device)
    with torch.no_grad():
        depth_map = midas(img).squeeze().cpu().numpy()
    
    depth_map = cv2.resize(depth_map, (frame.shape[1], frame.shape[0]))
    depth_map = ((depth_map - depth_map.min()) / (depth_map.max() - depth_map.min()) * 255).astype(np.uint8)
    return depth_map

def send_email(image_path):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = "🚨 Suspicious Activity Detected"

    body = "Suspicious activity has been detected. Please find the attached frame."
    msg.attach(MIMEText(body, 'plain'))

    with open(image_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())

    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(image_path)}')
    msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print(" Email sent successfully!")
    except Exception as e:
        print(f" Failed to send email: {e}")

def initiate_alert_call():
    call = twilio_client.calls.create(
        twiml='<Response><Say>Alert! Suspicious activity detected. Check your surveillance system immediately.</Say></Response>',
        to=ALERT_PHONE,
        from_=TWILIO_PHONE
    )
    print(f"📞 Call initiated: {call.sid}")

def process_frame(frame):
    result = model(frame, conf=0.6, classes=[0])[0]  # Detect only persons (class 0)
    detections = result.boxes.xyxy.cpu().numpy() if result.boxes else []
    
    # Depth estimate
    depth_map = estimate_depth(frame)
    depth_colored = cv2.applyColorMap(depth_map, cv2.COLORMAP_JET)
    frame_3d = cv2.addWeighted(frame, 0.6, depth_colored, 0.4, 0)

    return detections, frame_3d

def extract_frame_and_alert(frame, detection, frame_count):
    x1, y1, x2, y2 = map(int, detection)
    extracted_frame = frame[y1:y2, x1:x2]
    
    frame_path = os.path.join(output_dir, f"thief_{frame_count}.png")
    cv2.imwrite(frame_path, extracted_frame)
    
    print(f"📷 Theft frame saved: {frame_path}")

    send_email(frame_path)
    initiate_alert_call()

frame_count = 0
alert_triggered = False#reducing false positive rates

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        detections, frame_3d = process_frame(frame)
        if len(detections) > 0 and not alert_triggered:
            for detection in detections:
                extract_frame_and_alert(frame, detection, frame_count)
                alert_triggered = True
                break  

        
        cv2.imshow("Security Surveillance (3D)", frame_3d)

        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
if all_gt_labels and all_pred_labels:
    precision = precision_score(all_gt_labels, all_pred_labels, zero_division=1)
    recall = recall_score(all_gt_labels, all_pred_labels, zero_division=1)
    print(f"Precision: {precision:.2f}, Recall: {recall:.2f}")
else:
    print("No valid detections for precision/recall calculation.")

def make_call(to_phone_number, from_phone_number, message):
    try:
        account_sid = 'your account sid from twilio'
        auth_token = ' your auth_token form twilio'

        if not account_sid or not auth_token:
            print("❌ Twilio credentials are missing! Set TWILIO_SID and TWILIO_AUTH_TOKEN.")
            return  

        client = Client(account_sid, auth_token)
        call = client.calls.create(
            to=to_phone_number,
            from_=from_phone_number,
            twiml=f'<Response><Say>{message}</Say></Response>'
        )
        print("Call placed successfully.")
        print(f"Call SID: {call.sid}")

    except Exception as e:
        print(f" Error making the call: {e}")
if __name__ == "__main__":
    to_phone_number = 'your phone number'
    from_phone_number = 'twilio number'
    message = "Alert! Unrecognized person detected by CCTV. Immediate action required."
    make_call(to_phone_number, from_phone_number, message)

