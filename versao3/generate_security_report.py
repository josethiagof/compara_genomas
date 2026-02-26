import pandas as pd

# Caminho do arquivo gerado no passo anterior
PATH_VULNERABILIDADES = "/media/thiago/thiago_linux/codigos_python/analise_genera/relatorio_vulnerabilidades_final.csv"
OUTPUT_HTML = "audit_report.html"

def gerar_dashboard():
    df = pd.read_csv(PATH_VULNERABILIDADES)
    
    # Ordenar: Pathogenic no topo, depois Risk Factor
    df['priority'] = df['ClinicalSignificance'].apply(lambda x: 1 if 'pathogenic' in str(x).lower() else 2)
    df = df.sort_values('priority')

    # Componente: Cards de Resumo
    total_bugs = len(df)
    pathogenic_count = len(df[df['ClinicalSignificance'].str.contains('pathogenic', case=False, na=False)])
    risk_factor_count = total_bugs - pathogenic_count

    rows_html = ""
    for _, row in df.iterrows():
        # Lógica de cor baseada na severidade
        color_class = "text-red-500" if 'pathogenic' in str(row['ClinicalSignificance']).lower() else "text-yellow-500"
        bg_class = "border-red-900/30 bg-red-900/10" if 'pathogenic' in str(row['ClinicalSignificance']).lower() else "border-slate-700 bg-slate-800/50"

        rows_html += f"""
        <tr class="border-b border-slate-700 hover:bg-slate-700/30 transition">
            <td class="p-4 font-mono text-blue-400">{row['RSID']}</td>
            <td class="p-4"><span class="px-2 py-1 rounded text-xs font-bold bg-slate-700 text-white">{row['RESULT']}</span></td>
            <td class="p-4 font-bold {color_class}">{row['ClinicalSignificance']}</td>
            <td class="p-4 text-slate-300 text-sm">{row['PhenotypeList']}</td>
        </tr>
        """

    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-br" class="dark">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdn.tailwindcss.com"></script>
        <title>Genome Security Audit</title>
    </head>
    <body class="bg-slate-900 text-slate-100 font-sans">
        <div class="max-w-6xl mx-auto p-8">
            <header class="flex justify-between items-center mb-12 border-b border-slate-700 pb-8">
                <div>
                    <h1 class="text-4xl font-black tracking-tighter text-white">GENOME_AUDIT <span class="text-red-500">v1.0</span></h1>
                    <p class="text-slate-400 font-mono text-sm mt-2">Target: Local User | Source: ClinVar GRCh37</p>
                </div>
                <div class="flex gap-4">
                    <div class="bg-slate-800 border border-slate-700 p-4 rounded-lg text-center">
                        <p class="text-xs text-slate-500 uppercase">Critical (Pathogenic)</p>
                        <p class="text-2xl font-bold text-red-500">{pathogenic_count}</p>
                    </div>
                    <div class="bg-slate-800 border border-slate-700 p-4 rounded-lg text-center">
                        <p class="text-xs text-slate-500 uppercase">Warnings (Risk Factors)</p>
                        <p class="text-2xl font-bold text-yellow-500">{risk_factor_count}</p>
                    </div>
                </div>
            </header>

            <main>
                <div class="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
                    <table class="w-full text-left border-collapse">
                        <thead class="bg-slate-900/50 text-slate-400 uppercase text-xs shadow-sm">
                            <tr>
                                <th class="p-4">RSID</th>
                                <th class="p-4">Your_Genotype</th>
                                <th class="p-4">Severity</th>
                                <th class="p-4">Phenotype / Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows_html}
                        </tbody>
                    </table>
                </div>
            </main>

            <footer class="mt-12 p-6 bg-red-900/10 border border-red-900/30 rounded-lg">
                <h3 class="text-red-500 font-bold mb-2">🛑 DISCLAIMER DE ENGENHARIA BIOLÓGICA:</h3>
                <p class="text-xs text-slate-400 leading-relaxed">
                    1. <b>Falsos Positivos:</b> Chips de Microarray podem ter erros de leitura ("noise").<br>
                    2. <b>Penetrância Incerta:</b> Possuir o código de risco não garante a execução do fenótipo (Doença).<br>
                    3. <b>Multifatorial:</b> Diabetes e Doenças Coronárias são Polygenic (dependem de centenas de outros SNPs e do ambiente).<br>
                    4. <b>Ação:</b> Use este relatório para discutir com um médico geneticista. Não tome decisões clínicas isoladas.
                </p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"[*] Dashboard de Auditoria gerado: {OUTPUT_HTML}")

if __name__ == "__main__":
    gerar_dashboard()