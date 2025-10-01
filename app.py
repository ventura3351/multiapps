from flask import Flask, jsonify, request
import json
import requests
import logging

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "online", "message": "API MULTIAPPS"})

@app.route('/api/status')
def status():
    return jsonify({"status": "online", "server": "Heroku"})

@app.route('/api/test-connection')
def test_connection():
    return jsonify({"success": True, "message": "✅ Conexão OK!"})

@app.route('/api/load-cookies/<service>')
def load_cookies(service):
    try:
        service_urls = {
            'canvapro': 'https://meusdownloads.com/multiapp/licenca/canvapro.txt',
            'capcutpro': 'https://meusdownloads.com/multiapp/licenca/capcutpro.txt'
        }
        
        if service not in service_urls:
            return jsonify({"success": False, "error": "Serviço não encontrado"})
        
        response = requests.get(service_urls[service])
        cookies_text = response.text.strip()
        
        return jsonify({
            "success": True,
            "cookies": cookies_text,
            "service": service
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/open-browser', methods=['POST'])
def open_browser():
    return jsonify({
        "success": True, 
        "message": "Navegador seria aberto aqui",
        "test": "Funcionando!"
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
