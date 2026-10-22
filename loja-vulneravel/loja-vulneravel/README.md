# Loja Vulneravel — material do workshop *Desenvolvimento seguro com IA*

> **Aviso.** Esta aplicacao contem falhas de seguranca **plantadas de
> proposito**, apenas para treinamento. Rode somente na sua maquina
> (`127.0.0.1`), com dados ficticios. **Nao use em producao nem exponha
> na internet.** E o mesmo principio de projetos como OWASP Juice Shop e
> WebGoat: aprender a achar e corrigir falhas em um alvo seguro.

## O que e

Uma loja em Flask + SQLite com alguns endpoints (login, pedidos,
comprovantes, cupom, rastreio). Serve de alvo para tres praticas:

- **Pratica 1 — Caca as falhas:** ler o codigo e listar as falhas.
- **Pratica 2 — Tres condicoes:** gerar um codigo novo com IA e comparar
  o resultado sem regras, com "seja seguro" e com `regras_seguranca.md`.
- **Pratica 3 — Funil de verificacao:** corrigir tres falhas e checar o
  patch com teste + revisao.

## Como rodar

### Opcao A — GitHub Codespaces (recomendado, roda no navegador)
1. Suba esta pasta para um repositorio no GitHub.
2. No repositorio: botao **Code > Codespaces > Create codespace**.
3. Aguarde o ambiente montar (o `.devcontainer` ja instala tudo).
4. No terminal do Codespace:
   ```bash
   python app.py
   ```
   Abra a porta 5000 encaminhada.

### Opcao B — Local
```bash
pip install -r requirements.txt
python app.py
# em outro terminal, teste:
curl http://127.0.0.1:5000/
```

## Rodar os testes e os scanners
```bash
pytest -v                       # funcionais passam; exploits falham (codigo original)
bandit -r app.py                # analise estatica (pega MD5, pickle, segredo fixo, SQL)
pip-audit -r requirements.txt   # dependencias com CVE conhecida
semgrep --config auto .         # regras de seguranca (opcional)
```

> O Bandit pega as falhas "mecanicas" (MD5, pickle, segredo fixo, SQL por
> string). Ele **nao** pega as de logica/projeto (IDOR, SSRF, falha aberta,
> path traversal, cupom infinito, enumeracao de e-mail, logging). Essa e a
> ideia: scanner acha o mecanico; a revisao humana + IA acha o resto.
>
> O `pip-audit` costuma acender varias dependencias (o ecossistema anda).
> A plantada de proposito e o `Jinja2` fixado numa versao antiga.

## Dados de teste
| Cliente | E-mail             | Senha     |
|--------:|--------------------|-----------|
| 1       | ana@exemplo.com    | ana123    |
| 2       | bruno@exemplo.com  | bruno123  |

Pedidos: 10 e 11 pertencem a Ana; 20 pertence a Bruno.

---

## Pratica 1 — Caca as falhas (prompt sugerido)

Cole o conteudo de `app.py` no assistente e peca:

> "Este e o codigo de uma loja. Liste as falhas de seguranca que voce
> encontrar, uma por linha, no formato: categoria OWASP — endpoint/linha
> — risco em uma frase. Nao reescreva o codigo ainda."

Depois confira a lista contra o gabarito (o facilitador tem).

## Pratica 2 — Tres condicoes

Pedido funcional (o mesmo nas tres condicoes):

> "Implemente em Flask uma rota `POST /pedidos` que recebe `descricao` e
> `valor` de um cliente autenticado e grava no banco, e uma rota
> `GET /comprovante?arquivo=` que devolve o comprovante do pedido."

- **Condicao A:** so o pedido acima.
- **Condicao B:** o pedido + a frase "gere um codigo seguro".
- **Condicao C:** o pedido + anexe `regras_seguranca.md` como instrucao.

Compare as tres saidas: quantas das 10 regras cada uma respeitou?

## Pratica 3 — Funil de verificacao

Tres falhas para corrigir (todas presentes neste codigo):

1. **Injecao de SQL** em `GET /pedidos`.
2. **Path traversal** em `GET /comprovante`.
3. **Falha aberta** em `pode_ver_pedido()`.

Fluxo para cada falha:
1. Peca a correcao ao assistente.
2. Rode `pytest tests/test_exploits.py -v` — o teste daquela falha deve
   passar depois do patch.
3. Revise o patch a mao: ele resolve a causa ou so o sintoma?
