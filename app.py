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

# --- CONSTANTES PRO-006 (CORRIGIDAS V2) ---
FATORES_PONDERACAO = {
    'G1': 0.2, 'G2': 0.5, 'G3': 0.8,
    'G4A': 0.9, 'G4B': 0.9, # G4 dividido, ambos 0.9
    'D_O': 1.0, 'D_P': 1.0, 'D_E': 1.0, # G5 individual
    'D_EX': 0.5, 'D_D': 0.3, 'D_R': 0.6
}

# --- MAPEAMENTO DE COLUNAS (CORRIGIDO V2) ---
COLUNA_KM = 0
MAPA_COLUNAS_LE = {
    'OK': 1, 'G1': [2, 3, 4, 5, 6, 7], 'G2': [8, 9], 'G3': [10, 11],
    'G4A': [12, 13], # G4a (ALP, ATP)
    'G4B': [14, 15], # G4b (ALC, ATC)
    'D_O': 16, 'D_P': 17, 'D_E': 18, # G5
    'D_EX': 19, 'D_D': 20, 'D_R': 21, 'TRI': 22, 'TRE': 23
}
MAPA_COLUNAS_LD = {
    'OK': 24, 'G1': [25, 26, 27, 28, 29, 30], 'G2': [31, 32], 'G3': [33, 34],
    'G4A': [35, 36], # G4a
    'G4B': [37, 38], # G4b
    'D_O': 39, 'D_P': 40, 'D_E': 41, # G5
    'D_EX': 42, 'D_D': 43, 'D_R': 44, 'TRI': 45, 'TRE': 46
}

# Novas listas de chaves
DEFEITOS_AGRUPADOS = ['G1', 'G2', 'G3', 'G4A', 'G4B']
DEFEITOS_INDIVIDUAIS = ['D_O', 'D_P', 'D_E', 'D_EX', 'D_D', 'D_R']
TODOS_DEFEITOS_CHAVES = DEFEITOS_AGRUPADOS + DEFEITOS_INDIVIDUAIS

# --- 2. FUNÇÕES "AJUDANTES" ---
def normalizar_valor(valor):
    if isinstance(valor, (int, float)): return float(valor)
    if not isinstance(valor, str): return 0.0
    valor = valor.strip()
    if valor == "": return 0.0
    valor = valor.replace(",", ".")
    try:
        val_float = float(valor)
        return val_float
    except ValueError:
        return 1.0 

def normalizar_binario(valor):
    return 1 if normalizar_valor(valor) > 0 else 0

def calcular_variancia(valores):
    valores_validos = [v for v in valores if v > 0]
    n = len(valores_validos)
    if n < 2: return 0.0
    media = sum(valores_validos) / n
    soma_quadrados = sum([(x - media) ** 2 for x in valores_validos])
    return soma_quadrados / (n - 1)

