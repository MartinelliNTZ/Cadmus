# Substituir Texto em Layouts — Guia Rapido

Esta ferramenta procura texto em labels dos layouts do projeto e substitui pelo novo valor informado.

No estado atual do codigo, ela atua sobre itens do tipo `QgsLayoutItemLabel`.

## Como usar

1. Abra `Cadmus > Replace Text in Layouts`.
2. Preencha o texto a buscar.
3. Preencha o novo texto.
4. Se quiser, use o botao de troca para inverter os dois campos.
5. Ajuste as opcoes:
- `Case Sensitive`: diferencia maiusculas e minusculas.
- `Full Label Replace`: substitui todo o texto do label quando houver correspondencia.
6. Clique em executar e confirme a operacao destrutiva.

## O que o plugin faz de verdade

- Salva os ultimos valores digitados e as opcoes marcadas nas preferencias.
- Exige que o campo de busca nao esteja vazio.
- Exibe uma confirmacao antes de alterar os layouts.
- Se o projeto estiver salvo em disco, cria um backup do `.qgz` na pasta `backup`.
- Percorre todos os layouts do projeto.
- Dentro de cada layout, altera apenas itens que sao `QgsLayoutItemLabel`.
- Ao final, mostra um resumo com quantidade de layouts analisados e numero de alteracoes aplicadas.

## Como funciona a substituicao

- Com `Case Sensitive` ligado, a busca respeita letras maiusculas e minusculas.
- Com `Case Sensitive` desligado, a busca ignora essa diferenca.
- Com `Full Label Replace` desligado, o plugin faz substituicao parcial dentro do texto do label.
- Com `Full Label Replace` ligado, o plugin troca o conteudo inteiro do label pelo novo texto quando encontrar correspondencia.

## Comportamento importante

- A ferramenta nao altera outros tipos de item de layout; ela trabalha apenas com labels.
- O backup so e criado se o projeto ja estiver salvo.
- Se o projeto nao estiver salvo, a ferramenta ainda pode executar, mas sem criar backup.
- O resumo final informa numero de mudancas, nao uma lista detalhada por item.

## Quando usar

Use esta ferramenta quando precisar atualizar rapidamente textos repetidos em varios layouts do mesmo projeto.

Ela e especialmente util para:

- trocar ano, nome de cliente ou responsavel;
- atualizar textos padronizados em varios layouts;
- corrigir termos repetidos sem editar label por label.

## Cuidados

- Revise o texto buscado para evitar substituicoes amplas demais.
- Use `Full Label Replace` apenas quando quiser substituir o conteudo inteiro do label.
- Se o projeto for importante, salve antes de executar para garantir a criacao do backup.
