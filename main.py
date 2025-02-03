from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import xml.etree.ElementTree as ET
import json
import time

app = Flask(__name__)
CORS(app)  # 允许所有域名跨域访问

# 固定的文件哈希
FILE_HASH = '00000000000000000000000000000000'

def convert_danmaku_json_to_xml(json_string):
    data = json.loads(json_string)
    root = ET.Element('i')
    for comment in data.get('comments', []):
        p = comment['p'].split(',')
        time_val = float(p[0])
        mode = int(p[1])
        color = int(p[2])
        user_id = p[3]
        font_size = 25
        unix_timestamp = int(time.time())
        danmaku_pool = 0
        row_id = comment['cid']
        p_attribute = f"{time_val},{mode},{font_size},{color},{unix_timestamp},{danmaku_pool},{user_id},{row_id}"
        d_element = ET.SubElement(root, 'd', p=p_attribute)
        d_element.text = comment['m']
    return ET.tostring(root, encoding='utf-8').decode('utf-8')

@app.route('/<path:file_name>', methods=['GET'])
def get_danmaku(file_name):
    match_url = "https://api.dandanplay.net/api/v2/match"
    match_payload = {
        "fileName": file_name,
        "fileHash": FILE_HASH,
        "fileSize": 0,
        "videoDuration": 0,
        "matchMode": "hashAndFileName"
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(match_url, json=match_payload, headers=headers)
    response.raise_for_status()
    match_result = response.json()
    episode_id = match_result['matches'][0]['episodeId']
    danmaku_url = f"https://api.dandanplay.net/api/v2/comment/{episode_id}?withRelated=true&chConvert=1"
    danmaku_response = requests.get(danmaku_url)
    danmaku_response.raise_for_status()
    xml_data = convert_danmaku_json_to_xml(danmaku_response.text)
    return xml_data, 200, {'Content-Type': 'application/xml'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=11001, debug=True)
