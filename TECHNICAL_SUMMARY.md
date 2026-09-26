# 📋 Resumo Técnico - Botnet v2.0

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Control (cli.py)                 │
│  - Menu interativo                                      │
│  - Adiciona até 5 requisições                           │
│  - Monitoramento automático e contínuo                  │
│  - Teste de acessibilidade automático                   │
│  - Relatório de efetividade                             │
└─────────────────┬───────────────────────────────────────┘
                  │ POST /admin/send_command
                  │ GET /get_attack_status
                  │
┌─────────────────▼───────────────────────────────────────┐
│                C2 Server (app.py)                       │
│  - Gerencia fila de tarefas                             │
│  - Rastreia ataques com UUID único                      │
│  - Armazena logs em memória (últimos 50)                │
│  - Endpoints de status de ataque                        │
└─────────────────┬───────────────────────────────────────┘
                  │ GET /get_task/<bot_id>
                  │ POST /report_attack_status
                  │ POST /finish_attack
                  │
┌─────────────────▼───────────────────────────────────────┐
│              Bot Agent (agent.py) [x N]                 │
│  - Loop infinito aguardando tarefas                     │
│  - Executa múltiplas requisições em paralelo            │
│  - Conta sucessos/falhas                                │
│  - Reporta progresso ao C2                              │
└─────────────────────────────────────────────────────────┘
```

## Mudanças Principais

### 1. C2 Server (app.py)

#### Novo Dicionário de Ataques
```python
botnet_state["attacks"] = {
    "attack-uuid": {
        "status": "running|completed",
        "requests_sent": 0,
        "requests_successful": 0,
        "requests_failed": 0,
        "num_requests": 5,
        "start_time": "HH:MM:SS",
        "end_time": "HH:MM:SS"
    }
}
```

#### Novos Endpoints
```
POST /admin/send_command
- Cria novo ataque com UUID
- Retorna: attack_id

POST /report_attack_status
- Atualiza contadores de sucesso/falha

GET /get_attack_status/<attack_id>
- Retorna status atual do ataque

POST /finish_attack
- Marca ataque como concluído
```

### 2. Bot Agent (agent.py)

#### Função attack_task() Modificada
```python
async def attack_task(session, request_config):
    # request_config = {
    #     "url": "http://...",
    #     "method": "GET|POST|PUT",
    #     "headers": {...},
    #     "body": "..."
    # }
```

**Mudanças:**
- ✅ Suporta GET, POST, PUT
- ✅ Headers customizados por requisição
- ✅ Body customizado
- ✅ Mantém user-agents aleatórios

#### Função flood_target() Modificada
```python
async def flood_target(requests_list, intensity, attack_id):
    # requests_list = lista de até 5 requisições
    # intensity = quantas vezes executar cada uma
    # Executa em paralelo com asyncio.gather()
```

**Mudanças:**
- ✅ Aceita lista de requisições
- ✅ Executa cada lote em paralelo
- ✅ Conta sucessos/falhas por HTTP status
- ✅ Retorna estatísticas detalhadas
- ✅ Reporta ao C2

#### Loop Main Modificado
```python
order = {
    "action": "flood",
    "requests": [...],
    "intensity": 100,
    "attack_id": "uuid"
}
# Bot reporta progresso via:
# POST /report_attack_status
# POST /finish_attack
```

### 3. CLI (cli.py)

#### Novo Menu de Requisições
```python
def add_request():
    # Coleta: URL, método, headers, body
    # Valida método HTTP
    # Retorna dict com config
```

#### Novo Monitoramento Automático
```python
def monitor_attack(attack_id, target_url):
    # Loop contínuo com GET /get_attack_status
    # Atualiza a cada 2 segundos
    # Aguarda até status = "completed"
    # Então inicia teste de acessibilidade
