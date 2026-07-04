# Cálculo e Análise de Value at Risk

Projeto de portfólio em Python para calcular e comparar métodos básicos de Value
at Risk (VaR) e Expected Shortfall (ES), com foco em risco de mercado, estatística
e aplicações financeiras.

Esta versão trabalha com **uma única série de preços ou retornos**. Os preços
podem ser obtidos do Yahoo Finance ou gerados sinteticamente para demonstrações
reproduzíveis. O projeto não calcula VaR de carteiras nesta etapa.

## Métodos implementados

- cálculo de retornos simples a partir de preços;
- download de fechamentos ajustados pelo Yahoo Finance;
- VaR histórico;
- VaR paramétrico com distribuição normal;
- Expected Shortfall histórico;
- Expected Shortfall paramétrico normal;
- identificação e contagem de violações de VaR;
- teste de cobertura incondicional de Kupiec;
- teste de independência de Christoffersen;
- teste de cobertura condicional de Christoffersen.

As medidas de risco são apresentadas como números não negativos: um VaR ou ES de
`0.02` representa uma perda de 2%. Consulte a [metodologia](docs/methodology.md)
para uma explicação dos conceitos e limitações.

## Instalação

Requer Python 3.10 ou superior. Na raiz do projeto, crie e ative um ambiente
virtual e instale as dependências:

```bash
python -m venv .venv
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

No Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Em seguida:

```bash
python -m pip install -r requirements.txt
```

## Fontes de dados

O módulo `src/market_data.py` usa a biblioteca `yfinance` para obter preços
diários de fechamento ajustados por dividendos e desdobramentos. Não é necessária
uma chave de API. Para ações brasileiras, use o sufixo `.SA`, como `PETR4.SA` ou
`VALE3.SA`.

O `yfinance` é um projeto independente, sem afiliação ou aprovação do Yahoo. A
própria biblioteca informa que os dados são destinados a pesquisa, educação e
uso pessoal; consulte os [termos indicados na documentação do
yfinance](https://ranaroussi.github.io/yfinance/) antes de outros usos.

## Executar os exemplos

### Dados reais do Yahoo Finance

O comando abaixo baixa dois anos de preços ajustados da Petrobras:

```bash
python examples/yahoo_var_demo.py PETR4.SA --period 2y
```

O ticker é opcional e o padrão é `PETR4.SA`. Também é possível alterar o período
e o nível de confiança:

```bash
python examples/yahoo_var_demo.py AAPL --period 5y --confidence 0.99
```

Períodos usuais incluem `6mo`, `1y`, `2y`, `5y`, `10y` e `max`. Como esse exemplo
consulta um serviço externo, ele requer conexão com a internet e pode ser afetado
por indisponibilidade ou mudanças no Yahoo Finance.

### Dados sintéticos

O exemplo sintético usa uma semente aleatória fixa, funciona sem internet e
permanece útil para reproduzir os resultados apresentados neste README:

```bash
python examples/simple_var_demo.py
```

Para reproduzir os gráficos apresentados neste README:

```bash
python examples/generate_var_charts.py
```

## Executar os testes

```bash
pytest
```

## Estrutura do projeto

```text
calculo-analise-var/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── returns.py
│   ├── var_methods.py
│   ├── backtesting.py
│   └── market_data.py
├── examples/
│   ├── simple_var_demo.py
│   ├── yahoo_var_demo.py
│   └── generate_var_charts.py
├── tests/
│   ├── test_returns.py
│   ├── test_var_methods.py
│   ├── test_backtesting.py
│   └── test_market_data.py
└── docs/
    ├── methodology.md
    └── images/
        ├── synthetic_prices.png
        └── var_analysis.png
```

## Resultados e conclusão

Os gráficos e números abaixo continuam baseados no exemplo sintético, para que
não mudem a cada consulta à API. Com a semente aleatória fixa, foram obtidas 499
observações de retorno e os seguintes resultados para 95% de confiança:

| Métrica | Resultado |
| --- | ---: |
| VaR histórico | 1,8589% |
| VaR paramétrico normal | 1,8729% |
| Expected Shortfall histórico | 2,2828% |
| Expected Shortfall paramétrico normal | 2,3547% |
| Violações do VaR histórico | 25 (5,01%) |
| Kupiec (p-valor) | 0,9918 |
| Christoffersen — independência (p-valor) | 0,8044 |
| Christoffersen — cobertura condicional (p-valor) | 0,9697 |

![Trajetória da série sintética de preços](docs/images/synthetic_prices.png)

![Retornos, violações e distribuição](docs/images/var_analysis.png)

Os dois métodos produziram estimativas próximas, resultado coerente com a geração
de retornos por uma distribuição normal. O VaR histórico indica que, em condições
semelhantes às observadas, uma perda diária de aproximadamente 1,86% seria
excedida em cerca de 5% dos dias. As 25 violações correspondem a 5,01% da amostra,
valor próximo à taxa esperada para o nível de confiança adotado.

O Expected Shortfall histórico estima uma perda média de 2,28% nos piores 5% dos
dias, acima do limite indicado pelo VaR. O resultado paramétrico de 2,35% é um
pouco mais conservador neste exemplo e incorpora a severidade média da cauda, não
apenas o ponto de corte.

Ao nível de significância de 5%, os três p-valores são superiores a 0,05. Assim,
não há evidência para rejeitar a frequência esperada de violações, sua
independência temporal ou a cobertura condicional neste exemplo sintético.

Essa leitura é apenas didática: o VaR foi estimado e avaliado na mesma amostra
sintética. Portanto, o resultado não constitui uma validação fora da amostra nem
garante desempenho futuro. Os testes de Kupiec e Christoffersen avaliam aspectos
específicos das violações, mas não demonstram isoladamente que o modelo é adequado.

## Próximos passos

- VaR de carteiras com múltiplos ativos;
- suporte a pesos de carteira;
- estimação e uso da matriz de covariância;
- VaR por simulação de Monte Carlo;
- Expected Shortfall por simulação de Monte Carlo;
- backtesting fora da amostra com janelas móveis;
- visualizações e geração de relatórios.

Essas extensões serão feitas em etapas para preservar a clareza do código e
permitir a inclusão futura de métricas como a contribuição marginal de risco.
