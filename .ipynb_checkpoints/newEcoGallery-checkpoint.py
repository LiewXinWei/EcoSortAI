import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import cv2
from ultralytics import YOLO
import os
from PIL import Image
import numpy as np

# 🚀 App Logo (Left Side)
st.sidebar.image("ecosort_logo3.png", width=450)

# ✅ Store Checkbox Value in Session State
if "accepted_terms" not in st.session_state:
    st.session_state.accepted_terms = False

# ✅ Initialize detection counts & history
if "detection_count" not in st.session_state:
    st.session_state.detection_count = {"Cardboard": 0, "Metal": 0, "Paper": 0, "Plastic": 0}

if "detection_history" not in st.session_state:
    st.session_state.detection_history = pd.DataFrame(columns=["Timestamp", "Material", "Credits"])

if "webcam_active" not in st.session_state:
    st.session_state.webcam_active = False

# ✅ Dropdown Menu with Tabs
menu = st.sidebar.selectbox("Navigation", ["Terms & Conditions", "Ecosort's Overview", "Waste Tracking", "Materials Recognition", "Eco Gallery", "About"])

# ✅ Terms & Conditions Tab
if menu == "Terms & Conditions":
    st.header("📜 Terms & Conditions")

    terms_text = """
    **Ecosort Terms & Conditions**
    
    _Last Updated: May 2025_
    
    ### **1️⃣ Data Protection & Privacy**
    - **Data Encryption:** All images and sensor data used for sorting are encrypted to protect user privacy.
    - **Secure Data Storage:** Sorting records are securely stored to prevent unauthorized access or accidental loss.
    - **Privacy Compliance:** No personal data is recorded—sorting reports contain only general recycling statistics.
    
    ### **2️⃣ Authorized Access & Security**
    - **Authentication Protocols:** Only authorized personnel (e.g., town council staff) can access system settings.
    - **User Access:** Residents can view basic stats, but only designated staff can modify sorting configurations.
    - **Secure Data Transfer:** All data exchanged between smart bins and the main system is encrypted for security.
    
    ### **3️⃣ System Reliability & Accuracy**
    - **Accurate Sorting:** The system ensures items are classified correctly, even if they are slightly damaged or dirty.
    - **Consistency:** Sorting accuracy is maintained regardless of environmental conditions (e.g., day/night, object size).
    - **Supports Recycling:** Proper sorting increases the likelihood that recyclable materials are reused instead of wasted.
    
    ### **4️⃣ Transparency & Environmental Responsibility**
    - **Transparency:** The system provides clear feedback, allowing users to track recycling performance and improvements.
    - **Environmental Responsibility:** Encourages responsible waste disposal, promoting sustainability in the community.
    - **Data Backup:** Sorting history is backed up regularly to ensure continuity, even in the event of system outages.
    
    ### **5️⃣ Acceptance of Terms**
    By using the Ecosort system, you agree to:
    ✅ Respect the security measures in place.
    ✅ Accept that data privacy is prioritized.
    ✅ Follow proper recycling practices to support environmental efforts.
    """

    # ✅ Display Hardcoded Terms (Users CANNOT Edit)
    st.write(terms_text)  

    # ✅ Checkbox to Accept Terms
    if st.checkbox("I Accept the Terms & Conditions", value=st.session_state.accepted_terms):
        st.session_state.accepted_terms = True
        st.success("✅ You can now access other tabs!")


# ✅ Ecosort's Overview Tab (Live Bar Chart)
if menu == "Ecosort's Overview":
    if not st.session_state.accepted_terms:
        st.warning("⚠ You must accept the terms to access this page!")
    else:
        st.header("📊 Ecosort's Overview - Monthly Data")

        # 🚀 Select Month (Dropdown)
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        selected_month = st.selectbox("Select Month", months, index=4)  # Default is May

        # ✅ Use Model Detection Data
        df = pd.DataFrame(list(st.session_state.detection_count.items()), columns=["Material", "Count"])

        # 🚀 Plot Live Bar Chart
        fig, ax = plt.subplots()
        colors = {"Cardboard": "green", "Metal": "yellow", "Paper": "red", "Plastic": "blue"}
        ax.bar(df["Material"], df["Count"], color=[colors[m] for m in df["Material"]])
        ax.legend([f"{m} ({colors[m]})" for m in df["Material"]], loc="upper right")
        ax.set_ylabel("Detection Count")
        ax.set_title(f"Detected Materials in {selected_month}")

        st.pyplot(fig)

# ✅ Waste Tracking Tab (Live Line Graph & Table)
if menu == "Waste Tracking":
    if not st.session_state.accepted_terms:
        st.warning("⚠ You must accept the terms to access this page!")
    else:
        st.header("♻️ Waste Tracking - Live Data")

        # 🚀 Dynamic Live Line Graph
        fig, ax = plt.subplots()
        for material in st.session_state.detection_count.keys():
            material_data = st.session_state.detection_history[st.session_state.detection_history["Material"] == material]
            if not material_data.empty:
                ax.plot(material_data.index, material_data["Credits"].cumsum(), label=material)  # ✅ Accumulate values over time

        ax.set_ylabel("Total Credits Earned")
        ax.set_xlabel("Detection Events")
        ax.set_title("Material Deposits Over Time")
        ax.legend(loc="upper right")
        st.pyplot(fig)

        # ✅ Update Waste Tracking Table Format
        if not st.session_state.detection_history.empty:
            st.session_state.detection_history["Timestamp"] = pd.to_datetime(st.session_state.detection_history["Timestamp"], errors='coerce')  # ✅ Convert Timestamp
            st.session_state.detection_history.dropna(subset=["Timestamp"], inplace=True)  # ✅ Remove invalid timestamps
            st.session_state.detection_history["Date"] = st.session_state.detection_history["Timestamp"].dt.date
            st.session_state.detection_history["Time"] = st.session_state.detection_history["Timestamp"].dt.time
            formatted_history = st.session_state.detection_history[["Date", "Time", "Material", "Credits"]]  # ✅ Separate Date & Time
        else:
            formatted_history = st.session_state.detection_history

        # 🚀 Display Updated Live Table
        st.write("📋 **Detected Materials History**")
        st.dataframe(formatted_history)
        
