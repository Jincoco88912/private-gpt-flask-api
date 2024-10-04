from pgpt_python.client import PrivateGPTApi
from flask import Flask, jsonify, request
import os
import glob

app = Flask(__name__)

client = PrivateGPTApi(base_url="https://private-gpt.jincoco.site")

def _upload_all_localfile():
    """
    上傳 ./catalogs_data 目錄中的所有文件到 PrivateGPT。
    
    返回:
    list: 包含所有上傳文件的 doc_id。
    """
    files = glob.glob(os.path.join("./catalogs_data", "*"))
    ingested_doc_ids = []
    
    for file_path in files:
        with open(file_path, "rb") as f:
            ingested_file = client.ingestion.ingest_file(file=f)
            ingested_doc_ids.extend([doc.doc_id for doc in ingested_file.data])
    
    print("已上傳文件的 doc_id: ", ingested_doc_ids)
    return ingested_doc_ids

@app.route('/upload_all_localfile', methods=['GET'])
def upload_all_localfile():
    """處理上傳所有本地文件的 HTTP GET 請求。"""
    try:
        result = _upload_all_localfile()
        return jsonify({"status": "成功", "ingested_doc_ids": result})
    except Exception as e:
        return jsonify({"status": "錯誤", "message": str(e)}), 500

def _contextual_completion(prompt, use_context=True, context_filter=None, include_sources=True):
    """
    執行上下文完成。
    
    參數:
    prompt (str): 要完成的提示。
    use_context (bool): 是否使用上下文，預設為 True。
    context_filter (dict): 用於過濾上下文的條件，預設為 None（使用所有文檔）。可跳過
    include_sources (bool): 是否包含來源信息，預設為 True。
    
    返回:
    dict: 包含完成結果和來源信息的字典。
    """
    result = client.contextual_completions.prompt_completion(
        prompt=prompt,
        use_context=use_context,
        context_filter=context_filter,
        include_sources=include_sources
    ).choices[0]

    response = {
        "content": result.message.content,
        "sources": []
    }

    if include_sources and result.sources:
        response["sources"] = [
            {
                "file_name": source.document.doc_metadata.get('file_name', 'Unknown'),
                "doc_id": source.document.doc_id
            }
            for source in result.sources
        ]

    return response

@app.route('/contextual_completion', methods=['POST'])
def contextual_completion():
    """處理上下文完成的 HTTP POST 請求。"""
    try:
        data = request.json
        if not data or 'prompt' not in data:
            return jsonify({"status": "錯誤", "message": "缺少 'prompt' 欄位"}), 400
        
        prompt = data['prompt']
        use_context = data.get('use_context', True)
        context_filter = data.get('context_filter')
        include_sources = data.get('include_sources', True)

        response = _contextual_completion(prompt, use_context, context_filter, include_sources)
        return jsonify({"status": "成功", "response": response})
    except Exception as e:
        return jsonify({"status": "錯誤", "message": str(e)}), 500
     
def _list_all_ingested_docs():
    """
    列出所有已上傳到 PrivateGPT 的文件。
    
    返回:
    list: 包含所有已上傳文件的 doc_id。
    """
    ingested_docs = []
    for doc in client.ingestion.list_ingested().data:
        ingested_docs.append(doc.doc_id)
        print(f"已上傳文件 ID: {doc.doc_id}")
    return ingested_docs


@app.route('/list_ingested_docs', methods=['GET'])
def list_ingested_docs():
    """處理列出所有已上傳文件的 HTTP GET 請求。"""
    try:
        result = _list_all_ingested_docs()
        return jsonify({"status": "成功", "ingested_doc_ids": result})
    except Exception as e:
        return jsonify({"status": "錯誤", "message": str(e)}), 500

# def _chat_completion(content):
#     """
#     使用 PrivateGPT 的聊天完成功能。
    
#     參數:
#     content (str): 用戶的輸入內容。
    
#     返回:
#     str: PrivateGPT 的回應內容。
#     """
#     chat_result = client.contextual_completions.chat_completion(
#         messages=[{"role": "user", "content": content}]
#     )
#     return chat_result.choices[0].message.content

# @app.route('/chat', methods=['POST'])
# def chat():
#     """處理聊天完成的 HTTP POST 請求。"""
#     try:
#         data = request.json
#         if not data or 'content' not in data:
#             return jsonify({"status": "錯誤", "message": "缺少 'content' 欄位"}), 400
        
#         content = data['content']
#         response = _chat_completion(content)
#         return jsonify({"status": "成功", "response": response})
#     except Exception as e:
#         return jsonify({"status": "錯誤", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5111)