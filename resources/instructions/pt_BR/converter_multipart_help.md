# Converter Multipart — Guia Rapido

Esta ferramenta, no estado atual do plugin, atua sobre feicoes multipart e as separa em feicoes simples.

Em outras palavras: apesar do nome "Converter para Multipart", o processamento executado hoje quebra cada geometria multipart em partes individuais.

## Como usar

1. Ative uma camada vetorial no QGIS.
2. Abra `Cadmus > Converter para Multipart`.
3. Se houver feicoes selecionadas, o plugin pergunta se deve processar apenas as selecionadas.
4. Se nao houver selecao, o plugin pergunta se deve processar todas as feicoes da camada.
5. Confirme a operacao.
6. Revise o resultado na camada antes de salvar as edicoes.

## O que a ferramenta faz de verdade

- Processa a camada ativa somente se ela for vetorial e possuir feicoes.
- Se a camada tiver feicoes multipart, remove a feicao original e cria novas feicoes simples, uma para cada parte da geometria.
- Copia os mesmos atributos da feicao original para cada nova feicao criada.
- Respeita a selecao atual quando houver feicoes selecionadas.

## Comportamento de edicao

- Se a camada nao estiver em modo de edicao, o plugin inicia a edicao antes de processar.
- As alteracoes acontecem na propria camada, sem criar uma camada nova.
- O codigo atual nao faz salvamento automatico ao final.
- Se a operacao falhar ou for cancelada, o plugin executa `rollBack()`.

## Limitacoes importantes

- A rotina atual so altera feicoes cuja geometria ja esteja em formato multipart.
- Feicoes que ja sao simples nao sao modificadas.
- Se a camada nao estiver definida como tipo multipart, a rotina pode encerrar sem alterar nada.
- O texto da interface e o nome da ferramenta ainda estao desalinhados com o comportamento real do codigo.

## Quando usar

Use esta ferramenta quando voce tiver uma feicao multipart e quiser transformar cada parte em uma feicao separada, mantendo os atributos originais.

## Cuidados

- Revise a quantidade final de feicoes apos a execucao.
- Confira se a duplicacao de atributos atende ao seu fluxo de trabalho.
- Salve a camada somente depois de validar o resultado.
- Se a camada for sensivel, faca backup antes de executar.