# 🚀 Load YOLOv8 Model
@st.cache_resource
def load_yolo_model():
    return YOLO("AiPD/ecosortai/train33/weights/best.pt")

model = load_yolo_model()

# 🔍 Detect material from a single image frame
def detect_material_from_frame(frame):
    if frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

    results = model(frame, conf=0.8, iou=0.7, classes=[0, 1, 2, 3])

    for result in results:
        class_ids = result.boxes.cls.cpu().numpy()
        for cls_id in class_ids:
            material_name = model.names[int(cls_id)].lower()
            return material_name  # Return first detected class

    return "none"

# 🖼️ EcoGallery Feature
def run_eco_gallery():
    st.title("🖼️ EcoGallery")
    st.markdown("Snap a photo of a recyclable item and help improve our recognition system!")

    st.info("🤖 If the material was detected incorrectly, help us train the AI by labeling it correctly below!")

    # 📸 Camera Input
    camera_input = st.camera_input("Take a photo of your item")

    if camera_input is not None:
        # 🖼️ Process the image
        img = Image.open(camera_input)
        img_array = np.array(img)
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
        img_array = cv2.flip(img_array, 1)  # ✅ Flip horizontally for mirror effect

        # 🤖 Detect material
        detected_material = detect_material_from_frame(img_array)
        st.write(f"🤖 Detected: **{detected_material.upper()}**")

        # ✅ User feedback for dataset improvement
        correct_label = st.selectbox("What is the correct material?", ["cardboard", "metal", "paper", "plastic"])
        
        if st.button("Submit to Dataset"):
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{correct_label}_{timestamp}.jpg"
            save_path = os.path.join("eco_gallery_dataset", correct_label, filename)

            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            cv2.imwrite(save_path, cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR))
            st.success(f"✅ Image saved to dataset under: {correct_label}")

# ✅ Run only if this menu item is selected
if menu == "Eco Gallery":
    run_eco_gallery()

# ✅ Materials Recognition Tab (Live YOLO Detection & Image Saving)
if menu == "Materials Recognition":
    st.header("🔍 **Materials Recognition - Live Detection**")

    camera_status = "🟥 **Not Active**" if not st.session_state.webcam_active else "🟩 **Running**"
    st.markdown(f"**Camera Status:** {camera_status}")

    if not st.session_state.webcam_active:
        if st.button("Start Webcam"):
            st.session_state.webcam_active = True

    if st.session_state.webcam_active:
        if st.button("Stop Webcam"):
            st.session_state.webcam_active = False

        # 🚀 Load YOLO Model
        model = YOLO("runs/detect/train33/weights/best.pt")

        # ✅ Initialize Webcam
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)

        if not cap.isOpened():
            st.error("❌ Error: Could not open webcam.")
            st.session_state.webcam_active = False
            st.stop()

        stframe = st.empty()
        material_display = st.empty()
        table_display = st.empty()

        while st.session_state.webcam_active:
            ret, frame = cap.read()
            if not ret:
                st.error("❌ Error: Could not read frame.")
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)  

            img_path = None  # ✅ Set default

            # 🚀 Run YOLO Detection
            results = model(frame, conf=0.8, iou=0.7, classes=[0, 1, 2, 3])
            detected_material = "None"

            for result in results:
                class_ids = result.boxes.cls.cpu().numpy()
                for cls_id in class_ids:
                    material_name = model.names[int(cls_id)].capitalize()
                    detected_material = material_name

                    # ✅ Save Image
                    img_path = f"C:/Practice/AiPD/eco_gallery/{material_name}_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(img_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

                    if material_name in st.session_state.detection_count:
                        st.session_state.detection_count[material_name] += 1  

                        credit_mapping = {"Cardboard": 7, "Metal": 10, "Paper": 5, "Plastic": 6}
                        detected_credits = credit_mapping.get(material_name, 0)
                        detected_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                        new_entry = pd.DataFrame([[detected_timestamp, material_name, detected_credits]],
                                                 columns=["Timestamp", "Material", "Credits"])
                        st.session_state.detection_history = pd.concat([st.session_state.detection_history, new_entry],
                                                                       ignore_index=True)

            # 🚀 Update Webcam Feed
            stframe.image(frame, channels="RGB")

            # ✅ Detection Summary Table
            df = pd.DataFrame(
                [["No. of materials scanned", "Cardboard", "Metal", "Paper", "Plastic"],
                 ["Total Count", st.session_state.detection_count["Cardboard"], 
                  st.session_state.detection_count["Metal"],
                  st.session_state.detection_count["Paper"],
                  st.session_state.detection_count["Plastic"]]],
                columns=["Category", "Cardboard", "Metal", "Paper", "Plastic"]
            )
            table_display.table(df)  

        cap.release()
        cv2.destroyAllWindows()