# Google Docs, Sheets & Drive: Acesso Direto


> **REQUISITO EXTERNO:** os scripts `~/.claude/scripts/google-api.sh` e `google-oauth-capture.py` NAO acompanham este repo. Sem eles instalados e autenticados na maquina, esta integracao NAO funciona: pular e pedir o conteudo do documento ao usuario (colar texto / exportar PDF).
Acesso autenticado ao Google Docs, Sheets e Drive do usuario via OAuth2. Usar para ler conteudo de documentos, planilhas, e listar/buscar arquivos no Drive.

### Setup

Credenciais e tokens ficam em:
- `~/.claude/google-credentials.json`: Client ID + Secret
- `~/.claude/google-tokens.json`: Access token + Refresh token (auto-refresh)
- `~/.claude/scripts/google-api.sh`: Script helper principal
- `~/.claude/scripts/google-oauth-capture.py`: Servidor OAuth para reautorizacao

### Comandos Disponiveis

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

### Workflow: Usuario Pede pra Acessar um Documento

1. **Se o usuario manda um link**: extrair o ID da URL e usar `google-api.sh doc <ID>` ou `sheet <ID>`
2. **Se o usuario pede pra listar**: usar `google-api.sh list` ou `google-api.sh list "filtro"`
3. **Se o usuario pede pra buscar conteudo**: usar `google-api.sh search "termo"`
4. **Se token expirar (erro 401 persistente)**: rodar reautorizacao:
   ```bash
   lsof -ti:8080 | xargs kill -9 2>/dev/null
   python3 ~/.claude/scripts/google-oauth-capture.py &
   # Abrir URL no navegador:
   open "https://accounts.google.com/o/oauth2/v2/auth?client_id=SEU_CLIENT_ID.apps.googleusercontent.com&redirect_uri=http://localhost:8080&response_type=code&scope=https%3A//www.googleapis.com/auth/documents.readonly%20https%3A//www.googleapis.com/auth/spreadsheets.readonly%20https%3A//www.googleapis.com/auth/drive.readonly&access_type=offline&prompt=consent"
   # Depois trocar o code por token via curl POST
   ```

### Casos de Uso na Skill

- **Ler briefing/copy de uma pagina** que o usuario escreveu no Google Docs
- **Ler planilha de conteudo** (textos, precos, features) pra montar secoes da pagina
- **Buscar documentos de referencia** no Drive sem o usuario precisar copiar/colar
- **Importar dados de planilhas** pra popular componentes dinamicos (testimonials, FAQ, etc.)

### APIs Utilizadas

| API | Endpoint | Uso |
|-----|----------|-----|
| Google Drive v3 | `GET /drive/v3/files` | Listar e buscar arquivos |
| Google Drive v3 | `GET /drive/v3/files/{id}/export` | Exportar Doc como texto |
| Google Sheets v4 | `GET /spreadsheets/{id}` | Metadata da planilha |
| Google Sheets v4 | `GET /spreadsheets/{id}/values/{range}` | Ler dados de aba |
| Google Docs v1 | `GET /documents/{id}` | Ler estrutura do documento (JSON) |

### Notas Tecnicas

- **Auto-refresh**: o script detecta HTTP 401 e renova o token automaticamente usando o refresh_token
- **App publicado em producao**: se o app Google Cloud estiver publicado (nao em modo teste), o refresh_token nao expira. Se receber erro 401 persistente apos refresh, rodar reautorizacao completa (ver workflow acima).
- **Projeto Google Cloud**: usar o seu proprio projeto Google Cloud (configurar OAuth client)
- **Redirect URI cadastrado**: `http://localhost:8080`
- **Scopes**: `documents.readonly`, `spreadsheets.readonly`, `drive.readonly` (somente leitura)

---
