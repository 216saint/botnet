# Botnet v2.0 - Changelog

## 🚀 Melhorias Implementadas

### 1. **Suporte a Múltiplas Requisições**
- Agora é possível enviar até **5 requisições diferentes** por ataque
- Cada requisição pode ter:
  - URL customizada
  - Método HTTP (GET, POST, PUT)
  - Headers customizados
  - Body/Payload customizado
- Os bots executam todas as 5 requisições **em paralelo** na mesma intensidade

### 2. **CLI Melhorada**
#### Menu de Requisições
- Assistente interativo para adicionar até 5 requisições
- Suporta métodos HTTP customizados
- Permite definir headers e payloads específicos
- Indicação clara do que foi configurado

#### Monitoramento Automático
- Após iniciar um ataque, a CLI **entra automaticamente em modo de monitoramento**
- Exibe em **tempo real**:
  - Total de requisições enviadas
  - Requisições bem-sucedidas
  - Requisições falhadas
  - Status do ataque
- Monitor aguarda até a conclusão do ataque

#### Teste de Acessibilidade
- Ao terminar o ataque, a CLI **testa automaticamente** se o site continua acessível
- Retorna relatório com:
  - **Status do site** (acessível ou indisponível)
  - **Código HTTP** recebido
  - **Tempo de resposta**
  - **Efetividade do ataque** (0% = sem efeito, 100% = site fora)

### 3. **Backend Melhorado (C2 Server)**
- Novo sistema de rastreamento de ataques com ID único
- Endpoints para:
  - `/report_attack_status` - Relatar progresso do ataque
  - `/get_attack_status/<attack_id>` - Obter status de um ataque
  - `/finish_attack` - Finalizar ataque
- Timestamps de início e fim de cada ataque

### 4. **Bot Agent Aprimorado**
- Suporte a diferentes métodos HTTP (GET, POST, PUT)
- Processamento de múltiplas requisições em paralelo
- Contagem de sucessos/falhas por ataque
- Relatório automático ao C2 ao final do ataque

---

## 📊 Exemplo de Uso

### Configuração de Ataque com 3 Requisições:

**Requisição 1 - GET com Headers customizados:**
```
URL: http://target.com/api/users
Método: GET
Headers: {"X-Attack": "test", "Authorization": "Bearer token"}
```

**Requisição 2 - POST com Payload:**
```
URL: http://target.com/api/auth/login
Método: POST
Body: {"username": "admin", "password": "test"}
```

**Requisição 3 - PUT:**
```
URL: http://target.com/api/config
Método: PUT
Body: {"setting": "value"}
```

### Fluxo de Execução:
1. ✅ Configurar as 3 requisições
2. ✅ Definir intensidade (ex: 100 = cada requisição executada 100 vezes)
3. ✅ Enviar comando ao C2
4. ✅ **Monitoramento automático inicia**
5. ✅ Aguarda conclusão dos 300 requests (3 requisições × 100 intensidade)
6. ✅ **Teste de acessibilidade**
7. ✅ **Relatório de efetividade**

---

## 🔧 Compatibilidade
- Python 3.8+ (por uso de walrus operator `:=`)
- Docker Compose
- Requer aiohttp, flask, requests

## 📝 Notas Importantes
- O monitoramento é **bloqueante** até o ataque terminar
- O teste de acessibilidade usa timeout de 10 segundos
- Headers customizados são **mesclados** com user-agents aleatórios
- Falhas são contadas como status HTTP >= 400 ou timeouts
