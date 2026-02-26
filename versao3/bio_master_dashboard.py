import pandas as pd
import os

# --- Configurações de Paths ---
PATH_GENERA = "/media/thiago/thiago_linux/codigos_python/analise_genera/dados/genera.csv"
PATH_VULNS = "/media/thiago/thiago_linux/codigos_python/analise_genera/relatorio_vulnerabilidades_final.csv"
OUTPUT_HTML = "master_dashboard.html"

# --- Dicionários de Conhecimento (Static Assets) ---
TRAITS = {
    "rs1815739": {"n": "Performance Muscular (ACTN3)", "c": "Performance"},
    "rs762551": {"n": "Metabolismo de Cafeína (CYP1A2)", "c": "Metabolismo"},
    "rs4680": {"n": "Foco e Resiliência (COMT)", "c": "Cognição"},
    "rs1801260": {"n": "Ritmo Circadiano (CLOCK)", "c": "Sistema"}
}

ADVANTAGES = {
    "rs602662": {"n": "Eficiência de B12 (FUT2)", "c": "Metabolismo", "v": "A"},
    "rs174546": {"n": "Conversão de Ômega-3 (FADS1)", "c": "Metabolismo", "v": "C"},
    "rs2802288": {"n": "Longevidade (FOXO3)", "c": "Sistema", "v": "G"}
}

def generate_master_dashboard():
    df_genoma = pd.read_csv(PATH_GENERA)
    df_vulns = pd.read_csv(PATH_VULNS)
    
    # 1. Processar Vantagens (Green Team)
    adv_list = []
    for rsid, info in ADVANTAGES.items():
        row = df_genoma[df_genoma['RSID'] == rsid]
        if not row.empty:
            gen = str(row.iloc[0]['RESULT'])
            if info['v'] in gen:
                adv_list.append(f"""
                <div class="bg-emerald-900/20 border border-emerald-500/30 p-4 rounded-lg">
                    <p class="text-xs text-emerald-500 font-bold uppercase">{info['c']}</p>
                    <h3 class="text-white font-bold">{info['n']}</h3>
                    <p class="text-emerald-400 text-sm mt-1">Status: Otimizado ({gen.count(info['v'])} cópia(s))</p>
                </div>""")

    # 2. Processar Vulnerabilidades (Red Team - Top 15 Severas)
    df_vulns['sev'] = df_vulns['ClinicalSignificance'].apply(lambda x: 1 if 'pathogenic' in str(x).lower() else 2)
    vuln_rows = ""
    # Removemos o .head(15) para iterar por TODO o dataframe
    for _, row in df_vulns.sort_values('sev').iterrows():
        color = "text-red-500" if row['sev'] == 1 else "text-yellow-500"
        vuln_rows += f"""
        <tr class="border-b border-slate-800 text-sm hover:bg-slate-800/50">
            <td class="p-3 font-mono text-blue-400">{row['RSID']}</td>
            <td class="p-3 font-bold {color} uppercase text-[10px]">{row['ClinicalSignificance']}</td>
            <td class="p-3 text-slate-300 text-[11px] leading-tight">{row['PhenotypeList']}</td>
        </tr>"""

    # 3. HTML Template
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-br" class="dark">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdn.tailwindcss.com"></script>
        <title>Bio-Kernel Master Dashboard</title>
        <style> @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap'); </style>
    </head>
    <body class="bg-slate-950 text-slate-200 font-sans selection:bg-blue-500/30">
        <div class="max-w-7xl mx-auto p-6">
            <div class="flex justify-between items-start mb-10 border-b border-slate-800 pb-6">
                <div>
                    <h1 class="text-3xl font-black tracking-tighter text-white uppercase italic">Bio-Kernel <span class="text-blue-600">v1.0.stable</span></h1>
                    <p class="font-mono text-xs text-slate-500 mt-1">Host: Localhost | Build: GRCh37 | Status: <span class="text-emerald-500">Running</span></p>
                </div>
                <div class="grid grid-cols-3 gap-4 text-center">
                    <div class="px-4 py-2 bg-slate-900 rounded-md border border-slate-800">
                        <p class="text-[10px] text-slate-500 uppercase">Bugs (Vulns)</p>
                        <p class="text-xl font-bold text-red-500">{len(df_vulns)}</p>
                    </div>
                    <div class="px-4 py-2 bg-slate-900 rounded-md border border-slate-800">
                        <p class="text-[10px] text-slate-500 uppercase">Features (Optimized)</p>
                        <p class="text-xl font-bold text-emerald-500">{len(adv_list)}</p>
                    </div>
                    <div class="px-4 py-2 bg-slate-900 rounded-md border border-slate-800">
                        <p class="text-[10px] text-slate-500 uppercase">Analyzed SNPs</p>
                        <p class="text-xl font-bold text-blue-500">{len(df_genoma)}</p>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div class="lg:col-span-1 space-y-4">
                    <h2 class="text-sm font-mono text-slate-500 uppercase tracking-widest mb-4 flex items-center">
                        <span class="w-2 h-2 bg-emerald-500 rounded-full mr-2"></span> Hardware_Optimizations
                    </h2>
                    {"".join(adv_list) if adv_list else "<p class='text-slate-600 italic'>Nenhum overclock detectado.</p>"}
                </div>

                <div class="lg:col-span-2">
                    <h2 class="text-sm font-mono text-slate-500 uppercase tracking-widest mb-4 flex items-center">
                        <span class="w-2 h-2 bg-red-500 rounded-full animate-pulse mr-2"></span> Security_Audit_Full_Log
                    </h2>
                    <div class="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
                        <div class="max-h-[700px] overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700">
                            <table class="w-full text-left">
                                <thead class="bg-slate-950 text-[10px] text-slate-500 uppercase sticky top-0 z-10 border-b border-slate-800">
                                    <tr>
                                        <th class="p-3 bg-slate-950">Reference_ID</th>
                                        <th class="p-3 bg-slate-950">Severity</th>
                                        <th class="p-3 bg-slate-950">Phenotype_Impact</th>
                                    </tr>
                                </thead>
                                <tbody>{vuln_rows}</tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <div class="mt-12 pt-6 border-t border-slate-900 text-[10px] text-slate-600 leading-relaxed text-center">
                ESTE RELATÓRIO É UM EXERCÍCIO DE BIOINFORMÁTICA E DATA SCIENCE. 
                DADOS DE MICROARRAY NÃO SÃO DIAGNÓSTICOS MÉDICOS. 
                O CONTEXTO AMBIENTAL (EPIGENÉTICA) PODE SOBREPOR QUALQUER CONFIGURAÇÃO DE HARDWARE AQUI LISTADA.
            </div>
        </div>
    </body>
    </html>
    """
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[*] Master Dashboard gerado com sucesso: {OUTPUT_HTML}")

if __name__ == "__main__":
    generate_master_dashboard()