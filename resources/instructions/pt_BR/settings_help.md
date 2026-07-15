# Configuracoes Cadmus — Guia Rapido

Esta ferramenta centraliza preferencias globais usadas por partes do plugin Cadmus.

No estado atual do codigo, ela permite:

- escolher o metodo padrao de calculo vetorial;
- definir a precisao numerica de campos vetoriais;
- definir o limiar de feicoes para processamento assincrono;
- abrir a pasta local de preferencias do Cadmus.

## Como usar

1. Abra `Cadmus > Configuracoes Cadmus`.
2. Escolha o metodo de calculo vetorial:
- `Elipsoidal`
- `Cartesiano`
- `Ambos`
3. Ajuste a precisao de campos vetoriais.
4. Ajuste o limiar assincrono.
5. Clique em `Salvar`.

## O que o plugin faz de verdade

- Carrega preferencias salvas com `load_tool_prefs()`.
- Salva as configuracoes no conjunto de preferencias da chave `settings`.
- Mostra uma mensagem de confirmacao apos salvar.
- Fecha a janela logo depois de aplicar as preferencias.
- Permite abrir a pasta local onde os arquivos de preferencias ficam armazenados.

## Significado de cada opcao

- `Metodo de calculo vetorial`: define o texto da preferencia `calculation_method`.
- `Precisao de campos vetoriais`: salva um valor inteiro em `vector_field_precision`.
- `Limiar assincrono`: salva um valor inteiro em `async_threshold_features`.

## Comportamento importante

- O limiar assincrono atual e medido em numero de feicoes, nao em MB.
- O codigo aceita valores de precisao entre 0 e 10.
- O limiar assincrono aceita valores de 1 ate 100000000.
- Ha retrocompatibilidade de leitura com a antiga chave `async_threshold_bytes`, mas ao carregar o plugin passa a usar o limite por feicoes.
- Este plugin apenas salva preferencias; ele nao executa calculos vetoriais por conta propria.

## Pasta de preferencias

- O link da interface tenta abrir a pasta `PREF_FOLDER` no sistema operacional.
- Se a pasta nao existir, o plugin exibe um aviso em vez de abrir o explorador.

## Quando usar

Use esta ferramenta quando quiser ajustar o comportamento padrao de outras ferramentas do Cadmus que dependem dessas preferencias globais.

## Cuidados

- Altere o metodo de calculo apenas se ele fizer sentido para o seu fluxo.
- Se voce reduzir demais o limiar assincrono, mais operacoes podem passar a rodar em segundo plano.
- Se houver comportamento estranho apos mudar preferencias, vale revisar os arquivos salvos na pasta de preferencias.
