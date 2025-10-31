import os
import sqlite3
import pandas as pd
import traceback
import math
import json
import plotly.graph_objects as go
import plotly.utils
from flask import Flask, render_template, request, redirect, url_for

# --- 1. CONFIGURAÇÃO INICIAL E CONSTANTES ---
app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

AREA_ESTACAO = 20 * 3.5 

FATORES_PONDERACAO = {
    'G1': 0.2, 'G2': 0.5, 'G3': 0.8, 'G4': 0.9,
    'D_O': 1.0, 'D_P': 1.0, 'D_E': 1.0, # Grupo 5
    'D_EX': 0.5, # Grupo 6
    'D_D': 0.3,  # Grupo 7
    'D_R': 0.6   # Grupo 8
}

# --- MAPEAMENTO DE COLUNAS (Corrigido para defeitos individuais G5-G8) ---
COLUNA_KM = 0 
MAPA_COLUNAS_LE = {
    'OK': 1, 
    'G1': [2, 3, 4, 5, 6, 7],         # FI, TTC, TTL, TLC, TLL, TRR
    'G2': [8, 9],                     # J, TB
    'G3': [10, 11],                   # JE, TBE
    'G4': [12, 13, 14, 15],           # ALP, ATP, ALC, ATC
    'D_O': 16, 'D_P': 17, 'D_E': 18,  # G5 (Individuais)
    'D_EX': 19,                       # G6
    'D_D': 20,                        # G7
    'D_R': 21,                        # G8
    'TRI': 22, 'TRE': 23
}
MAPA_COLUNAS_LD = {
    'OK': 24, 
    'G1': [25, 26, 27, 28, 29, 30],
    'G2': [31, 32],
    'G3': [33, 34],
    'G4': [35, 36, 37, 38],
    'D_O': 39, 'D_P': 40, 'D_E': 41,
    'D_EX': 42,
    'D_D': 43,
    'D_R': 44,
    'TRI': 45, 'TRE': 46
}

DEFEITOS_AGRUPADOS = ['G1', 'G2', 'G3', 'G4']
DEFEITOS_INDIVIDUAIS = ['D_O', 'D_P', 'D_E', 'D_EX', 'D_D', 'D_R']

# --- 2. FUNÇÕES "AJUDANTES" ---
def normalizar_valor(valor):
    """Lê o valor da célula. Retorna 0 para vazio, ou o valor numérico."""
    if isinstance(valor, (int, float)):
        return float(valor)
    if not isinstance(valor, str):
        return 0.0 
    valor = valor.strip()
    if valor == "":
        return 0.0
    valor = valor.replace(",", ".")
    try:
        return float(valor)
    except ValueError:
        return 1.0 

def normalizar_binario(valor):
    """Converte um valor normalizado em 1 (se > 0) ou 0."""
    return 1 if normalizar_valor(valor) > 0 else 0

def calcular_variancia_2p(a, b):
    """Cálculo da variância amostral para 2 pontos, como você pediu."""
    if a == 0 or b == 0:
        return 0.0 

    media = (a + b) / 2
    var = ((a - media)**2 + (b - media)**2) / 1 
    return var

