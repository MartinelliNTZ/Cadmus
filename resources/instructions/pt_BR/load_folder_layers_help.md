# Carregar Camadas de Pasta — Guia Rapido

Esta ferramenta varre uma pasta e suas subpastas para carregar arquivos vetoriais e raster no projeto QGIS.

Ela tambem pode:

- filtrar por tipos de arquivo;
- evitar recarregar arquivos que ja estao no projeto;
- preservar a estrutura de pastas como grupos;
- ignorar a ultima pasta na criacao desses grupos;
- criar backup do projeto antes da carga, quando o projeto ja estiver salvo.

## Como usar

1. Abra `Cadmus > Load Folder Layers`.
2. Escolha a pasta raiz que contem os arquivos.
3. Marque um ou mais tipos de arquivo na secao `File Types`.
4. Ajuste as opcoes extras, se necessario:
- `Load only missing files`: ignora arquivos que ja estejam carregados no projeto.
- `Preserve folder structure`: cria grupos no painel de camadas com base nas subpastas.
- `Do not group last folder`: remove o ultimo nivel da pasta ao criar grupos.
- `Create project backup if saved`: tenta criar backup do projeto antes da operacao.
5. Clique em executar.

## O que o plugin faz de verdade

- Faz busca recursiva com `os.walk()` na pasta escolhida.
- Filtra os arquivos pelas extensoes marcadas na interface.
- Trata como vetor formatos como `shp`, `gpkg`, `geojson`, `kml`, `csv`, `gpx`, `tab`, `las` e `laz`.
- Trata como raster formatos como `tif`, `tiff`, `ecw`, `jp2` e `asc`.
- Cria cada camada usando `ExplorerUtils.create_layer()`.
- Adiciona as camadas na raiz do projeto ou em grupos, dependendo da opcao marcada.

## Estrutura de grupos

- Se `Preserve folder structure` estiver desmarcado, todas as camadas entram na raiz do projeto.
- Se estiver marcado, o plugin usa o caminho relativo da pasta do arquivo para montar grupos aninhados.
- Se `Do not group last folder` estiver ativo, o ultimo segmento da pasta e removido antes de criar o grupo.
- Quando o caminho relativo vira `.` ou vazio, a camada entra na raiz do projeto.

## Comportamento importante

- E obrigatorio escolher uma pasta valida.
- E obrigatorio marcar pelo menos um tipo de arquivo.
- A opcao de backup so fica habilitada quando o projeto atual ja foi salvo em disco.
- O filtro `Load only missing files` compara o caminho normalizado do arquivo com as fontes das camadas ja abertas.

## Execucao sincrona e assincrona

- Ate 19 arquivos, a ferramenta roda de forma sincrona.
- Acima de 19 arquivos, ela inicia uma pipeline assincrona para reduzir impacto na interface.
- No modo assincrono, ha uma janela de progresso propria para a etapa de adicao das camadas.
- Se o usuario cancelar, a operacao para no ponto atual e as camadas ja adicionadas permanecem no projeto.

## Quando usar

Use esta ferramenta quando precisar carregar muitos arquivos de uma pasta sem adicionar camada por camada manualmente.

Ela e especialmente util para:

- projetos organizados por subpastas;
- cargas recorrentes de dados atualizados;
- pastas com mistura de vetores e rasters.

## Cuidados

- Revise os tipos de arquivo marcados antes de executar.
- Se quiser manter a arvore organizada, use `Preserve folder structure`.
- Se a pasta tiver muitos arquivos, espere uma carga parcial caso voce cancele no meio do processo.
