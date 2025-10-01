from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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
            "http://127.0.0.1:5000",
            "https://meusdownloads-multiapps-386c5337f064.herokuapp.com"
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
    response.headers.add('Access-Control-Max-Age', '86400')
    return response

class BrowserManager:
    def __init__(self):
        self.active_drivers = []
    
    def setup_chrome(self):
        """Configuração simplificada para Heroku"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logging.info("✅ Chrome iniciado com sucesso")
            return driver
        except Exception as e:
            logging.error(f"❌ Erro ao iniciar Chrome: {str(e)}")
            return None
    
    def extract_domain_from_cookies(self, cookies_json):
        try:
            cookies = json.loads(cookies_json)
            if not cookies:
                return "https://www.canva.com"
            
            domains = {}
            for cookie in cookies:
                domain = cookie.get('domain', '').strip()
                if domain:
                    clean_domain = domain.lstrip('.')
                    if clean_domain:
                        domains[clean_domain] = domains.get(clean_domain, 0) + 1
            
            if domains:
                main_domain = max(domains, key=domains.get)
                return f"https://{main_domain}"
            else:
                return "https://www.canva.com"
                    
        except Exception as e:
            logging.error(f"Erro ao extrair domínio: {e}")
            return "https://www.canva.com"
    
    def open_authenticated_browser(self, cookies_json):
        driver = None
        try:
            url = self.extract_domain_from_cookies(cookies_json)
            logging.info(f"🌐 Iniciando navegador para: {url}")
            
            driver = self.setup_chrome()
            if not driver:
                return {"success": False, "error": "Não foi possível iniciar o navegador"}
            
            driver.get(url)
            time.sleep(2)
            
            try:
                cookies = json.loads(cookies_json)
            except Exception as e:
                if driver:
                    driver.quit()
                return {"success": False, "error": f"Erro nos cookies: {str(e)}"}
            
            driver.delete_all_cookies()
            time.sleep(1)
            
            cookies_adicionados = 0
            for cookie in cookies:
                try:
                    cookie_dict = {
                        'name': str(cookie.get('name', '')),
                        'value': str(cookie.get('value', '')),
                        'domain': cookie.get('domain', ''),
                        'path': cookie.get('path', '/'),
                        'secure': cookie.get('secure', False)
                    }
                    
                    if 'expirationDate' in cookie:
                        cookie_dict['expiry'] = int(cookie['expirationDate'])
                    
                    driver.add_cookie(cookie_dict)
                    cookies_adicionados += 1
                    logging.info(f"🍪 Cookie adicionado: {cookie_dict['name']}")
                    
                except Exception as e:
                    logging.warning(f"⚠️ Erro ao adicionar cookie: {e}")
                    continue
            
            driver.refresh()
            time.sleep(3)
            
            self.active_drivers.append(driver)
            
            return {
                "success": True,
                "cookies_added": cookies_adicionados,
                "detected_url": url,
                "current_url": driver.current_url,
                "message": "Navegador aberto com sucesso!"
            }
            
        except Exception as e:
            logging.error(f"❌ Erro crítico: {str(e)}")
            if driver:
                driver.quit()
            return {"success": False, "error": str(e)}

browser_manager = BrowserManager()

@app.route('/')
def index():
    return jsonify({
        "status": "online", 
        "message": "🚀 Servidor MULTIAPPS API - Heroku",
        "endpoints": {
            "status": "/api/status",
            "test": "/api/test-connection", 
            "load_cookies": "/api/load-cookies/<service>",
            "open_browser": "/api/open-browser"
        },
        "cors": {
            "allowed_origins": ["https://meusdownloads.com", "https://www.meusdownloads.com"],
            "status": "configured"
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
        if not cookies:
            return jsonify({"success": False, "error": "Cookies são obrigatórios"})
        
        logging.info("🔄 Recebida requisição para abrir navegador")
        result = browser_manager.open_authenticated_browser(cookies)
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
        json.loads(cookies_text)
        
        logging.info(f"✅ Cookies carregados com sucesso para {service}")
            
        return jsonify({
            "success": True,
            "cookies": cookies_text,
            "service_name": service,
            "message": f"Cookies carregados: {service}"
        })
            
    except Exception as e:
        logging.error(f"❌ Erro ao carregar cookies: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/status')
def status():
    return jsonify({
        "status": "online", 
        "active_browsers": len(browser_manager.active_drivers),
        "server": "MULTIAPPS API - Heroku",
        "cors_enabled": True,
        "allowed_origin": "https://meusdownloads.com",
        "timestamp": time.time()
    })

@app.route('/api/test-connection')
def test_connection():
    return jsonify({
        "success": True,
        "message": "✅ Conexão estabelecida com sucesso!",
        "server": "Heroku - MULTIAPPS",
        "cors": "Configurado para meusdownloads.com",
        "client_ip": request.remote_addr,
        "timestamp": time.time()
    })

@app.route('/api/cors-test')
def cors_test():
    return jsonify({
        "success": True,
        "message": "✅ CORS test - Deve funcionar do meusdownloads.com",
        "cors_configured": True,
        "allowed_origins": ["https://meusdownloads.com", "https://www.meusdownloads.com"]
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy", 
        "service": "multiapps-api",
        "timestamp": time.time()
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print("🚀 Servidor MULTIAPPS iniciando no Heroku...")
    print(f"📍 Porta: {port}")
    print("🌐 Domínio: meusdownloads.com/mobile")
    print("🔧 CORS Configurado para: https://meusdownloads.com")
    print("📊 Endpoints disponíveis:")
    print("   /api/status")
    print("   /api/test-connection")
    print("   /api/load-cookies/<service>")
    print("   /api/open-browser")
    print("   /api/cors-test")
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
