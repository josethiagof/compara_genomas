import pandas as pd

# Caminho para o seu arquivo da Genera
PATH_GENERA = "/media/thiago/thiago_linux/codigos_python/analise_genera/dados/genera.csv"

# Dicionário expandido com mais de 25 características
FEATURES = {
    # --- NUTRIÇÃO E METABOLISMO ---
    "rs4988235": {
        "nome": "Tolerância à Lactose",
        "opcoes": {"TT": "Tolerante: Você provavelmente digere leite normalmente na vida adulta.", 
                   "CT": "Tolerante: Você provavelmente digere leite normalmente.", 
                   "CC": "Intolerante: Tendência a desenvolver má digestão de laticínios."},
        "cat": "Nutrição"
    },
    "rs1801133": {
        "nome": "Processamento de Folato (Vitamina B9)",
        "opcoes": {"CC": "Eficiência Normal.", 
                   "CT": "Eficiência Reduzida: O corpo demora mais para processar o ácido fólico.", 
                   "TT": "Eficiência Baixa: Requer atenção aos níveis de B9 na dieta."},
        "cat": "Nutrição"
    },
    "rs9939609": {
        "nome": "Tendência à Obesidade (Gene FTO)",
        "opcoes": {"TT": "Risco Baixo: Menor tendência genética ao acúmulo de gordura abdominal.", 
                   "AT": "Risco Intermediário.", 
                   "AA": "Risco Aumentado: Maior dificuldade em sentir saciedade e tendência ao ganho de peso."},
        "cat": "Nutrição"
    },
    "rs174537": {
        "nome": "Conversão de Ômega-3",
        "opcoes": {"GG": "Eficiente: Seu corpo converte bem gorduras vegetais em gorduras essenciais.", 
                   "GT": "Eficiência Média.", 
                   "TT": "Baixa Eficiência: Beneficia-se mais do consumo direto de peixes e algas."},
        "cat": "Nutrição"
    },
    "rs7501331": {
        "nome": "Conversão de Vitamina A (Betacaroteno)",
        "opcoes": {"CC": "Eficiente: Converte bem o betacaroteno de vegetais em vitamina A ativa.", 
                   "CT": "Eficiência Reduzida.", 
                   "TT": "Baixa Eficiência: Necessidade de consumir fontes diretas como fígado ou ovos."},
        "cat": "Nutrição"
    },

    # --- CARACTERÍSTICAS FÍSICAS ---
    "rs12913832": {
        "nome": "Cor dos Olhos (HERC2)",
        "opcoes": {"GG": "Probabilidade alta de olhos castanhos.", 
                   "AG": "Provavelmente olhos castanhos, mas carrega o traço para claros.", 
                   "AA": "Probabilidade alta de olhos azuis ou claros."},
        "cat": "Físico"
    },
    "rs17822931": {
        "nome": "Tipo de Cera de Ouvido e Odor Corporal",
        "opcoes": {"CC": "Cera úmida e maior tendência a odor nas axilas.", 
                   "CT": "Cera úmida.", 
                   "TT": "Cera seca e menor odor corporal característico."},
        "cat": "Físico"
    },
    "rs1805007": {
        "nome": "Tendência a Cabelo Ruivo (MC1R)",
        "opcoes": {"CC": " improvável ser ruivo.", 
                   "CT": "Carrega uma cópia do traço ruivo.", 
                   "TT": "Alta probabilidade de ter cabelos ruivos ou sardas."},
        "cat": "Físico"
    },
    "rs6152": {
        "nome": "Calvície Masculina",
        "opcoes": {"GG": "Risco Baixo de perda de cabelo precoce.", 
                   "GA": "Risco Moderado.", 
                   "AA": "Risco Aumentado de calvície masculina."},
        "cat": "Físico"
    },
    "rs10427255": {
        "nome": "Espirro por Claridade",
        "opcoes": {"CC": "Normal.", 
                   "CT": "Tendência a espirrar ao olhar para o sol ou luz forte.", 
                   "TT": "Forte tendência ao reflexo de espirro fótico."},
        "cat": "Físico"
    },

    # --- COMPORTAMENTO E SONO ---
    "rs1801260": {
        "nome": "Relógio Biológico (Gene CLOCK)",
        "opcoes": {"AA": "Matutino: Prefere acordar cedo e ser produtivo de manhã.", 
                   "AG": "Intermediário.", 
                   "GG": "Vespertino: Funciona melhor tarde da noite e tem dificuldade para acordar cedo."},
        "cat": "Comportamento"
    },
    "rs4680": {
        "nome": "Resiliência ao Estresse (COMT)",
        "opcoes": {"GG": "Resiliente: Lida bem com pressão, mas se entedia fácil com tarefas repetitivas.", 
                   "AG": "Equilibrado.", 
                   "AA": "Focado: Ótima concentração em tarefas complexas, mas se estressa com facilidade."},
        "cat": "Comportamento"
    },
    "rs53576": {
        "nome": "Sociabilidade (Receptor de Ocitocina)",
        "opcoes": {"GG": "Sociável: Maior facilidade em demonstrar empatia e lidar com o estresse social.", 
                   "AG": "Intermediário.", 
                   "AA": "Reservado: Perfil mais focado em si mesmo e menor necessidade de interação social."},
        "cat": "Comportamento"
    },

    # --- SENSIBILIDADES E SAÚDE ---
    "rs713598": {
        "nome": "Percepção de Gosto Amargo",
        "opcoes": {"CC": "Sensível: Sente muito o gosto amargo de vegetais (como brócolis).", 
                   "CG": "Sensibilidade Média.", 
                   "GG": "Pouco Sensível: Não se incomoda com alimentos amargos."},
        "cat": "Sensorial"
    },
    "rs1229984": {
        "nome": "Sensibilidade ao Álcool",
        "opcoes": {"CC": "Normal.", 
                   "CT": "Sensível: O corpo processa o álcool de forma a causar mal-estar rápido.", 
                   "TT": "Muito Sensível: Intolerância severa com vermelhidão no rosto."},
        "cat": "Metabolismo"
    },
    "rs16969968": {
        "nome": "Dependência de Nicotina",
        "opcoes": {"GG": "Risco Normal.", 
                   "AG": "Risco Aumentado.", 
                   "AA": "Risco Alto: Maior facilidade em se viciar em cigarro e dificuldade em parar."},
        "cat": "Saúde"
    },
    "rs1800562": {
        "nome": "Absorção de Ferro (Hereditária)",
        "opcoes": {"GG": "Normal.", 
                   "AG": "Carreador: Absorção de ferro pode ser levemente aumentada.", 
                   "AA": "Risco de Sobrecarga de Ferro: Necessidade de monitorar níveis de ferritina."},
        "cat": "Saúde"
    },
    "rs5051": {
        "nome": "Sensibilidade ao Sal e Pressão Alta",
        "opcoes": {"GG": "Sensibilidade Normal.", 
                   "AG": "Sensibilidade Aumentada.", 
                   "AA": "Alta Sensibilidade: O consumo de sal impacta fortemente a pressão arterial."},
        "cat": "Saúde"
    },
    "rs17608059": {
        "nome": "Consumo de Açúcar",
        "opcoes": {"GG": "Normal.", 
                   "GA": "Preferência aumentada por doces.", 
                   "AA": "Alta preferência: Geneticamente inclinado a consumir mais açúcar."},
        "cat": "Nutrição"
    },
    "rs1800497": {
        "nome": "Busca por Novidades / Impulsividade",
        "opcoes": {"GG": "Equilibrado.", 
                   "GA": "Tendência moderada a buscar novas experiências e recompensas.", 
                   "AA": "Inquieto: Maior busca por estímulos novos e tendência à impulsividade."},
        "cat": "Comportamento"
    }
}

