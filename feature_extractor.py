import pandas as pd

PATH_GENERA = "/media/thiago/thiago_linux/codigos_python/analise_genera/dados/genera.csv"

# Dicionário de Características Gerais (UX/UI do Corpo)
FEATURES = {
    "rs4988235": {
        "nome": "Tolerância à Lactose (LCT)",
        "opcoes": {"TT": "Persistente: Driver ativo. Você digere leite normalmente.", 
                   "CT": "Persistente: Driver ativo.", 
                   "CC": "Não-Persistente: Driver desativado. Tendência a intolerância."},
        "cat": "Dieta"
    },
    "rs713598": {
        "nome": "Sensibilidade ao Amargo (TAS2R38)",
        "opcoes": {"CC": "Super-taster: Filtro de entrada ultra-sensível a amargo.", 
                   "CG": "Taster médio.", 
                   "GG": "Non-taster: Você mal sente o amargo de vegetais."},
        "cat": "Sensorial"
    },
    "rs53576": {
        "nome": "Receptor de Ocitocina (OXTR)",
        "opcoes": {"GG": "Alta Sensibilidade: Otimizado para interações sociais e empatia.", 
                   "AG": "Sensibilidade Média.", 
                   "AA": "Menor Sensibilidade: Perfil mais focado em lógica/individual."},
        "cat": "Cognição"
    },
    "rs1544410": {
        "nome": "Receptor de Vitamina D (VDR)",
        "opcoes": {"AA": "Eficiência Máxima: Receptor com alta afinidade.", 
                   "AG": "Eficiência Normal.", 
                   "GG": "Eficiência Reduzida: Requer maior monitoramento dos níveis."},
        "cat": "Metabolismo"
    }
}

def extract_general_traits():
    df = pd.read_csv(PATH_GENERA)
    results = []
    
    print("[*] Extraindo Configurações de UX/UI Genômica...")
    
    for rsid, info in FEATURES.items():
        row = df[df['RSID'] == rsid]
        if not row.empty:
            gen = row.iloc[0]['RESULT']
            # Normalização simples
            gen_norm = "".join(sorted(gen))
            
            desc = info['opcoes'].get(gen_norm) or info['opcoes'].get(gen, "Configuração customizada (não mapeada)")
            
            results.append({
                "Feature": info['nome'],
                "Genótipo": gen,
                "Descrição": desc,
                "Categoria": info['cat']
            })
            
    return pd.DataFrame(results)

traits_df = extract_general_traits()
print("\n", traits_df.to_string(index=False))