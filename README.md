# Botnet v1.0

botnet com C2 server em Python/FastAPI, agentes bot independentes e interface CLI.

## Configuração Rápida

### 1. Clonar o Repositório

```bash
git clone <seu-repositorio>
cd lab-botnet
```

### 2. Configurar Arquivos Sensíveis

Os seguintes arquivos devem ser criados localmente:

#### `proxies.json` - Lista de Proxies
Use o exemplo fornecido como template:
```bash
cp proxies.example.json proxies.json
```

#### `attacks.json` - Configuração de Ataques
Use o exemplo fornecido como template:
```bash
cp attacks.example.json attacks.json
```

#### Variáveis de Ambiente (`.env`)
```bash
cat > .env << 'EOF'
C2_HOST=localhost
C2_PORT=8000
C2_SECRET=sua-chave-secreta-aqui
DB_URL=sqlite:///./botnet.db
EOF
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Executar com Docker Compose

```bash
docker-compose up -d
```

Ou manualmente:
```bash
# Terminal 1: C2 Server
cd c2_server
python -m uvicorn app:app --host 0.0.0.0 --port 8000

# Terminal 2: Bot Agent
cd bot_agent
python agent.py

# Terminal 3: CLI Control
cd cli_control
python cli.py
```


## Requisitos

- Python 3.8+
- Docker & Docker Compose (opcional)
- pip/virtualenv


