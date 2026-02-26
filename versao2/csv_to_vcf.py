#!/usr/bin/env python3
import pandas as pd
import sys
import warnings
warnings.filterwarnings('ignore')

def csv_to_vcf(csv_file, output_vcf):
    # Lê SEM assumir colunas específicas
    df = pd.read_csv(csv_file, low_memory=False)
    print("Colunas detectadas:", df.columns.tolist())
    print("Primeiras 3 linhas:\n", df.head(3))
    
    # Detecta automaticamente nomes das colunas
    col_map = {}
    if 'SID' in df.columns:
        col_map['sid'] = 'SID'
    elif 'RSID' in df.columns or 'rsID' in df.columns:
        col_map['sid'] = df.columns[df.columns.str.contains('RS|ID', case=False)][0]
    else:
        col_map['sid'] = df.columns[0]  # Primeira coluna
    
    col_map['chrom'] = df.columns[df.columns.str.contains('CHR|CHROM', case=False)][0]
    col_map['pos'] = df.columns[df.columns.str.contains('POS|POSITION', case=False)][0]
    col_map['geno'] = df.columns[df.columns.str.contains('RESULT|GENO', case=False)][0]
    
    print("Mapeamento automático:", col_map)
    
    with open(output_vcf, 'w') as f:
        f.write('##fileformat=VCFv4.2\n')
        f.write('#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE\n')
        
        for _, row in df.iterrows():
            sid = str(row[col_map['sid']])
            chrom = str(row[col_map['chrom']])
            pos = int(row[col_map['pos']])
            geno = str(row[col_map['geno']])
            
            # Parse genótipo simples (heterozigotos mais comuns)
            if len(geno) >= 2:
                ref = geno[0]
                alt = geno[-1] if len(geno) > 2 else geno[1]
            else:
                continue  # Pula inválidos
            
            dosage = 0 if ref == alt else 1
            
            f.write(f"{chrom}\t{pos}\t{sid}\t{ref}\t{alt}\t.\t.\t.\tGT\t{dosage}\n")
    
    print(f"✅ VCF criado: {output_vcf} ({len(df)} SNPs processados)")

if __name__ == "__main__":
    csv_to_vcf(sys.argv[1], sys.argv[2])
