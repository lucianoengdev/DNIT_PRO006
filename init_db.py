import sqlite3
conn = sqlite3.connect('projeto_pro006.db') # Novo nome de arquivo!
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS estacas')
cursor.execute('''
CREATE TABLE estacas (
    id INTEGER PRIMARY KEY AUTOINCREMENT, km REAL NOT NULL,
    area_g1_le REAL, fr_g1_le REAL, igi_g1_le REAL, area_g1_ld REAL, fr_g1_ld REAL, igi_g1_ld REAL,
    area_g2_le REAL, fr_g2_le REAL, igi_g2_le REAL, area_g2_ld REAL, fr_g2_ld REAL, igi_g2_ld REAL,
    area_g3_le REAL, fr_g3_le REAL, igi_g3_le REAL, area_g3_ld REAL, fr_g3_ld REAL, igi_g3_ld REAL,
    area_g4_le REAL, fr_g4_le REAL, igi_g4_le REAL, area_g4_ld REAL, fr_g4_ld REAL, igi_g4_ld REAL,
    area_g5_le REAL, fr_g5_le REAL, igi_g5_le REAL, area_g5_ld REAL, fr_g5_ld REAL, igi_g5_ld REAL,
    area_g6_le REAL, fr_g6_le REAL, igi_g6_le REAL, area_g6_ld REAL, fr_g6_ld REAL, igi_g6_ld REAL,
    area_g7_le REAL, fr_g7_le REAL, igi_g7_le REAL, area_g7_ld REAL, fr_g7_ld REAL, igi_g7_ld REAL,
    area_g8_le REAL, fr_g8_le REAL, igi_g8_le REAL, area_g8_ld REAL, fr_g8_ld REAL, igi_g8_ld REAL,
    igg_defeitos_g1_g8 REAL,
    valor_tri_le REAL, valor_tri_ld REAL, valor_tre_le REAL, valor_tre_ld REAL,
    mean_le REAL, mean_ld REAL, var_le REAL, var_ld REAL,
    tri_agg REAL, tre_agg REAL,
    igi_trilha REAL, igi_var REAL, igi_flechas_final REAL,
    igg_total_final_estaca REAL
);
''')
conn.commit()
conn.close()
print("Banco de dados 'projeto_pro006.db' (V3) criado com sucesso!")