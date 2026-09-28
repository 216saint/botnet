# Setup script para Lab Botnet v2.0 (Windows PowerShell)
# Este script configura o ambiente para executar o botnet

Write-Host "=== Lab Botnet v2.0 - Setup ===" -ForegroundColor Green
Write-Host ""

# Verificar se Python está instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[✓] Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[!] Python não encontrado. Por favor, instale Python 3.8+" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Criar virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "[*] Criando virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "[✓] Virtual environment criado" -ForegroundColor Green
} else {
    Write-Host "[✓] Virtual environment já existe" -ForegroundColor Green
}

# Ativar virtual environment
Write-Host "[*] Ativando virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "[✓] Virtual environment ativado" -ForegroundColor Green

# Instalar dependências
Write-Host ""
Write-Host "[*] Instalando dependências..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Write-Host "[✓] Dependências instaladas" -ForegroundColor Green

# Criar arquivos de configuração
Write-Host ""
Write-Host "[*] Configurando arquivos sensíveis..." -ForegroundColor Yellow

if ((-not (Test-Path "proxies.json")) -and (Test-Path "proxies.example.json")) {
    Copy-Item proxies.example.json proxies.json
    Write-Host "[✓] proxies.json criado (use o template como referência)" -ForegroundColor Green
}

if ((-not (Test-Path "attacks.json")) -and (Test-Path "attacks.example.json")) {
    Copy-Item attacks.example.json attacks.json
    Write-Host "[✓] attacks.json criado (use o template como referência)" -ForegroundColor Green
}

if (-not (Test-Path ".env")) {
    @"
C2_HOST=localhost
C2_PORT=8000
C2_SECRET=seu-secret-key-aqui
DB_URL=sqlite:///./botnet.db
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "[✓] .env criado" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Setup Completo! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:"
Write-Host "1. Edite os arquivos de configuração:"
Write-Host "   - proxies.json (suas proxies)"
Write-Host "   - attacks.json (suas configurações de ataque)"
Write-Host "   - .env (variáveis de ambiente)"
Write-Host ""
Write-Host "2. Execute o servidor em um terminal:"
Write-Host "   cd c2_server; python -m uvicorn app:app --host 0.0.0.0 --port 8000"
Write-Host ""
Write-Host "3. Em outro terminal, execute o bot agent:"
Write-Host "   cd bot_agent; python agent.py"
Write-Host ""
Write-Host "4. Em um terceiro terminal, use a CLI:"
Write-Host "   cd cli_control; python cli.py"
Write-Host ""
