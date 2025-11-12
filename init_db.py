import sqlite3

conn = sqlite3.connect('projeto_pro006.db')
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS estacas')

cursor.execute('''
CREATE TABLE estacas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    km REAL NOT NULL,
    km_segmento INTEGER NOT NULL, 

    tipo_pista TEXT NOT NULL,
    modo_calculo TEXT NOT NULL,
    modo_segmentacao TEXT NOT NULL, -- <-- A CORREÇÃO ESTÁ AQUI
    foi_inventariada INTEGER NOT NULL,

    -- Colunas BINÁRIAS (1 ou 0) para defeitos agrupados
    g1 INTEGER DEFAULT 0,
    g2 INTEGER DEFAULT 0,
    g3 INTEGER DEFAULT 0,
    g4a INTEGER DEFAULT 0,
    g4b INTEGER DEFAULT 0,

    -- Colunas BINÁRIAS (1 ou 0) para defeitos individuais
    d_o INTEGER DEFAULT 0,
    d_p INTEGER DEFAULT 0,
    d_e INTEGER DEFAULT 0,
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

print("Banco de dados 'projeto_pro006.db' (V7) criado com sucesso!")
print("Coluna 'modo_segmentacao' foi adicionada.")