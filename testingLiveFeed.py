import firebase_admin
from firebase_admin import credentials, db
import base64
import requests
import tkinter as tk
from tkinter import ttk  # Importing ttk for the Treeview widget
from PIL import Image, ImageTk
from io import BytesIO  # Import BytesIO from io module

# Initialize Firebase Admin SDK
cred = credentials.Certificate(
    r"C:\Users\Amulya\PycharmProjects\CrashDet\crash-detection-f1dab-firebase-adminsdk-vuj5v-a1af355410.json"
)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://crash-detection-f1dab-default-rtdb.firebaseio.com/'  # Your Realtime Database URL
})
# Function to update live feed from Firebase
def update_live_feed(camera_feed_ref, label):
    # Get the live feed from Firebase
    img_data = camera_feed_ref.get()  # Retrieve the base64 image string


    if img_data:
        # Decode the base64 string to an image
        img_bytes = base64.b64decode(img_data)
        img = Image.open(BytesIO(img_bytes))

        # Convert the image to a format Tkinter can use
        img_tk = ImageTk.PhotoImage(img)

        # Update the label with the new image
        label.config(image=img_tk)
        label.image = img_tk  # Keep a reference to avoid garbage collection

    # Schedule the next update
    root.after(1000, update_live_feed, camera_feed_ref, label)  # Update every 1000 ms (1 second)

# Set up the Tkinter window
root = tk.Tk()
root.title("Live Feeds from Cameras")
root.geometry("1400x700")  # Set window size to 1400x700
# Create labels to display the images for each camera
label1 = tk.Label(root)
label1.place(x=40, y=40, width=160*2, height=90*2)  # First camera feed (1/3 of the window height)

label2 = tk.Label(root)
label2.place(x=40, y=240, width=160*2, height=90*2)  # Second camera feed (1/3 of the window height)

label3 = tk.Label(root)
label3.place(x=40, y=440, width=160*2, height=90*2)  # Third camera feed (1/3 of the window height)



# Create a Treeview table to display alerts
columns = ('Image', 'Timestamp', 'Maps', 'Tickbox')
tree = ttk.Treeview(root, columns=columns, show='headings')

# Set the headings for each column
tree.heading('Image', text='Image')
tree.heading('Timestamp', text='Timestamp')
tree.heading('Maps', text='Maps')
tree.heading('Tickbox', text='Tickbox')

# Set the column widths
tree.column('Image', width=100)
tree.column('Timestamp', width=200)
tree.column('Maps', width=100)
tree.column('Tickbox', width=80)

# Place the Treeview at the specified coordinates
tree.place(x=620, y=10, width=600, height=650)  # Adjust width and height as necessary

# Add a scrollbar to the Treeview
scrollbar = ttk.Scrollbar(root, orient='vertical', command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.place(x=1220, y=10, height=650)  # Place scrollbar next to the tree


# Start updating the live feeds
camera_feed_ref1 = db.reference('Camera1_Feed')
camera_feed_ref2 = db.reference('Camera2_Feed')
camera_feed_ref3 = db.reference('Camera3_Feed')

update_live_feed(camera_feed_ref1, label1)
update_live_feed(camera_feed_ref2, label2)
update_live_feed(camera_feed_ref3, label3)

# Run the Tkinter main loop
root.mainloop()
