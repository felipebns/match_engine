from matching_engine.engine import MatchingEngine

"""
Matching Engine roda como uma CLI, mande a order para preencher o Book.
Utilize 'quit' para sair
"""

if __name__ == "__main__":
    matching_engine = MatchingEngine()
    matching_engine.run()