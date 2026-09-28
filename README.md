# Lab Botnet v2.0

Um projeto educacional de pesquisa de segurança que implementa um botnet com C2 (Command and Control) server em Python/FastAPI, agentes bot independentes e interface CLI.

> ⚠️ **Aviso Legal**: Este projeto é apenas para fins educacionais e de pesquisa em ambientes controlados. Uso não autorizado pode violar leis.

## Configuração Rápida

### 1. Clonar o Repositório

```bash
git clone <seu-repositorio>
cd lab-botnet
```

### 2. Configurar Arquivos Sensíveis

Os seguintes arquivos devem ser criados localmente (estão no `.gitignore` por segurança):

#### `proxies.json` - Lista de Proxies
Use o exemplo fornecido como template:
```bash
cp proxies.example.json proxies.json
# Edite proxies.json com suas proxies
```

#### `attacks.json` - Configuração de Ataques
Use o exemplo fornecido como template:
```bash
cp attacks.example.json attacks.json
# Edite attacks.json com suas configurações
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

## Documentação

- **[QUICKSTART.md](QUICKSTART.md)** - Guia rápido de primeiros passos
- **[TECHNICAL_SUMMARY.md](TECHNICAL_SUMMARY.md)** - Arquitetura técnica detalhada
- **[CHANGELOG.md](CHANGELOG.md)** - Histórico de versões

## Estrutura do Projeto

```
lab-botnet/
├── c2_server/           # Servidor de Comando e Controle (FastAPI)
├── bot_agent/           # Agente Bot (cliente)
├── cli_control/         # Interface de Linha de Comando
├── .gitignore          # Arquivos ignorados (sensíveis)
├── docker-compose.yml   # Orquestração Docker
└── README.md           # Este arquivo
```

## Arquivos Ignorados (Segurança)

Os seguintes arquivos são ignorados pelo Git por conterem dados sensíveis:

- `proxies.json` - Lista de proxies pessoal
- `proxies.txt` - Lista de proxies em formato texto
- `attacks.json` - Configurações de ataques
- `.env` - Variáveis de ambiente
- `*.key`, `*.pem`, `*.crt` - Chaves privadas e certificados
- `__pycache__/`, `*.pyc` - Cache Python

**Nunca commite estes arquivos!** Use os arquivos `.example` como templates.

## Requisitos

- Python 3.8+
- Docker & Docker Compose (opcional)
- pip/virtualenv

## Licença

Educacional - Use responsavelmente.

## Contribuindo

Contribuições são bem-vindas! Por favor:
1. Não inclua dados sensíveis nos commits
2. Use os templates `.example` para configurações
3. Siga as diretrizes de segurança

---

Desenvolvido como projeto de pesquisa em segurança.
