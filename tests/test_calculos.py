import pytest
from backend.calculos import time_to_minutes, minutes_to_time, calcular_horas_dia, calcular_saldo_dia, validar_lancamento, arredondar_minutos

def test_time_to_minutes():
    assert time_to_minutes('08:30') == 510
    assert time_to_minutes('18:00') == 1080

def test_minutes_to_time():
    assert minutes_to_time(510) == '08:30'
    assert minutes_to_time(1080) == '18:00'

def test_calcular_horas_dia():
    # E=08:30, SA=12:00, VA=13:30, S=18:00 -> 8:00
    assert calcular_horas_dia('08:30', '12:00', '13:30', '18:00') == 480
    # E=08:25, SA=12:05, VA=13:35, S=19:10 -> 9:15
    assert calcular_horas_dia('08:25', '12:05', '13:35', '19:10') == 555

def test_calcular_saldo_dia():
    assert calcular_saldo_dia(480, 480) == 0
    assert calcular_saldo_dia(555, 480) == 75

def test_validar_lancamento():
    assert validar_lancamento({'entrada': '08:30', 'saida_almoco': '12:00', 'volta_almoco': '13:30', 'saida': '18:00'})
    assert not validar_lancamento({'entrada': '18:00', 'saida_almoco': '12:00', 'volta_almoco': '13:30', 'saida': '08:00'})

def test_arredondar_minutos():
    assert arredondar_minutos(62, 5) == 60
    assert arredondar_minutos(63, 5) == 65
    assert arredondar_minutos(62, None) == 62