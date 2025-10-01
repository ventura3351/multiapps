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
CORS(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response

class BrowserManager:
    def __init__(self):
        self.active_drivers = []
    
    def setup_chrome(self):
    """Configura Chrome com múltiplas tentativas"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Tentativa 1: Chrome padrão
    try:
        driver = webdriver.Chrome(options=chrome_options)
        logging.info("✅ Chrome iniciado com sucesso (Método 1)")
        return driver
    except Exception as e1:
        logging.warning(f"⚠️ Método 1 falhou: {e1}")
        
        # Tentativa 2: Com Service
        try:
            service = Service()
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logging.info("✅ Chrome iniciado com sucesso (Método 2)")
            return driver
        except Exception as e2:
            logging.error(f"❌ Todos os métodos falharam: {e2}")
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
            logging.info(f"Iniciando navegador para: {url}")
            
            # Usar Chrome configurado
            driver = self.setup_chrome()
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            driver.get(url)
            time.sleep(3)
            
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
                    
                except Exception as e:
                    logging.warning(f"Erro ao adicionar cookie: {e}")
                    continue
            
            driver.refresh()
            time.sleep(5)
            
            self.active_drivers.append(driver)
            
            return {
                "success": True,
                "cookies_added": cookies_adicionados,
                "detected_url": url,
                "current_url": driver.current_url,
                "message": "Navegador aberto com sucesso!"
            }
            
        except Exception as e:
            logging.error(f"Erro crítico: {str(e)}")
            if driver:
                driver.quit()
            return {"success": False, "error": str(e)}

browser_manager = BrowserManager()

@app.route('/')
def index():
    return jsonify({
        "status": "online", 
        "message": "Servidor MULTIAPPS API - Heroku",
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
        return jsonify({"status": "ok"})
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Dados JSON são obrigatórios"})
        
        cookies = data.get('cookies')
        if not cookies:
            return jsonify({"success": False, "error": "Cookies são obrigatórios"})
        
        result = browser_manager.open_authenticated_browser(cookies)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/load-cookies/<service>')
def load_cookies(service):
    try:
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
            
        return jsonify({
            "success": True,
            "cookies": cookies_text,
            "service_name": service,
            "message": f"Cookies carregados: {service}"
        })
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/status')
def status():
    return jsonify({
        "status": "online", 
        "active_browsers": len(browser_manager.active_drivers),
        "server": "MULTIAPPS API - Heroku",
        "timestamp": time.time()
    })

@app.route('/api/test-connection')
def test_connection():
    return jsonify({
        "success": True,
        "message": "✅ Conexão estabelecida com sucesso!",
        "server": "Heroku - MULTIAPPS",
        "client_ip": request.remote_addr,
        "timestamp": time.time()
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "multiapps-api"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print("🚀 Servidor MULTIAPPS iniciando no Heroku...")
    print(f"📍 Porta: {port}")
    print("🌐 Domínio: meusdownloads.com/mobile")
    print("📊 Endpoints disponíveis:")
    print("   /api/status")
    print("   /api/test-connection")
    print("   /api/load-cookies/<service>")
    print("   /api/open-browser")
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
