"""Testes do REPL ponta a ponta, via stdin/stdout."""

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def repl(*comandos: str) -> str:
    entrada = "".join(f"{c}\n" for c in comandos) + "quit\n"
    saida = subprocess.run(
        [sys.executable, "main.py"],
        input=entrada, capture_output=True, text=True, cwd=RAIZ,
    )
    return saida.stdout


def test_cenario_do_enunciado_saida_completa():
    """A saida precisa bater exatamente com o exemplo do TODO."""
    out = repl(
        "limit buy 10 100",
        "limit sell 20 100",
        "limit sell 20 200",
        "market buy 150",
        "market buy 200",
        "market sell 200",
    )
    # o prompt do input() fica colado na saida; separa por ele
    trades = [
        pedaco.strip()
        for linha in out.splitlines()
        for pedaco in linha.split(">>> Digite sua ordem:")
        if "Trade" in pedaco
    ]
    assert trades == [
        "Trade, price: 20, qty: 150",
        "Trade, price: 20, qty: 150",
        "Trade, price: 10, qty: 100",
    ]


def test_print_book_mostra_os_dois_lados():
    out = repl("limit buy 10 100", "limit sell 20 300", "print book")
    assert "100 @ 10" in out
    assert "300 @ 20" in out


def test_ordem_invalida_nao_derruba_o_repl():
    out = repl("foo bar", "limit buy 10 100", "print book")
    assert "inválida" in out
    assert "100 @ 10" in out


def test_quit_encerra():
    assert "fechada" in repl()


def test_entrada_vazia_e_ignorada():
    out = repl("", "   ", "limit buy 10 100")
    assert "100 @ 10" in repl("limit buy 10 100", "print book")
    assert "Traceback" not in out


def test_maiusculas_sao_aceitas():
    out = repl("LIMIT BUY 10 100", "print book")
    assert "100 @ 10" in out
