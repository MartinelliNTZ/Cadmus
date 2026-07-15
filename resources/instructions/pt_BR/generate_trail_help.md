# Gerar Rastro de Maquinas — Guia Rapido

Esta ferramenta gera a faixa ocupada por um implemento a partir de uma camada de linhas.

No fluxo atual do codigo, ela transforma a linha de entrada em um resultado buffered, usando metade da largura informada como distancia de buffer.

## Como usar

1. Abra `Cadmus > Gerar Rastro de Maquinas`.
2. Selecione a camada de linhas de entrada.
3. Informe o tamanho do implemento em metros.
4. Se quiser, ative o salvamento em arquivo e escolha o caminho de saida.
5. Se quiser, selecione um arquivo QML para aplicar estilo ao resultado.
6. Execute a ferramenta.

## O que o plugin faz de verdade

- Valida se a entrada e uma camada vetorial de linhas.
- Converte a distancia informada em metros para a unidade da camada.
- Usa `buffer_distance = tamanho_do_implemento / 2`.
- Se a opcao de apenas selecionadas estiver ativa, processa somente as feicoes selecionadas.
- Executa a pipeline `Explode -> Buffer -> Save`.
- Quando nao ha salvamento em arquivo, cria a camada final em memoria.
- Quando ha salvamento em arquivo, grava no caminho escolhido e usa renomeacao automatica se o arquivo ja existir.
- Adiciona a camada final ao projeto caso ela ainda nao esteja carregada.
- Aplica o estilo QML somente se essa opcao estiver habilitada e houver arquivo informado.

## Execucao sincrona e assincrona

- O plugin consulta a configuracao global `async_threshold_features`.
- Se a camada tiver mais feicoes que esse limiar, roda em pipeline assincrona.
- Se estiver abaixo do limiar, roda de forma sincrona.
- Nos dois casos, o objetivo final e gerar a mesma camada resultante.

## Comportamento importante

- O valor do implemento nao pode ser `0`.
- A entrada precisa ser uma camada de linhas.
- O nome padrao do resultado e `Rastro_implemento`.
- O resultado representa a faixa gerada por buffer em torno das linhas processadas.
- Se voce nao salvar em arquivo, o resultado fica como camada em memoria.

## Quando usar

Use esta ferramenta quando quiser representar a largura de trabalho de um implemento a partir de trajetorias, passadas ou linhas de deslocamento.

Ela e especialmente util para:

- criar faixa de cobertura operacional;
- visualizar largura ocupada em campo;
- gerar um produto vetorial derivado de linhas de percurso.

## Cuidados

- Revise o CRS da camada para garantir que a conversao de distancia faca sentido.
- Como o buffer usa metade da largura informada, confirme se o valor digitado corresponde a largura total do implemento.
- Se quiser persistir o resultado, prefira salvar em `gpkg`.