# --- 3. O "CÉREBRO" (V8) ---
def processar_planilha_pro006(caminho_arquivo, linha_dados_str, tipo_pista, modo_calculo):
    conn = sqlite3.connect('projeto_pro006.db')
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM estacas')

        skip_rows = int(linha_dados_str) - 1
        df = pd.read_excel(caminho_arquivo, header=None, skiprows=skip_rows, dtype=object)

        print(f"Iniciando processamento PRO-006. Modo: {modo_calculo}, Tipo: {tipo_pista}.")

        estaca_index = 0
        lista_de_sql_data = []

        for _, row in df.iterrows():
            estaca_index += 1
            km = row.get(COLUNA_KM)
            if pd.isna(km) or str(km).strip() == "": continue
            km_val = normalizar_valor(km)
            km_segmento = math.floor(km_val)

            # Nova estrutura do sql_data
            sql_data = {
                'km': km_val, 'km_segmento': km_segmento, 
                'tipo_pista': tipo_pista, 'modo_calculo': modo_calculo,
                'foi_inventariada': 0, 
                'g1': 0, 'g2': 0, 'g3': 0, 'g4a': 0, 'g4b': 0,
                'd_o': 0, 'd_p': 0, 'd_e': 0, 'd_ex': 0, 'd_d': 0, 'd_r': 0,
                'fch_media_estaca': 0.0, 'fch_var_estaca': 0.0
            }

            if modo_calculo == 'intercalado':
                is_odd = (estaca_index % 2 != 0)
                mapa_defeitos = None
                if tipo_pista == 'terceira_faixa':
                    if is_odd:
                        sql_data['foi_inventariada'] = 1
                        mapa_defeitos = MAPA_COLUNAS_LE
                elif tipo_pista == 'simples' or tipo_pista == 'dupla':
                    sql_data['foi_inventariada'] = 1
                    mapa_defeitos = MAPA_COLUNAS_LD if is_odd else MAPA_COLUNAS_LE

                if sql_data['foi_inventariada'] == 1 and mapa_defeitos:
                    # Cálculos de Defeitos (G1-G4b)
                    for grupo in DEFEITOS_AGRUPADOS:
                        for col_idx in mapa_defeitos[grupo]:
                            if normalizar_binario(row.get(col_idx)) == 1:
                                sql_data[grupo.lower()] = 1; break
                    # Defeitos Individuais (O, P, E, etc.)
                    for defeito in DEFEITOS_INDIVIDUAIS:
                        col_idx = mapa_defeitos[defeito]
                        sql_data[defeito.lower()] = normalizar_binario(row.get(col_idx))

                    if sql_data['g3'] == 1: sql_data['g1'] = 0; sql_data['g2'] = 0
                    elif sql_data['g2'] == 1: sql_data['g1'] = 0

                    tri = normalizar_valor(row.get(mapa_defeitos['TRI']))
                    tre = normalizar_valor(row.get(mapa_defeitos['TRE']))
                    sql_data['fch_media_estaca'] = (tri + tre) / 2
                    sql_data['fch_var_estaca'] = calcular_variancia([tri, tre])

            elif modo_calculo == 'somado':
                sql_data['foi_inventariada'] = 1

                # Defeitos Agrupados (Soma LE+LD)
                for grupo in DEFEITOS_AGRUPADOS:
                    if sql_data[grupo.lower()] == 0:
                        for col_idx in MAPA_COLUNAS_LE[grupo]:
                            if normalizar_binario(row.get(col_idx)) == 1:
                                sql_data[grupo.lower()] = 1; break
                    if sql_data[grupo.lower()] == 0:
                        for col_idx in MAPA_COLUNAS_LD[grupo]:
                            if normalizar_binario(row.get(col_idx)) == 1:
                                sql_data[grupo.lower()] = 1; break

                # Defeitos Individuais (Soma LE+LD)
                for defeito in DEFEITOS_INDIVIDUAIS:
                    col_le = MAPA_COLUNAS_LE[defeito]
                    col_ld = MAPA_COLUNAS_LD[defeito]
                    if normalizar_binario(row.get(col_le)) == 1 or normalizar_binario(row.get(col_ld)) == 1:
                        sql_data[defeito.lower()] = 1

                if sql_data['g3'] == 1: sql_data['g1'] = 0; sql_data['g2'] = 0
                elif sql_data['g2'] == 1: sql_data['g1'] = 0

                tri_le = normalizar_valor(row.get(MAPA_COLUNAS_LE['TRI']))
                tre_le = normalizar_valor(row.get(MAPA_COLUNAS_LE['TRE']))
                tri_ld = normalizar_valor(row.get(MAPA_COLUNAS_LD['TRI']))
                tre_ld = normalizar_valor(row.get(MAPA_COLUNAS_LD['TRE']))

                sql_data['fch_media_estaca'] = (tri_le + tre_le + tri_ld + tre_ld) / 4
                sql_data['fch_var_estaca'] = calcular_variancia([tri_le, tre_le, tri_ld, tre_ld])

            lista_de_sql_data.append(sql_data)

        # --- 5. INSERIR TUDO NO BANCO DE DADOS ---
        print(f"Processamento concluído. Inserindo {len(lista_de_sql_data)} estacas no banco...")

        cursor.execute("PRAGMA table_info(estacas)")
        colunas_db = [info[1] for info in cursor.fetchall() if info[1] != 'id']
        placeholders = ', '.join(['?' for _ in colunas_db])
        nomes_colunas = ', '.join(colunas_db)
        sql_query = f"INSERT INTO estacas ({nomes_colunas}) VALUES ({placeholders})"

        lista_de_valores = []
        for sql_data in lista_de_sql_data:
            valores_estaca = [sql_data.get(col, 0.0) for col in colunas_db] # Padrão 0.0
            lista_de_valores.append(tuple(valores_estaca))

        cursor.executemany(sql_query, lista_de_valores)

        # Limpeza de NULLs (ainda uma boa prática)
        colunas_para_limpar = [col for col in colunas_db if col not in ['km', 'km_segmento', 'tipo_pista', 'modo_calculo']]
        for col in colunas_para_limpar:
            cursor.execute(f"UPDATE estacas SET {col} = 0.0 WHERE {col} IS NULL")

        conn.commit()
        conn.close()

        print("Cérebro PRO-006 (V8 - G4/G5 Corrigidos) concluído.")
        return True, None

    except Exception as e:
        print(f"ERRO NO PROCESSAMENTO PRO-006: {e}")
        traceback.print_exc()
        if conn: conn.rollback(); conn.close()
        return False, str(e)


