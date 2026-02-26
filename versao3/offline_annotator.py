import pandas as pd

# Seus caminhos configurados
PATH_GENERA = "/media/thiago/thiago_linux/codigos_python/analise_genera/dados/genera.csv"
PATH_CLINVAR = "/media/thiago/thiago_linux/codigos_python/analise_genera/dados/variant_summary.txt.gz"

def run_deep_scan_v2():
    print("[*] Iniciando Auditoria Profunda (VCF Mode)...")

    # 1. Carga do ClinVar usando colunas VCF (mais precisas)
    cols_clinvar = [
        'RS# (dbSNP)', 'ReferenceAlleleVCF', 'AlternateAlleleVCF', 
        'ClinicalSignificance', 'PhenotypeList', 'Assembly'
    ]
    
    # Carregando em blocos para performance
    chunks = pd.read_csv(PATH_CLINVAR, sep='\t', compression='gzip', 
                         usecols=cols_clinvar, chunksize=100000, low_memory=False)
    
    # Filtramos por Build GRCh37 (o padrão da Genera)
    print("[*] Filtrando base por Build GRCh37...")
    clinvar_df = pd.concat([chunk[chunk['Assembly'] == 'GRCh37'] for chunk in chunks])
    
    # Normalização de Nomes e Tipos
    clinvar_df.rename(columns={
        'RS# (dbSNP)': 'RSID',
        'ReferenceAlleleVCF': 'Ref',
        'AlternateAlleleVCF': 'Alt'
    }, inplace=True)
    
    clinvar_df['RSID'] = 'rs' + clinvar_df['RSID'].astype(str)
    
    # Removemos linhas onde os alelos de referência estão vazios
    clinvar_df = clinvar_df.dropna(subset=['Ref', 'Alt'])

    # 2. Ingestão do seu Genoma
    df_genera = pd.read_csv(PATH_GENERA)

    # 3. O JOIN
    merged = pd.merge(df_genera, clinvar_df, on='RSID')

    # 4. Lógica de Match Genético
    def check_risk(row):
        meu_resultado = str(row['RESULT']).strip().upper()
        alelo_risco = str(row['Alt']).strip().upper()
        
        # Tratamento para Deleções (D) e Inserções (I) comuns em chips
        if alelo_risco in meu_resultado:
            count = meu_resultado.count(alelo_risco)
            return f"RISCO DETECTADO ({count} cópia(s))"
        return "Clean"

    print("[*] Executando pattern matching nos alelos...")
    merged['Status'] = merged.apply(check_risk, axis=1)

    # 5. Filtragem de Vulnerabilidades Reais
    # Removemos o que deu "Clean" e o que é classificado como "Benign"
    vulnerabilidades = merged[
        (merged['Status'].str.contains('RISCO')) & 
        (~merged['ClinicalSignificance'].str.contains('Benign', case=False, na=False))
    ]

    # Ordenação por Gravidade
    vulnerabilidades = vulnerabilidades.sort_values(by='ClinicalSignificance', ascending=False)

    print(f"\n[!] SCAN FINALIZADO: {len(vulnerabilidades)} vulnerabilidades encontradas.")
    
    if not vulnerabilidades.empty:
        print("\nTop 10 Vulnerabilidades:")
        print(vulnerabilidades[['RSID', 'RESULT', 'Alt', 'ClinicalSignificance', 'PhenotypeList']].head(10))
        
        vulnerabilidades.to_csv("relatorio_vulnerabilidades_final.csv", index=False)
        print("\n[+] Relatório gerado: relatorio_vulnerabilidades_final.csv")
    else:
        print("\n[i] Nenhuma vulnerabilidade patogênica detectada nos RSIDs cruzados.")

if __name__ == "__main__":
    run_deep_scan_v2()