# Gabarito do facilitador — NAO distribuir aos participantes

Falhas plantadas na Loja Vulneravel, por categoria OWASP Top 10:2025.
As 11 primeiras sao as "principais" (batem com o slide da palestra). A
12a (path traversal) foi incluida para a Pratica 3.

| # | OWASP | Onde (funcao) | Falha |
|--:|-------|---------------|-------|
| 1 | A01 Broken Access Control | `ver_pedido` / `GET /pedidos/<id>` | IDOR: nao confere dono; confia em `pode_ver_pedido`, que falha aberta |
| 2 | A01 (SSRF) | `rastreio` / `GET /rastreio?url=` | Busca qualquer URL que o cliente informar |
| 3 | A02 Security Misconfig | `app.config` | `DEBUG=True` + `SECRET_KEY` fixa/padrao |
| 4 | A03 Supply Chain | `requirements.txt` | `Jinja2==3.1.3` com CVE conhecida (pip-audit aponta) |
| 5 | A04 Cryptographic | `init_db` / `login` | Senhas em **MD5** |
| 6 | A05 Injection | `listar_pedidos` / `GET /pedidos` | SQL montado com **f-string** |
| 7 | A06 Insecure Design | `aplicar_cupom` / `POST /cupom` | Cupom aplicavel infinitas vezes |
| 8 | A07 Auth Failures | `login` / `POST /login` | Sem limite de tentativas + mensagem revela se o e-mail existe |
| 9 | A08 Integrity Failures | `carregar_preferencias` / `POST /preferencias` | `pickle.loads` em dado do cliente |
| 10 | A09 Logging Failures | `login` | Tentativas falhas nao sao registradas |
| 11 | A10 Exceptional Conditions | `pode_ver_pedido` | Falha **aberta** (`except: return True`, CWE-636) + stack trace ao cliente (DEBUG) |
| 12 | A01 (path traversal) | `ver_comprovante` / `GET /comprovante?arquivo=` | Nome do arquivo usado direto, sem validar — le fora de `comprovantes/` |

## As tres falhas da Pratica 3 e as correcoes

### 1. Injecao de SQL (`listar_pedidos`)
**Robusta** — consulta parametrizada:
```python
sql = "SELECT id, descricao, valor FROM pedidos WHERE cliente_id = ? AND descricao LIKE ?"
linhas = con.execute(sql, (cliente, f"%{busca}%")).fetchall()
```

### 2. Falha aberta (`pode_ver_pedido`)
**Robusta** — falhe fechada e registre:
```python
def pode_ver_pedido(usuario, pedido_id):
    try:
        pedido = buscar_pedido(pedido_id)
        return pedido["cliente_id"] == usuario["id"]
    except Exception:
        app.logger.warning("falha ao checar acesso ao pedido %s", pedido_id)
        return False   # falha fechada
```

### 3. Path traversal (`ver_comprovante`) — AQUI MORA A "REVELACAO"
**Fragil** (o que a IA costuma sugerir) — passa no teste automatico mas
continua vulneravel:
```python
nome = arquivo.replace("../", "")
caminho = os.path.join(COMPROVANTES, nome)
with open(caminho) as fh:
    return fh.read()
```
Por que e fragil: o teste usa `../segredo.txt`. O `.replace` transforma
em `segredo.txt`, que nao existe em `comprovantes/` -> 404 -> teste passa.
Mas o `.replace` nao e recursivo: o payload **`....//segredo.txt`** vira
`../segredo.txt` depois da remocao e **vaza o arquivo**.

**Demonstre ao vivo (com o patch fragil aplicado):**
```bash
curl "http://127.0.0.1:5000/comprovante?arquivo=....//segredo.txt"
# retorna o conteudo de segredo.txt -> bypass
```

**Robusta** — ancora no diretorio base (precisa de `from flask import abort`):
```python
base = os.path.realpath(COMPROVANTES)
caminho = os.path.realpath(os.path.join(base, arquivo))
if not caminho.startswith(base + os.sep):
    abort(400)
try:
    with open(caminho) as fh:
        return fh.read()
except FileNotFoundError:
    return jsonify(erro="arquivo nao encontrado"), 404
```

## Mensagem central
O teste automatico e necessario, mas nao suficiente. Ele valida *o caso
que voce escreveu*. A revisao humana pergunta *o que o teste nao cobre*
(aqui, `....//`). Verificar o patch da IA e trabalho de pessoa.
