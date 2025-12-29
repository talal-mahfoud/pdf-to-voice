from flask import Flask, render_template, request, send_file, after_this_request
from werkzeug.utils import secure_filename
import os
from gtts import gTTS
import PyPDF2
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
 

app = Flask(__name__)

# إعداد المجلدات
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# دالة لاستخراج النص من PDF
def extract_text_from_pdf(pdf_path):
    
# Create a directory to store the extracted images
   images_dir = 'extracted_images'
   os.makedirs(images_dir, exist_ok=True)

# Open the PDF file
   with open(pdf_path, 'rb') as file:
    # Create a PDF reader object
      pdf_reader = PyPDF2.PdfReader(file)
    
    # Get the number of pages in the PDF
      num_pages = len(pdf_reader.pages)
    
    # Iterate through each page
      for page_num in range(num_pages):
        # Extract the page
          page = pdf_reader.pages[page_num]
        
        # Extract the text from the page
          text = page.extract_text()
        
        # Save the extracted text to a file
          with open(f'page_{page_num+1}.txt', 'w', encoding='utf-8') as text_file:
              text_file.write(text)
        
        # Convert the PDF page to images
          images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
        
        # Process each image and perform OCR
          for i, image in enumerate(images):
            # Save the image
             image_filename = f'page_{page_num+1}_image_{i+1}.png'
             image_path = os.path.join(images_dir, image_filename)
             image.save(image_path)
            
            # Extract text from image using OCR
             ocr_text = pytesseract.image_to_string(image, lang='eng')
            
            # Save OCR text to a file
             with open(f'ocr_page_{page_num+1}.txt', 'w', encoding='utf-8') as ocr_file:
                ocr_file.write(ocr_text)
                        
           
      return ocr_text

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 1. التحقق من وجود ملف
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"

        if file:
            filename = secure_filename(file.filename)
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(pdf_path)

            ocr_text = extract_text_from_pdf(pdf_path)

            
            
            tts = gTTS(text=ocr_text, lang='en', slow=False)
            
            filename = "voice-pdf"
            audio_path=(rf"E:\python\{filename}.mp3")
            tts.save(audio_path)

            

            return send_file(audio_path, as_attachment=True)

    return render_template('index.html')

if __name__ =="__main__":
    with app.app_context():
         db.create_all()
         port = int(os.environ.get("PORT", 18012))
    app.run(host='0.0.0.0',port=port)
