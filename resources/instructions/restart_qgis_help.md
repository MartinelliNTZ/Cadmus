# 🔄 Salvar, Fechar e Reabrir Projeto – Manual de Utilização
Ferramenta do pacote **Cadmus** para reiniciar **QGIS com o projeto atual** de forma automática.

---

## 📌 O que esta ferramenta faz?

Esta ferramenta permite:

- **Salvar o projeto** automaticamente (se houver alterações)
- **Fechar QGIS** de forma segura
- **Reabrir QGIS** com o mesmo projeto carregado
- **Aguardar alguns segundos** antes de reabrir (permite limpeza de memória/buffers)

---

## 🎯 Quando usar?

### ✔ Reiniciar para "descongelar" QGIS
Se a aplicação está lenta ou responsiva, um restart pode resolver:
- Libera memória acumulada em cache
- Reseta estado interno de plugins
- Limpa buffers de renderização

### ✔ Após instalação de novo plugin
Alguns plugins requerem restart para funcionar corretamente.

### ✔ Recuperação de travamento parcial
Se certos recursos não respondem mas QGIS não completamente congelado.

### ⚠️ NÃO USAR para:
- Salvar um projeto não salvo (use **Arquivo → Salvar** primeiro)
- Fechar projetos sem que você queira reabrir (use **Arquivo → Sair**)

---

## ▶ Como usar

### 1. Abrir a ferramenta
Menu → **Cadmus** → **Sistema** → **Salvar, Fechar e Reabrir Projeto**

---

### 2. Confirmar (se necessário)
Se o projeto **não estiver salvo**:
- A ferramenta perguntará: _"Deseja salvar agora?"_
- Clique em **Sim** para salvar antes do restart
- Escolha o local e nome do arquivo `.qgz`
- Clique em **Salvar**

---

### 3. Aguardar
A ferramenta irá:
1. Salvar o projeto (se houver alterações)
2. Exibir mensagem: _"QGIS será reiniciado em alguns segundos..."_
3. Fechar QGIS (~2 segundos depois)
4. Reabrir QGIS automaticamente com o projeto

---

## ⚙️ Como funciona (internamente)

A ferramenta executa estas etapas:

1. **Validação:** Verifica se o projeto foi salvo em disco
2. **Save:** Executa `project.write()` para gravar alterações
3. **Script Criação:** Gera arquivo temporário `restart_qgis.bat` em `%TEMP%`
4. **Shell Execution:** Executa o script via `subprocess.Popen()`
5. **Shutdown:** Conecta callback ao sinal `aboutToQuit` do Qt
6. **Restart:** Script aguarda ~1 segundo (PING) e abre QGIS com o arquivo `.qgz`

---

## ⚠️ Observações Importantes

### ✔ Projeto Não Salvo
Se o projeto ainda não foi salvo em disco (novo projeto):
- A ferramenta **solicita um caminho de salvamento**
- User escolhe pasta e nome (ex: `meu_projeto.qgz`)
- Projeto é salvo antes do restart

### ✔ Alterações Serão Salvas
Todas as alterações desde a última save serão **gravadas em disco** antes de fechar.

### ✔ Camadas Temporárias Perdidas
Se você criou camadas de **memória** (não salvas em arquivo):
- Elas **NÃO serão restabelecidas** após o restart
- Workaround: Salve as camadas em arquivo antes do restart (**Arquivo → Exportar**)

### ✔ Plugins em Extensão
Se algum plugin está gerando um arquivo temporário:
- Ele pode ser **perdido** durante o restart
- Plugins bem-estruturados salvam estado em preferências (seguro)

### ✔ Tempo de Restart
- **Fechar QGIS:** ~1-2 segundos
- **Reabrir QGIS:** ~5-15 segundos (depende do tamanho do projeto)
- **Total:** ~6-17 segundos

### ✔ Executável QGIS
A ferramenta **automaticamente detecta** o executável do QGIS em uso:
- Obtém via `QCoreApplication.applicationFilePath()`
- Nenhuma configuração manual necessária

---

## 🔑 Chave Interna da Ferramenta

Esta ferramenta **não salva preferências** (não há configurações).

---

## 🐛 Possíveis Problemas

### Problema: "QGIS não reabre"
**Causa:** Executável do QGIS não encontrado.
**Solução:**
- Reinstalar QGIS
- Verificar que QGIS foi instalado em local padrão
- Usar ferramenta novamente

### Problema: "Projeto não foi salvo"
**Causa:** Erro ao escrever arquivo `.qgz`.
**Solução:**
- Verificar **permissões de pasta** (pasta precisa de escrita)
- Verificar **espaço em disco** disponível
- Verify arquivo `.qgz` não está aberto em outro programa

### Problema: "Projeto vazio após restart"
**Causa:** Projeto salvo mas não carregado corretamente.
**Solução:**
- Abrir **Arquivo → Abrir Recente** e selecionar projeto
- Ou **Arquivo → Abrir** e navegar até arquivo `.qgz`

---

## ℹ️ Informações Técnicas (Desenvolvedores)

- **Classe principal:** `run_restart_qgis(iface)`
- **Executor:** `_RestartExecutor` (isolamento de responsabilidades)
- **Logging:** Estruturado via `LogUtilsNew` com codes semânticos:
  - `RESTART_START` — Início do fluxo
  - `RESTART_SAVED` — Projeto salvo com sucesso
  - `RESTART_SCRIPT_OK` — Script `.bat` criado
  - `RESTART_EXECUTING` — Iniciando sequência de restart
  - `RESTART_CLOSING` — Encerrando QGIS
- **Script temporário:** Salvo em `%TEMP%/restart_qgis.bat`
- **Thread-safety:** Script executado via `aboutToQuit` signal (main thread)

---

## 💡 Dicas de Uso

✓ Use regularmente (a cada 30-60 min) se QGIS estiver lento
✓ Salve seus projetos **frequentemente** (Ctrl+S)
✓ Feche projetos desnecessários antes do restart
✓ Aumente tempo de pausa no script se restart falhar (edite `restart_qgis.bat`)

---

## Conclusão

Ferramenta segura para reiniciar QGIS sem perder dados. **Sempre salva antes de fechar** e **reaverte alterações não salvas são preservadas**.
