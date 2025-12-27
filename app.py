import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import base64
## Streamlit App

# Configure the API key
genai.configure(api_key=st.secrets["google_api_key"])

# Set up the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

system_prompts = [
    """
    You are a domain expert in medical image analysis. You are tasked with 
    examining medical images for a renowned hospital.
    Your expertise will help in identifying or 
    discovering any anomalies, diseases, conditions or
    any health issues that might be present in the image.
    
    Your key responsibilites:
    1. Detailed Analysis : Scrutinize and thoroughly examine each image, 
    focusing on finding any abnormalities.
    2. Analysis Report : Document all the findings and 
    clearly articulate them in a structured format.
    3. Recommendations : Basis the analysis, suggest remedies, 
    tests or treatments as applicable.
    4. Treatments : If applicable, lay out detailed treatments 
    which can help in faster recovery.
    
    Important Notes to remember:
    1. Scope of response : Only respond if the image pertains to 
    human health issues.
    2. Clarity of image : In case the image is unclear, 
    note that certain aspects are 
    'Unable to be correctly determined based on the uploaded image'
    3. Disclaimer : Accompany your analysis with the disclaimer: 
    "Consult with a Doctor before making any decisions."
    4. Your insights are invaluable in guiding clinical decisions. 
    Please proceed with the analysis, adhering to the 
    structured approach outlined above.
    
    Please provide the final response with these 4 headings : 
    Detailed Analysis, Analysis Report, Recommendations and Treatments
    
"""
]

model = genai.GenerativeModel(model_name="gemini-3-flash-preview",
                              generation_config=generation_config,
                              safety_settings=safety_settings)


st.set_page_config(
  page_title="Visual Medical Assistant",
  page_icon="🩺",
  layout="wide",
  initial_sidebar_state="expanded"
)
st.title("Visual Medical Assistant 👨‍⚕️ 🩺 🏥")
st.subheader("An app to help with medical analysis using images")
st.markdown("---") 
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        backdrop-filter: blur(10px);
        color: white;
        text-align: center;
        padding: 10px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 14px;
        font-weight: 500;
        border-top: 1px solid #e6e6e6;
        z-index: 1000;
    }
    </style>
    <div class="footer">
        🚀 Built with ❤️ by <b>Vaishnavi Choudhary</b> | © 2025 Visual Medical Assistant
    </div>
    """,
    unsafe_allow_html=True
)

# function to generate pdf
def generate_pdf(text,filename="Medical_Image_Analysis_Report.pdf"):
    pdf=FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    if language=="Hindi":
      pdf.add_font("NotoHindi", style="", fname="NotoSansDevanagari-VariableFont_wdth,wght.ttf", uni=True)
      pdf.set_font("NotoHindi", size=12)
      title_text = "चिकित्सा छवि विश्लेषण रिपोर्ट"
    else:
      pdf.add_font("NotoLatin", style="", fname="NotoSans-Italic-VariableFont_wdth,wght.ttf", uni=True)
      pdf.set_font("NotoLatin", size=12)

      titles={
          "English": "Medical Image Analysis Report",
          "Spanish": "Informe de Análisis de Imágenes Médicas",
          "French": "Rapport d'Analyse d'Image Médicale"
      }
      title_text = titles.get(language, "Medical Image Analysis Report")
    pdf.cell(0, 10, title_text, ln=True, align='C')
    pdf.ln(10)

    pdf.multi_cell(0, 8,text=text)

    return bytes(pdf.output())

#  language selection 
language=st.sidebar.selectbox("🌐 Preferred Language for Analysis Report", ["English", "Hindi","Spanish", "French"])

# file uploader
file_uploaded = st.file_uploader('Upload the image for Analysis', 
type=['png','jpg','jpeg'])

if file_uploaded:
    st.image(file_uploaded, width=200, caption='Uploaded Image')
    
submit=st.button("Generate Analysis")

if submit:

    image_data = file_uploaded.getvalue()

    mime_type = file_uploaded.type
    if mime_type == "image/jpg":
        mime_type = "image/jpeg"
    
    image_parts = [
        {
            "mime_type" : mime_type,
            "data" : image_data
        }
    ]
    
# making our prompt ready
    prompt_parts = [
        image_parts[0],
        system_prompts[0]+f"\n\nIMPORTANT: Please provide the entire response in {language}.",
    ]
    
# generate response
    
    with st.spinner('👨‍⚕️ Analyzing medical image... Please wait.'):
        try:
          response = model.generate_content(prompt_parts)
          if response:
            st.title('Detailed analysis based on the uploaded image')
            st.write(response.text)

            pdf_data= generate_pdf(response.text)
            st.download_button(
                label="📄 Download Analysis Report as PDF",
                data=pdf_data,
                file_name="Medical_Image_Analysis_Report.pdf",
                mime="application/pdf"
              ) 
        except Exception as e:
            st.error(f"An error occurred: {e}")