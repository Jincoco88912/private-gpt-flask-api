import glob
import os
from flask import Flask, jsonify, request
from gradio_client import Client, handle_file

app = Flask(__name__)

client = Client("https://private-gpt.jincoco.site")

def _upload_file(url):
    result = client.predict(
        files=[handle_file(url)],
        api_name="/_upload_file"
    )
    print(result)
    return result

def _upload_all_localfile():
    files = glob.glob(os.path.join("./catalogs_data", "*"))
    file_handles = [handle_file(f) for f in files]
    print(file_handles)
    
    result = client.predict(
        files=file_handles,
        api_name="/_upload_file"
    )
    print(result)
    return result

def _list_ingested_files():
    result = client.predict(api_name="/_list_ingested_files")
    print(result)
    return result

def _set_system_prompt(prompt):
    result = client.predict(
            system_prompt_input=prompt,
            api_name="/_set_system_prompt"
    )
    print(result)
    return result

def _chat(message):
    files = glob.glob(os.path.join("./catalogs_data", "*"))
    result = client.predict(
            message=message,
            mode="RAG",
            param_3=[handle_file(f) for f in files],
            param_4="你是一搜尋機器人助理，請用繁體中文回答問題",
            api_name="/chat"
    )
    print(result)
    return result

def handle_request(func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 上傳文件指定連結文件
@app.route('/upload_file', methods=['GET'])
def upload_file():
    path = request.args.get('url')
    if not path:
        return jsonify({'error': 'Missing file path parameter'}), 400
    return handle_request(_upload_file, path)

# 上傳文件同步本地文件
@app.route('/upload_all_localfile', methods=['GET'])
def upload_all_localfile():
    return handle_request(_upload_all_localfile)

# 列出已上傳的文件
@app.route('/list_ingested_files', methods=['GET'])
def list_ingested_files():
    return handle_request(_list_ingested_files)

@app.route('/set_system_prompt', methods=['GET'])
def set_system_prompt():
    path = request.args.get('prompt')
    if not path:
        return jsonify({'error': 'Missing file path parameter'}), 400
    return handle_request(_set_system_prompt, path)

@app.route('/chat', methods=['GET'])
def chat():
    message = request.args.get('message')
    # param_3 = request.args.getlist('param_3')

    try:
        result = _chat(message)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5111)
