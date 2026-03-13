# 📘 Configurações Cadmus — Guia Rápido e Intuitivo

Breve: gerencia preferências globais do Cadmus, incluindo método de cálculo vetorial, precisão de campos e limiar de processamento assíncrono. ⚙️

---

## ▶ Passo a passo (rápido) ✅

1. Abra: Menu → **Cadmus** → **Configurações Cadmus**
2. Na seção **Método de Cálculo Vetorial**, escolha:
   - **Elipsoidal**: Calcula considerando a forma da Terra (mais preciso para grandes distâncias). 🌍
   - **Cartesiana**: Calcula em linha reta (rápido, útil para áreas pequenas). 📐
   - **Ambos**: Calcula os dois métodos e cria dois campos (comparativo). 🔄
3. (Opcional) Ajuste:
   - **Precisão de campos vetoriais**: Número de casas decimais (padrão: 2). 🎯
   - **Limiar assíncrono**: Tamanho acima do qual o processamento fica assíncrono em MB (padrão: 20 MB). 📦
4. Clique em **Salvar** 💾 — as configurações são aplicadas imediatamente.

---

## ℹ️ O que acontece por trás (resumido)

- **Método de Cálculo**: Preferência padrão usada em **Calcular Campos Vetoriais**. Se a camada for geográfica (graus) e você selecionar "Cartesiana", o plugin automaticamente muda para "Ambos". ⚠️
- **Precisão**: Define quantas casas decimais os valores calculados terão (ex.: 2 = 10.45 metros, 4 = 10.4532 metros).
- **Limiar Assíncrono**: Acima desse tamanho, camadas rodam em processamento assíncrono (não trava a interface). Abaixo, rodam em processamento rápido (síncrono).
- **Pasta de Preferências**: Clique em "Abrir Pasta de Preferências" para acessar os arquivos `.json` de configuração localmente. 📁

---

## 💡 Dicas rápidas

- **Não tem certeza?** Deixe no padrão (Elipsoidal, Precisão 2, Limiar 20 MB). 🎯
- **Camadas grandes em memória?** Reduza o "Limiar assíncrono" para forçar processamento assíncrono mais cedo. 🚀
- **Quer máxima precisão?** Aumente a "Precisão de campos vetoriais" para 4 ou 6 casas decimais. 🔬
- As preferências são **globais** — aplicadas a todos os plugins do Cadmus. 🌐

---

## ⚠️ Problemas comuns e solução

- **"Configurações não estão sendo salvas"** → Verifique permissões de escrita na pasta de preferências. 🔐
- **Processamento ainda está lento/rápido demais** → Ajuste o "Limiar assíncrono" (reduz o valor para forçar async mais cedo). ⏳
- **Valores com muitas casas decimais** → Reduza a "Precisão de campos vetoriais" (padrão é 2). ✂️
- **Erro ao abrir Pasta de Preferências** → Pasta pode estar em local protegido; verifique permissões do Windows. 🔓

---

## ✅ Checklist rápido pós-execução

- Método de cálculo selecionado está correto? ✔️
- Precisão está conforme desejado? ✔️
- Limiar assíncrono faz sentido para suas camadas? ✔️
- Mensagem "Configurações Salvas" foi exibida? ✔️

---

## 🔧 Preferências e suporte

- **Arquivo de configuração**: Localizado em `C:\Users\[seu_user]\AppData\Roaming\QGIS\QGIS3\profiles\[seu_perfil]\python\plugins\Cadmus\prefs\`
- **Formato**: Arquivos `.json` para cada ferramenta (ex.: `settings.json`).
- **Backup**: Faça backup da pasta de preferências antes de atualizações do plugin. 💾
- Em caso de problema, delete o arquivo `settings.json` e as configurações voltarão ao padrão. 🔄
- Reporte problemas com: versão do QGIS, sistema operacional e print de erro do painel de logs. 🐞
