from flask import Flask, request,render_template,send_from_directory,send_file
import fitz
import docx
import datetime 
from gtts import gTTS
# import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("ttos.html")

@app.route('/upload', methods=['POST'])
def upload():
    #Accepting file submitted on app
    file = request.files['fileInput']
    if file.filename == '':
        return 'Please choose a file.'
    if file:
        # File processing logic here
        file_contents = file.read()
        
        # Get file extension
        file_extension = file.filename.split('.')[-1].lower()
        
        if file_extension == 'txt':
            # Convert binary file content to text
            text = file_contents.decode('utf-8')
        elif file_extension == 'pdf':
            # Read PDF contents
            pdf = fitz.open(stream=file_contents, filetype='pdf')
            text = ''
            for page in range(pdf.page_count):
                text += pdf.load_page(page).get_text("text")
        elif file_extension == 'doc' or file_extension == 'docx':
            # Read DOC/DOCX contents
            doc = docx.Document(file)
            text = ' '.join([paragraph.text for paragraph in doc.paragraphs])
        else:
            return render_template("ttos.html",message="Unsupported file format. Please upload a txt, pdf, or doc file.")
            # return 'Unsupported file format. Please upload a txt, pdf, or doc file.'

        # blob = TextBlob(text)
        # input_language = blob.detect_language()
        input_language = request.form['inputLanguage']
        output_language = request.form['outputLanguage']
        # print(input_language)
        # print(output_language)

        print("Entered text: ",text)
        from translate import Translator

        if len(text) > 500:
            # Split the input text into smaller chunks of 500 characters or less
            text_chunks = [text[i:i+500] for i in range(0, len(text), 500)]
            translations = []
            for chunk in text_chunks:
                translator = Translator(from_lang=input_language, to_lang=output_language)
                translation = translator.translate(chunk)
                translations.append(translation)
            # Concatenate the translated chunks to get the complete translation
            translation = ''.join(translations)
        else:
            # Translate the entire text if it's within the limit
            translator = Translator(from_lang=input_language, to_lang=output_language)
            translation = translator.translate(text)

        print("Translated text: ", translation)

        # Create a text-to-speech object
        tts = gTTS(translation, lang=output_language)

        timestamp = datetime.datetime.now().strftime("%H%M%S_%d%m%Y")
        output_file = f"file_{timestamp}.mp3"
        tts.save(output_file)

        # Play audio
        # os.system(f"start file_{timestamp}.mp3")  

        print("\nText converted to Speech Successfully")
        download_link = '/download/' + output_file
        return render_template("download.html", download_link=download_link, filename=output_file)
    else:
        return 'Error uploading file. Please try again.'

@app.route('/download/<path:filename>')
def download(filename):
    # Generate download prompt for the specified file
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

