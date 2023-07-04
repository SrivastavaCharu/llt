from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import boto3
import io


app = Flask(__name__)
cors = CORS(app)


@app.after_request
def after_request(response):

    return response



polly_client = boto3.client('polly', region_name='ap-northeast-1')
translate_client = boto3.client('translate', region_name='ap-northeast-1')
rekognition_client = boto3.client('rekognition', region_name='ap-northeast-1')


@app.route('/speak', methods=['POST'])
@cross_origin(origin='http://43.206.222.228')
def text_to_speech():
    data = request.get_json()
    text = data.get('text', '')
    language = data.get('speechLanguage', 'en-US')
    response = polly_client.synthesize_speech(VoiceId='Joanna',
                                              OutputFormat='mp3',
                                              Text=text,
                                              LanguageCode=language)
    audio_stream = response["AudioStream"].read()
    return audio_stream, 200, {'Content-Type': 'audio/mpeg'}


@app.route('/translate', methods=['POST'])
@cross_origin(origin='http://43.206.222.228')
def translate_text():
    data = request.get_json()
    text = data.get('text', '')
    source_language = data.get('source_language', '')
    target_language = data.get('target_language', '')
    result = translate_client.translate_text(Text=text,
                                             SourceLanguageCode=source_language,
                                             TargetLanguageCode=target_language)
    translated_text = result.get('TranslatedText')
    return jsonify({'translated_text': translated_text})


@app.route('/upload', methods=['POST'])
@cross_origin(origin='http://43.206.222.228')
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
    return jsonify({'translation': translation})


if __name__ == "__main__":
    app.run(debug=True)
