# Conversor de Vetor para SVG - Guia Rapido

Esta ferramenta exporta uma camada vetorial do QGIS para SVG, respeitando opcoes de fundo, borda, rotulo e geracao por feicao.

## Como usar

1. Abra `Cadmus > Conversor de Vetor para SVG`.
2. Selecione a camada vetorial de entrada.
3. Se quiser, ative `Somente feicoes selecionadas`.
4. Configure cor de fundo, cor/espessura da borda e cor/tamanho do rotulo.
5. Marque ou desmarque as opcoes de fundo transparente, mostrar borda, mostrar rotulo e gerar um SVG por feicao.
6. Escolha a pasta de saida ou use a pasta do projeto.
7. Execute a ferramenta.

## O que o plugin faz de verdade

- Valida se a entrada e uma camada vetorial valida com feicoes.
- Usa apenas as feicoes selecionadas quando essa opcao estiver ativa.
- Reprojeta as geometrias para WGS84 antes de montar o SVG.
- Exporta um unico SVG da camada inteira ou um SVG por feicao, conforme a opcao marcada.
- Aplica fundo transparente ou cor de fundo fixa.
- Controla a borda das geometrias com cor e espessura configuradas pelo usuario.
- Tenta desenhar rotulos reais da camada a partir da configuracao de labeling do QGIS, com fallback para `displayExpression()` e campo `Name`.

## Nomeacao dos arquivos

- Quando gera um unico SVG, usa o nome da camada do QGIS.
- Quando gera um SVG por feicao:
  - usa o campo `Name` se existir e tiver valor;
  - caso contrario, usa `NomeDaCamada_1`, `NomeDaCamada_2`, `NomeDaCamada_3`...
- Se o arquivo ja existir, o plugin gera um nome incremental para nao sobrescrever.

## Comportamento importante

- Se `Fundo transparente` estiver ativo, o SVG nao recebe cor de fundo.
- Se `Mostrar Borda` estiver desmarcado, o contorno das geometrias nao e desenhado.
- Se `Mostrar Rotulo` estiver desmarcado, nenhum texto e exportado.
- O tamanho do rotulo pode ser controlado diretamente na ferramenta.
- O resultado final e salvo apenas em disco, na pasta escolhida.

## Quando usar

Use esta ferramenta quando quiser:

- gerar icones ou figuras SVG a partir de vetores do projeto;
- exportar feicoes individualmente para uso em layout, web ou automacao;
- reaproveitar simbologia basica da camada em uma saida vetorial leve.

## Cuidados

- Revise o labeling da camada se quiser que os rotulos aparecam.
- Camadas com muitas feicoes podem gerar muitos arquivos quando a opcao por feicao estiver ativa.
- Para resultados mais organizados, prefira preencher o campo `Name` antes da exportacao por feicao.
