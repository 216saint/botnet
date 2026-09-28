#!/bin/bash
# Setup script para Lab Botnet v2.0
# Este script configura o ambiente para executar o botnet

set -e

echo "=== Lab Botnet v2.0 - Setup ==="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] Python 3 não encontrado. Por favor, instale Python 3.8+${NC}"
    exit 1
fi

echo -e "${GREEN}[✓] Python encontrado: $(python3 --version)${NC}"
echo ""

# Criar virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}[*] Criando virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}[✓] Virtual environment criado${NC}"
else
    echo -e "${GREEN}[✓] Virtual environment já existe${NC}"
fi

# Ativar virtual environment
source venv/bin/activate

# Instalar dependências
echo ""
echo -e "${YELLOW}[*] Instalando dependências...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}[✓] Dependências instaladas${NC}"

# Criar arquivos de configuração
echo ""
echo -e "${YELLOW}[*] Configurando arquivos sensíveis...${NC}"

if [ ! -f "proxies.json" ] && [ -f "proxies.example.json" ]; then
    cp proxies.example.json proxies.json
    echo -e "${GREEN}[✓] proxies.json criado (use o template como referência)${NC}"
fi

if [ ! -f "attacks.json" ] && [ -f "attacks.example.json" ]; then
    cp attacks.example.json attacks.json
    echo -e "${GREEN}[✓] attacks.json criado (use o template como referência)${NC}"
fi

if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
C2_HOST=localhost
C2_PORT=8000
C2_SECRET=seu-secret-key-aqui
DB_URL=sqlite:///./botnet.db
EOF
    echo -e "${GREEN}[✓] .env criado${NC}"
fi

echo ""
echo -e "${GREEN}=== Setup Completo! ===${NC}"
echo ""
echo "Próximos passos:"
echo "1. Edite os arquivos de configuração:"
echo "   - proxies.json (suas proxies)"
echo "   - attacks.json (suas configurações de ataque)"
echo "   - .env (variáveis de ambiente)"
echo ""
echo "2. Execute o servidor:"
echo "   cd c2_server && python -m uvicorn app:app --host 0.0.0.0 --port 8000"
echo ""
echo "3. Em outro terminal, execute o bot agent:"
echo "   cd bot_agent && python agent.py"
echo ""
echo "4. Em um terceiro terminal, use a CLI:"
echo "   cd cli_control && python cli.py"
echo ""
