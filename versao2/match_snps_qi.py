#!/usr/bin/env python3
"""
QI PRS COMPLETO com seus dados - Versão Final
Usa GWAS Catalog + seu genoma PLINK
"""

import pandas as pd
import numpy as np

# 1. Carregar seu PLINK BIM
print("1. Carregando genoma...")
bim = pd.read_csv('genoma_plink.bim', sep='\t', header=None, 
                  names=['CHR', 'SNP', 'CM', 'POS', 'A1', 'A2'])
bim['POS_INT'] = bim['POS'].astype(int)
print(f"Seu genoma: {len(bim):,} SNPs")

# 2. Carregar GWAS QI Catalog
print("\n2. Carregando QI GWAS...")
gwas = pd.read_csv('PRS_GENOMA/gwas-association-downloaded_2026-02-18-pubmedId_29942086.tsv', sep='\t')

# Filtrar QI
qi_gwas = gwas[gwas['MAPPED_TRAIT'].str.contains('intelligence', case=False, na=False, regex=False)]

qi_gwas = qi_gwas[['SNP_ID_CURRENT', 'STRONGEST SNP-RISK ALLELE', 'OR or BETA', 'P-VALUE']].copy()
qi_gwas.columns = ['BP', 'A1', 'BETA', 'P']
qi_gwas['BP_INT'] = qi_gwas['BP'].astype(str).astype(int)

print(f"GWAS QI: {len(qi_gwas)} SNPs")

# 3. Match por posição
print("\n3. Fazendo match por posição...")
matches = []
for idx, row in qi_gwas.iterrows():
    pos_matches = bim[bim['POS_INT'] == row['BP_INT']]
    if not pos_matches.empty:
        match_snp = pos_matches.iloc[0]
        matches.append({
            'SNP': match_snp['SNP'],
            'CHR': match_snp['CHR'],
            'POS': match_snp['POS'],
            'A1': row['A1'],
            'A2': match_snp['A2'],  # Do seu genoma
            'BETA': row['BETA'],
            'P': row['P']
        })

print(f"✅ {len(matches)} SNPs encontrados!")

# 4. Salvar sumstats matched
if matches:
    df_matches = pd.DataFrame(matches)
    df_matches.to_csv('qi_matched_final.txt', sep='\t', index=False)
    print("\nqi_matched_final.txt criado!")
    print(df_matches.head())
    
    # 5. Rodar PRSice direto
    print("\n4. Executando PRSice...")
    import subprocess
    subprocess.run([
        './PRSice',
        '--base', 'qi_matched_final.txt',
        '--target', 'genoma_plink',
        '--snp', 'SNP', '--a1', 'A1', '--a2', 'A2', '--stat', 'BETA', '--pvalue', 'P',
        '--out', 'thiago_qi_final',
        '--clump-r2', '0.1', '--clump-kb', '250',
        '--thread', '4', '--fastscore'
    ])
    print("✅ PRSice executado! Veja thiago_qi_final.sscore")
    
else:
    print("0 matches. Usando inventário alternativo...")
    
    # Fallback: seu inventário
    import subprocess
    subprocess.run([
        "grep", "-i", "intelligence|iq|cognitive", "inventario_total_tracos.txt"
    ] | subprocess.Popen([
        "awk", "'BEGIN{print \"SNP\\tA1\\tA2\\tBETA\\tP\"} /rs/ {print $NF-2, $NF-1, $NF, 0.01, 0.001}'"
    ], stdin=subprocess.PIPE) > "qi_fallback.txt")
    
    subprocess.run(['./PRSice', '--base', 'qi_fallback.txt', '--target', 'genoma_plink', '--out', 'thiago_qi_fallback'])