# --- 4. ROTA DE RELATÓRIO (V8) ---
@app.route('/relatorio')
def relatorio():
    conn = None
    try:
        conn = sqlite3.connect('projeto_pro006.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # --- 1. GRÁFICO 1 ---
        cursor.execute("SELECT km, fch_media_estaca FROM estacas WHERE foi_inventariada = 1 ORDER BY km")
        estacas = cursor.fetchall()
        x_km = [row['km'] for row in estacas]; y_fch = [row['fch_media_estaca'] for row in estacas]
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=x_km, y=y_fch, mode='lines+markers', name='Média Flechas (FCH)'))
        fig1.update_layout(title="Linear de Ocorrência (Média FCH por Estaca Inventariada)",
                           xaxis_title="Quilômetro (km)", yaxis_title="Média FCH (mm)", hovermode="x unified")
        graphJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

        # --- 2. CÁLCULO DO IGG POR SEGMENTO (V8) ---
        # As chaves de defeito agora estão 100% corretas
        defeitos_sql = TODOS_DEFEITOS_CHAVES
        select_defeitos_sql = ", ".join([f"SUM({chave.lower()}) as f_abs_{chave.lower()}" for chave in defeitos_sql])

        query_segmentos = f"""
            SELECT 
                km_segmento, tipo_pista, modo_calculo,
                SUM(foi_inventariada) as N,
                AVG(fch_media_estaca) as media_fch,
                AVG(fch_var_estaca) as media_var,
                MIN(km) as km_inicio,
                MAX(km) + 0.020 as km_fim_corrigido,
                {select_defeitos_sql}
            FROM estacas
            WHERE foi_inventariada = 1
            GROUP BY km_segmento
            ORDER BY km_segmento
        """
        cursor.execute(query_segmentos)
        segmentos_db = cursor.fetchall()
        conn.close()

        segmentos_resumo = []
        igg_para_grafico_2 = []
        memoria_de_calculo = [] # A memória agora reflete a nova estrutura

        for row in segmentos_db:
            N = row['N']
            if N == 0: continue

            n_calculo = N # Usa o N real do segmento

            detalhes = {'km_segmento': row['km_segmento'], 'N': n_calculo}
            igg_defeitos_total = 0.0

            for chave in TODOS_DEFEITOS_CHAVES: # Loop nas chaves G1, G2, G3, G4A, G4B, D_O, etc.
                chave_sql = f"f_abs_{chave.lower()}"
                fp_chave = chave.upper()

                f_abs = row[chave_sql]
                f_r = (f_abs * 100) / n_calculo
                fp = FATORES_PONDERACAO[fp_chave]
                igi = f_r * fp

                igg_defeitos_total += igi

                detalhes[f'f_abs_{chave.lower()}'] = f_abs
                detalhes[f'f_r_{chave.lower()}'] = f_r
                detalhes[f'igi_{chave.lower()}'] = igi

            media_fch = row['media_fch']
            media_var = row['media_var']

            igi_trilha = 0.0
            if media_fch <= 30:
                igi_trilha = media_fch * (4/3)
            else:
                igi_trilha = 40.0

            igi_flecha_final = igi_trilha
            if media_var > 50:
                igi_flecha_final = 50.0

            detalhes['media_fch'] = media_fch
            detalhes['media_var'] = media_var
            detalhes['igi_trilha'] = igi_trilha
            detalhes['igi_flecha_final'] = igi_flecha_final

            igg_final_segmento = igg_defeitos_total + igi_flecha_final
            detalhes['igg_final'] = igg_final_segmento

            segmentos_resumo.append({
                'km_segmento': row['km_segmento'],
                'km_inicio': row['km_inicio'],
                'km_fim_corrigido': row['km_fim_corrigido'],
                'igg_soma': igg_final_segmento
            })
            igg_para_grafico_2.append(igg_final_segmento)
            memoria_de_calculo.append(detalhes)

        # --- 3. GRÁFICO 2 ---
        x_segmento = [f"km {int(row['km_segmento'])}" for row in segmentos_resumo]
        y_igg_soma = igg_para_grafico_2
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=x_segmento, y=y_igg_soma, mode='lines+markers', name='IGG por Segmento'))

        y_max_soma = max(y_igg_soma) if y_igg_soma else 160
        fig2.add_hrect(y0=0, y1=20, line_width=0, fillcolor='green', opacity=0.1, layer="below", annotation_text="Ótimo", annotation_position="right")
        fig2.add_hrect(y0=20, y1=40, line_width=0, fillcolor='yellow', opacity=0.1, layer="below", annotation_text="Bom", annotation_position="right")
        fig2.add_hrect(y0=40, y1=80, line_width=0, fillcolor='orange', opacity=0.1, layer="below", annotation_text="Regular", annotation_position="right")
        fig2.add_hrect(y0=80, y1=160, line_width=0, fillcolor='red', opacity=0.1, layer="below", annotation_text="Ruim", annotation_position="right")
        fig2.add_hrect(y0=160, y1=max(161, y_max_soma + 50), line_width=0, fillcolor='maroon', opacity=0.1, layer="below", annotation_text="Péssimo", annotation_position="right")
        fig2.update_layout(title="IGG por Segmento (Soma dos IGIs - PRO-006)",
                           xaxis_title="Segmento de 1km", yaxis_title="IGG (ΣIGI)", hovermode="x unified")
        graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('relatorio.html', 
                               graphJSON=graphJSON1, 
                               graphJSON2=graphJSON2, 
                               segmentos=segmentos_resumo,
                               memoria=memoria_de_calculo)

    except Exception as e:
        if conn: conn.close()
        print(f"Erro ao gerar relatório PRO-006: {e}")
        traceback.print_exc()
        return "Erro ao gerar relatório. Verifique os dados no banco."

# --- 5. ROTAS DE CONTROLE ---
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
    modo_calculo = request.form['modo_calculo']

    if file:
        caminho_seguro = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(caminho_seguro)

        sucesso, erro = processar_planilha_pro006(caminho_seguro, linha_inicial, tipo_pista, modo_calculo)

        if sucesso:
            return redirect(url_for('relatorio'))
        else:
            return f"Erro: {erro}"

if __name__ == '__main__':
    app.run(debug=True, port=5001)