import pandas as pd
import os

# CONFIGURAÇÕES
PATH_GENERA = "/media/thiago/thiago_linux/codigos_python/analise_genera/dados/genera.csv"
PATH_MAPEAMENTO = "mapeamento_completo_100.csv"
OUTPUT_HTML = "manual_do_corpo_100.html"

def processar_dna():
    if not os.path.exists(PATH_MAPEAMENTO):
        print("Erro: Execute o script de setup primeiro!")
        return

    # 1. Carregar os dados
    df_meu = pd.read_csv(PATH_GENERA)
    df_map = pd.read_csv(PATH_MAPEAMENTO)

    # 2. Cruzar as informações
    df_final = pd.merge(df_meu, df_map, on="RSID")
    
    resultados_formatados = []

    for _, linha in df_final.iterrows():
        # Captura seu DNA e organiza as letras (ex: 'GA' -> 'AG')
        letras_originais = str(linha['RESULT']).strip().upper()
        letras_ordenadas = "".join(sorted(letras_originais))
        
        # Faz o mesmo com o dicionário de tradução
        # Transformamos a string 'AA:Tolerante, CT:Tolerante' em um dicionário organizado
        dicionario_traducao = {}
        for par in linha['Tradução'].split(", "):
            codigo, significado = par.split(":")
            codigo_ordenado = "".join(sorted(codigo))
            dicionario_traducao[codigo_ordenado] = significado
            
        # Busca a tradução
        o_que_diz = dicionario_traducao.get(letras_ordenadas, "Informação não mapeada para este par de letras.")

        resultados_formatados.append({
            "Categoria": linha['Categoria'],
            "Característica": linha['Característica'],
            "RSID": linha['RSID'],
            "Seu_DNA": letras_originais,
            "Interpretacao": o_que_diz
        })

    # 3. Gerar o Relatório HTML
    df_res = pd.DataFrame(resultados_formatados)
    
    # Montagem do HTML
    html_cards = ""
    for cat in df_res['Categoria'].unique():
        html_cards += f"<h2 style='color:#1e3a8a; border-bottom:2px solid #bfdbfe; margin-top:40px; padding-bottom:10px;'>{cat}</h2>"
        html_cards += "<div style='display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px;'>"
        
        sub = df_res[df_res['Categoria'] == cat]
        for _, r in sub.iterrows():
            html_cards += f"""
            <div style='background:white; padding:15px; border-radius:10px; border:1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);'>
                <p style='margin:0; font-size:10px; color:#94a3b8; font-weight:bold;'>{r['RSID']}</p>
                <h3 style='margin:5px 0; font-size:16px; color:#1e293b;'>{r['Característica']}</h3>
                <p style='margin:10px 0; font-size:18px; color:#2563eb; font-weight:bold;'>{r['Interpretacao']}</p>
                <div style='background:#f1f5f9; padding:5px 10px; border-radius:5px; font-family:monospace; font-size:12px; color:#475569;'>
                    Seu DNA: <b>{r['Seu_DNA']}</b>
                </div>
            </div>
            """
        html_cards += "</div>"

    full_html = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head><meta charset="UTF-8"><title>Manual Biológico 100 Itens</title></head>
    <body style="background:#f8fafc; font-family:sans-serif; padding:40px; color:#334155;">
        <div style="max-width:1100px; margin:auto;">
            <h1 style="text-align:center; color:#1e3a8a; font-size:36px;">🧬 Manual do Meu Corpo</h1>
            <p style="text-align:center; color:#64748b; margin-bottom:50px;">Análise completa de 100 características genéticas</p>
            {html_cards}
        </div>
    </body>
    </html>
    """
    
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"Relatório gerado: {OUTPUT_HTML}")

if __name__ == "__main__":
    processar_dna()