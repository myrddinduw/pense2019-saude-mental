"""Replica as tabelas oficiais do IBGE (Tema 12) a partir dos microdados e mede as diferenças.

Uso: python src/validacao_ibge.py <PENSE2019_MICRODADOS.csv> <tidy.csv> <saida.csv> [niveis]
niveis: lista separada por vírgula entre brasil,regiao_idade,uf,capital (padrão: todos)
"""
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import estatistica as es  # noqa: E402
import preparar_dados as pdd  # noqa: E402

UF = {11: "Rondônia", 12: "Acre", 13: "Amazonas", 14: "Roraima", 15: "Pará", 16: "Amapá", 17: "Tocantins",
      21: "Maranhão", 22: "Piauí", 23: "Ceará", 24: "Rio Grande do Norte", 25: "Paraíba", 26: "Pernambuco",
      27: "Alagoas", 28: "Sergipe", 29: "Bahia", 31: "Minas Gerais", 32: "Espírito Santo", 33: "Rio de Janeiro",
      35: "São Paulo", 41: "Paraná", 42: "Santa Catarina", 43: "Rio Grande do Sul", 50: "Mato Grosso do Sul",
      51: "Mato Grosso", 52: "Goiás", 53: "Distrito Federal"}
REG = {1: "Norte", 2: "Nordeste", 3: "Sudeste", 4: "Sul", 5: "Centro-Oeste"}
CAP = {1100205: "Porto Velho", 1200401: "Rio Branco", 1302603: "Manaus", 1400100: "Boa Vista", 1501402: "Belém",
       1600303: "Macapá", 1721000: "Palmas", 2111300: "São Luís", 2211001: "Teresina", 2304400: "Fortaleza",
       2408102: "Natal", 2507507: "João Pessoa", 2611606: "Recife", 2704302: "Maceió", 2800308: "Aracaju",
       2927408: "Salvador", 3106200: "Belo Horizonte", 3205309: "Vitória", 3304557: "Rio de Janeiro",
       3550308: "São Paulo", 4106902: "Curitiba", 4205407: "Florianópolis", 4314902: "Porto Alegre",
       5002704: "Campo Grande", 5103403: "Cuiabá", 5208707: "Goiânia", 5300108: "Brasília"}
IND = {"Sem amigos próximos": "sem_amigos", "Muito preocupado(a)": "preocupado", "Triste": "triste",
       "Ninguém se preocupa comigo": "ninguem_se_importa", "Irritado(a)/nervoso(a)": "irritado",
       "Vida não vale a pena": "vida_nao_vale", "Autoavaliação negativa": "autoavaliacao_neg"}


def main(csv, tidy, saida, niveis):
    raw = pd.read_csv(csv, usecols=pdd.COLUNAS + ["MUNICIPIO_CAP"] if "MUNICIPIO_CAP" not in pdd.COLUNAS else pdd.COLUNAS)
    b = pdd.construir_base(raw, convencao_ibge=True)
    b["cap"] = raw["MUNICIPIO_CAP"].to_numpy()
    T = pd.read_csv(tidy)
    base = b.dom.to_numpy() & b.idade_16_17.notna().to_numpy()
    sexo = {"Total": np.ones(len(b), bool), "Homem": (b.feminino == 0).to_numpy(), "Mulher": (b.feminino == 1).to_numpy(),
            "Pública": (b.dep_admin == 1).to_numpy(), "Privada": (b.dep_admin == 2).to_numpy()}
    locais = []   # (nivel, faixa, nome, máscara)
    if "brasil" in niveis or "regiao_idade" in niveis:
        for faixa, m in [("13 a 17 anos", base), ("13 a 15 anos", base & (b.idade_16_17 == 0).to_numpy()),
                         ("16 e 17 anos", base & (b.idade_16_17 == 1).to_numpy())]:
            locais.append(("regiao_idade", faixa, "Brasil", m))
            if "regiao_idade" in niveis:
                for k, nome in REG.items():
                    locais.append(("regiao_idade", faixa, nome, m & (b.regiao == k).to_numpy()))
    if "uf" in niveis:
        locais.append(("uf", "13 a 17 anos", "Brasil", base))
        for k, nome in REG.items():
            locais.append(("uf", "13 a 17 anos", nome, base & (b.regiao == k).to_numpy()))
        for k, nome in UF.items():
            locais.append(("uf", "13 a 17 anos", nome, base & (b.uf == k).to_numpy()))
    if "capital" in niveis:
        locais.append(("capital", "13 a 17 anos", "Total", base & (b.cap > 0).to_numpy()))
        for k, nome in CAP.items():
            locais.append(("capital", "13 a 17 anos", nome, base & (b.cap == k).to_numpy()))
    linhas, t0 = [], time.time()
    for nivel, faixa, nome, m in locais:
        for ind, col in IND.items():
            for g, mg in sexo.items():
                r = es.proporcao(b, col, "peso", "estrato", "upa", dominio=m & mg, posest="posest", totais="totais")
                t = T[(T.nivel == nivel) & (T.faixa_idade == faixa) & (T.local == nome) & (T.indicador == ind) & (T.grupo == g)]
                if t.empty:
                    continue
                t = t.iloc[0]
                linhas.append({"nivel": nivel, "faixa": faixa, "local": nome, "indicador": ind, "grupo": g,
                               "p": 100 * r["p"], "p_ibge": t.p, "ic_inf": 100 * r["ic_inf"], "ic_inf_ibge": t.ic_inf,
                               "ic_sup": 100 * r["ic_sup"], "ic_sup_ibge": t.ic_sup, "n": r["n_validos"]})
        print(nivel, faixa, nome, f"{time.time()-t0:.0f}s", flush=True)
    R = pd.DataFrame(linhas)
    R["d_p"] = R.p - R.p_ibge
    R["d_ic"] = np.maximum((R.ic_inf - R.ic_inf_ibge).abs(), (R.ic_sup - R.ic_sup_ibge).abs())
    R.to_csv(saida, index=False)
    print(len(R), "estimativas comparadas | max|dp|=%.3f | p99 |dp|=%.3f | max d_ic=%.3f" %
          (R.d_p.abs().max(), R.d_p.abs().quantile(.99), R.d_ic.max()))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(",") if len(sys.argv) > 4 else ["brasil", "regiao_idade", "uf", "capital"])
