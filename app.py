from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import requests
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# CORS CONFIGURADO CORRETAMENTE
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://meusdownloads.com",
            "https://www.meusdownloads.com", 
            "https://meusdownloads.com/mobile",
            "http://localhost:3000",
            "http://127.0.0.1:5000"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
    }
})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://meusdownloads.com')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

class BrowserManager:
    def __init__(self):
        self.active_sessions = []
    
    def open_authenticated_browser(self, cookies_json, service_name):
        """Versão simplificada - retorna instruções para o usuário"""
        try:
            # Extrair domínio dos cookies
            cookies = json.loads(cookies_json)
            domains = {}
            for cookie in cookies:
                domain = cookie.get('domain', '').strip().lstrip('.')
                if domain:
                    domains[domain] = domains.get(domain, 0) + 1
            
            main_domain = max(domains, key=domains.get) if domains else "www.canva.com"
            url = f"https://{main_domain}"
            
            logging.info(f"🔑 Autenticação solicitada para: {service_name}")
            logging.info(f"🌐 URL: {url}")
            logging.info(f"🍪 Cookies carregados: {len(cookies)}")
            
            self.active_sessions.append({
                "service": service_name,
                "url": url,
                "timestamp": time.time()
            })
            
            return {
                "success": True,
                "service": service_name,
                "url": url,
                "cookies_count": len(cookies),
                "message": "✅ Pronto para autenticação!",
                "instructions": [
                    "1. O site será aberto em uma nova janela",
                    "2. Use a extensão Cookie-Editor para injetar os cookies",
                    "3. Recarregue a página para acessar sua conta premium"
                ],
                "action": "open_url",
                "target_url": url
            }
            
        except Exception as e:
            logging.error(f"❌ Erro na autenticação: {str(e)}")
            return {"success": False, "error": str(e)}

browser_manager = BrowserManager()

@app.route('/')
def index():
    return jsonify({
        "status": "online", 
        "message": "🚀 Servidor MULTIAPPS API - Heroku",
        "version": "2.0 - Modo Instruções",
        "endpoints": {
            "status": "/api/status",
            "test": "/api/test-connection", 
            "load_cookies": "/api/load-cookies/<service>",
            "open_browser": "/api/open-browser"
        }
    })

@app.route('/api/open-browser', methods=['POST', 'OPTIONS'])
def open_browser():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Dados JSON são obrigatórios"})
        
        cookies = data.get('cookies')
        service_name = data.get('service_name', 'Serviço')
        
        if not cookies:
            return jsonify({"success": False, "error": "Cookies são obrigatórios"})
        
        logging.info(f"🔄 Recebida requisição para: {service_name}")
        result = browser_manager.open_authenticated_browser(cookies, service_name)
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"❌ Erro na API open-browser: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/load-cookies/<service>')
def load_cookies(service):
    try:
        logging.info(f"📥 Carregando cookies para: {service}")
        
        service_urls = {
            'arteseditaveis': 'https://meusdownloads.com/multiapp/licenca/arteseditaveis.txt',
            'capcutpro': 'https://meusdownloads.com/multiapp/licenca/capcutpro.txt',
            'canvapro': 'https://meusdownloads.com/multiapp/licenca/canvapro.txt',
            'chatgpt-conta1': 'https://meusdownloads.com/multiapp/licenca/chatgpt-conta1.txt',
            'chatgpt-conta2': 'https://meusdownloads.com/multiapp/licenca/chatgpt-conta2.txt',
            'leonardoai': 'https://meusdownloads.com/multiapp/licenca/leonardoai.txt',
            'freepik-conta1': 'https://meusdownloads.com/multiapp/licenca/freepik-conta1.txt',
            'freepik-conta2': 'https://meusdownloads.com/multiapp/licenca/freepik-conta2.txt',
            'freepik-conta3': 'https://meusdownloads.com/multiapp/licenca/freepik-conta3.txt',
            'sora': 'https://meusdownloads.com/multiapp/licenca/sora.txt',
            'vectorizer': 'https://meusdownloads.com/multiapp/licenca/vectorizer.txt',
            'envato': 'https://meusdownloads.com/multiapp/licenca/envato.txt'
        }
        
        if service not in service_urls:
            return jsonify({"success": False, "error": "Serviço não encontrado"})
        
        response = requests.get(service_urls[service], timeout=10)
        response.raise_for_status()
        
        cookies_text = response.text.strip()
        
        if not cookies_text:
            return jsonify({"success": False, "error": "Arquivo vazio"})
        
        # Validar JSON
        cookies_data = json.loads(cookies_text)
        
        # Detectar URL do serviço
        service_urls_map = {
            'canvapro': 'https://www.canva.com',
            'capcutpro': 'https://www.capcut.com',
            'chatgpt-conta1': 'https://chat.openai.com',
            'chatgpt-conta2': 'https://chat.openai.com',
            'leonardoai': 'https://leonardo.ai',
            'freepik-conta1': 'https://www.freepik.com',
            'freepik-conta2': 'https://www.freepik.com',
            'freepik-conta3': 'https://www.freepik.com',
            'sora': 'https://openai.com/sora',
            'vectorizer': 'https://vectorizer.ai',
            'envato': 'https://elements.envato.com'
        }
        
        target_url = service_urls_map.get(service, 'https://www.canva.com')
        
        logging.info(f"✅ Cookies carregados: {service} -> {target_url}")
            
        return jsonify({
            "success": True,
            "cookies": cookies_text,
            "service_name": service,
            "target_url": target_url,
            "cookies_count": len(cookies_data),
            "message": f"✅ Cookies de {service} carregados!",
            "instructions": "Use a extensão Cookie-Editor para injetar estes cookies"
        })
            
    except Exception as e:
        logging.error(f"❌ Erro ao carregar cookies: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/status')
def status():
    return jsonify({
        "status": "online", 
        "active_sessions": len(browser_manager.active_sessions),
        "server": "MULTIAPPS API - Heroku",
        "mode": "instructions_mode",
        "cors_enabled": True,
        "timestamp": time.time()
    })

@app.route('/api/test-connection')
def test_connection():
    return jsonify({
        "success": True,
        "message": "✅ Conexão estabelecida com sucesso!",
        "server": "Heroku - MULTIAPPS",
        "mode": "Modo Instruções - Sem Chrome",
        "timestamp": time.time()
    })

@app.route('/api/cors-test')
def cors_test():
    return jsonify({
        "success": True,
        "message": "✅ CORS test - Funcionando!",
        "cors_configured": True
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "multiapps-api"})

if __name__ == '__main__':
    import time
    port = int(os.environ.get("PORT", 5000))
    print("🚀 Servidor MULTIAPPS iniciando no Heroku...")
    print("📍 MODO: Instruções (Sem Chrome)")
    print("🌐 Domínio: meusdownloads.com/mobile")
    print("🔧 CORS Configurado para: https://meusdownloads.com")
    print("📊 Endpoints disponíveis:")
    print("   /api/status")
    print("   /api/load-cookies/<service>")
    print("   /api/open-browser")
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
