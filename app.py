import streamlit as st
from pypdf import PdfReader, PdfWriter
import io

st.set_page_config(
    page_title="PDF Unlocker – Absa Statements",
    page_icon="🔓",
    layout="centered"
)

st.title("🔓 PDF Unlocker")
st.caption("Upload a password-protected Absa bank statement → get an unprotected version")

# --- Password section ---
st.subheader("1. Password")

# Use session state to remember the password during the session
if "saved_password" not in st.session_state:
    st.session_state.saved_password = ""

password = st.text_input(
    "Enter password",
    value=st.session_state.saved_password,
    type="password",
    placeholder="e.g. 22042003A.",
    help="This password is only kept in your current browser session. It is never stored on any server."
)

col1, col2 = st.columns([1, 3])
with col1:
    if st.button("Remember for this session", use_container_width=True):
        st.session_state.saved_password = password
        st.success("Password saved for this session")
with col2:
    if st.session_state.saved_password:
        st.info(f"Using saved password: {'•' * min(len(st.session_state.saved_password), 8)}")

# --- Upload section ---
st.subheader("2. Upload PDF")
uploaded_file = st.file_uploader(
    "Choose a password-protected PDF",
    type=["pdf"],
    accept_multiple_files=False
)

# --- Process ---
if uploaded_file is not None:
    st.subheader("3. Unlock")

    if not password:
        st.warning("Please enter the password first.")
    else:
        if st.button("Unlock PDF", type="primary", use_container_width=True):
            try:
                # Read the uploaded file
                pdf_bytes = uploaded_file.read()
                reader = PdfReader(io.BytesIO(pdf_bytes))

                if reader.is_encrypted:
                    result = reader.decrypt(password)
                    if result == 0:
                        st.error("Incorrect password. Please check and try again.")
                        st.stop()
                else:
                    st.info("This PDF is not password-protected. You can download it as-is.")

                # Create unlocked version
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)

                # Optional: copy metadata
                if reader.metadata:
                    writer.add_metadata(reader.metadata)

                # Save to memory
                output = io.BytesIO()
                writer.write(output)
                output.seek(0)

                # Prepare download name
                original_name = uploaded_file.name
                if original_name.lower().endswith(".pdf"):
                    unlocked_name = original_name[:-4] + "_unlocked.pdf"
                else:
                    unlocked_name = original_name + "_unlocked.pdf"

                st.success("PDF unlocked successfully!")
                st.download_button(
                    label="⬇️ Download Unlocked PDF",
                    data=output,
                    file_name=unlocked_name,
                    mime="application/pdf",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"Error while processing the PDF: {str(e)}")
                st.info("Make sure the file is a valid PDF and the password is correct.")

st.markdown("---")
st.caption("All processing happens in your session. The password and PDF are not stored permanently.")
