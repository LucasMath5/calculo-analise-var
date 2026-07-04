# Metodologia

## O que é Value at Risk

Value at Risk (VaR) é uma medida que resume uma perda potencial para um horizonte
e um nível de confiança definidos. Um VaR diário de 2% a 95%, por exemplo, indica
que, segundo o método adotado, há 5% de probabilidade de a perda diária superar
2%. O VaR não informa qual seria o tamanho da perda além desse limite.

Nesta versão, todos os cálculos usam retornos simples de uma única série de preços.

## Dados de mercado

O projeto pode gerar preços sintéticos ou baixar dados diários do Yahoo Finance
por meio da biblioteca `yfinance`. Para os dados reais, é usado o fechamento com
ajuste automático, reduzindo distorções provocadas por dividendos e
desdobramentos. A consulta recebe um ticker e um período, mas continua retornando
somente uma série de preços; múltiplos ativos ainda não são agregados.

Dados externos podem conter lacunas, erros ou revisões e dependem da
disponibilidade do provedor. A implementação remove fechamentos ausentes e rejeita
respostas vazias, preços não positivos e valores não finitos. O `yfinance` é uma
biblioteca independente do Yahoo e seu uso deve respeitar os termos aplicáveis à
fonte dos dados.

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

## Expected Shortfall

Expected Shortfall (ES) mede a perda média nos cenários que ultrapassam o VaR.
Enquanto o VaR fornece um ponto de corte, o ES descreve a severidade média da
cauda. Assim, um ES diário de 3% a 95% indica que a perda média nos piores 5% dos
cenários é de aproximadamente 3%.

No método histórico, o projeto calcula a média dos retornos iguais ou inferiores
ao quantil usado no VaR e converte o resultado para uma perda positiva. No método
paramétrico, assume normalidade e calcula analiticamente a média da cauda inferior
a partir da média e do desvio-padrão amostral dos retornos.

Em condições usuais, o ES é maior ou igual ao VaR calculado no mesmo nível de
confiança porque resume perdas que já ultrapassaram aquele limite.

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

VaR e ES dependem da qualidade dos dados, da janela de estimação, do nível de
confiança e das hipóteses do método. O ES descreve melhor a severidade da cauda,
mas ambos podem não capturar adequadamente mudanças de regime, caudas pesadas ou
falta de liquidez. A versão paramétrica também herda a hipótese de normalidade.

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

- Basel Committee on Banking Supervision. *Market risk terminology* — definição
  de Expected Shortfall. <https://www.bis.org/basel_framework/chapter/MAR/10.htm>
- Kupiec, P. H. (1995). *Techniques for Verifying the Accuracy of Risk
  Measurement Models*. The Journal of Derivatives, 3(2), 73–84.
  <https://doi.org/10.3905/jod.1995.407942>
- Christoffersen, P. F. (1998). *Evaluating Interval Forecasts*. International
  Economic Review, 39(4), 841–862. <https://doi.org/10.2307/2527341>
