import pandas as pd
import requests
import time
import json
import os

# Paths
PATH_VULNS = "/media/thiago/thiago_linux/codigos_python/analise_genera/relatorio_vulnerabilidades_final.csv"
DIR_CACHE = "cache"

def buscar_deep_metadata(rsid):
    """Consulta a API do Ensembl para pegar a telemetria molecular."""
    cache_path = os.path.join(DIR_CACHE, f"{rsid}.json")
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f: return json.load(f)
    
    url = f"https://rest.ensembl.org/variation/human/{rsid}?content-type=application/json"
    try:
        time.sleep(0.2) # Rate limit protection
        r = requests.get(url, timeout=5)
        if r.ok:
            data = r.json()
            with open(cache_path, 'w') as f: json.dump(data, f)
            return data
    except: return None

def executar_triage():
    df = pd.read_csv(PATH_VULNS)
    
    # Triage: Vamos focar no que é MAIS crítico primeiro
    # Filtramos Pathogenic ou pegamos os primeiros Risk Factors
    triage_list = df.head(30).copy() # Pegando os primeiros 30 para teste
    
    results = []
    print(f"[*] Iniciando Deep Triage em {len(triage_list)} registros...")

    for _, row in triage_list.iterrows():
        rsid = row['RSID']
        print(f" -> Analisando {rsid}...")
        
        meta = buscar_deep_metadata(rsid)
        
        impacto = "N/A"
        frequencia = "N/A"
        
        if meta:
            # Pegando a consequência mais grave (O 'Tipo de Erro' de software)
            impacto = meta.get('most_severe_consequence', 'unknown')
            # Pegando a frequência global (A 'Raridade')
            frequencia = meta.get('MAF', 'Muito Raro / < 0.01')

        results.append({
            "RSID": rsid,
            "Doença": str(row['PhenotypeList'])[:50],
            "Severidade": row['ClinicalSignificance'],
            "Tipo_Erro_Molecular": impacto,
            "Freq_Global": frequencia
        })

    df_final = pd.DataFrame(results)
    print("\n=== RESULTADO DO HYBRID ENRICHMENT ===")
    print(df_final.to_string(index=False))
    df_final.to_csv("deep_triage_report.csv", index=False)

if __name__ == "__main__":
    executar_triage()