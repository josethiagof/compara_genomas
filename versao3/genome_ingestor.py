import pandas as pd
import requests
import os
import json
import time

# Configurações de Infra
PATH_GENOMA = "/media/thiago/thiago_linux/codigos_python/analise_genera/dados/genera.csv"
DIR_CACHE = "cache"

# Garante que o diretório de cache exista (o nosso Local Storage)
os.makedirs(DIR_CACHE, exist_ok=True)

def carregar_genoma(path):
    try:
        # Pulando linhas de comentário se existirem e carregando
        df = pd.read_csv(path)
        print(f"[*] {len(df)} SNPs carregados com sucesso.")
        return df
    except Exception as e:
        print(f"[!] Erro ao ler CSV: {e}")
        return None

def buscar_snp_com_cache(rsid):
    """
    Tenta ler do cache local (Disk I/O). 
    Se não existir, faz o GET (Network I/O) e salva.
    """
    cache_file = os.path.join(DIR_CACHE, f"{rsid}.json")
    
    # 1. Check Cache (Hit)
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    
    # 2. Cache Miss: Request API
    print(f"[!] Cache Miss para {rsid}. Consultando API...")
    server = "https://rest.ensembl.org"
    ext = f"/variation/human/{rsid}?content-type=application/json"
    
    try:
        # Adicionamos um pequeno delay para não sermos bloqueados (Rate Limit)
        time.sleep(0.2) 
        r = requests.get(server + ext, headers={"Content-Type": "application/json"})
        
        if r.ok:
            dados = r.json()
            # 3. Persistência (Write to Disk)
            with open(cache_file, 'w') as f:
                json.dump(dados, f)
            return dados
        else:
            print(f"[?] SNP {rsid} não encontrado na base Ensembl.")
    except Exception as e:
        print(f"[!] Erro na conexão: {e}")
    
    return None

# --- Main Pipeline ---

df = carregar_genoma(PATH_GENOMA)

# Lista de SNPs para nosso primeiro report (Traços físicos e Metabolismo)
# rs1815739: ACTN3 (Músculo)
# rs1229984: ADH1B (Metabolismo de Álcool - o "flush" facial)
# rs6152: AR (Calvície masculina)
#interesses = ["rs1815739", "rs1229984", "rs6152"]
# Dicionário de Tradução: A nossa "Camada de Negócio"
# Aqui definimos o que cada valor (Alelo) significa na prática.
MAPEAMENTO_INTERESSE = {
    # PERFORMANCE E MÚSCULO
    "rs1815739": {
        "nome": "Performance Muscular (ACTN3)",
        "interpretação": {
            "CC": "Explosão (Velocista): Seu sistema produz a proteína ACTN3. Alta performance em força.",
            "CT": "Misto: Perfil equilibrado entre explosão e resistência.",
            "TT": "Resistência (Maratonista): Deficiência de ACTN3. Melhor performance em endurance."
        }
    },
    # METABOLISMO DE CAFEÍNA (O "Garbage Collector" do Café)
    "rs762551": {
        "nome": "Metabolismo de Cafeína (CYP1A2)",
        "interpretação": {
            "AA": "Metabolismo Rápido: O café é processado rapidamente. Você sente o 'boost' e ele logo sai do sistema.",
            "AC": "Metabolismo Lento: A cafeína fica circulando mais tempo. Cuidado com café à tarde.",
            "CC": "Metabolismo Muito Lento: Alta sensibilidade. Café à noite causa 'System Hang' no sono."
        }
    },
    # CICLO CIRCADIANO (O "Cron Job" do Sono)
    "rs1801260": {
        "nome": "Ritmo Circadiano (Gene CLOCK)",
        "interpretação": {
            "AA": "Perfil Matutino: O sistema inicia o boot cedo. Mais produtivo pela manhã.",
            "AG": "Perfil Misto: Flexível entre manhã e noite.",
            "GG": "Perfil Vespertino: 'Night Owl'. O sistema demora a entrar em estado de alerta; melhor performance à noite."
        }
    },
    # COGNIÇÃO E MEMÓRIA (O "Write Cache" do Cérebro)
    "rs6265": {
        "nome": "Neuroplasticidade / Memória (BDNF)",
        "interpretação": {
            "GG": "Val/Val: Alta secreção de BDNF. O sistema faz o 'commit' de novas memórias com mais facilidade.",
            "AG": "Val/Met: Secreção intermediária. Equilíbrio em processos de aprendizagem.",
            "AA": "Met/Met: Menor secreção de BDNF. Pode exigir mais repetições para consolidar dados na memória de longo prazo."
        }
    },
    # SENSIBILIDADE AO ÁLCOOL (O "Error Handling" do Fígado)
    "rs1229984": {
        "nome": "Metabolismo de Álcool (ADH1B)",
        "interpretação": {
            "CC": "Metabolismo Normal: O processamento de álcool segue o fluxo padrão.",
            "CT": "Metabolismo Rápido: O álcool vira acetaldeído (tóxico) muito rápido. Gera ressaca ou rubor facial mais cedo.",
            "TT": "Metabolismo Ultra Rápido: Alta intolerância. O sistema aciona 'Exceptions' (mal-estar) quase imediatamente."
        }
    }
}


for snp, config in MAPEAMENTO_INTERESSE.items():
    meu_dado = df[df['RSID'] == snp]
    
    if not meu_dado.empty:
        genotipo = meu_dado.iloc[0]['RESULT']
        print(f"\n--- Relatório: {config['nome']} [{snp}] ---")
        print(f"Seu Genótipo: {genotipo}")
        
        # Busca a tradução amigável
        traducao = config['interpretação'].get(genotipo, "Combinação não mapeada")
        print(f"O que significa: {traducao}")
        
        # Ainda trazemos o dado bruto da API como "Logs de Debug"
        info_publica = buscar_snp_com_cache(snp)
        if info_publica:
            print(f"Bio-Status: {info_publica.get('most_severe_consequence', 'N/A')}")
    else:
        print(f"\n[-] {snp} ({config['nome']}) não está presente no seu chip da Genera.")