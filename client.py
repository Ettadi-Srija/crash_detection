import cv2
import firebase_admin
from firebase_admin import credentials, db, storage
import datetime
import base64
import time

# Initialize Firebase Admin SDK
cred = credentials.Certificate(
    r"C:\Users\preetham\OneDrive\Desktop\CRASHDetectn\crash-detection-f1dab-firebase-adminsdk-vuj5v-a1af355410.json"
)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://crash-detection-f1dab-default-rtdb.firebaseio.com/',  # Your Realtime Database URL
    'storageBucket': 'crash-detection-f1dab.appspot.com'  # Your Firebase Storage bucket name
})

# Function to capture image and send data
def send_data(camera_name, gps_link):
    cap = cv2.VideoCapture(0)  # Adjust camera index as needed

    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image.")
        return

    # Save the captured frame temporarily
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    image_filename = f"{camera_name}_{timestamp}.jpg"
    cv2.imwrite(image_filename, frame)

    # Upload image to Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob(f"images/{image_filename}")  # Specify folder in storage
    blob.upload_from_filename(image_filename)

    # Get public URL for the uploaded image
    blob.make_public()
    image_url = blob.public_url

    # Store alert details in Realtime Database
    alerts_ref = db.reference('alerts')
    alert_id = alerts_ref.push().key  # Generate a new alert ID
    alerts_ref.child(alert_id).set({
        'image': image_url,
        'timestamp': timestamp,
        'gpsLink': gps_link,
        'flag': False
    })
    print("Crash detected! Image and data sent to Firebase.")

    # Release the capture
    cap.release()

# Function to continuously capture and update live feed to Firebase
def update_live_feed():
    cap = cv2.VideoCapture(0)  # Open the camera
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image.")
            break

        # Encode the frame to base64
        _, buffer = cv2.imencode('.jpg', frame)
        img_string = base64.b64encode(buffer).decode('utf-8')

        # Update the Camera1_Feed reference in Firebase
        camera_feed_ref = db.reference('Camera1_Feed')
        camera_feed_ref.set(img_string)  # Set the base64 string in the database

        # Print confirmation
        print("Live feed updated in Firebase.")

        # Delay to control the capture rate (e.g., every 1 second)
        time.sleep(1)

    cap.release()

# Example usage for a client
send_data("Camera1", "https://maps.app.goo.gl/ZRntm7ibUyP8M8846?g_st=iw")
update_live_feed()  # Start the live feed
