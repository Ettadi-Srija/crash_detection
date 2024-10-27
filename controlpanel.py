import firebase_admin
from firebase_admin import credentials, db
import requests
from io import BytesIO
from PIL import Image
import tkinter as tk
from PIL import ImageTk

# Initialize Firebase Admin SDK
cred = credentials.Certificate(
    r"C:\Users\Amulya\PycharmProjects\CrashDet\crash-detection-f1dab-firebase-adminsdk-vuj5v-a1af355410.json"
)

try:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://crash-detection-f1dab-default-rtdb.firebaseio.com/'
    })
except Exception as e:
    print(f"Failed to initialize Firebase: {e}")
    exit()

# Function to retrieve and display the latest alert images with a timeout
def fetch_latest_alert_images():
    alerts_ref = db.reference('alerts')
    alerts = alerts_ref.get()

    # Check if alerts is a dictionary
    if not isinstance(alerts, dict):
        print("No alerts found or alerts is not a dictionary.")
        return

    # Process each alert
    for alert_id, alert in alerts.items():
        image_url = alert.get('image')  # Use .get() to avoid KeyError
        timestamp = alert.get('timestamp')
        gps_link = alert.get('gpsLink')
        flag = alert.get('flag', False)  # Default to False if not present

        if not flag:  # Check if flag is False
            try:
                # Fetch the image with a 10-second timeout
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()

                # Load the image data
                image_data = BytesIO(response.content)
                img = Image.open(image_data)

                # Display the image in a Tkinter window
                img_tk = ImageTk.PhotoImage(img)
                label = tk.Label(root, image=img_tk)
                label.image = img_tk  # Keep a reference to avoid garbage collection
                label.pack()  # Add to the Tkinter window

                # Print or log the alert details
                print(f"Timestamp: {timestamp}, GPS: {gps_link}")

                # Update the flag to True in the database
                alerts_ref.child(alert_id).update({'flag': True})

            except requests.exceptions.Timeout:
                print(f"Timeout occurred while fetching image for alert {alert_id}.")
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
        else:
            print(f"Alert {alert_id} has already been shown. Skipping.")

    # Schedule the next check
    root.after(5000, fetch_latest_alert_images)  # Check for new alerts every 5 seconds

# Set up the Tkinter window
root = tk.Tk()
root.title("Alert Images")
root.geometry("800x600")  # Adjust as necessary

# Start fetching the latest alert images
fetch_latest_alert_images()

# Run the Tkinter main loop
root.mainloop()
