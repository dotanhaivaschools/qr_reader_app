import streamlit as st
from PIL import Image
import numpy as np
import re
import cv2
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import time

st.set_page_config(page_title="📷 Quét mã QR", layout="centered")
st.title("📷 Ứng dụng Quét Mã QR (Ảnh + Webcam)")
tab1, tab2 = st.tabs(["📤 Tải ảnh lên", "📷 Webcam trực tiếp"])

# Kiểm tra URL
def is_url(text):
    return re.match(r'^https?://', text) is not None

# Hiển thị kết quả
def show_result(data, result_placeholder):
    result_placeholder.markdown("---")
    result_placeholder.success("✅ Đã phát hiện mã QR:")
    if is_url(data):
        result_placeholder.markdown(f"🔗 `{data}`", unsafe_allow_html=True)
        result_placeholder.markdown(f"[👉 Truy cập liên kết]({data})", unsafe_allow_html=True)
    else:
        result_placeholder.code(data)

# Tab 1: Quét từ ảnh
with tab1:
    uploaded_file = st.file_uploader("🖼️ Tải ảnh chứa mã QR", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="📷 Ảnh đã tải", use_container_width=True)
        img_np = np.array(image)
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(img_np)
        if data:
            show_result(data, st)
        else:
            st.warning("⚠️ Không phát hiện mã QR nào.")

# Tab 2: Webcam
class QRScanner(VideoTransformerBase):
    def __init__(self):
        self.qr_data = None
        self.detector = cv2.QRCodeDetector()

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        data, _, _ = self.detector.detectAndDecode(img)
        if data:
            self.qr_data = data
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

with tab2:
    result_placeholder = st.empty()
    ctx = webrtc_streamer(
        key="qr-webcam",
        video_transformer_factory=QRScanner,
        async_transform=True
    )

    # Tự động kiểm tra mã QR mỗi 0.5 giây
    while ctx.state.playing:
        if ctx.video_transformer and ctx.video_transformer.qr_data:
            show_result(ctx.video_transformer.qr_data, result_placeholder)
            break
        time.sleep(0.5)