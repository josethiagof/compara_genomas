import pandas as pd

# Caminhos
PATH_GENERA = "/media/thiago/thiago_linux/codigos_python/analise_genera/dados/genera.csv"
PATH_FEATURES = "mapeamento_100_features.csv"

def processar_relatorio():
    # Carregando dados
    df_meu = pd.read_csv(PATH_GENERA)
    df_map = pd.read_csv(PATH_FEATURES)
    
    # Cruzamento de dados
    resultado = pd.merge(df_meu, df_map, on="RSID")
    
    lista_final = []
    for _, row in resultado.iterrows():
        gen = str(row['RESULT']).strip().upper()
        gen_norm = "".join(sorted(gen))
        
        # Traduzindo o resultado baseado no dicionário
        traducoes = dict(item.split(":") for item in row['Tradução'].split(", "))
        significado = traducoes.get(gen_norm) or traducoes.get(gen, "Informação não disponível para este resultado.")
        
        lista_final.append({
            "Categoria": row['Categoria'],
            "Característica": row['Característica'],
            "Seu Resultado": gen,
            "O que isso diz": significado
        })
    
    return pd.DataFrame(lista_final)

# Gerando o HTML
def gerar_html(df):
    tabela_html = ""
    for cat in df['Categoria'].unique():
        sub_df = df[df['Categoria'] == cat]
        tabela_html += f"<h2 class='text-2xl font-bold mt-8 mb-4 text-blue-800 border-b-2 border-blue-100 pb-2'>{cat}</h2>"
        tabela_html += "<div class='grid grid-cols-1 md:grid-cols-2 gap-4'>"
        for _, row in sub_df.iterrows():
            tabela_html += f"""
            <div class='bg-white p-4 rounded-lg shadow-sm border border-gray-100'>
                <p class='text-sm text-gray-500 font-bold uppercase tracking-wider'>{row['Característica']}</p>
                <p class='text-lg text-gray-800 mt-1'>{row['O que isso diz']}</p>
                <p class='text-xs text-blue-500 mt-2 font-mono'>Seu código: {row['Seu Resultado']}</p>
            </div>
            """
        tabela_html += "</div>"

    html_completo = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdn.tailwindcss.com"></script>
        <title>Manual do Meu Corpo</title>
    </head>
    <body class="bg-slate-50 p-8 font-sans text-gray-900">
        <div class="max-w-5xl mx-auto">
            <header class="text-center mb-12">
                <h1 class="text-4xl font-black text-blue-900 uppercase">Manual de Instruções Biológicas</h1>
                <p class="text-gray-600 mt-2 text-lg">Análise detalhada baseada no seu DNA</p>
            </header>
            {tabela_html}
            <footer class="mt-20 pt-8 border-t border-gray-200 text-center text-gray-400 text-sm italic">
                Aviso: Este relatório mostra tendências genéticas. O seu ambiente e hábitos atuais 
                têm um papel fundamental na forma como estas instruções se manifestam.
            </footer>
        </div>
    </body>
    </html>
    """
    with open("relatorio_estilo_vida.html", "w", encoding="utf-8") as f:
        f.write(html_completo)

# Execução Final
df_res = processar_relatorio()
gerar_html(df_res)
print("[+] Relatório HTML gerado: relatorio_estilo_vida.html")