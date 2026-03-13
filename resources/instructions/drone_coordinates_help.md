# 📘 Obter Coordenadas de Drone (MRK) – Manual de Utilização  
Ferramenta do pacote **Cadmus** para geração de **pontos e trajetos de voo de drone** a partir de arquivos **MRK** (DJI).

---

## 📌 O que esta ferramenta faz?

Esta ferramenta lê arquivos **MRK gerados por drones DJI** e permite:

- Gerar **pontos das fotos** do voo
- Gerar o **trajeto (linha)** do drone
- Opcionalmente **cruzar os pontos com metadados das fotos JPG**
- Salvar resultados em arquivo ou criar **camadas temporárias**
- Aplicar **estilos QML** automaticamente
- Processar grandes volumes sem travar o QGIS

---

## 🧩 Componentes principais

### ✔ Pasta dos MRK
Define a pasta onde estão os arquivos `.mrk`.

- Pode conter **subpastas**
- Pode haver **vários MRKs**

---

### ✔ Vasculhar subpastas
Quando marcado, a ferramenta procura arquivos `.mrk` em **todas as subpastas recursivamente** da pasta selecionada.

⚠ **Atenção:**  
- Se desmarcado, apenas MRKs na **pasta raiz** serão processados
- Esta opção é ignorada se arquivos individuais forem selecionados diretamente

---

### ✔ Unir todos os MRK
Quando ativado, todos os arquivos MRK encontrados são **agregados em um único voo**, gerando:

- **Um único conjunto de pontos** (com todos os waypoints combinados)
- **Um único trajeto** (com a rota completa do voo unificada)

Se desmarcado, cada MRK é processado **independentemente**, criando múltiplas camadas de pontos e trajetos.

---

### ✔ Cruzar com metadados das fotos
Permite enriquecer os pontos MRK com informações extraídas das **fotos JPG** do voo, como:

- **Nome do arquivo** da foto
- **Tamanho** do arquivo (bytes)
- **Data de modificação** do arquivo
- **Dimensões** da imagem (largura × altura)
- **Metadados EXIF**: ISO, abertura (f-stop), distância focal, marca da câmera, etc.

Requer que as fotos estejam disponíveis **na mesma pasta** do MRK ou em subpastas.

⚠ **Atenção:**  
- Não recomendado para **grandes volumes de fotos** (>5000 imagens), pois o processamento é assíncrono e pode levar minutos
- Se a foto não for encontrada, o ponto MRK será criado **sem os metadados de foto** (processamento continua)

---

## 📍 Pontos MRK

### ✔ Salvar pontos em arquivo
Permite salvar os pontos em:

- Shapefile (`.shp`)
- GeoPackage (`.gpkg`)
- GeoJSON (`.geojson`)
- KML (`.kml`)

Se desmarcado, os pontos serão criados como **camada temporária**.

---

### ✔ Aplicar estilo (QML) nos pontos
Permite selecionar um arquivo `.qml` para estilizar automaticamente a camada de pontos.

---

## 🧭 Trajeto do Drone (Linha)

### ✔ Salvar trajeto em arquivo
Permite salvar o trajeto do drone em:

- Shapefile
- GeoPackage
- GeoJSON
- KML
- CSV

Se desmarcado, o trajeto será criado como **camada temporária**.

---

### ✔ Aplicar estilo (QML) no trajeto
Permite aplicar um estilo `.qml` ao rastro do drone.

Se nenhum QML for informado, a ferramenta pode aplicar um **estilo padrão do plugin**.

---

## ▶ Como usar

### 1. Abrir a ferramenta  
Menu → **Cadmus** → **Agricultura de Precisão** → *Obter Coordenadas de Drone*

---

### 2. Selecionar a pasta dos MRK
Clique em **…** e escolha a pasta onde estão os arquivos `.mrk`.

---

### 3. Definir opções desejadas
Marque conforme sua necessidade:

- Vasculhar subpastas
- Unir MRKs
- Cruzar com fotos
- Salvar pontos
- Salvar trajeto
- Aplicar estilos

---

### 4. Definir caminhos de saída (opcional)
Caso opte por salvar em arquivo:

- Escolha o local e formato
- Selecione QMLs, se desejar

---

### 5. Clique em **Executar**
A ferramenta irá:

1. Ler todos os MRKs encontrados  
2. Criar os pontos  
3. Criar o trajeto  
4. Cruzar com fotos (se ativado)  
5. Adicionar as camadas ao projeto  

O progresso e mensagens são registrados automaticamente.

---

## 🔄 Persistência de Configurações

Todas as opções escolhidas são salvas automaticamente nas **preferências do QGIS** para a próxima abertura:
- Última pasta/arquivos selecionados
- Estado dos checkboxes (vasculhar subpastas, unir MRKs, etc.)
- Caminhos de saída e estilos QML

⚠ **Nota:**  
Apenas o **primeiro caminho** (pasta ou arquivo) é lembrado. Se múltiplos arquivos foram selecionados, apenas o primeiro será restaurado.

---

## ℹ️ Observações Importantes

- **Processamento assíncrono:** Especialmente quando cruzando com metadados de fotos, a ferramenta executa em **background thread** para não travar o QGIS
- **Reprojeção automática:** Arquivos KML são automaticamente reprojetados para **EPSG:4326** (WGS84)
- **Camadas temporárias:** Se nenhum caminho de saída for fornecido, pontos e trajetos são criados como **camadas de memória** (temporárias)
- **MRK não encontrados:** Se a pasta contém " .mrk arquivos inválidos ou corrompidos, a ferramenta reportará warnings mas continuará processando os válidos
- **Fotos não encontradas:** Se ativar "Cruzar com fotos" mas alguma JPG estiver faltando, a ferramenta criará o ponto MRK sem metadados de foto (não falha)

---

## 🔑 Chave interna da ferramenta

Esta ferramenta utiliza a seguinte chave para salvar preferências:

`drone_coordinates`