def processar_planilha_pro006(caminho_arquivo, linha_dados_str, tipo_pista):
    """O "Cérebro" do PRO-006: Lógica binária e inventário alternado."""
    conn = sqlite3.connect('projeto_pro006.db')
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM estacas')

        skip_rows = int(linha_dados_str) - 1
        df = pd.read_excel(caminho_arquivo, header=None, skiprows=skip_rows, dtype=object)

        print(f"Iniciando processamento PRO-006. Tipo: {tipo_pista}. Lendo a partir da linha {linha_dados_str}.")

        estaca_index = 0 
        lista_de_sql_data = [] 

        for _, row in df.iterrows():
            estaca_index += 1

            km = row.get(COLUNA_KM)
            if pd.isna(km) or str(km).strip() == "":
                continue 

            km_val = normalizar_valor(km)
            km_segmento = math.floor(km_val)

            # Inicializa a "ficha binária" para esta estaca
            sql_data = {
                'km': km_val,
                'km_segmento': km_segmento,
                'tipo_pista': tipo_pista,
                'foi_inventariada': 0,
                'g1': 0, 'g2': 0, 'g3': 0, 'g4': 0,
                'd_o': 0, 'd_p': 0, 'd_e': 0, 'd_ex': 0, 'd_d': 0, 'd_r': 0,
                'fch_media_estaca': 0.0,
                'fch_var_estaca': 0.0
            }

            # --- 3. LÓGICA DE INVENTÁRIO (Sua regra) ---
            is_odd = (estaca_index % 2 != 0)
            mapa_defeitos = None

            if tipo_pista == 'terceira_faixa':
                if is_odd: 
                    sql_data['foi_inventariada'] = 1
                    mapa_defeitos = MAPA_COLUNAS_LE 

            elif tipo_pista == 'simples' or tipo_pista == 'dupla':
                sql_data['foi_inventariada'] = 1
                if is_odd: 
                    mapa_defeitos = MAPA_COLUNAS_LD 
                else: 
                    mapa_defeitos = MAPA_COLUNAS_LE 

            # --- 4. CÁLCULO (Se a estaca for inventariada) ---
            if sql_data['foi_inventariada'] == 1 and mapa_defeitos:

                for grupo in DEFEITOS_AGRUPADOS:
                    for col_idx in mapa_defeitos[grupo]:
                        if normalizar_binario(row.get(col_idx)) == 1:
                            sql_data[grupo] = 1
                            break 

                if sql_data['g3'] == 1:
                    sql_data['g1'] = 0; sql_data['g2'] = 0
                elif sql_data['g2'] == 1:
                    sql_data['g1'] = 0

                for defeito in DEFEITOS_INDIVIDUAIS:
                    col_idx = mapa_defeitos[defeito]
                    sql_data[defeito.lower()] = normalizar_binario(row.get(col_idx))

                tri = normalizar_valor(row.get(mapa_defeitos['TRI']))
                tre = normalizar_valor(row.get(mapa_defeitos['TRE']))

                sql_data['fch_media_estaca'] = (tri + tre) / 2
                sql_data['fch_var_estaca'] = calcular_variancia_2p(tri, tre)

            lista_de_sql_data.append(sql_data)

        # Fim do "Grande Loop"

        # --- 5. INSERIR TUDO NO BANCO DE DADOS ---
        print(f"Processamento concluído. Inserindo {len(lista_de_sql_data)} estacas no banco...")

        cursor.execute("PRAGMA table_info(estacas)")
        colunas_db = [info[1] for info in cursor.fetchall() if info[1] != 'id'] # Pega nomes, exceto 'id'

        placeholders = ', '.join(['?' for _ in colunas_db])
        nomes_colunas = ', '.join(colunas_db)
        sql_query = f"INSERT INTO estacas ({nomes_colunas}) VALUES ({placeholders})"

        lista_de_valores = []
        for sql_data in lista_de_sql_data:
            valores_estaca = [sql_data.get(col, None) for col in colunas_db]
            lista_de_valores.append(tuple(valores_estaca))

        cursor.executemany(sql_query, lista_de_valores)
        print("Inserção em massa concluída.")

        conn.commit()
        conn.close()

        print("RODANDO VERSÃO PRO-006 (Cérebro).")
        return True, None

    except Exception as e:
        print(f"ERRO NO PROCESSAMENTO PRO-006: {e}")
        traceback.print_exc()
        if conn:
            conn.rollback()
            conn.close()
        return False, str(e)


# --- 3. ROTAS FLASK ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'planilha' not in request.files: return "Nenhum arquivo encontrado!"
    file = request.files['planilha']
    if file.filename == '': return "Nenhum arquivo selecionado!"

    linha_inicial = request.form['linha_inicial']
    tipo_pista = request.form['tipo_pista'] 

    if file:
        caminho_seguro = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(caminho_seguro)

        sucesso, erro = processar_planilha_pro006(caminho_seguro, linha_inicial, tipo_pista)

        if sucesso:
            return redirect(url_for('relatorio'))
        else:
            return f"Erro: {erro}"

@app.route('/relatorio')
def relatorio():
    return "Processamento Concluído! O relatório PRO-006 será exibido aqui."

if __name__ == '__main__':
    app.run(debug=True, port=5001)