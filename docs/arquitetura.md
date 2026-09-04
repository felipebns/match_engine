# Arquitetura

Matching engine de ativo unico, em memoria. Nesta etapa: ordens **limit** e
**market**.

## Relacao entre as classes

```
MatchingEngine          le texto do usuario e cria Orders
      |
      | 1:1
      v
LimitOrderBook          o livro completo; cruza as ordens
      |
      | administra 
      v
Book (buy) / Book (sell)    um lado cada; ordena por PREÇO
      |
      | 1:n
      v
PriceLevel              fila FIFO de um preco; ordena por TEMPO
      |
      | 1:n
      v
Order                   o dado: side, type, price, quantity, status
```

Todas as relacoes sao de **composicao** ("tem um"), nunca heranca. Um
`LimitOrderBook` nao *e* um `Book` -- ele *tem* dois.

`Trade` fica fora dessa cadeia: e produzido pelo `LimitOrderBook` quando duas
ordens se cruzam, e guardado numa lista.

## O que cada classe faz

| Classe | Arquivo | Responsabilidade |
|---|---|---|
| `Order` | `orders/order.py` | Estado de uma ordem. Nao executa nada. |
| `Trade` | `orders/trade.py` | Fato consumado, imutavel. |
| `PriceLevel` | `books/price_level.py` | Fila FIFO das ordens de um mesmo preco. |
| `Book` | `books/book.py` | Um lado do livro, niveis ordenados por preco. |
| `LimitOrderBook` | `books/lob.py` | Os dois lados + logica de cruzamento. |
| `MatchingEngine` | `engine.py` | REPL: texto -> `Order` -> livro. |

Cada camada responde a **uma** pergunta:

- `Book` -- "qual o proximo **preco** a executar?"
- `PriceLevel` -- "qual a proxima **ordem** dentro deste preco?"
- `Order` -- "quanto ainda falta executar de mim?"

## Prioridade preco-tempo

O livro ordena por dois criterios, nesta ordem:

1. **Preco** -- melhor preco primeiro. Compra: maior preco. Venda: menor preco.
   Vive no `Book`.
2. **Tempo** -- dentro do mesmo preco, quem chegou antes sai antes (FIFO).
   Vive no `PriceLevel`.

Separar os dois em classes distintas e o que torna cada criterio testavel
sozinho.

## Fluxo de uma ordem

```
texto  ->  _parse_order  ->  dict  ->  Order  ->  lob.submit()
                                                      |
                                          1. cruza contra o lado oposto
                                                      |
                                          2. sobrou quantidade?
                                             limit  -> repousa no livro
                                             market -> descarta
```

**A ordem cruza ANTES de repousar.** Inserir primeiro deixaria o livro
"cruzado" (melhor compra acima da melhor venda) e faria a ordem cruzar consigo
mesma.

Invariante: `best_bid < best_offer` sempre. Se os dois se alcancassem, havia
trade a fazer que nao foi feito.

## Decisoes

**Limit agressiva e preenchida, nao ignorada.** Escolhi fazer o trade como limit agressiva, pois simula um cenário de matching engine real mais precisamente

**O preco do trade e o da ordem passiva.** Quem ja estava no livro assumiu o
risco de esperar e tem o preco garantido.

**Market nunca repousa.** Sem preco, nao ha nivel onde esperar. O saldo sem
liquidez e descartado.

**Um `Trade` por execucao internamente, agregado na exibicao.** Cada execucao
gera um `Trade` proprio, com a sua contraparte -- e o que preserva a
rastreabilidade de quem negociou com quem. Na saida, `aggregate()` junta
execucoes consecutivas de mesmo preco numa linha, reproduzindo o formato do
enunciado. Precos diferentes ficam separados: o preco exibido precisa ser um
preco de execucao real, e agregar tudo exigiria uma media que nao corresponde
a negocio nenhum.

**`Decimal` e nao `float`.** O preco e chave dos niveis; `10.1` em float vira
`10.100000000000000355...`, o que criaria dois niveis para o mesmo preco.

**`deque` e nao `list` no `PriceLevel`.** Remover da frente e a operacao mais
frequente do matching: O(1) no deque, O(n) na list.

## Cancelamento (requisito adicional 3)

O desafio do cancelamento e que o comando so traz um identificador -- mas o
livro e organizado por **preco**, nao por id. Sem indice, achar a ordem
exigiria varrer todos os niveis dos dois lados.

A solucao usa dois indices, um em cada camada:

| Indice | Onde | Mapeia | Para que |
|---|---|---|---|
| `order_book` | `LimitOrderBook` | `order_id -> side` | descobrir em qual dos dois lados procurar |
| `ids_to_orders` | `Book` | `order_id -> Order` | pegar a `Order` e, dela, o preco do nivel |

O fluxo de `cancel_order(order_id)`:

1. `LimitOrderBook` consulta `order_book` e descobre o lado (`buy`/`sell`);
2. delega para o `Book` daquele lado;
3. `Book` consulta `ids_to_orders` e obtem a propria `Order`;
4. `order.price` indica o nivel; a ordem sai da fila daquele `PriceLevel`;
5. o nivel e descartado se ficou vazio, e o id sai dos dois indices.

Todos os passos sao O(1), exceto a remocao dentro do `deque`, que percorre a
fila do nivel.

**Guardar a `Order` e nao so o preco.** `ids_to_orders` poderia mapear
`order_id -> price`, o que bastaria para achar o nivel. Mas o `deque.remove()`
precisa da referencia do objeto para compara-lo por identidade -- com apenas o
preco, seria preciso varrer a fila procurando o id. Guardando a `Order`, a
referencia ja esta em maos.

**Ordens executadas saem dos indices.** Quando uma ordem e totalmente
executada durante o matching, ela e removida da fila e tambem dos dois
indices. Sem isso os dicionarios cresceriam indefinidamente, e um cancelamento
tardio encontraria uma entrada que nao corresponde a nada no livro.

**Market nao pode ser cancelada.** Ela nunca repousa no livro, entao nunca
entra nos indices. Tentar cancelar uma market cai na mesma mensagem de "ordem
nao encontrada" -- o que esta correto, porque de fato nao ha nada para
cancelar.

**`PriceLevel` nao guarda o proprio preco.** O preco ja e a chave do
dicionario `levels` no `Book`, e cada `Order` tambem carrega o seu. Um terceiro
lugar guardando a mesma informacao seria redundancia a manter sincronizada.

