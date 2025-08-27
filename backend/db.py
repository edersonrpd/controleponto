import sqlite3
import json
from datetime import date

def init_db():
    conn = sqlite3.connect('controle_ponto.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS lancamentos (
        id INTEGER PRIMARY KEY,
        data DATE,
        entrada TEXT,
        saida_almoco TEXT,
        volta_almoco TEXT,
        saida TEXT,
        observacao TEXT,
        valido BOOLEAN DEFAULT 1,
        feriado BOOLEAN DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS configuracoes (
        id INTEGER PRIMARY KEY DEFAULT 1,
        carga_horaria_diaria_min INTEGER DEFAULT 480,
        entrada_padrao TEXT DEFAULT '08:30',
        saida_padrao TEXT DEFAULT '18:00',
        almoco_padrao_min INTEGER DEFAULT 90,
        considerar_ausencia_como_debito BOOLEAN DEFAULT 0,
        dias_uteis TEXT DEFAULT '["seg","ter","qua","qui","sex"]',
        arredondamento_min INTEGER
    )''')
    # Inserir config padrão se não existir
    c.execute('INSERT OR IGNORE INTO configuracoes (id) VALUES (1)')
    conn.commit()
    conn.close()

def get_lancamentos(start_date, end_date):
    conn = sqlite3.connect('controle_ponto.db')
    c = conn.cursor()
    c.execute('SELECT * FROM lancamentos WHERE data BETWEEN ? AND ? ORDER BY data', (start_date, end_date))
    rows = c.fetchall()
    conn.close()
    return [{'id': r[0], 'data': r[1], 'entrada': r[2], 'saida_almoco': r[3], 'volta_almoco': r[4], 'saida': r[5], 'observacao': r[6], 'valido': bool(r[7]), 'feriado': bool(r[8])} for r in rows]

def save_lancamento(lancamento):
    conn = sqlite3.connect('controle_ponto.db')
    c = conn.cursor()
    c.execute('INSERT INTO lancamentos (data, entrada, saida_almoco, volta_almoco, saida, observacao) VALUES (?, ?, ?, ?, ?, ?)',
              (lancamento['data'], lancamento['entrada'], lancamento['saida_almoco'], lancamento['volta_almoco'], lancamento['saida'], lancamento['observacao']))
    conn.commit()
    conn.close()

def delete_lancamento(id):
    conn = sqlite3.connect('controle_ponto.db')
    c = conn.cursor()
    c.execute('DELETE FROM lancamentos WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def get_config():
    conn = sqlite3.connect('controle_ponto.db')
    c = conn.cursor()
    c.execute('SELECT * FROM configuracoes WHERE id = 1')
    row = c.fetchone()
    conn.close()
    return {
        'carga_horaria_diaria_min': row[1],
        'entrada_padrao': row[2],
        'saida_padrao': row[3],
        'almoco_padrao_min': row[4],
        'considerar_ausencia_como_debito': bool(row[5]),
        'dias_uteis': json.loads(row[6]),
        'arredondamento_min': row[7]
    }

def save_config(config):
    conn = sqlite3.connect('controle_ponto.db')
    c = conn.cursor()
    c.execute('UPDATE configuracoes SET carga_horaria_diaria_min = ?, entrada_padrao = ?, saida_padrao = ?, almoco_padrao_min = ?, considerar_ausencia_como_debito = ?, dias_uteis = ?, arredondamento_min = ? WHERE id = 1',
              (config['carga_horaria_diaria_min'], config['entrada_padrao'], config['saida_padrao'], config['almoco_padrao_min'], config['considerar_ausencia_como_debito'], json.dumps(config['dias_uteis']), config['arredondamento_min']))
    conn.commit()
    conn.close()