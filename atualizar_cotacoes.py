# -*- coding: utf-8 -*-
"""
atualizar_cotacoes.py (versão GitHub Actions)
-----------------------------------------------
Roda dentro de um "runner" do GitHub Actions (Linux, na nuvem — não é a
máquina do Rene), agendado por .github/workflows/atualizar.yml. Busca as
cotações das 10 incorporadoras de capital aberto acompanhadas pela
Trisul e gera `cotacoes.js`, que o próprio workflow commita de volta
neste repositório.

Diferente da versão que roda localmente na máquina do Rene
(01_Projetos/Cotacoes_Mercado/atualizar_cotacoes.py, que chama o
curl.exe do Windows por causa de um bloqueio de segurança local), este
script pode usar a biblioteca `requests` do Python diretamente, porque
os servidores do GitHub Actions não têm esse tipo de bloqueio.

Nunca inventa números: um ticker que falhar é só omitido do arquivo,
sem derrubar os demais.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

TICKERS = [
    "TRIS3",
    "CYRE3",
    "CURY3",
    "DIRR3",
    "EZTC3",
    "EVEN3",
    "MRVE3",
    "LAVV3",
    "PLPL3",
    "TEND3",
]

SAIDA_JS = Path(__file__).parent / "cotacoes.js"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def buscar_cotacao(ticker_b3):
    simbolo_yahoo = ticker_b3 + ".SA"
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{simbolo_yahoo}"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"  [AVISO] {ticker_b3}: falha na requisição ({e})")
        return None

    chart = data.get("chart", {})
    if chart.get("error"):
        print(f"  [AVISO] {ticker_b3}: Yahoo retornou erro ({chart['error']})")
        return None

    resultados = chart.get("result") or []
    if not resultados:
        print(f"  [AVISO] {ticker_b3}: resposta sem dados (possível rate limit)")
        return None

    meta = resultados[0].get("meta", {})
    preco = meta.get("regularMarketPrice")
    fechamento_anterior = meta.get("previousClose") or meta.get("chartPreviousClose")

    if preco is None:
        print(f"  [AVISO] {ticker_b3}: campo de preço ausente na resposta")
        return None

    pct = None
    if fechamento_anterior:
        pct = (preco - fechamento_anterior) / fechamento_anterior * 100

    return {
        "symbol": ticker_b3,
        "price": round(float(preco), 2),
        "pct": round(float(pct), 2) if pct is not None else None,
    }


def main():
    print(f"Consultando {len(TICKERS)} tickers no Yahoo Finance...")
    acoes = []
    for ticker in TICKERS:
        resultado = buscar_cotacao(ticker)
        if resultado:
            acoes.append(resultado)
            sinal = "+" if (resultado["pct"] or 0) >= 0 else ""
            pct_txt = f"{sinal}{resultado['pct']}%" if resultado["pct"] is not None else "—"
            print(f"  {ticker}: R$ {resultado['price']} ({pct_txt})")

    if not acoes:
        print("\nERRO: nenhuma cotação foi obtida. cotacoes.js NÃO foi alterado.")
        sys.exit(1)

    payload = {
        "ts": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "acoes": acoes,
    }

    conteudo = (
        "// Gerado automaticamente pelo GitHub Actions — NÃO editar à mão.\n"
        "// Consumido pelo ticker do TITAN.html (window.TITAN_COTACOES).\n"
        "window.TITAN_COTACOES = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n"
    )

    SAIDA_JS.write_text(conteudo, encoding="utf-8")
    print(f"\nOK: {len(acoes)}/{len(TICKERS)} cotações gravadas em {SAIDA_JS}")


if __name__ == "__main__":
    main()
