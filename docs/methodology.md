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
menor que -2%. A sequência usada no backtesting contém `1` nos dias de violação e
`0` nos demais dias.

## Teste de Kupiec

O teste de cobertura incondicional de Kupiec compara a proporção observada de
violações com a proporção esperada. Para um VaR de 95%, espera-se uma taxa de 5%.
A hipótese nula afirma que essas proporções são iguais. A implementação usa uma
razão de verossimilhança e calcula o p-valor por uma distribuição qui-quadrado com
um grau de liberdade.

## Testes de Christoffersen

O teste de independência verifica se uma violação altera a probabilidade de uma
nova violação no período seguinte. Para isso, compara as transições `0 → 0`,
`0 → 1`, `1 → 0` e `1 → 1` com uma cadeia de Markov de primeira ordem. Um número
elevado de violações consecutivas pode revelar agrupamento de risco mesmo quando
a frequência total parece correta.

O teste de cobertura condicional soma as estatísticas de Kupiec e de independência.
Sua hipótese nula exige simultaneamente frequência correta e ausência de
dependência temporal. A estatística conjunta usa uma distribuição qui-quadrado
com dois graus de liberdade.

Por padrão, o projeto usa significância de 5%. Um p-valor inferior a 0,05 leva à
rejeição da hipótese nula; um valor superior não prova que o modelo está correto,
apenas indica que o teste não encontrou evidência suficiente para rejeitá-lo.

## Limitações

O VaR depende da qualidade dos dados, da janela de estimação, do nível de confiança
e das hipóteses do método. Além disso, não mede a severidade das perdas que
ultrapassam seu limite e pode não capturar adequadamente mudanças de regime,
caudas pesadas ou falta de liquidez.

Os testes de cobertura têm baixo poder em amostras pequenas, especialmente para
níveis de confiança elevados, nos quais as violações são raras. Além disso, uma
avaliação rigorosa deve comparar retornos realizados com previsões de VaR geradas
fora da amostra, sem usar o próprio retorno futuro na estimação.

## Expansão para carteiras

Esta versão trata uma única série. Uma evolução para carteiras poderá receber
retornos de vários ativos e seus pesos, estimar a matriz de covariância e agregar
o risco. A estrutura separada em retornos, métodos de VaR e backtesting permite
adicionar essas funcionalidades — inclusive contribuições marginais de risco —
sem alterar a proposta simples deste primeiro módulo.

## Referências

- Kupiec, P. H. (1995). *Techniques for Verifying the Accuracy of Risk
  Measurement Models*. The Journal of Derivatives, 3(2), 73–84.
  <https://doi.org/10.3905/jod.1995.407942>
- Christoffersen, P. F. (1998). *Evaluating Interval Forecasts*. International
  Economic Review, 39(4), 841–862. <https://doi.org/10.2307/2527341>
