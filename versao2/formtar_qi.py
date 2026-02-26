import pandas as pd

df = pd.read_csv('PRS_GENOMA/gwas-association-downloaded_2026-02-18-pubmedId_29942086.tsv', sep='\t')

# Selecionar colunas PRSice
df_prs = df[['SNP_ID_CURRENT', 'STRONGEST SNP-RISK ALLELE', 'OR or BETA', 'P-VALUE']].copy()
df_prs.columns = ['SNP', 'A1', 'BETA', 'P']

# Limpar e salvar
df_prs = df_prs.dropna()
df_prs.to_csv('savage_qi_formatted.txt', sep='\t', index=False)

print(f"✅ {len(df_prs)} SNPs formatados para PRSice!")
