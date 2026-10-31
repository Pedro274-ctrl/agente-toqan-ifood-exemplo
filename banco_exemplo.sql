-- Exemplo mínimo para testar o agente
-- Use seu banco.sql completo do Barra Space para produção

CREATE TABLE IF NOT EXISTS condominos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  sala VARCHAR(50),
  categoria VARCHAR(100),
  contato VARCHAR(255),
  visibilidade ENUM('ativo','inativo') DEFAULT 'ativo'
);

INSERT INTO condominos (nome, sala, categoria, contato, visibilidade) VALUES
('Empresa Exemplo Tech', '101', 'Tecnologia', 'contato@exemplotech.com', 'ativo'),
('Consultoria Barra', '205', 'Consultoria', '11 99999-0000', 'ativo'),
('Advocacia Silva', '310', 'Jurídico', 'contato@silva.adv.br', 'ativo');
