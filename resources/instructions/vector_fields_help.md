# 📘 Calcular Campos Vetoriais — Guia Rápido e Intuitivo

Breve: calcula campos de coordenadas (X, Y) para pontos, comprimento para linhas e área para polígonos, com suporte a diferentes sistemas de coordenadas. 📐

---

## ▶ Passo a passo (rápido) ✅

1. Abra: Menu → **Cadmus** → **Calcular Campos Vetoriais**
2. Selecione a **camada vetorial** (pontos, linhas ou polígonos). 🗂️
3. (Opcional) Acesse **Configurações** para escolher:
   - **Método de cálculo**: Elipsoidal, Cartesiana ou Ambos. ⚙️
   - **Precisão**: Número de casas decimais (padrão: 2). 🎯
4. Clique em **Executar** ▶️ — o processamento roda em segundo plano e novos campos são adicionados automaticamente.

---

## ℹ️ O que acontece por trás (resumido)

- **Pontos**: Cria campos `X` e `Y` com as coordenadas do ponto. 
- **Linhas**: Cria campo `Length` (ou `Length_Ellip` / `Length_Cart`) com o comprimento da linha.
- **Polígonos**: Cria campo `Area` (ou `Area_Ellip` / `Area_Cart`) com a área do polígono.
- **Processamento**: Para camadas com < 1000 feições = processamento rápido (síncrono); para >= 1000 feições = assíncrono (não trava a interface). ⚙️
- **CRS Geográfico**: Se a camada usar CRS em graus (ex.: EPSG:4326) e você selecionar "Cartesiana", o plugin automaticamente muda para "Ambos" para evitar resultados em graus². ⚠️

---

## 💡 Dicas rápidas

- **CRS em graus?** Reprojete para um CRS métrico (ex.: UTM) para resultados precisos em metros. 🌍 → 📐
- **Método "Ambos"**: Cria dois campos (Elipsoidal e Cartesiano) — útil para análises comparativas. 🔄
- **Precisão 0**: Resulta em valores inteiros (sem casas decimais). 🎯
- A camada fica em modo de edição — você pode revisar os resultados antes de salvar. 💾

---

## ⚠️ Problemas comuns e solução

- **Valores muito grandes/estranhos** → Verifique o CRS da camada. Se estiver em graus, reprojete. 🔁
- **"Camada não editável"** → Camada está bloqueada. Desbloqueia-a antes de tentar novamente. 🔐
- **Valores em graus² (área/comprimento)** → Você selecionou "Cartesiana" em CRS geográfico. O plugin avisa, mas você pode ignorar. ⚠️
- **Processamento lento (camada com 10k+ feições)** → Normal! Processamento assíncrono está funcionando; veja a barra de progresso. ⏳

---

## ✅ Checklist rápido pós-execução

- Novos campos foram criados na camada? ✔️
- Os valores estão corretos (amostra visual)? ✔️
- Precisão está conforme esperado (casas decimais)? ✔️
- Savedos os dados se necessário? ✔️

---

## 🔧 Preferências e suporte

- Acesse **Configurações Cadmus** para ajustar:
  - **Método de cálculo** padrão (Elipsoidal, Cartesiana ou Ambos)
  - **Precisão padrão** para campos novos
  - **Limiar assíncrono** (quando o processamento fica assíncrono)
- As preferências são salvas e aplicadas automaticamente em próximas execuções.
- Em caso de erro, abra o painel de logs do plugin e reporte com: tipo de geometria, número de feições e CRS da camada. 🐞
