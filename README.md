# Controle de Ponto Pessoal

Aplicação para controle de ponto pessoal com front-end em React + TypeScript e backend em Streamlit.

## Funcionalidades

- Registro de horários diários (entrada, saída para almoço, volta do almoço, saída final)
- Cálculo de horas trabalhadas no dia e saldo diário
- Saldo acumulado no mês ou período selecionado
- Relatório gráfico (barras por dia e linha acumulada)
- Persistência de dados em SQLite

## Regras de Negócio

- Entradas por dia: data, hora_entrada, hora_saida_almoco, hora_volta_almoco, hora_saida_final, observação (opcional)
- Cálculo de horas no dia: H_dia = (SA - E) + (S - VA)
- Saldo diário: Saldo_dia = H_dia - H_esperada
- Saldo do período: Saldo_período = Σ Saldo_dia
- Dias úteis padrão: seg–sex
- Validação: E < SA ≤ VA < S
- Granularidade em minutos, exibição em HH:MM

## Configurações

- Carga horária diária esperada (padrão 8:00)
- Jornada padrão (entrada 08:30, saída 18:00, almoço 1:30)
- Dias úteis (checkboxes seg–sex)
- “Contar ausência como débito”
- Arredondamento opcional (5/10/15 min)

## Stack Tecnológico

- **Front-end**: React 18 + TypeScript com Vite, Chakra UI, Recharts, dayjs
- **Backend/Host**: Python 3.10+ com Streamlit, SQLite via sqlite3, Pandas
- **Integração**: Componente personalizado Streamlit ↔ React via `streamlit.components.v1`

## Estrutura do Projeto

```
controle_ponto/
├── frontend/          # React + TS app
│   ├── src/
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
├── backend/           # Python modules
│   ├── db.py
│   └── calculos.py
├── tests/             # Test files
├── app.py             # Streamlit main app
└── README.md
```

## Setup

### Pré-requisitos

- Node.js 18+ (para front-end)
- Python 3.10+ (para backend)
- npm ou yarn

### Instalação

1. **Front-end**:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Backend**:
   ```bash
   pip install streamlit pandas
   ```

### Execução

```bash
streamlit run app.py
```

O banco de dados SQLite (`controle_ponto.db`) será criado automaticamente na primeira execução.

## Modelo de Dados

### Tabela `lancamentos`
- id (PK)
- data (DATE)
- entrada (TEXT, HH:MM)
- saida_almoco (TEXT, HH:MM)
- volta_almoco (TEXT, HH:MM)
- saida (TEXT, HH:MM)
- observacao (TEXT)
- valido (BOOLEAN)
- feriado (BOOLEAN, default FALSE)

### Tabela `configuracoes`
- id (PK, default 1)
- carga_horaria_diaria_min (INTEGER, default 480)
- entrada_padrao (TEXT, default '08:30')
- saida_padrao (TEXT, default '18:00')
- almoco_padrao_min (INTEGER, default 90)
- considerar_ausencia_como_debito (BOOLEAN, default FALSE)
- dias_uteis (TEXT, JSON array)
- arredondamento_min (INTEGER, nullable)

## Critérios de Aceitação

- Dado E=08:30, SA=12:00, VA=13:30, S=18:00, H_esperada=8:00:
  - H_dia = 8:00; Saldo_dia = 0:00
- Dado E=08:25, SA=12:05, VA=13:35, S=19:10:
  - H_dia = 9:15; Saldo_dia = +1:15
- Dado E=08:40, SA=12:10, VA=13:40, S=17:35:
  - H_dia = 7:25; Saldo_dia = -0:35
- Mês com 22 dias úteis:
  - Sem “ausência como débito”: dias sem lançamento não entram no esperado
  - Com “ausência como débito”: cada dia útil sem lançamento subtrai 8:00 do saldo

## Testes

### Python (pytest)
```bash
pip install pytest
pytest tests/
```

### Front-end (Vitest)
```bash
cd frontend
npm test
```

## Export/Import CSV

- **Exportar**: Botão na sidebar gera CSV com lançamentos do período e resumo
- **Importar**: Funcionalidade opcional para importar lançamentos via CSV

## Desenvolvimento

- Código limpo, documentado e modular
- Funções puras para cálculos (testáveis)
- UI responsiva e intuitiva
- Validações claras para entradas inválidas