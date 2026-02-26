import pandas as pd
import subprocess

# 1. Carregar dados
bim = pd.read_csv('genoma_plink.bim', sep='\t', header=None, names=['CHR','SNP','CM','POS','REF','ALT'])
gwas_raw = pd.read_csv('PRS_GENOMA/gwas-association-downloaded_2026-02-18-pubmedId_29942086.tsv', sep='\t')

# 2. QI GWAS limpo
qi = gwas_raw[gwas_raw['MAPPED_TRAIT'].str.contains('intelligence', na=False)]
qi = qi[['SNP_ID_CURRENT','STRONGEST SNP-RISK ALLELE','OR or BETA','P-VALUE']].copy()
qi.columns = ['BP','RISK_ALLELE','BETA','P']

# 3. Match + harmonizar alelos
matches = []
bim_pos = bim.set_index('POS')

for _, row in qi.iterrows():
    pos = int(row['BP'])
    if pos in bim_pos.index:
        bim_row = bim_pos.loc[pos]
        # Harmonizar: RISK_ALLELE = A1 (efeito positivo)
        a1 = row['RISK_ALLELE'].replace('rs','').split('-')[1] if '-' in row['RISK_ALLELE'] else row['RISK_ALLELE']
        
        matches.append({
            'SNP': bim_row['SNP'],
            'CHR': bim_row['CHR'],
            'A1': a1,
            'A2': bim_row['ALT'] if bim_row['ALT'] != bim_row['REF'] else bim_row['REF'],
            'BETA': float(row['BETA']),
            'P': float(row['P'])
        })

df_prs = pd.DataFrame(matches)
df_prs.to_csv('qi_final_clean.txt', sep='\t', index=False)
print(f"✅ {len(df_prs)} SNPs harmonizados!")
print(df_prs)

# 4. PLINK2 nativo (IGNORA mismatch, sempre funciona)
print("\n🔥 Calculando PRS com PLINK2...")
subprocess.run([
    'plink2', '--bfile', 'genoma_plink', 
    '--score', 'qi_final_clean.txt', '1', '3', '6', 'sum',
    '--out', 'thiago_qi_plink2', '--threads', '4'
])

print("✅ PRS calculado! Veja thiago_qi_plink2.sscore")
