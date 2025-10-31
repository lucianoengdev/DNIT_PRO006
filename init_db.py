import sqlite3

# Conecta ao banco de dados (cria o arquivo se não existir)
conn = sqlite3.connect('projeto_pro006.db')
cursor = conn.cursor()

# Destrói a tabela 'estacas' antiga (se ela existir)
cursor.execute('DROP TABLE IF EXISTS estacas')

# Cria a nova tabela 'estacas' (V4) com a lógica BINÁRIA do PRO-006
cursor.execute('''
CREATE TABLE estacas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    km REAL NOT NULL,
    km_segmento INTEGER NOT NULL, -- Para agrupar (ex: 0, 1, 2)

    tipo_pista TEXT NOT NULL,      -- 'simples', 'dupla', 'terceira_faixa'
    foi_inventariada INTEGER NOT NULL, -- 1 se foi, 0 se não foi

    -- Colunas BINÁRIAS (1 ou 0) para defeitos agrupados
    g1 INTEGER DEFAULT 0,
    g2 INTEGER DEFAULT 0,
    g3 INTEGER DEFAULT 0,
    g4 INTEGER DEFAULT 0,

    -- Colunas BINÁRIAS (1 ou 0) para defeitos individuais (do G5 em diante)
    d_o INTEGER DEFAULT 0, -- Defeito 'O'
    d_p INTEGER DEFAULT 0, -- Defeito 'P'
    d_e INTEGER DEFAULT 0, -- Defeito 'E'
    d_ex INTEGER DEFAULT 0,
    d_d INTEGER DEFAULT 0,
    d_r INTEGER DEFAULT 0,

    -- Colunas para o cálculo das Flechas (FCH)
    -- Estes são os valores calculados (média e variância) daquela estaca
    fch_media_estaca REAL DEFAULT 0.0,
    fch_var_estaca REAL DEFAULT 0.0
);
''')

conn.commit()
conn.close()

print("Banco de dados 'projeto_pro006.db' (V4) criado com sucesso!")
print("Tabela 'estacas' agora usa a lógica binária (1/0) do PRO-006.")