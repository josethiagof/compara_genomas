import pandas as pd
import os
import json

# Configurações
PATH_GENOMA = "dados/genera.csv"
FILE_OUTPUT = "relatorio_genetico.html"

# Dicionário Refatorado com suporte a "Endianness" (Strand) e Normalização
MAPEAMENTO = {
    "rs1815739": {
        "nome": "Performance Muscular (ACTN3)",
        "categoria": "Performance",
        "opcoes": {
            "CC": "Explosão: Perfil de velocista/força. Produção normal de ACTN3.",
            "CT": "Misto: Equilíbrio entre força e resistência.",
            "TT": "Resistência: Perfil maratonista. Ausência de ACTN3."
        }
    },
    "rs762551": {
        "nome": "Metabolismo de Cafeína (CYP1A2)",
        "categoria": "Metabolismo",
        "opcoes": {
            "AA": "Rápido: O café é processado eficientemente.",
            "AC": "Lento: Cafeína permanece mais tempo no sistema.",
            "CC": "Muito Lento: Alta sensibilidade à cafeína."
        }
    },
    "rs6265": {
        "nome": "Neuroplasticidade e Memória (BDNF)",
        "categoria": "Cognição",
        "opcoes": {
            "GG": "Val/Val: Alta secreção de BDNF. Facilidade em plasticidade neural.",
            "CC": "Val/Val (Fita Reversa): Alta secreção de BDNF. (Igual ao GG).",
            "AG": "Val/Met: Secreção intermediária.",
            "AA": "Met/Met: Menor secreção de BDNF basal."
        }
    },
    "rs1801260": {
        "nome": "Ritmo Circadiano (CLOCK)",
        "categoria": "Estilo de Vida",
        "opcoes": {
            "AA": "Matutino: Maior produtividade cedo.",
            "AG": "Misto: Perfil flexível.",
            "GG": "Vespertino: 'Night Owl'. Maior alerta à noite."
        }
    },
    "rs1229984": {
        "nome": "Metabolismo de Álcool (ADH1B)",
        "categoria": "Metabolismo",
        "opcoes": {
            "CC": "Normal: Processamento padrão de etanol.",
            "CT": "Rápido: Conversão acelerada em acetaldeído (pode causar rubor).",
            "TT": "Muito Rápido: Alta intolerância."
        }
    }
}

def gerar_html(resultados):
    cards_html = ""
    for r in resultados:
        cards_html += f"""
        <div class="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500 mb-4">
            <div class="flex justify-between items-start">
                <div>
                    <span class="text-xs font-bold uppercase px-2 py-1 bg-blue-100 text-blue-700 rounded-full">{r['categoria']}</span>
                    <h2 class="text-xl font-bold text-gray-800 mt-2">{r['nome']}</h2>
                    <p class="text-sm text-gray-500">SNP: {r['rsid']} | Genótipo: <span class="font-mono font-bold text-blue-600">{r['genotipo']}</span></p>
                </div>
            </div>
            <p class="mt-4 text-gray-700">{r['interpretacao']}</p>
        </div>
        """

    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Genome Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 p-8">
        <div class="max-w-4xl mx-auto">
            <header class="mb-10 text-center">
                <h1 class="text-4xl font-extrabold text-gray-900">🧬 Bio-Kernel Report</h1>
                <p class="text-gray-600">Análise de Configuração de Hardware Humano</p>
            </header>
            <div class="grid grid-cols-1 gap-4">
                {cards_html}
            </div>
            <footer class="mt-10 text-center text-xs text-gray-400">
                Aviso: Este relatório tem fins informativos e não substitui aconselhamento médico. 
                Risco Poligênico: Um único SNP é apenas uma variável em um sistema complexo.
            </footer>
        </div>
    </body>
    </html>
    """
    with open(FILE_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_template)

# --- Execução ---
df = pd.read_csv(PATH_GENOMA)
lista_final = []

for rsid, info in MAPEAMENTO.items():
    filtro = df[df['RSID'] == rsid]
    if not filtro.empty:
        g_raw = filtro.iloc[0]['RESULT']
        # Normalização: "CA" vira "AC"
        g_norm = "".join(sorted(g_raw))
        
        # Tenta achar no dicionário (normalizado ou original)
        traducao = info['opcoes'].get(g_norm) or info['opcoes'].get(g_raw, "Genótipo não mapeado para este SNP.")
        
        lista_final.append({
            "rsid": rsid,
            "nome": info['nome'],
            "categoria": info['categoria'],
            "genotipo": g_raw,
            "interpretacao": traducao
        })

gerar_html(lista_final)
print(f"[*] Dashboard gerado com sucesso em: {FILE_OUTPUT}")