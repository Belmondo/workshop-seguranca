# Regras de seguranca (arquivo de instrucoes da Pratica 2 - condicao C)

Use estas regras como contexto/instrucao do assistente ao gerar codigo.
Toda saida deve respeitar, sem excecao:

1. **Consultas parametrizadas.** Nunca montar SQL com concatenacao ou
   f-string; usar sempre parametros (`?` ou `:nome`).
2. **Validar toda entrada.** Tamanho, tipo e formato antes de usar;
   rejeitar o que nao casar com o esperado.
3. **Hash adaptativo de senha.** bcrypt ou argon2 com custo configurado.
   Nunca MD5, SHA1 ou texto puro.
4. **Erros nao revelam detalhes internos.** Mensagem generica para o
   cliente; o detalhe (stack trace, SQL, caminho) vai so para o log.
5. **Falhe fechado.** Em caso de erro ou duvida, negar o acesso — nunca
   liberar por padrao.
6. **Uploads limitados.** Restringir tamanho e extensao, gerar o nome do
   arquivo no servidor e salvar fora da raiz web.
7. **Checar autorizacao.** Confirmar que o usuario logado e dono do
   recurso antes de devolver ou alterar qualquer dado.
8. **Segredos em variaveis de ambiente.** Nada de chave, senha ou token
   fixo no codigo.
9. **Dependencias fixadas e auditadas.** Versoes travadas e verificadas
   contra vulnerabilidades conhecidas (pip-audit).
10. **Testes negativos para funcoes criticas.** Para cada funcao sensivel,
    um teste que garante que o caminho de ataque falha.
