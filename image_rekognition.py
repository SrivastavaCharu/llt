from flask import Flask, jsonify, request, render_template
from flask_cors import CORS, cross_origin
import boto3
import io


app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.after_request
def after_request(response):

    return response




polly_client = boto3.client('polly', region_name='ap-northeast-1')
translate_client = boto3.client('translate', region_name='ap-northeast-1')
rekognition_client = boto3.client('rekognition', region_name='ap-northeast-1')


@app.route('/speak', methods=['POST'])
@cross_origin()
def text_to_speech():
    data = request.get_json()
    text = data.get('text', '')
    VOICE_LANGUAGE_MAP = {
    'en-US': 'Joanna',
    'ja-JP': 'Mizuki',
    'hi-IN': 'Aditi',
    'es-ES': 'Conchita',
    }

    language = data.get('speechLanguage', 'en-US')
    voice = VOICE_LANGUAGE_MAP.get(language, 'Joanna')
    response = polly_client.synthesize_speech(VoiceId=voice,
                                              OutputFormat='mp3',
                                              Text=text,
                                              LanguageCode=language)
    audio_stream = response["AudioStream"].read()
    headers = {
        'Content-Type': 'audio/mpeg',
    }
    return audio_stream, 200, headers


@app.route('/translate', methods=['POST'])
@cross_origin()
def translate_text():
    data = request.get_json()
    text = data.get('text', '')
    source_language = data.get('source_language', '')
    target_language = data.get('target_language', '')
    result = translate_client.translate_text(Text=text,
                                             SourceLanguageCode=source_language,
                                             TargetLanguageCode=target_language)
    translated_text = result.get('TranslatedText')
    response = jsonify({'translated_text': translated_text})
    return response


@app.route('/upload', methods=['POST'])
@cross_origin()
def upload_image():
    img = request.files.get("imgUpload")
    language = request.form.get("language")
    if img is None:
        return jsonify({'error': 'No image uploaded'}), 400
    img_bytes = img.read()
    response = rekognition_client.detect_labels(
        Image={'Bytes': img_bytes}, MaxLabels=10)
    labels = [label['Name'] for label in response['Labels']]
    translations = [translate_client.translate_text(Text=label,
                                                    SourceLanguageCode='en',
                                                    TargetLanguageCode=language)['TranslatedText']
                    for label in labels]
    translation = ', '.join(translations)
    response = jsonify({'translation': translation})
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
