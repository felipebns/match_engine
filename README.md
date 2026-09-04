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
limit  <buy|sell> <price> <qty>     ordem com preco fixo
market <buy|sell> <qty>             ordem ao melhor preco disponivel
cancel order <id>                   cancela uma ordem do livro
print book                          mostra o livro
quit                            sai
```

## Cancelamento

Ao ser criada, uma ordem limit recebe um identificador e o exibe:

```
>>> limit buy 10 100
Order created: buy 100 @ 10 | OrderID: order-1
>>> cancel order order-1
Order cancelled
```

Ordens **market nao podem ser canceladas**: elas executam imediatamente contra
o livro e nunca repousam, entao nao ha o que cancelar depois.

O cancelamento e O(1) na busca. Cada `Book` mantem `ids_to_orders`, um indice
`order_id -> Order`, e o `LimitOrderBook` mantem `order_book`, um indice
`order_id -> lado`. Com os dois, achar a ordem e ir direto na fila do preco
dela -- sem varrer os niveis atras do identificador.

## Por que `deque` e nao `list`

A fila de cada nivel de preco usa `collections.deque`. Remover do inicio da
fila e a operacao mais frequente do matching, e no `deque` ela e O(1); numa
`list`, `pop(0)` desloca todos os outros elementos e custa O(n).

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
