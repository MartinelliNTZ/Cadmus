# Copiar Atributos — Guia Rapido

Esta ferramenta seleciona campos de uma camada de origem e os adiciona na estrutura da camada de destino.

Importante: no estado atual do codigo, ela nao copia valores das feicoes. Ela copia apenas a estrutura dos campos, com tratamento de conflitos de nome.

## Como usar

1. Abra `Cadmus > Copiar Atributos`.
2. Escolha a camada destino.
3. Escolha a camada origem.
4. Marque os campos desejados da camada origem, ou use a opcao para todos os campos.
5. Clique em executar.

## O que o plugin faz de verdade

- Valida se origem e destino sao camadas vetoriais.
- Exige que a camada destino ja esteja em modo de edicao.
- Lista os campos com base na camada de origem selecionada.
- Permite copiar todos os campos ou apenas os selecionados.
- Para cada campo escolhido:
- se o campo nao existir no destino, ele e criado;
- se o campo ja existir, o plugin pede uma acao de conflito.

## Tratamento de conflitos

- `skip`: ignora o campo que ja existe.
- `rename`: cria um novo campo com sufixo como `_1`, `_2` e assim por diante.
- `cancel`: interrompe a operacao.

## Comportamento importante

- A ferramenta nao transfere valores entre feicoes.
- Ela tambem nao faz correspondencia espacial nem por chave entre registros.
- O resultado principal e a alteracao do esquema de atributos da camada destino.
- Se nenhum campo estiver selecionado e a opcao de todos os campos nao estiver ativa, a operacao nao continua.

## Quando usar

Use esta ferramenta quando quiser preparar a camada destino com novos campos baseados na estrutura de outra camada.

Ela e especialmente util para:

- padronizar esquemas de atributos;
- criar campos faltantes antes de outra etapa de processamento;
- replicar nomes e tipos de campos de uma camada modelo.

## Cuidados

- Coloque a camada destino em edicao antes de executar.
- Se voce precisava copiar valores, esta ferramenta ainda nao faz isso no codigo atual.
- Revise conflitos de nome com cuidado para nao criar campos duplicados desnecessarios.
