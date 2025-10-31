import sqlite3

conn = sqlite3.connect('projeto_pro006.db')
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS estacas')

# Cria a nova tabela (V5) com o G5 agrupado
cursor.execute('''
CREATE TABLE estacas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    km REAL NOT NULL,
    km_segmento INTEGER NOT NULL, 

    tipo_pista TEXT NOT NULL,
    modo_calculo TEXT NOT NULL, -- Nova coluna
    foi_inventariada INTEGER NOT NULL,

    -- Colunas BINÁRIAS (1 ou 0) para defeitos agrupados
    g1 INTEGER DEFAULT 0,
    g2 INTEGER DEFAULT 0,
    g3 INTEGER DEFAULT 0,
    g4 INTEGER DEFAULT 0,
    g5 INTEGER DEFAULT 0, -- CORREÇÃO: G5 (O, P, E) agora é um grupo

    -- Colunas BINÁRIAS (1 ou 0) para defeitos individuais
    d_ex INTEGER DEFAULT 0,
    d_d INTEGER DEFAULT 0,
    d_r INTEGER DEFAULT 0,

    -- Colunas para o cálculo das Flechas (FCH)
    fch_media_estaca REAL DEFAULT 0.0,
    fch_var_estaca REAL DEFAULT 0.0
);
''')

conn.commit()
conn.close()

print("Banco de dados 'projeto_pro006.db' (V5) criado com sucesso!")
print("Tabela 'estacas' atualizada com G5 agrupado e 'modo_calculo'.")