import pandas as pd
import os
import json
import requests
import base64
from io import BytesIO
import matplotlib.pyplot as plt

# --- Configurações de Infra ---
PATH_GENOMA = "/media/thiago/thiago_linux/codigos_python/analise_genera/dados/genera.csv"
DIR_CACHE = "cache"
os.makedirs(DIR_CACHE, exist_ok=True)

# --- Business Logic: Dicionário Expandido (Foco, Performance, Metabolismo) ---
MAPEAMENTO = {
    "rs4680": {
        "nome": "Foco e Resiliência (COMT)",
        "categoria": "Cognição",
        "opcoes": {
            "AA": "Worrier: GC de Dopamina lento. Foco profundo, mas vulnerável ao estresse.",
            "AG": "Equilibrado: Gerenciamento de tarefas e estresse balanceado.",
            "GG": "Warrior: GC de Dopamina rápido. Ótimo sob pressão, mas tedia fácil."
        }
    },
    "rs1815739": {
        "nome": "Performance Muscular (ACTN3)",
        "categoria": "Performance",
        "opcoes": {"CC": "Explosão/Força", "CT": "Misto", "TT": "Resistência"}
    },
    "rs762551": {
        "nome": "Metabolismo de Cafeína (CYP1A2)",
        "categoria": "Metabolismo",
        "opcoes": {"AA": "Rápido", "AC": "Lento", "CC": "Muito Lento"}
    }
}

def get_api_data(rsid):
    cache_path = os.path.join(DIR_CACHE, f"{rsid}.json")
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f: return json.load(f)
    
    url = f"https://rest.ensembl.org/variation/human/{rsid}?content-type=application/json"
    try:
        r = requests.get(url, timeout=5)
        if r.ok:
            data = r.json()
            with open(cache_path, 'w') as f: json.dump(data, f)
            return data
    except: return None

def gerar_grafico_maf(maf_value):
    """Gera um gráfico de barras em Base64 para o HTML."""
    if maf_value == 'N/A' or maf_value is None: return ""
    
    plt.figure(figsize=(4, 1))
    plt.barh(['Global'], [maf_value], color='#3b82f6')
    plt.xlim(0, 1)
    plt.title(f"Frequência do Alelo Raro: {maf_value}", fontsize=8)
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- Main Engine ---
df = pd.read_csv(PATH_GENOMA)
lista_resultados = []
warnings_seguranca = []

print("[*] Iniciando Full Scan Genômico...")

# 1. Processamento de Traços (Dashboard Principal)
for rsid, info in MAPEAMENTO.items():
    res = df[df['RSID'] == rsid]
    if not res.empty:
        g_raw = res.iloc[0]['RESULT']
        g_norm = "".join(sorted(g_raw))
        api = get_api_data(rsid)
        
        maf = api.get('MAF') if api else None
        img_b64 = gerar_grafico_maf(maf)
        
        lista_resultados.append({
            "rsid": rsid,
            "nome": info['nome'],
            "categoria": info['categoria'],
            "genotipo": g_raw,
            "desc": info['opcoes'].get(g_norm, "Variação não mapeada"),
            "img": img_b64
        })

# 2. Scanner de Segurança (Auto-Discovery)
# Scaneando uma amostra para detectar 'Pathogenic'
for rsid in df['RSID'].tail(1000):
    api = get_api_data(rsid)
    if api and 'clinical_significance' in api:
        sigs = api['clinical_significance']
        if any(x in sigs for x in ['pathogenic', 'risk_factor']):
            warnings_seguranca.append({"rsid": rsid, "status": sigs})

# --- Geração do HTML (Tailwind CSS) ---
cards_html = ""
for r in lista_resultados:
    img_tag = f'<img src="data:image/png;base64,{r["img"]}" class="mt-2">' if r['img'] else ""
    cards_html += f"""
    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-4 hover:shadow-md transition">
        <span class="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded-full uppercase">{r['categoria']}</span>
        <h3 class="text-lg font-bold text-gray-800 mt-2">{r['nome']}</h3>
        <p class="text-gray-600 mt-1">{r['desc']}</p>
        <div class="mt-4 flex items-center justify-between">
            <span class="font-mono text-sm bg-gray-100 p-1 rounded">Genótipo: {r['genotipo']}</span>
            <span class="text-xs text-gray-400">ID: {r['rsid']}</span>
        </div>
        {img_tag}
    </div>
    """

bugs_html = "".join([f'<li class="text-red-600 font-mono text-sm">⚠️ {b["rsid"]}: {b["status"]}</li>' for b in warnings_seguranca])

html_final = f"""
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <title>Bio-Kernel Analytics</title>
</head>
<body class="bg-slate-50 p-8">
    <div class="max-w-5xl mx-auto">
        <div class="flex justify-between items-end mb-8">
            <div>
                <h1 class="text-3xl font-black text-slate-900">🧬 BIO-KERNEL <span class="text-blue-600">ANALYTICS</span></h1>
                <p class="text-slate-500">Relatório de Configuração de Hardware Humano</p>
            </div>
            <div class="text-right text-xs text-slate-400 font-mono">Build: 2024.Q1 | Source: Genera + Ensembl</div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="md:col-span-2">{cards_html}</div>
            <div class="bg-slate-900 text-white p-6 rounded-xl h-fit shadow-lg">
                <h2 class="text-xl font-bold mb-4 text-blue-400">Security Scanner</h2>
                <p class="text-xs text-slate-400 mb-4 italic">Vredura automática em busca de "Clinical Significance: Pathogenic"</p>
                <ul class="space-y-2">{bugs_html if warnings_seguranca else "<li>Nenhum bug crítico detectado na amostra.</li>"}</ul>
                <div class="mt-8 pt-4 border-t border-slate-700 text-[10px] text-slate-500">
                    Nota: Resultados baseados em bases acadêmicas (ClinVar/dbSNP). Consultas de saúde devem ser feitas com geneticistas.
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

with open("dashboard_biokernel.html", "w", encoding="utf-8") as f:
    f.write(html_final)

print("[+] Dashboard gerado: dashboard_biokernel.html")