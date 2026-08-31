# Matching Engine

Matching engine de ativo unico, em memoria, com ordens **limit** e **market**.
Roda como uma CLI.

## Como rodar

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python main.py
```

## Comandos

```
limit  <buy|sell> <price> <qty>    ordem com preco fixo
market <buy|sell> <qty>            ordem ao melhor preco disponivel
print book                         mostra o livro
quit                               sai
```

## Testes

```bash
pytest
```

Organizados por parte do projeto:

```
tests/
  conftest.py       fabricas de ordens usadas pelos testes
  orders/           Order e Trade
  books/            PriceLevel, Book e LimitOrderBook
  engine/           parser e o cenario completo do enunciado
```

## Documentacao

[docs/arquitetura.md](docs/arquitetura.md) descreve as classes e como se
relacionam.
