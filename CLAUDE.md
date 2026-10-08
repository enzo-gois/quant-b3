# Projeto: Análise Quantitativa de Ações da B3

## Contexto

Sou o Enzo, desenvolvedor (Python, SQL, TypeScript, Java) no último período de ADS no IFPE.
Estou me candidatando a um programa quant do Itaú e quero construir este projeto para
**aprender finanças quantitativas de verdade**, não só ter código pronto.

Meu nível atual:
- Programação: intermediário. Já usei pandas e NumPy para gráficos em estudos de IA.
- Finanças: básico. Não presuma que conheço termos financeiros.
- Estatística: base da faculdade (média, desvio padrão, correlação), precisa ser relembrada.

O objetivo final é um repositório no GitHub que eu consiga **explicar linha por linha
numa entrevista técnica**.

---

## Regras de ensino (siga sempre)

1. **Uma fase por vez.** Nunca avance para a próxima fase sem eu escrever "pode seguir".
2. **Conceito antes do código.** Em cada etapa, explique primeiro o conceito financeiro ou
   estatístico em linguagem simples, com um exemplo numérico pequeno feito à mão.
   Depois mostre a fórmula. Só então o código.
3. **Eu escrevo partes importantes.** Deixe as funções centrais (cálculo de retorno,
   volatilidade, drawdown, Sharpe, sinal da estratégia) com marcadores `TODO(human)` para
   eu implementar. Você pode escrever a estrutura, a coleta de dados e os gráficos.
4. **Revise meu código como um mentor.** Quando eu implementar algo, aponte erros e
   melhorias, mas me dê dicas antes de dar a resposta pronta.
5. **Checkpoint ao fim de cada fase.** Faça 2 ou 3 perguntas curtas, no estilo de entrevista,
   para eu responder com minhas palavras. Corrija o que eu errar.
6. **Peça para eu atualizar o `APRENDIZADO.md`** ao fim de cada fase com um resumo meu
   (não escreva por mim; pode revisar depois).
7. **Seja honesto sobre limitações.** Se um resultado parecer bom demais, explique por quê
   pode ser ilusão (viés, overfitting, período escolhido).
8. **Responda em português.** Código e nomes de variáveis podem ser em inglês;
   comentários e docstrings em português.

---

## Stack e padrões

- Python 3.11+, ambiente virtual (`venv`), dependências em `requirements.txt`
- Bibliotecas: `pandas`, `numpy`, `matplotlib`, `yfinance`, `requests`, `scipy`, `pytest`
- Funções puras e tipadas (type hints), com docstrings curtas
- Nada de lógica escondida em notebook: a lógica fica em `src/`, notebooks só exploram
- Commits pequenos e descritivos ao fim de cada etapa (sugira a mensagem, eu faço o commit)

Estrutura esperada:

```
quant-b3/
├── CLAUDE.md
├── APRENDIZADO.md          # minhas anotações, escritas por mim
├── README.md
├── requirements.txt
├── config.py               # tickers, datas, parâmetros
├── data/                   # cache de dados (no .gitignore)
├── reports/figures/        # gráficos gerados
├── notebooks/exploracao.ipynb
├── src/quant_b3/
│   ├── data.py             # coleta e cache
│   ├── metrics.py          # retorno, volatilidade, drawdown, Sharpe
│   ├── portfolio.py        # carteiras e fronteira eficiente
│   └── backtest.py         # estratégia e backtest
├── tests/
│   ├── test_metrics.py
│   └── test_backtest.py
└── main.py                 # roda tudo e gera o relatório
```

---

## Roteiro do projeto

### Fase 0: Preparação
- Criar estrutura, venv, `requirements.txt`, `.gitignore`, repositório git.
- **Conceitos:** o que é uma ação, o que é o Ibovespa, o que é o CDI e por que ele é a
  referência de "dinheiro sem risco" no Brasil.

### Fase 1: Coleta de dados
- Baixar preços diários de 5 anos via `yfinance` para: `ITUB4.SA`, `BBDC4.SA`, `PETR4.SA`,
  `VALE3.SA`, `WEGE3.SA` e o índice `^BVSP`.
- Ser explícito sobre preço ajustado (`auto_adjust`) e explicar a diferença.
- Baixar o CDI diário da API do Banco Central (SGS, série 12). Verificar os limites de
  período da API e dividir a consulta se necessário.
- Salvar em cache local (CSV ou Parquet) para não baixar de novo toda vez.
- Tratar dados faltantes (feriados, dias sem negociação) e explicar a escolha.
- **Conceitos:** preço ajustado por dividendos e desdobramentos, dias úteis, por que dados
  sujos destroem análises.

### Fase 2: Retorno e risco de cada ativo
- Retorno diário simples e logarítmico; retorno acumulado; retorno anualizado (252 dias).
- Volatilidade anualizada.
- Drawdown e drawdown máximo.
- Índice de Sharpe usando o CDI como taxa livre de risco.
- Tabela-resumo comparando os ativos e o Ibovespa + gráficos de preço normalizado e drawdown.
- Testes com `pytest` usando séries pequenas com resultado calculado à mão.
- **Conceitos:** por que volatilidade mede risco (e o que ela não captura), risco × retorno,
  o que o Sharpe diz e quando engana.

### Fase 3: Correlação e carteira
- Matriz de correlação dos retornos + heatmap.
- Carteira de pesos iguais comparada com cada ativo isolado.
- Simulação de milhares de carteiras aleatórias (Monte Carlo) e gráfico risco × retorno.
- Carteira de mínima variância e de máximo Sharpe com `scipy.optimize`.
- **Conceitos:** diversificação, por que correlação baixa reduz risco, teoria de Markowitz
  e suas limitações (depende muito de estimativas do passado).

### Fase 4: Estratégia e backtest
- Estratégia de cruzamento de médias móveis (ex.: 50 e 200 dias) em um ativo e no Ibovespa.
- Backtest vetorizado com `shift(1)` no sinal para evitar usar informação do futuro.
- Incluir custo de transação por operação.
- Comparar com "comprar e segurar" (buy and hold) e com o CDI: retorno, volatilidade,
  drawdown máximo, Sharpe, número de operações.
- Separar período de teste (in-sample) e de validação (out-of-sample).
- **Conceitos:** look-ahead bias, survivorship bias, overfitting, custos que matam estratégias,
  por que um backtest bonito não garante nada.

### Fase 5: Entrega
- `main.py` que roda o pipeline completo e salva gráficos em `reports/figures/`.
- `README.md` com: objetivo, como rodar, principais resultados (tabela + 2 ou 3 gráficos),
  limitações honestas e próximos passos.
- Revisão final do código (clareza, nomes, testes passando).
- **Simulação de entrevista:** faça 8 a 10 perguntas que um entrevistador quant faria sobre
  este projeto, uma de cada vez, e avalie minhas respostas.

---

## Como começar cada sessão

Leia o `APRENDIZADO.md` para saber em que fase estou, faça um resumo de 3 linhas do que
já foi feito e pergunte se posso seguir.
