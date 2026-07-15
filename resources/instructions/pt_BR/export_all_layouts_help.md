# Exportar Todos os Layouts — Guia Rapido

Esta ferramenta exporta todos os layouts do projeto atual em PDF, PNG ou nos dois formatos.

Ela tambem pode:

- unir todos os PDFs exportados em um arquivo final;
- transformar os PNGs exportados em um PDF unico;
- evitar sobrescrita criando nomes com sufixo;
- salvar as preferencias usadas na interface.

## Como usar

1. Abra `Cadmus > Export All Layouts`.
2. Marque pelo menos um formato de saida: `Export PDF` e/ou `Export PNG`.
3. Ajuste as opcoes extras, se necessario:
- `Merge PDF`: junta os PDFs exportados em `_PDF_UNICO_FINAL.pdf`.
- `Merge PNG`: converte os PNGs exportados em um PDF final chamado `_PNG_MERGED_FINAL.pdf`.
- `Replace Existing`: sobrescreve arquivos existentes.
- `Max Width`: define a largura maxima usada no PDF gerado a partir dos PNGs.
4. Escolha a pasta de saida.
5. Se quiser usar a pasta do projeto, clique no botao que aponta para `.../exports`.
6. Clique em `Export`.

## O que o plugin faz de verdade

- Lê todos os layouts do projeto atual via `layoutManager().layouts()`.
- Cria a pasta de saida automaticamente se ela nao existir.
- Limpa caracteres invalidos do nome de cada layout antes de gerar os arquivos.
- Quando `Replace Existing` estiver desmarcado, cria nomes como `Layout_1`, `Layout_2` e assim por diante para evitar conflito.
- Exporta cada layout individualmente com `QgsLayoutExporter`.
- Exibe uma janela de progresso durante o processamento.
- Permite cancelar a exportacao no meio do processo.
- Ao final, mostra um resumo com sucessos, erros e a pasta de destino.

## Dependencias opcionais

- `PyPDF2` e usado apenas se voce marcar a uniao dos PDFs.
- `Pillow` e usado apenas se voce marcar a uniao dos PNGs em PDF.
- Se a dependencia estiver faltando, o plugin pede confirmacao para instalar.
- Se voce recusar a instalacao, a exportacao continua sem a etapa de merge correspondente.

## Comportamento importante

- E obrigatorio selecionar pelo menos um formato de exportacao.
- O plugin conta um layout como sucesso se pelo menos um dos formatos selecionados for exportado com sucesso.
- Se um layout falhar em um formato e funcionar no outro, o erro aparece no resumo final.
- O cancelamento interrompe o loop no ponto atual; o que ja foi exportado permanece na pasta.

## Quando usar

Use esta ferramenta quando precisar exportar rapidamente todos os layouts de um projeto sem abrir e salvar um por um.

Ela e especialmente util para:

- entregar um conjunto completo de pranchas;
- gerar revisoes em lote;
- consolidar saidas PDF em um unico arquivo final.

## Cuidados

- Revise a pasta de saida antes de executar, principalmente se `Replace Existing` estiver marcado.
- Se houver layouts com nomes parecidos, confira os arquivos gerados apos a exportacao.
- Para projetos grandes, considere exportar primeiro sem merge para validar o resultado.
