# Metodologia

## O que é Value at Risk

Value at Risk (VaR) é uma medida que resume uma perda potencial para um horizonte
e um nível de confiança definidos. Um VaR diário de 2% a 95%, por exemplo, indica
que, segundo o método adotado, há 5% de probabilidade de a perda diária superar
2%. O VaR não informa qual seria o tamanho da perda além desse limite.

Nesta versão, todos os cálculos usam retornos simples de uma única série de preços.

## VaR histórico

O método histórico usa diretamente a distribuição dos retornos observados. Para
95% de confiança, é calculado o percentil de 5% dos retornos e seu sinal é
convertido para que o VaR represente uma perda como valor positivo. O método é
intuitivo e não pressupõe uma distribuição, mas depende do período histórico e
supõe que ele seja representativo do risco futuro.

## VaR paramétrico normal

O método paramétrico estima a média e o desvio-padrão dos retornos e assume uma
distribuição normal. O quantil correspondente ao nível de confiança é então
obtido com esses parâmetros. É simples e rápido, mas a hipótese de normalidade
pode subestimar eventos extremos e assimetrias observadas em mercados financeiros.

## Violações de VaR

Uma violação ocorre quando a perda realizada excede o VaR estimado. Como os
retornos negativos representam perdas, um VaR de 2% é violado quando o retorno é
menor que -2%. A contagem implementada aqui é uma verificação introdutória, não um
teste estatístico completo de backtesting.

## Limitações

O VaR depende da qualidade dos dados, da janela de estimação, do nível de confiança
e das hipóteses do método. Além disso, não mede a severidade das perdas que
ultrapassam seu limite e pode não capturar adequadamente mudanças de regime,
caudas pesadas ou falta de liquidez.

## Expansão para carteiras

Esta versão trata uma única série. Uma evolução para carteiras poderá receber
retornos de vários ativos e seus pesos, estimar a matriz de covariância e agregar
o risco. A estrutura separada em retornos, métodos de VaR e backtesting permite
adicionar essas funcionalidades — inclusive contribuições marginais de risco —
sem alterar a proposta simples deste primeiro módulo.
