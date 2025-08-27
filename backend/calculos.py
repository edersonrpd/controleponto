def time_to_minutes(time_str):
    h, m = map(int, time_str.split(':'))
    return h * 60 + m

def minutes_to_time(minutes):
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"

def calcular_horas_dia(entrada, saida_almoco, volta_almoco, saida):
    e = time_to_minutes(entrada)
    sa = time_to_minutes(saida_almoco)
    va = time_to_minutes(volta_almoco)
    s = time_to_minutes(saida)
    return (sa - e) + (s - va)

def calcular_saldo_dia(horas_trabalhadas_min, carga_esperada_min):
    return horas_trabalhadas_min - carga_esperada_min

def calcular_saldo_periodo(saldos_diarios):
    return sum(saldos_diarios)

def validar_lancamento(lancamento):
    try:
        e = time_to_minutes(lancamento['entrada'])
        sa = time_to_minutes(lancamento['saida_almoco'])
        va = time_to_minutes(lancamento['volta_almoco'])
        s = time_to_minutes(lancamento['saida'])
        return e < sa <= va < s
    except:
        return False

def arredondar_minutos(minutos, arredondamento):
    if not arredondamento:
        return minutos
    resto = minutos % arredondamento
    if resto >= arredondamento / 2:
        return minutos + (arredondamento - resto)
    else:
        return minutos - resto