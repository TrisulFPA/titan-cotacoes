name: Atualizar cotações TITAN

on:
  schedule:
    # A cada 15 min, das 10h às 17h55 (BRT) em dias úteis.
    # BRT = UTC-3 (sem horário de verão), então isso é 13h-20h55 UTC.
    - cron: '*/15 13-20 * * 1-5'
  workflow_dispatch: {}
    # ^ permite clicar em "Run workflow" na aba Actions do GitHub
    #   pra rodar na hora, sem esperar o horário agendado.

permissions:
  contents: write
  # necessário para o workflow conseguir commitar o cotacoes.js de volta
  # neste repositório.

jobs:
  atualizar:
    runs-on: ubuntu-latest
    steps:
      - name: Baixar o repositório
        uses: actions/checkout@v4

      - name: Preparar Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Instalar dependências
        run: pip install requests

      - name: Buscar cotações e gerar cotacoes.js
        run: python atualizar_cotacoes.py

      - name: Commitar cotacoes.js atualizado
        run: |
          git config user.name "titan-bot"
          git config user.email "actions@users.noreply.github.com"
          git add cotacoes.js
          git diff --quiet --cached || git commit -m "Atualiza cotações do TITAN"
          git push
