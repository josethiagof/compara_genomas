import pandas as pd

df = pd.read_csv('PRS_GENOMA/gwas-association-downloaded_2026-02-18-pubmedId_29942086.tsv', sep='\t')

# Filtrar só QI + colunas corretas
qi_df = df[df['MAPPED_TRAIT'].str.contains('intelligence', case=False, na=False)]

qi_df = qi_df[['SNP_ID_CURRENT', 'STRONGEST SNP-RISK ALLELE', 'OR or BETA', 'P-VALUE']].copy()
qi_df.columns = ['SNP', 'A1', 'BETA', 'P']

# Limpar e adicionar A2 dummy (necessário!)
qi_df['A2'] = qi_df['A1'].apply(lambda x: 'C' if x in 'AT' else 'A' if x in 'CG' else 'G')
qi_df = qi_df.dropna(subset=['SNP', 'P'])

print(f"QI SNPs válidos: {len(qi_df)}")
qi_df.to_csv('savage_qi_fixed.txt', sep='\t', index=False)
print(qi_df.head())