```

#### Novo Teste de Acessibilidade
```python
# Após ataque terminar:
1. GET http://target_url (timeout 10s)
2. Analisa status HTTP:
   - 200-299: ❌ Acessível = Efetividade 0%
   - 500+: ✓ Erro = Efetividade 100%
   - Timeout/ConnectionError: ✓ = Efetividade 100%
```

---

## Fluxo de Execução

### Cenário: Ataque com 3 Requisições, Intensidade 100

```
1. CLI: Coleta 3 requisições
   ├─ Req1: GET /api/users (sem body)
   ├─ Req2: POST /api/login (com body JSON)
   └─ Req3: PUT /api/config (com headers custom)

2. CLI: Envia POST /admin/send_command
   C2: Cria attack_id = "a1b2c3d4..."
   C2: Adiciona à fila

3. Bot: GET /get_task/<bot_id>
   C2: Retorna as 3 requisições + attack_id

4. Bot: Executa 100 iterações
   └─ Cada iteração: 3 requisições em paralelo = 3 tasks
   └─ Total: 300 requisições assíncronas
   └─ Conta: sucessos (HTTP 200-299) e falhas (HTTP 400+/timeout)

5. Bot: POST /report_attack_status com resultados
   C2: Atualiza contadores

6. Bot: POST /finish_attack
   C2: Marca como "completed"

7. CLI: Detecta status = "completed"
   CLI: Inicia teste GET http://target_url

8. CLI: Analisa resposta
   ├─ Se 200: "❌ Efetividade 0%"
   ├─ Se 500+: "✓ Efetividade 100%"
   └─ Se timeout/erro: "✓ Efetividade 100%"
```

---

## Métricas Rastreadas

### Por Ataque
```
- Total requisições enviadas
- Requisições bem-sucedidas (status 200-299)
- Requisições falhadas (status 400+, timeout)
- Tempo de início/fim
- Taxa de sucesso = bem-sucedidas / total
```

### Nos Logs
```
[HH:MM:SS] [bot-abc123] INICIANDO ATAQUE (ID: a1b2c3d4...) 
           com 3 requisição(ões) - Intensidade: 100

[HH:MM:SS] [bot-abc123] ATAQUE CONCLUÍDO (ID: a1b2c3d4...) 
           | Total: 300 | Sucesso: 298 | Falhas: 2
```

---

## Tratamento de Erros

### No Bot
```python
try:
    async with session.get(url, ...) as response:
        return response.status
except Exception:
    return None  # Contabilizado como falha
```

### Na CLI
```python
try:
    response = requests.get(target_url, timeout=10)
    # Analisa status_code
except requests.exceptions.Timeout:
    # Contado como sucesso do ataque
except requests.exceptions.ConnectionError:
    # Contado como sucesso do ataque
```

---

## Performance

### Asyncio
- Usa `aiohttp.TCPConnector(limit=None)` para sem limite
- `asyncio.gather()` para executar requisições em paralelo
- Aguarda todas as requisições antes de próxima iteração

### Exemplo
```
3 requisições × 100 intensidade = 300 requests
Com asyncio: ~30 iterações/segundo (dependendo da rede)
Tempo total: ~10 segundos
```

---

## Compatibilidade

- **Python:** 3.8+ (usa type hints, walrus operator removido)
- **Async:** aiohttp, asyncio
- **Web:** Flask
- **HTTP:** requests
- **Docker:** docker-compose v1.29+

---

## Segurança / Observações

1. **Sem validação de URL:** Aceita qualquer URL
2. **Headers arbitrários:** CLI aceita qualquer header JSON
3. **Body arbitrário:** Permite payload customizado
4. **Sem rate limiting:** C2 não limita requisições
5. **Sem autenticação:** CLI se conecta sem credenciais

Considere adicionar:
- Validação de URL (whitelist/blacklist)
- Autenticação no C2
- Rate limiting por bot
- Validação de headers (XSS prevention)

---

## Versão
- **v2.0** - 2026-09-26
- Primeira release com suporte a múltiplas requisições
