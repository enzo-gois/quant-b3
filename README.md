# quant-b3

Projeto de estudo em Python sobre **análise quantitativa de ações da B3**.

A ideia é aprender, na prática, como o mercado financeiro mede retorno e risco de um investimento,
escrevendo cada cálculo do zero com `pandas` e `numpy`, em vez de usar bibliotecas prontas de finanças.

## O que o projeto faz

- Baixa 5 anos de preços diários de cinco ações (Itaú, Bradesco, Petrobras, Vale e WEG) e do Ibovespa.
- Baixa o CDI diário direto da API do Banco Central, usado como referência de "dinheiro sem risco".
- Limpa e organiza os dados (feriados, dias sem negociação) e guarda em cache local.
- Calcula, para cada ativo, retorno, volatilidade, maior queda (drawdown) e índice de Sharpe.
- Gera uma tabela-resumo e gráficos comparando os ativos com o Ibovespa e o CDI.

## Conceitos estudados

| Conceito                      |
| ----------------------------- | ------------------------------------------------------------------------------------- |
| Preço ajustado                | Preço corrigido por dividendos e desdobramentos, para não distorcer o retorno         |
| Retorno simples e logarítmico | Duas formas de medir quanto um ativo variou de um dia para o outro                    |
| Retorno anualizado            | Taxa por ano equivalente ao ganho do período inteiro                                  |
| Volatilidade                  | O quanto o preço oscila; a medida de risco mais usada                                 |
| Drawdown                      | A maior queda desde o último topo, ou seja, o "susto" que o investidor teria passado  |
| Índice de Sharpe              | Quanto o ativo rendeu acima do CDI para cada unidade de risco                         |
| CDI                           | Taxa de juros entre bancos, usada como referência de investimento sem risco no Brasil |

## Tecnologias

- **Python 3.11+**
- **pandas** e **numpy**: manipulação de séries temporais e cálculos
- **matplotlib**: gráficos
- **yfinance** e **requests**: coleta de dados (Yahoo Finance e API do Banco Central)
- **pytest**: testes automatizados com valores calculados à mão

## Estrutura

```
quant-b3/
├── config.py               # ativos, período e caminhos
├── main.py                 # roda o pipeline e gera o relatório
├── src/quant_b3/
│   ├── data.py             # coleta, limpeza e cache dos dados
│   ├── metrics.py          # retorno, volatilidade, drawdown e Sharpe
│   └── plots.py            # gráficos
├── tests/                  # testes de dados e métricas
└── reports/                # tabela-resumo e gráficos gerados
```

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
pip install -e .

python main.py                # gera reports/summary.csv e os gráficos
pytest                        # roda os testes
```

## Boas práticas aplicadas

- Lógica separada em módulos dentro de `src/`, com funções pequenas e tipadas.
- Testes com séries pequenas cujo resultado pode ser conferido à mão.
- Cache local para não baixar os dados toda vez.
- Versões das dependências fixadas para o resultado ser reproduzível.

## Próximos passos

- [x] Coleta e limpeza de dados
- [x] Métricas de retorno e risco
- [ ] Correlação entre ativos e montagem de carteiras (teoria de Markowitz)
- [ ] Teste de uma estratégia simples de compra e venda (backtest)

> Projeto com fins de estudo. Nada aqui é recomendação de investimento.
