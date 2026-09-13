import streamlit as st
import cv2
import base64
import numpy as np
from main import process_image    


st.set_page_config(page_title="License Plate Privacy Protector", layout="wide")

st.markdown(
    "<style>.block-container{padding-top:2rem;padding-bottom:1rem;}</style>",
    unsafe_allow_html=True,
)

st.title("License Plate Privacy Protector")


def to_rgb(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def img_to_b64(bgr):
    """Encode a BGR image to a base64 string for inline HTML display."""
    ok, buf = cv2.imencode(".jpg", bgr)
    return base64.b64encode(buf).decode() if ok else ""


# Problem / Solution / Result
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**Problem**")
    st.caption("Car photos may contain private information like license plates.")
with c2:
    st.markdown("**Solution**")
    st.caption("Automatically detect the license plate and blur it.")
with c3:
    st.markdown("**Result**")
    st.caption("A safer image that can be shared publicly without exposing private information.")

uploaded_file = st.file_uploader("Upload a car image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    Car_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    out = process_image(Car_image)

    # Processing pipeline
    st.markdown("**Processing Pipeline**")
    cols = st.columns(6)
    stages = [
        (to_rgb(out["original"]), "1 · Original Image"),
        (out["gray"],             "2 · Grayscale Conversion"),
        (out["blur"],             "3 · Noise Reduction"),
        (out["edges"],            "4 · Edge Detection"),
        (to_rgb(out["annotated"]) if out["location"] is not None else to_rgb(out["original"]), "5 · Plate Detection"),
        (to_rgb(out["final"]) if out["final"] is not None else to_rgb(out["original"]), "6 · Privacy Protected"),
    ]
    for col, (img, cap) in zip(cols, stages):
        with col:
            st.image(img, use_container_width=True)
            st.caption(cap)

    # Divider between pipeline and Input/Output
    st.divider()

    # Input -> Output
    st.markdown("**Input vs Output**")

    final_bgr = out["final"] if out["final"] is not None else out["original"]
    in_b64 = img_to_b64(out["original"])
    out_b64 = img_to_b64(final_bgr)

    card = (
        "border:1px solid #ddd;border-radius:12px;padding:10px;"
        "box-shadow:0 2px 6px rgba(0,0,0,0.08);text-align:center;background:#fff;"
    )
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;justify-content:center;gap:24px;">
            <div style="{card}">
                <img src="data:image/jpeg;base64,{in_b64}" style="height:300px;border-radius:8px;"/>
                <div style="margin-top:6px;color:#666;">Input</div>
            </div>
            <div style="font-size:48px;color:#888;">&#8594;</div>
            <div style="{card}">
                <img src="data:image/jpeg;base64,{out_b64}" style="height:300px;border-radius:8px;"/>
                <div style="margin-top:6px;color:#666;">Output</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Download
    st.write("")
    if out["final"] is not None:
        success, buffer = cv2.imencode(".jpg", out["final"])
        if success:
            st.download_button("Download Final Result", buffer.tobytes(),
                               "license_plate_protected.jpg", "image/jpeg")
    else:
        st.error("License plate could not be detected. Please try another image.")