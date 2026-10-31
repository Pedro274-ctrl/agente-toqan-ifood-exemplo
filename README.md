<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:001F3F,100:00BFFF&height=160&section=header&text=Pedro%20Henrique&fontSize=40&fontColor=fff&animation=fadeIn&fontAlignY=36&desc=Eng.%20Software%204%C2%BA%20sem%20%7C%20Full-Stack%20%7C%20Automa%C3%A7%C3%A3o%20%7C%20IA&descAlignY=58" />

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=JetBrains+Mono&size=20&pause=1000&center=true&vCenter=true&width=600&lines=Construo+sistemas+que+economizam+horas;Portais+internos+%2B+automa%C3%A7%C3%A3o+%2B+integra%C3%A7%C3%A3o+de+APIs;Rio+de+Janeiro+-+Remoto" />
</p>

<p align="center">
  <a href="https://www.linkedin.com/in/pedro-henrique-costa-0a8648260"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" /></a>
  <a href="mailto:pedro274.phh@gmail.com"><img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" /></a>
  <a href="https://github.com/Pedro274-ctrl"><img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" /></a>
</p>

---

```javascript
const pedro = {
  formação: "Eng. Software - Estácio - 4º semestre - conclusão Out/2028",
  trabalho: "Analista de Suporte de Sistemas - Marinha - Mar/2022 até hoje",
  infra: "Linux Debian, LAMP, DNS, DHCP, iptables, Samba 4, Squid, FTP, IredMail - 99% uptime",
  código: "PHP + APIs Email/WhatsApp, MySQL, PDO, RBAC, React, Node, REST",
  ia: "Python, FastAPI, OpenAI API, RAG, Prompt Engineering",
  conquista: "1º Lugar - Formação de Fuzileiros Navais"
}
```

---

### Como eu construo

```mermaid
flowchart LR
    A[Webhook] --> B[OpenAI API + n8n]
    B --> C[RAG + Enriquecimento]
    C --> D[MySQL / PostgreSQL]
    D --> E[Email / WhatsApp API]
    style B fill:#00BFFF,stroke:#001F3F,color:#fff
```

Ferramentas internas deployadas, não protótipos. Backend + frontend + banco + automação conectados.

---

### Stack

<p align="center">
  <img src="https://skillicons.dev/icons?i=py,fastapi,js,php,react,nodejs,express,mysql,postgres,sqlite,linux,git&perline=8" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/OpenAI_API-412991?style=flat&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/n8n-EA4B71?style=flat&logo=n8n&logoColor=white" />
  <img src="https://img.shields.io/badge/Pydantic-E92063?style=flat&logo=pydantic&logoColor=white" />
  <img src="https://img.shields.io/badge/PDO-4479A1?style=flat" />
  <img src="https://img.shields.io/badge/PHPMailer-777BB4?style=flat" />
</p>

---

### Projetos

**[Agente Toqan - RAG no Diretório do Barra Space Center](https://github.com/Pedro274-ctrl/agente-toqan-ifood-exemplo)**
Camada de IA sobre o diretório de empresas do Barra Space Center, no padrão de orquestração do Toqan (iFood): Webhook → LLM → Banco → Resposta. Recebe perguntas em linguagem natural ("quais empresas de tecnologia estão ativas?"), busca o contexto no MySQL e gera a resposta com a OpenAI API, restrita ao que existe no diretório e com as fontes (IDs) e o tempo de resposta. Um primeiro passo com o LLM extrai os filtros da pergunta em JSON (categoria + termos), com fallback local se a API falhar. Validação com Pydantic, consultas parametrizadas e chaves em `.env`. Próximos passos: busca vetorial com embeddings, workflow n8n com Email/WhatsApp e Docker.
`Python | FastAPI | OpenAI API | RAG | MySQL | Pydantic | REST API`

**[Barra Space Center](https://github.com/Pedro274-ctrl/barraspace)**
Site institucional + painel admin com RBAC (gerência, operador, padrão). Diretório dinâmico com busca, ordenação, filtros e exportação. Autenticação com hash, PDO parametrizado, validação server-side e SMTP.
`PHP | MySQL | PDO | RBAC | JavaScript | Composer`

**[Banca de Chopp - Sistema de Comandas](https://github.com/Pedro274-ctrl/banca-de-Chopp)**
Sistema de comanda digital para feira de rua. Gestão de vendas, estoque e pedidos com dashboard interno. Automação que elimina planilha manual.
`React | Node.js | SQLite | REST API`

**[Site TF Soluções](https://github.com/274-ctrl/site-tf-solucoes)**
Site institucional da TF Soluções Tecnológicas com formulário seguro e envio SMTP.
`PHP | MySQL | PHPMailer | HTML/CSS/JS`

---

### Experiência e Formação

- **Marinha do Brasil** - Analista de Suporte - 4 anos - LAMP, ticketing, automações PHP + APIs
- **TF Soluções Tecnológicas** - Full-Stack - sistemas de gestão e portais internos para clientes reais
- **Eng. Software - Estácio** - 4º semestre
- **Formação Completa em IA 2026**, Servidores Linux Debian, Cisco Cybersecurity, LGPD, Automação IFRS, Liderança IFRS

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:00BFFF,100:001F3F&height=80&section=footer&text=Full-Stack+%7C+Automa%C3%A7%C3%A3o+%7C+IA&fontSize=14&fontColor=fff" />
</p>
