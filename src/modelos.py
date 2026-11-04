"""Modelos confirmatórios, secundários e de sensibilidade (PeNSE 2019, microdados IBGE).

Desfecho principal: autoavaliação negativa (>=4 de 5 itens em 'na maioria das vezes/sempre').
Exposição confirmatória: sem amigos próximos (B12003 = 1). NÃO é item do desfecho.
ATENÇÃO (ajuste ao protocolo): 'ninguém se preocupa comigo' é um dos 5 itens do desfecho composto;
testá-lo contra o composto seria circular, por isso só aparece como desfecho de item único.
"""
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import estatistica as es  # noqa: E402
import preparar_dados as pdd  # noqa: E402

D = dict(w="peso", strata="estrato", psu="upa", posest="posest", totais="totais")
COV_BASE = ["feminino", "idade_16_17", "escola_privada"]
COV_FAM = ["pais_raramente_entendem", "agressao_familia"]
COV_PARES = ["bullying_sofrido", "cyberbullying"]


def ajustar(b, y, X, nome, dom=None):
    dom = b.dom.to_numpy() if dom is None else dom
    r = es.logistica_ponderada(b, y, X, dominio=dom, **D)
    r.insert(0, "modelo", nome); r.insert(1, "desfecho", y)
    return r, int((b[[y] + X].notna().all(axis=1).to_numpy() & dom).sum())


def tudo(b):
    out, ns = [], {}
    def add(y, X, nome, dom=None):
        r, n = ajustar(b, y, X, nome, dom); r["n_usados"] = n; out.append(r); ns[nome] = n
    Y = "autoavaliacao_neg"
    add(Y, ["sem_amigos"], "M0 bruto")
    add(Y, ["sem_amigos"] + COV_BASE, "M1 +sexo/idade/escola")
    add(Y, ["sem_amigos"] + COV_BASE + COV_FAM, "M2 +família")
    add(Y, ["sem_amigos"] + COV_BASE + COV_FAM + COV_PARES, "M3 completo")
    # sensibilidade: desfechos de item único (sem circularidade) e limiares do composto
    for y in ["preocupado", "triste", "ninguem_se_importa", "irritado", "vida_nao_vale"]:
        add(y, ["sem_amigos"] + COV_BASE + COV_FAM + COV_PARES, f"S1 item: {y}")
    for lim in (3, 5):
        raw = b.attrs["raw"]
        alt = pdd.construir_base(raw, limite_autoavaliacao=lim)
        b2 = b.copy(); b2["alt"] = alt["autoavaliacao_neg"].to_numpy()
        r, n = ajustar(b2, "alt", ["sem_amigos"] + COV_BASE + COV_FAM + COV_PARES, f"S2 composto >= {lim}")
        r["n_usados"] = n; out.append(r)
    # sensibilidade: estratificado por sexo
    for nome, m in [("S3 só meninas", (b.feminino == 1).to_numpy()), ("S3 só meninos", (b.feminino == 0).to_numpy())]:
        add(Y, ["sem_amigos", "idade_16_17", "escola_privada"] + COV_FAM + COV_PARES, nome, b.dom.to_numpy() & m)
    # sensibilidade: escolaridade da mãe (perde casos 'não sei')
    add(Y, ["sem_amigos", "mae_ate_fund_incompleto"] + COV_BASE + COV_FAM + COV_PARES, "S4 +escolaridade da mãe")
    return pd.concat(out, ignore_index=True)


if __name__ == "__main__":
    raw = pd.read_csv(sys.argv[1], usecols=pdd.COLUNAS)
    b = pdd.construir_base(raw)
    b.attrs["raw"] = raw
    R = tudo(b)
    R.to_csv(sys.argv[2], index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
    print(R[R.termo != "(Intercepto)"][["modelo", "desfecho", "termo", "OR", "ic_inf", "ic_sup", "p_valor", "n_usados"]].round(3).to_string())
