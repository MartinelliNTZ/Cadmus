# Configurações Cadmus

## Visão Geral
O diálogo de Configurações permite que você personalize o comportamento do Cadmus de acordo com suas necessidades.

## Preferências do Aplicativo
Clique no link **"Abrir Pasta de Preferências"** para acessar a pasta onde todas as preferências do Cadmus são armazenadas.

As preferências são salvas em:
```
C:\Users\<usuario>\AppData\Roaming\QGIS\QGIS3\MTLTools\mtl_prefs.json
```

## Método de Cálculo Vetorial
Selecione o método que será utilizado para cálculos geométricos:

### 🌍 Elipsoidal
Usa o modelo elipsoidal (recomendado para cálculos geodésicos e projeções geográficas).
- Mais preciso para longas distâncias
- Leva em conta a curvatura da Terra

### 📐 Cartesiana
Usa cálculos cartesianos simples (distância euclidiana).
- Mais rápido para cálculos locais
- Apropriado para projeções UTM com áreas pequenas

### 🔄 Ambos
Executa ambos os métodos e exibe os resultados comparativos.
- Útil para validação e análise
- Pode ser mais lento em operações em massa

## Aplicar Configurações
Clique em **"Executar"** para salvar e aplicar as configurações selecionadas.
