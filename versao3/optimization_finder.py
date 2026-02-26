import pandas as pd

PATH_GENERA = "/media/thiago/thiago_linux/codigos_python/analise_genera/dados/genera.csv"

# Dicionário de Otimizações (Vantagens de Hardware)
VANTAGENS = {
    "rs2802288": {
        "nome": "Resiliência e Longevidade (FOXO3)",
        "alelo_vantage": "G",
        "desc": "Associado a uma maior capacidade de reparo celular e longevidade.",
        "categoria": "Sistema"
    },
    "rs602662": {
        "nome": "Eficiência de B12 (FUT2)",
        "alelo_vantage": "A",
        "desc": "Indica boa absorção de Vitamina B12 (essencial para energia e foco).",
        "categoria": "Metabolismo"
    },
    "rs174546": {
        "nome": "Conversão de Ômega-3 (FADS1)",
        "alelo_vantage": "C",
        "desc": "Conversão eficiente de gorduras vegetais em EPA/DHA.",
        "categoria": "Metabolismo"
    },
    "rs333": {
        "nome": "Firewall de Hardware (CCR5-Delta32)",
        "alelo_vantage": "D", # D para Deleção
        "desc": "Proteção natural contra certas infecções virais.",
        "categoria": "Segurança"
    }
}

def run_optimization_scan():
    df = pd.read_csv(PATH_GENERA)
    relatorio_vantagens = []

    print("[*] Iniciando Benchmark de Vantagens...")

    for rsid, info in VANTAGENS.items():
        res = df[df['RSID'] == rsid]
        if not res.empty:
            genotipo = str(res.iloc[0]['RESULT']).strip().upper()
            vantage = info['alelo_vantage']
            
            # Se você tem pelo menos uma cópia do alelo vantajoso
            if vantage in genotipo:
                hits = genotipo.count(vantage)
                relatorio_vantagens.append({
                    "rsid": rsid,
                    "nome": info['nome'],
                    "status": f"Otimizado ({hits} cópia(s))",
                    "detalhes": info['desc'],
                    "categoria": info['categoria']
                })

    return pd.DataFrame(relatorio_vantagens)

df_vantagens = run_optimization_scan()
print("\n=== TOP VANTAGENS ENCONTRADAS ===")
print(df_vantagens[['nome', 'status', 'categoria']].to_string(index=False))