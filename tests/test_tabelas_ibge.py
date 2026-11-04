import os, sys
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
CSV = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "pense2019_tema12_tidy.csv")

def test_totais_brasil_coincidem_com_artigo_publicado():
    """Valores de Antunes et al. 2022 (REME 26:e-1462), Brasil, 13-17 anos."""
    d = pd.read_csv(CSV)
    b = d[(d.nivel == "regiao_idade") & (d.local == "Brasil") & (d.faixa_idade == "13 a 17 anos") & (d.grupo == "Total")].set_index("indicador").p
    esperado = {"Muito preocupado(a)": 50.6, "Triste": 31.4, "Ninguém se preocupa comigo": 30.0,
                "Irritado(a)/nervoso(a)": 40.9, "Vida não vale a pena": 21.4,
                "Autoavaliação negativa": 17.7, "Sem amigos próximos": 4.0}
    for k, v in esperado.items():
        assert abs(b[k] - v) < 0.1, k

def test_ic_contem_estimativa_e_sem_ausentes():
    d = pd.read_csv(CSV)
    assert d.p.notna().all() and ((d.ic_inf <= d.p) & (d.p <= d.ic_sup)).all()
    assert len(d) == 2760
