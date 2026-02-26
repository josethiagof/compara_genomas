import pandas as pd
import os
import requests
import json
import time

# Configurações de Path
PATH_VULNS = "/media/thiago/thiago_linux/codigos_python/analise_genera/relatorio_vulnerabilidades_final.csv"
DIR_CACHE = "cache"
OUTPUT_CSV = "prioritized_vulnerabilities.csv"
OUTPUT_HTML = "prioritized_dashboard.html"
os.makedirs(DIR_CACHE, exist_ok=True)

def get_ensembl_data(rsid):
    cache_path = os.path.join(DIR_CACHE, f"{rsid}.json")
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f: return json.load(f)
    
    url = f"https://rest.ensembl.org/variation/human/{rsid}?content-type=application/json"
    try:
        time.sleep(0.2) # Proteção de Rate Limit
        r = requests.get(url, timeout=5)
        if r.ok:
            data = r.json()
            with open(cache_path, 'w') as f: json.dump(data, f)
            return data
    except: return None

def calcular_score(row, meta):
    score = 0
    
    # 1. Pontuação por Severidade (ClinVar)
    sig = str(row['ClinicalSignificance']).lower()
    if 'pathogenic' in sig: score += 50
    elif 'risk factor' in sig: score += 20
    
    if meta:
        # 2. Pontuação por Impacto Molecular (Ensembl)
        impacto = meta.get('most_severe_consequence', '')
        if impacto in ['stop_gained', 'frameshift_variant']: score += 30
        elif 'missense' in impacto: score += 15
        elif 'utr' in impacto: score += 5
        
        # 3. Pontuação por Raridade (MAF)
        maf = meta.get('MAF')
        if maf is not None:
            if maf < 0.001: score += 20
            elif maf < 0.01: score += 15
            elif maf < 0.05: score += 10
            
    return min(score, 100) # Cap em 100

def run_prioritization():
    print(f"[*] Carregando {PATH_VULNS}...")
    df = pd.read_csv(PATH_VULNS)
    
    # Para não estourar a API na primeira vez, vamos processar todos, 
    # mas o cache vai ajudar nas execuções seguintes.
    enriched_data = []
    print(f"[*] Enriquecendo e pontuando {len(df)} variantes. Isso pode demorar...")

    for i, row in df.iterrows():
        rsid = row['RSID']
        meta = get_ensembl_data(rsid)
        score = calcular_score(row, meta)
        
        enriched_data.append({
            "RSID": rsid,
            "Genotipo": row['RESULT'],
            "Significancia": row['ClinicalSignificance'],
            "Fenotipo": str(row['PhenotypeList'])[:100],
            "Impacto_Molecular": meta.get('most_severe_consequence', 'N/A') if meta else 'N/A',
            "MAF": meta.get('MAF', 'N/A') if meta else 'N/A',
            "Score_Prioridade": score
        })
        if (i+1) % 50 == 0: print(f"  > Processados: {i+1}/{len(df)}")

    df_final = pd.DataFrame(enriched_data).sort_values(by="Score_Prioridade", ascending=False)
    
    # Salvar CSV
    df_final.to_csv(OUTPUT_CSV, index=False)
    print(f"[+] CSV priorizado salvo em: {OUTPUT_CSV}")

    # Gerar HTML
    rows_html = ""
    for _, r in df_final.iterrows():
        # Cor baseada no Score
        bg_color = "bg-red-900/20" if r['Score_Prioridade'] >= 70 else "bg-slate-800/40"
        text_color = "text-red-400" if r['Score_Prioridade'] >= 70 else "text-slate-300"
        
        rows_html += f"""
        <tr class="border-b border-slate-700 {bg_color} hover:bg-slate-700/60 transition">
            <td class="p-4 font-mono text-blue-400">{r['RSID']}</td>
            <td class="p-4"><span class="bg-blue-900/50 px-2 py-1 rounded text-xs">{r['Genotipo']}</span></td>
            <td class="p-4 font-bold {text_color}">{r['Score_Prioridade']}</td>
            <td class="p-4 text-xs font-mono">{r['Impacto_Molecular']}</td>
            <td class="p-4 text-xs italic">{r['MAF']}</td>
            <td class="p-4 text-xs text-slate-400">{r['Fenotipo']}...</td>
        </tr>
        """

    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt" class="dark">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdn.tailwindcss.com"></script>
        <title>Prioritized Genomic Audit</title>
    </head>
    <body class="bg-slate-900 text-slate-100 p-8 font-sans">
        <div class="max-w-6xl mx-auto">
            <header class="mb-10 border-b border-slate-800 pb-6">
                <h1 class="text-3xl font-black text-white italic">PRIORITY_SCANNER <span class="text-blue-500 text-sm font-normal">v1.2</span></h1>
                <p class="text-slate-500 text-xs mt-2 font-mono">Algorithm: ClinVar + Ensembl Molecular Impact + MAF Frequency</p>
            </header>
            
            <div class="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden shadow-2xl">
                <table class="w-full text-left">
                    <thead class="bg-slate-950 text-[10px] text-slate-500 uppercase">
                        <tr>
                            <th class="p-4">RSID</th>
                            <th class="p-4">Genotype</th>
                            <th class="p-4">Priority_Score</th>
                            <th class="p-4">Molecular_Impact</th>
                            <th class="p-4">Global_Freq</th>
                            <th class="p-4">Phenotype_Description</th>
                        </tr>
                    </thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"[+] Dashboard de Prioridade gerado: {OUTPUT_HTML}")

if __name__ == "__main__":
    run_prioritization()