def extrair_caracteristicas():
    try:
        df = pd.read_csv(PATH_GENERA)
        print(f"[*] Analisando seu manual de instruções biológicas...\n")
        
        resultados = []
        for rsid, info in FEATURES.items():
            encontrado = df[df['RSID'] == rsid]
            if not encontrado.empty:
                resultado_dna = encontrado.iloc[0]['RESULT']
                # Organiza as letras (ex: 'GA' vira 'AG') para bater com o dicionário
                resultado_normalizado = "".join(sorted(resultado_dna))
                
                # Busca a explicação simples
                explicacao = info['opcoes'].get(resultado_normalizado) or \
                             info['opcoes'].get(resultado_dna, "Resultado não mapeado.")
                
                resultados.append({
                    "Categoria": info['cat'],
                    "Característica": info['nome'],
                    "Seu Resultado": resultado_dna,
                    "O que significa": explicacao
                })
        
        # Cria a tabela e organiza por categoria
        df_final = pd.DataFrame(resultados).sort_values(by="Categoria")
        return df_final
    except Exception as e:
        return f"Erro ao processar o arquivo: {e}"

# Execução
if __name__ == "__main__":
    tabela_caracteristicas = extrair_caracteristicas()
    if isinstance(tabela_caracteristicas, pd.DataFrame):
        # Exibe o resultado de forma organizada
        pd.set_option('display.max_colwidth', None)
        print(tabela_caracteristicas[['Categoria', 'Característica', 'O que significa']].to_string(index=False))
    else:
        print(tabela_caracteristicas)