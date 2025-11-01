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
    foi_inventariada INTEGER NOT NULL,

    -- Defeitos Agrupados
    g1 INTEGER DEFAULT 0,
    g2 INTEGER DEFAULT 0,
    g3 INTEGER DEFAULT 0,
    g4a INTEGER DEFAULT 0, -- CORREÇÃO: G4a (ALP, ATP)
    g4b INTEGER DEFAULT 0, -- CORREÇÃO: G4b (ALC, ATC)

    -- Defeitos Individuais
    d_o INTEGER DEFAULT 0,  -- CORREÇÃO: G5 (O)
    d_p INTEGER DEFAULT 0,  -- CORREÇÃO: G5 (P)
    d_e INTEGER DEFAULT 0,  -- CORREÇÃO: G5 (E)
    d_ex INTEGER DEFAULT 0,
    d_d INTEGER DEFAULT 0,
    d_r INTEGER DEFAULT 0,

    -- Flechas (FCH)
    fch_media_estaca REAL DEFAULT 0.0,
    fch_var_estaca REAL DEFAULT 0.0
);
''')

conn.commit()
conn.close()
