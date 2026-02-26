import pandas as pd
import os

# --- CONFIGURAÇÃO ---
PATH_GENERA = "/media/thiago/thiago_linux/codigos_python/analise_genera/dados/genera.csv"
PATH_MAPEAMENTO = "/media/thiago/thiago_linux/codigos_python/analise_genera/mapeamento_completo_100.csv"
OUTPUT_HTML = "dashboard_biologico_master.html"

def gerar_dashboard():
    print("[*] Iniciando análise master...")
    
    # 1. Carregar Dados
    if not os.path.exists(PATH_MAPEAMENTO):
        print(f"Erro: Arquivo {PATH_MAPEAMENTO} não encontrado. Rode o setup_database.py primeiro.")
        return

    df_meu = pd.read_csv(PATH_GENERA)
    df_map = pd.read_csv(PATH_MAPEAMENTO)

    # 2. Cruzamento (Merge)
    resultado = pd.merge(df_meu, df_map, on="RSID")
    
    print(f"[+] Cruzamento concluído: {len(resultado)} itens encontrados no seu DNA.")

    lista_final = []
    for _, linha in resultado.iterrows():
        dna_letras = str(linha['RESULT']).strip().upper()
        # Normaliza a ordem (ex: 'GA' vira 'AG')
        dna_ordenado = "".join(sorted(dna_letras))
        
        # Traduz baseado no CSV
        try:
            opcoes = dict(item.split(":") for item in linha['Tradução'].split(", "))
            significado = opcoes.get(dna_ordenado) or opcoes.get(dna_letras, "Informação não mapeada.")
            
            lista_final.append({
                "Categoria": linha['Categoria'],
                "Característica": linha['Característica'],
                "RSID": linha['RSID'],
                "Genotipo": dna_letras,
                "Significado": significado
            })
        except:
            continue

    df_final = pd.DataFrame(lista_final)

    # 3. Geração do HTML (Design Moderno)
    corpo_html = ""
    for cat in df_final['Categoria'].unique():
        corpo_html += f"""
        <h2 style='color:#1e40af; border-bottom: 2px solid #dbeafe; margin-top:40px; padding-bottom:10px; font-size: 24px;'>
            {cat}
        </h2>
        <div style='display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px;'>
        """
        
        sub = df_final[df_final['Categoria'] == cat]
        for _, r in sub.iterrows():
            corpo_html += f"""
            <div style='background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); transition: transform 0.2s;'>
                <p style='margin: 0; font-size: 10px; color: #94a3b8; font-weight: bold; text-transform: uppercase;'>{r['RSID']}</p>
                <h3 style='margin: 5px 0; font-size: 16px; color: #1e293b; height: 40px;'>{r['Característica']}</h3>
                <p style='margin: 10px 0; font-size: 18px; color: #2563eb; font-weight: 700; line-height: 1.2;'>{r['Significado']}</p>
                <div style='background: #f1f5f9; padding: 5px 10px; border-radius: 6px; display: inline-block; margin-top: 10px;'>
                    <span style='font-family: monospace; font-size: 12px; color: #475569;'>Seu Genótipo: <b>{r['Genotipo']}</b></span>
                </div>
            </div>
            """
        corpo_html += "</div>"

    template = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard Biológico Master</title>
    </head>
    <body style="background: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 50px; color: #334155;">
        <div style="max-width: 1200px; margin: auto;">
            <header style="text-align: center; margin-bottom: 60px;">
                <h1 style="font-size: 42px; color: #1e3a8a; margin-bottom: 10px; letter-spacing: -1px;">🧬 Dashboard Biológico Master</h1>
                <p style="font-size: 18px; color: #64748b;">Análise Completa de 100 Características Genéticas</p>
                <div style="display: inline-block; background: #dbeafe; padding: 5px 15px; border-radius: 20px; font-size: 12px; color: #1e40af; font-weight: bold; margin-top: 20px;">
                    {len(df_final)} itens analisados com sucesso
                </div>
            </header>
            {corpo_html}
            <footer style="margin-top: 80px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 30px;">
                As informações representam tendências genéticas e não substituem aconselhamento médico ou nutricional.
            </footer>
        </div>
    </body>
    </html>
    """
    
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(template)
    print(f"[+] Relatório gerado com sucesso: {OUTPUT_HTML}")

if __name__ == "__main__":
    gerar_dashboard()