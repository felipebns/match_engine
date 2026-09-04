from matching_engine.engine import MatchingEngine

"""
Matching Engine roda como uma CLI, mande a order para preencher o Book.
limit  <buy|sell> <price> <qty>     ordem com preco fixo
market <buy|sell> <qty>             ordem ao melhor preco disponivel
cancel order <id>                   cancela uma ordem do livro
print book                          mostra o livro
quit                                sai
"""

if __name__ == "__main__":
    matching_engine = MatchingEngine()
    matching_engine.run()