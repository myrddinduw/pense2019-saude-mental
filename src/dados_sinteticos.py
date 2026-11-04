"""Gerador de dados SINTÉTICOS, usado exclusivamente para testar código e interface.

ATENÇÃO: nada produzido a partir destes dados é resultado científico.
Todo arquivo gerado contém a coluna SINTETICO=1.
"""
import numpy as np
import pandas as pd


def gerar(n_estratos=20, psu_por_estrato=6, alunos_por_psu=25, seed=42,
          beta=(-1.2, 0.8, 0.5)):
    """beta = (intercepto, efeito de 'sem_amigos', efeito de 'feminino') em log-odds,
    valores arbitrários escolhidos pelo gerador (verdade conhecida para testes)."""
    rng = np.random.default_rng(seed)
    rows = []
    for h in range(n_estratos):
        for p in range(psu_por_estrato):
            peso_base = rng.uniform(50, 400)
            efeito_psu = rng.normal(0, 0.3)
            for _ in range(alunos_por_psu):
                fem = rng.binomial(1, 0.5)
                sem_amigos = rng.binomial(1, 0.06)
                eta = beta[0] + beta[1] * sem_amigos + beta[2] * fem + efeito_psu
                y = rng.binomial(1, 1 / (1 + np.exp(-eta)))
                rows.append((h, h * 100 + p, peso_base * rng.uniform(0.8, 1.2),
                             fem, sem_amigos, y))
    df = pd.DataFrame(rows, columns=["estrato", "upa", "peso", "feminino",
                                     "sem_amigos", "sofrimento"])
    df["SINTETICO"] = 1
    return df


if __name__ == "__main__":
    gerar().to_csv("data/processed/sintetico_TESTE.csv", index=False)
