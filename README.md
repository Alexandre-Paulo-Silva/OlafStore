# ❄️ OlafStore – Laboratório de Segurança Web

OlafStore é uma aplicação web de demonstração construída em **Flask**.  
O objetivo deste projeto é servir como **laboratório de vulnerabilidades** para estudo e portfólio, mostrando falhas comuns em aplicações web e como corrigi-las.

---

![Carrinho de Compras](docs/img/loja.png)


## 📌 Objetivos do Projeto
- Demonstrar vulnerabilidades reais em aplicações web.
- Mapear cada falha ao framework **MITRE ATT&CK**.
- Propor medidas de correção e boas práticas.
- Documentar **procedimentos e ferramentas** usadas na análise.

---

## 🔓 Vulnerabilidades Identificadas

### 1. Senhas em texto puro
- **Descrição:** As senhas são armazenadas diretamente no banco sem hashing.
- **MITRE ATT&CK:** [Credential Dumping – T1003](https://attack.mitre.org/techniques/T1003/)  
- **Procedimento:** Inspeção direta do banco SQLite (`sqlite3 store.db` → `SELECT * FROM users;`).  
- **Ferramenta:** Cliente SQLite.  
- **Correção:** Usar hashing seguro (`bcrypt`, `argon2`).

---

### 2. Login sem proteção contra força bruta
- **Descrição:** Não há limite de tentativas de login.  
- **MITRE ATT&CK:** [Brute Force – T1110](https://attack.mitre.org/techniques/T1110/)  
- **Procedimento:** Teste automatizado de múltiplas senhas.  
- **Ferramenta:** `Hydra` ou `Burp Suite Intruder`.  
- **Correção:** Implementar bloqueio temporário e CAPTCHA.

---

### 3. Sessão insegura
- **Descrição:** `secret_key` fraca e fixa.  
- **MITRE ATT&CK:** [Session Hijacking – T1185](https://attack.mitre.org/techniques/T1185/)  
- **Procedimento:** Inspeção do código-fonte (`app.secret_key`).  
- **Ferramenta:** Revisão manual de código.  
- **Correção:** Usar chave forte e rotativa, cookies `HttpOnly` e `Secure`.

---

### 4. Upload sem validação
- **Descrição:** Qualquer arquivo é aceito e salvo sem sanitização.  
- **MITRE ATT&CK:** [Exploitation for Client Execution – T1203](https://attack.mitre.org/techniques/T1203/)  
- **Procedimento:** Upload de arquivo `.php` ou `.exe`.  
- **Ferramenta:** Navegador + interceptação com Burp Suite.  
- **Correção:** Restringir tipos de arquivos e sanitizar nomes.

---

### 5. Checkout inseguro
- **Descrição:** Dados de cartão exibidos em texto puro.  
- **MITRE ATT&CK:** [Exfiltration Over Web Service – T1567](https://attack.mitre.org/techniques/T1567/)  
- **Procedimento:** Teste de compra fictícia e inspeção da resposta HTTP.  
- **Ferramenta:** Navegador + DevTools (Network).  
- **Correção:** Usar gateway de pagamento seguro (Stripe, PayPal).

---

### 6. Reviews vulneráveis a XSS
- **Descrição:** Conteúdo exibido sem sanitização.  
- **MITRE ATT&CK:** [Input Capture – T1056](https://attack.mitre.org/techniques/T1056/)  
- **Procedimento:** Inserção de `<script>alert('XSS')</script>` em review.  
- **Ferramenta:** Navegador.  
- **Correção:** Escapar HTML e usar bibliotecas de sanitização.

---

### 7. Painel admin com autorização fraca
- **Descrição:** Apenas verifica `session["username"] == "admin"`.  
- **MITRE ATT&CK:** [Privilege Escalation – T1068](https://attack.mitre.org/techniques/T1068/)  
- **Procedimento:** Manipulação manual de cookie de sessão.  
- **Ferramenta:** Burp Suite (modificação de cookies).  
- **Correção:** Implementar RBAC e autenticação multifator.

---

### 8. Debug mode ativo
- **Descrição:** Flask roda com `debug=True`.  
- **MITRE ATT&CK:** [Exploitation for Privilege Escalation – T1068](https://attack.mitre.org/techniques/T1068/)  
- **Procedimento:** Acesso ao debugger interativo via navegador.  
- **Ferramenta:** Navegador.  
- **Correção:** Desativar debug em produção.

---

### 9. CSRF ausente
- **Descrição:** Nenhuma rota POST tem proteção contra CSRF.  
- **MITRE ATT&CK:** [Exploitation of Web Service – T1190](https://attack.mitre.org/techniques/T1190/)  
- **Procedimento:** Criação de formulário malicioso externo que envia POST para OlafStore.  
- **Ferramenta:** HTML simples + navegador.  
- **Correção:** Implementar tokens CSRF em formulários.

---

### 10. Upload com path traversal
- **Descrição:** Nome do arquivo não é sanitizado.  
- **MITRE ATT&CK:** [Path Traversal – T1006](https://attack.mitre.org/techniques/T1006/)  
- **Procedimento:** Upload de arquivo com nome `../../etc/passwd`.  
- **Ferramenta:** Burp Suite (alteração do campo filename).  
- **Correção:** Normalizar nomes e usar UUIDs.

---

### 11. Busca vulnerável a SQL Injection
- **Descrição:** A rota `/search` concatena diretamente o input do usuário na query SQL.  
- **MITRE ATT&CK:** [Exploitation for Client Execution – T1190](https://attack.mitre.org/techniques/T1190/)  
- **Procedimento:**  
  - Teste manual: `' OR '1'='1` → retorna todos os produtos.  
  - Extração de credenciais (exemplo educacional):  
    ```sql
    ' UNION SELECT id, username, 0, password, 'fake.jpg' FROM users --
    ```  
  - Ferramenta automatizada:  
    ```bash
    sqlmap -u "http://localhost:5000/search?q=test" --dump
    ```  
    → Lista todas as tabelas e dados, incluindo usuários e senhas.  
- **Correção:** Usar parâmetros preparados:  
  ```python
  c.execute("SELECT id, name, price, description, image FROM products WHERE name LIKE ?", (f"%{term}%",))
