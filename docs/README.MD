# 📊 Dashboard Analítico Desktop em Python (PDF Analytics)

Projeto desktop em Python para **extração, tratamento e análise de dados de pedidos em PDF**, com visualização em dashboards interativos inspirados em ferramentas de Business Intelligence.

O sistema funciona **offline**, processa PDFs localmente e gera métricas e gráficos voltados ao **setor de vendas em varejo**.

---

## 🎯 Objetivo do Projeto

Criar um motor analítico que:

- Leia automaticamente pedidos em PDF a partir de uma pasta
- Extraia dados relevantes (cliente, data, produtos, valores)
- Normalize e valide as informações
- Armazene os dados localmente
- Gere métricas e KPIs de vendas
- Exiba dashboards interativos em uma aplicação desktop

---

## 🧠 Conceitos-chave

### ETL (Extract, Transform, Load)

- **Extract**: leitura de dados brutos dos PDFs  
- **Transform**: limpeza, padronização e validação dos dados  
- **Load**: persistência dos dados em banco local  

### UI (User Interface)

- Interface gráfica desktop  
- Responsável apenas por exibir dados e acionar ações  
- Implementada com **DearPyGui**  

---

## 🏗️ Arquitetura Geral

```
PDFs → ETL → SQLite → Analytics → UI (DearPyGui)
```

---

## 📁 Estrutura de Pastas

```
logosBi_desktop/
│
├── input/
│   └── pdfs/
├── processed/
├── failed/
├── data/
│   └── database.db
├── reports/
├── src/
│   ├── etl/
│   ├── storage/
│   ├── analytics/
│   ├── ui/
│   └── main.py
└── requirements.txt
```

---

## 🔄 Fluxo de Execução

1. PDFs são adicionados à pasta `input/pdfs`
2. Usuário aciona o processamento via interface
3. ETL extrai, transforma e salva os dados
4. Dados são analisados
5. Dashboards são atualizados

---

## 📦 Tecnologias Utilizadas

- Python 3.10+
- DearPyGui
- pandas
- SQLite
- pdfplumber
- pytesseract

---

## ✍️ Desenvolvimento

Projeto desenvolvido e em constante evolução pela **TH Sistemas**, como solução analítica desktop voltada ao setor de varejo, com foco em **automação, clareza arquitetural e manutenção a longo prazo**.
