import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import json
from datetime import datetime, date, timedelta
import pandas as pd
from backend.calculos import calcular_horas_dia, calcular_saldo_dia, calcular_saldo_periodo, validar_lancamento
from backend.db import init_db, get_lancamentos, save_lancamento, delete_lancamento, get_config, save_config
import os

def seed_data():
    lancamentos = [
        {'data': '2023-10-02', 'entrada': '08:30', 'saida_almoco': '12:00', 'volta_almoco': '13:30', 'saida': '18:00', 'observacao': 'Dia normal'},
        {'data': '2023-10-03', 'entrada': '08:25', 'saida_almoco': '12:05', 'volta_almoco': '13:35', 'saida': '19:10', 'observacao': 'Hora extra'},
        {'data': '2023-10-04', 'entrada': '08:40', 'saida_almoco': '12:10', 'volta_almoco': '13:40', 'saida': '17:35', 'observacao': 'Saída antecipada'},
        {'data': '2023-10-05', 'entrada': '08:30', 'saida_almoco': '12:00', 'volta_almoco': '13:30', 'saida': '18:00', 'observacao': 'Dia normal'},
        {'data': '2023-10-06', 'entrada': '08:30', 'saida_almoco': '12:00', 'volta_almoco': '13:30', 'saida': '18:00', 'observacao': 'Dia normal'}
    ]
    for l in lancamentos:
        save_lancamento(l)

# Inicializar banco
init_db()

# Componente React
if os.path.exists("frontend/dist"):
    controle_ponto = components.declare_component(
        "controle_ponto",
        path="frontend/dist"
    )
else:
    st.error("Front-end não encontrado. Execute 'cd frontend && npm install && npm run build' primeiro.")
    st.stop()

# Seed data if empty
if not get_lancamentos('2023-10-01', '2023-10-31'):
    seed_data()

# Funções auxiliares
def time_to_minutes(time_str):
    h, m = map(int, time_str.split(':'))
    return h * 60 + m

def minutes_to_time(minutes):
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"

def get_business_days(start_date, end_date, working_days):
    days = []
    current = start_date
    while current <= end_date:
        if current.strftime('%a').lower()[:3] in working_days:
            days.append(current)
        current += timedelta(days=1)
    return days

# Estado da sessão
if 'config' not in st.session_state:
    st.session_state.config = get_config()
if 'periodo' not in st.session_state:
    st.session_state.periodo = {'tipo': 'mes', 'inicio': date.today().replace(day=1).isoformat(), 'fim': date.today().isoformat()}
if 'lancamentos' not in st.session_state:
    st.session_state.lancamentos = get_lancamentos(st.session_state.periodo['inicio'], st.session_state.periodo['fim'])

# Calcular resumo e séries
def calcular_resumo():
    lancamentos = st.session_state.lancamentos
    config = st.session_state.config
    periodo = st.session_state.periodo

    total_trabalhado = 0
    total_esperado = 0
    saldo_diario = []
    saldo_acumulado = []
    acumulado = 0

    start_date = date.fromisoformat(periodo['inicio'])
    end_date = date.fromisoformat(periodo['fim'])
    business_days = get_business_days(start_date, end_date, config['dias_uteis'])

    for day in business_days:
        day_str = day.isoformat()
        lanc = next((l for l in lancamentos if l['data'] == day_str and l['valido']), None)
        if lanc:
            trabalhado = calcular_horas_dia(lanc['entrada'], lanc['saida_almoco'], lanc['volta_almoco'], lanc['saida'])
            saldo = calcular_saldo_dia(trabalhado, config['carga_horaria_diaria_min'])
            total_trabalhado += trabalhado
            total_esperado += config['carga_horaria_diaria_min']
            acumulado += saldo
        elif config['considerar_ausencia_como_debito']:
            saldo = -config['carga_horaria_diaria_min']
            total_esperado += config['carga_horaria_diaria_min']
            acumulado += saldo
        else:
            saldo = 0

        saldo_diario.append({'data': day_str, 'saldo_min': saldo})
        saldo_acumulado.append({'data': day_str, 'acumulado_min': acumulado})

    saldo_total = total_trabalhado - total_esperado
    media_por_dia = saldo_total / len(business_days) if business_days else 0

    return {
        'total_trabalhado_min': total_trabalhado,
        'total_esperado_min': total_esperado,
        'saldo_min': saldo_total,
        'media_por_dia_min': int(media_por_dia)
    }, {'saldo_diario': saldo_diario, 'saldo_acumulado': saldo_acumulado}

resumo, series = calcular_resumo()

# Renderizar componente
event = controle_ponto(
    config=st.session_state.config,
    periodo=st.session_state.periodo,
    lancamentos=st.session_state.lancamentos,
    resumo=resumo,
    series=series,
    key="controle_ponto"
)

# Processar eventos
if event:
    if event['action'] == 'create':
        payload = event['payload']
        if validar_lancamento(payload):
            save_lancamento(payload)
            st.session_state.lancamentos = get_lancamentos(st.session_state.periodo['inicio'], st.session_state.periodo['fim'])
            st.rerun()
    elif event['action'] == 'delete':
        delete_lancamento(event['payload']['id'])
        st.session_state.lancamentos = get_lancamentos(st.session_state.periodo['inicio'], st.session_state.periodo['fim'])
        st.rerun()
    elif event['action'] == 'set_config':
        save_config(event['payload'])
        st.session_state.config = get_config()
        st.rerun()
    elif event['action'] == 'set_period':
        st.session_state.periodo = event['payload']
        st.session_state.lancamentos = get_lancamentos(st.session_state.periodo['inicio'], st.session_state.periodo['fim'])
        st.rerun()
    elif event['action'] == 'export_csv':
        df = pd.DataFrame(st.session_state.lancamentos)
        csv = df.to_csv(index=False)
        st.download_button('Download CSV', csv, 'lancamentos.csv', 'text/csv')
    # Import CSV pode ser adicionado posteriormente