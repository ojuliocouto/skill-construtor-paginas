# Google Docs, Sheets & Drive: Acesso Direto


> **REQUISITO EXTERNO:** os scripts `~/.claude/scripts/google-api.sh` e `google-oauth-capture.py` NÃO acompanham este repo. Sem eles instalados e autenticados na máquina, esta integração NÃO funciona: pular e pedir o conteúdo do documento ao usuário (colar texto / exportar PDF).
Acesso autenticado ao Google Docs, Sheets e Drive do usuário via OAuth2. Usar para ler conteúdo de documentos, planilhas, e listar/buscar arquivos no Drive.

### Setup

Credenciais e tokens ficam em:
- `~/.claude/google-credentials.json`: Client ID + Secret
- `~/.claude/google-tokens.json`: Access token + Refresh token (auto-refresh)
- `~/.claude/scripts/google-api.sh`: Script helper principal
- `~/.claude/scripts/google-oauth-capture.py`: Servidor OAuth para reautorização

### Comandos Disponíveis

```bash
# Listar 20 arquivos mais recentes do Google Drive
bash ~/.claude/scripts/google-api.sh list

# Filtrar por nome
bash ~/.claude/scripts/google-api.sh list "Mentoria"

# Busca full-text no Drive (busca dentro do conteudo dos arquivos)
bash ~/.claude/scripts/google-api.sh search "programa aceleração"

# Ler Google Doc como texto puro (ideal pra copiar conteudo)
bash ~/.claude/scripts/google-api.sh doc <DOC_ID>

# Ver metadata de Google Sheet (lista abas disponiveis)
bash ~/.claude/scripts/google-api.sh sheet <SHEET_ID>

# Ler aba especifica de uma planilha
bash ~/.claude/scripts/google-api.sh sheet <SHEET_ID> "Nome da Aba"

# Renovar token manualmente (normalmente automatico)
bash ~/.claude/scripts/google-api.sh refresh
```

### Como Extrair o ID do Documento

De qualquer URL do Google Docs/Sheets/Drive, o ID e a parte entre `/d/` e `/edit`:

```
https://docs.google.com/document/d/SEU_DOC_ID_AQUI/edit
                                    ^^^^^^^^^^^^^^^
                                    Este e o DOC_ID
```

### Workflow: Usuário Pede pra Acessar um Documento

1. **Se o usuário manda um link**: extrair o ID da URL e usar `google-api.sh doc <ID>` ou `sheet <ID>`
2. **Se o usuário pede pra listar**: usar `google-api.sh list` ou `google-api.sh list "filtro"`
3. **Se o usuário pede pra buscar conteúdo**: usar `google-api.sh search "termo"`
4. **Se token expirar (erro 401 persistente)**: rodar reautorização:
   ```bash
   # Se algo já usa a porta 8080, feche o programa antes (Windows: netstat -ano | findstr :8080 e taskkill /PID <número> /F).
   node <dir-da-skill>/scripts/py.mjs ~/.claude/scripts/google-oauth-capture.py   # deixe rodando num segundo terminal
   # Abrir no navegador (macOS: open, Windows: start, Linux: xdg-open) a URL:
   "https://accounts.google.com/o/oauth2/v2/auth?client_id=SEU_CLIENT_ID.apps.googleusercontent.com&redirect_uri=http://localhost:8080&response_type=code&scope=https%3A//www.googleapis.com/auth/documents.readonly%20https%3A//www.googleapis.com/auth/spreadsheets.readonly%20https%3A//www.googleapis.com/auth/drive.readonly&access_type=offline&prompt=consent"
   # Depois trocar o code por token via curl POST
   ```

### Casos de Uso na Skill

- **Ler briefing/copy de uma página** que o usuário escreveu no Google Docs
- **Ler planilha de conteúdo** (textos, preços, features) pra montar seções da página
- **Buscar documentos de referência** no Drive sem o usuário precisar copiar/colar
- **Importar dados de planilhas** pra popular componentes dinâmicos (testimonials, FAQ, etc.)

### APIs Utilizadas

| API | Endpoint | Uso |
|-----|----------|-----|
| Google Drive v3 | `GET /drive/v3/files` | Listar e buscar arquivos |
| Google Drive v3 | `GET /drive/v3/files/{id}/export` | Exportar Doc como texto |
| Google Sheets v4 | `GET /spreadsheets/{id}` | Metadata da planilha |
| Google Sheets v4 | `GET /spreadsheets/{id}/values/{range}` | Ler dados de aba |
| Google Docs v1 | `GET /documents/{id}` | Ler estrutura do documento (JSON) |

### Notas Técnicas

- **Auto-refresh**: o script detecta HTTP 401 e renova o token automaticamente usando o refresh_token
- **App publicado em produção**: se o app Google Cloud estiver publicado (não em modo teste), o refresh_token não expira. Se receber erro 401 persistente após refresh, rodar reautorização completa (ver workflow acima).
- **Projeto Google Cloud**: usar o seu próprio projeto Google Cloud (configurar OAuth client)
- **Redirect URI cadastrado**: `http://localhost:8080`
- **Scopes**: `documents.readonly`, `spreadsheets.readonly`, `drive.readonly` (somente leitura)

---
