-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS = @@UNIQUE_CHECKS, UNIQUE_CHECKS = 0;
SET @OLD_FOREIGN_KEY_CHECKS = @@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS = 0;
SET @OLD_SQL_MODE = @@SQL_MODE, SQL_MODE ='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema database_elo
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `database_elo`;

-- -----------------------------------------------------
-- Schema database_elo
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `database_elo` DEFAULT CHARACTER SET utf8mb3;
USE `database_elo`;

-- -----------------------------------------------------
-- Table `database_elo`.`usuario`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`usuario`
(
    `id_usuario`         INT           NOT NULL AUTO_INCREMENT,
    `nm_nome`            VARCHAR(45)   NOT NULL,
    `nm_sobrenome`       VARCHAR(45)   NULL DEFAULT NULL,
    `ds_email`           VARCHAR(200)  NOT NULL,
    `senha`              VARCHAR(200)  NOT NULL,
    `dt_criacao`         DATETIME      NULL DEFAULT NULL,
    `tel_celular`        VARCHAR(45)   NULL DEFAULT NULL,
    `tel_whats`          VARCHAR(45)   NULL DEFAULT NULL,
    `qt_avaliacao_geral` DECIMAL(2, 1) NULL DEFAULT NULL,
    `qt_avaliacoes`      INT           NULL DEFAULT '0',
    `uri_perfil`         VARCHAR(255)  NULL DEFAULT NULL,
    `st_habilitado`      TINYINT(1)    NOT NULL,
    `dt_atualizacao`     DATETIME      NULL DEFAULT NULL,
    PRIMARY KEY (`id_usuario`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE UNIQUE INDEX `ds_email_UNIQUE` ON `database_elo`.`usuario` (`ds_email` ASC) VISIBLE;

CREATE INDEX `idx_usuario_atualizacao` ON `database_elo`.`usuario` (`dt_atualizacao` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`profissional`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`profissional`
(
    `usuario_id`            INT          NOT NULL,
    `dt_criacao`            DATETIME     NULL DEFAULT NULL,
    `st_disponivel`         TINYINT      NULL DEFAULT '0',
    `ds_apresentacao`       VARCHAR(200) NULL DEFAULT NULL,
    `uri_perfil`            VARCHAR(200) NULL DEFAULT NULL,
    `st_habilitado`         TINYINT(1)   NOT NULL,
    `qt_servicos_concluido` INT          NULL DEFAULT NULL,
    `ds_especialidades`     VARCHAR(255) NULL DEFAULT NULL,
    `dt_atualizacao`        DATETIME     NULL DEFAULT NULL,
    PRIMARY KEY (`usuario_id`),
    CONSTRAINT `fk_Profissional_Usuario0`
    FOREIGN KEY (`usuario_id`)
    REFERENCES `database_elo`.`usuario` (`id_usuario`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `fk_Profissional_Usuario_idx` ON `database_elo`.`profissional` (`usuario_id` ASC) VISIBLE;

CREATE INDEX `idx_profissional_atualizacao` ON `database_elo`.`profissional` (`dt_atualizacao` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`area_atendimento`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`area_atendimento`
(
    `id_area_Atendimento` INT         NOT NULL AUTO_INCREMENT,
    `fk_id_profissional`  INT         NOT NULL,
    `nr_latitude`         DOUBLE      NULL DEFAULT NULL,
    `nr_longitude`        DOUBLE      NULL DEFAULT NULL,
    `nr_raio`             INT         NULL DEFAULT NULL,
    `nm_cidade`           VARCHAR(45) NULL DEFAULT NULL,
    `nm_estado`           VARCHAR(45) NULL DEFAULT NULL,
    `nm_bairro`           VARCHAR(45) NULL DEFAULT NULL,
    `dt_criacao`          DATETIME    NULL DEFAULT NULL,
    PRIMARY KEY (`id_area_Atendimento`),
    CONSTRAINT `fk_Area_Atendimento_Profissional1`
    FOREIGN KEY (`fk_id_profissional`)
    REFERENCES `database_elo`.`profissional` (`usuario_id`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `fk_Area_Atendimento_Profissional1_idx` ON `database_elo`.`area_atendimento` (`fk_id_profissional` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`orcamento_status`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`orcamento_status`
(
    `id_orcamento_status` INT          NOT NULL AUTO_INCREMENT,
    `ds_status`           VARCHAR(100) NOT NULL,
    PRIMARY KEY (`id_orcamento_status`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE UNIQUE INDEX `uk_orcamento_status_ds_status` ON `database_elo`.`orcamento_status` (`ds_status` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`categoria_geral`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`categoria_geral`
(
    `id_categoria_geral` INT          NOT NULL AUTO_INCREMENT,
    `nm_categoria`       VARCHAR(100) NULL DEFAULT NULL,
    `ds_icon`            VARCHAR(50)  NULL DEFAULT NULL,
    PRIMARY KEY (`id_categoria_geral`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE UNIQUE INDEX `uk_categoria_geral_nome` ON `database_elo`.`categoria_geral` (`nm_categoria` ASC) VISIBLE;

CREATE INDEX `categoria_geral_id_idx` ON `database_elo`.`categoria_geral` (`id_categoria_geral` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`categoria_especifica`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`categoria_especifica`
(
    `id_categoria_especifica` INT          NOT NULL AUTO_INCREMENT,
    `fk_id_categoria_geral`   INT          NOT NULL,
    `nm_categoria_especifica` VARCHAR(100) NOT NULL,
    PRIMARY KEY (`id_categoria_especifica`),
    CONSTRAINT `fk_categoria_geral_id`
    FOREIGN KEY (`fk_id_categoria_geral`)
    REFERENCES `database_elo`.`categoria_geral` (`id_categoria_geral`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE UNIQUE INDEX `uk_categoria_especifica` ON `database_elo`.`categoria_especifica` (`fk_id_categoria_geral` ASC, `nm_categoria_especifica` ASC) VISIBLE;

CREATE INDEX `fk_categoria_geral_id_idx` ON `database_elo`.`categoria_especifica` (`fk_id_categoria_geral` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`servico`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`servico`
(
    `id_servico`                 INT                           NOT NULL AUTO_INCREMENT,
    `fk_id_profissional_usuario` INT                           NOT NULL,
    `fk_id_categoria_especifica` INT                           NOT NULL,
    `ds_descricao`               VARCHAR(200)                  NULL DEFAULT NULL,
    `vl_servico`                 DOUBLE                        NULL DEFAULT NULL,
    `ds_tag`                     VARCHAR(200)                  NULL DEFAULT NULL,
    `tp_execucao`                ENUM ('presencial', 'remoto') NULL DEFAULT NULL,
    `st_ativo`                   TINYINT(1)                    NULL DEFAULT NULL,
    `nr_tempo_experiencia`       INT                           NULL DEFAULT NULL,
    `dt_atualizacao`             DATETIME                      NULL DEFAULT NULL,
    `qt_reservado`               INT                           NULL DEFAULT NULL,
    `nr_avaliacao_geral`         DOUBLE                        NULL DEFAULT NULL,
    PRIMARY KEY (`id_servico`),
    CONSTRAINT `fk_Servico_Categoria_Especifica1`
    FOREIGN KEY (`fk_id_categoria_especifica`)
    REFERENCES `database_elo`.`categoria_especifica` (`id_categoria_especifica`),
    CONSTRAINT `fk_Servico_Profissional1`
    FOREIGN KEY (`fk_id_profissional_usuario`)
    REFERENCES `database_elo`.`profissional` (`usuario_id`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `fk_Servico_Profissional_idx` ON `database_elo`.`servico` (`fk_id_profissional_usuario` ASC) VISIBLE;

CREATE INDEX `fk_Servico_Categoria_Especifica1_idx` ON `database_elo`.`servico` (`fk_id_categoria_especifica` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`orcamento`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`orcamento`
(
    `id_orcamento`               INT          NOT NULL AUTO_INCREMENT,
    `fk_id_servico`              INT          NOT NULL,
    `fk_id_usuario`              INT          NOT NULL,
    `fk_id_orcamento_status`     INT          NOT NULL,
    `ds_descricao`               VARCHAR(100) NULL DEFAULT NULL,
    `ds_observacao_profissional` VARCHAR(200) NULL DEFAULT NULL,
    `tp_motivo_cancelamento`     VARCHAR(50)  NULL DEFAULT NULL,
    `ds_descricao_cancelamento`  VARCHAR(200) NULL DEFAULT NULL,
    `tp_autor_cancelamento`      VARCHAR(20)  NULL DEFAULT NULL,
    `fk_id_usuario_cancelamento` INT          NULL DEFAULT NULL,
    `dt_cancelamento`            DATETIME(3)  NULL DEFAULT NULL,
    `fk_id_usuario_conclusao`    INT          NULL DEFAULT NULL,
    `ds_observacao_conclusao`    VARCHAR(200) NULL DEFAULT NULL,
    `dt_conclusao`               DATETIME(3)  NULL DEFAULT NULL,
    `dt_preferido_solicitado`    DATETIME     NULL DEFAULT NULL,
    `dt_inicio_proposto`         DATETIME     NULL DEFAULT NULL,
    `dt_fim_proposto`            DATETIME     NULL DEFAULT NULL,
    `dt_criacao`                 DATETIME     NULL DEFAULT NULL,
    PRIMARY KEY (`id_orcamento`),
    CONSTRAINT `ck_orcamento_intervalo_proposto`
    CHECK (
(`dt_inicio_proposto` IS NULL AND `dt_fim_proposto` IS NULL)
    OR
(`dt_inicio_proposto` IS NOT NULL AND `dt_fim_proposto` IS NOT NULL AND `dt_inicio_proposto` < `dt_fim_proposto`)
    ),
    CONSTRAINT `fk_Orcamento_Orcamento_Status1`
    FOREIGN KEY (`fk_id_orcamento_status`)
    REFERENCES `database_elo`.`orcamento_status` (`id_orcamento_status`),
    CONSTRAINT `fk_Orcamento_Servico1`
    FOREIGN KEY (`fk_id_servico`)
    REFERENCES `database_elo`.`servico` (`id_servico`),
    CONSTRAINT `fk_Orcamento_Usuario1`
    FOREIGN KEY (`fk_id_usuario`)
    REFERENCES `database_elo`.`usuario` (`id_usuario`),
    CONSTRAINT `fk_Orcamento_Usuario_Cancelamento`
    FOREIGN KEY (`fk_id_usuario_cancelamento`)
    REFERENCES `database_elo`.`usuario` (`id_usuario`),
    CONSTRAINT `fk_Orcamento_Usuario_Conclusao`
    FOREIGN KEY (`fk_id_usuario_conclusao`)
    REFERENCES `database_elo`.`usuario` (`id_usuario`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `fk_Orcamento_Orcamento_Status1_idx` ON `database_elo`.`orcamento` (`fk_id_orcamento_status` ASC) VISIBLE;

CREATE INDEX `fk_Orcamento_Usuario1_idx` ON `database_elo`.`orcamento` (`fk_id_usuario` ASC) VISIBLE;

CREATE INDEX `fk_Orcamento_Servico1_idx` ON `database_elo`.`orcamento` (`fk_id_servico` ASC) VISIBLE;

CREATE INDEX `fk_Orcamento_Usuario_Cancelamento_idx` ON `database_elo`.`orcamento` (`fk_id_usuario_cancelamento` ASC) VISIBLE;

CREATE INDEX `idx_orcamento_cliente_status_cursor` ON `database_elo`.`orcamento`
    (`fk_id_usuario` ASC, `fk_id_orcamento_status` ASC, `id_orcamento` DESC) VISIBLE;

CREATE INDEX `fk_Orcamento_Usuario_Conclusao_idx` ON `database_elo`.`orcamento` (`fk_id_usuario_conclusao` ASC) VISIBLE;

CREATE INDEX `idx_orcamento_agenda` ON `database_elo`.`orcamento`
    (`fk_id_servico` ASC, `fk_id_orcamento_status` ASC, `dt_inicio_proposto` ASC, `dt_fim_proposto` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`avaliacao_reserva`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`avaliacao_reserva`
(
    `id_avaliacao_reserva`    INT          NOT NULL AUTO_INCREMENT,
    `fk_id_reserva`           INT          NOT NULL,
    `fk_id_avaliador_usuario` INT          NOT NULL,
    `fk_id_usuario_avaliado`  INT          NOT NULL,
    `qt_nota`                 TINYINT      NOT NULL,
    `ds_comentario`           VARCHAR(200) NULL DEFAULT NULL,
    `dt_criacao`              DATETIME     NULL DEFAULT NULL,
    `observacao_profisional`  VARCHAR(200) NULL DEFAULT NULL,
    `distancia`               DOUBLE       NULL DEFAULT NULL,
    `ds_endereco`             VARCHAR(45)  NULL DEFAULT NULL,
    PRIMARY KEY (`id_avaliacao_reserva`),
    CONSTRAINT `fk_Avaliacao_Reserva_Reserva1`
    FOREIGN KEY (`fk_id_reserva`)
    REFERENCES `database_elo`.`orcamento` (`id_orcamento`),
    CONSTRAINT `fk_Avaliacao_Reserva_Usuario1`
    FOREIGN KEY (`fk_id_avaliador_usuario`)
    REFERENCES `database_elo`.`usuario` (`id_usuario`),
    CONSTRAINT `fk_Avaliacao_Reserva_Usuario2`
    FOREIGN KEY (`fk_id_usuario_avaliado`)
    REFERENCES `database_elo`.`usuario` (`id_usuario`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE UNIQUE INDEX `uk_avaliacao_reserva_avaliador` ON `database_elo`.`avaliacao_reserva` (`fk_id_reserva` ASC, `fk_id_avaliador_usuario` ASC) VISIBLE;

CREATE INDEX `fk_Avaliacao_Reserva_Reserva1_idx` ON `database_elo`.`avaliacao_reserva` (`fk_id_reserva` ASC) VISIBLE;

CREATE INDEX `fk_Avaliacao_Reserva_Usuario1_idx` ON `database_elo`.`avaliacao_reserva` (`fk_id_avaliador_usuario` ASC) VISIBLE;

CREATE INDEX `fk_Avaliacao_Reserva_Usuario2_idx` ON `database_elo`.`avaliacao_reserva` (`fk_id_usuario_avaliado` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`endereco_usuario`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`endereco_usuario`
(
    `id_endereco_usuario` INT                                             NOT NULL AUTO_INCREMENT,
    `nm_rua`              VARCHAR(200)                                    NULL DEFAULT NULL,
    `nm_complemento`      VARCHAR(45)                                     NULL DEFAULT NULL,
    `nm_bairro`           VARCHAR(45)                                     NULL DEFAULT NULL,
    `nm_cidade`           VARCHAR(45)                                     NULL DEFAULT NULL,
    `nm_estado`           VARCHAR(2)                                      NULL DEFAULT NULL,
    `nr_cep`              VARCHAR(10)                                     NULL DEFAULT NULL,
    `st_tipo`             ENUM ('casa', 'empresa', 'comercial', 'remoto') NULL DEFAULT NULL,
    `dt_criacao`          DATETIME                                        NULL DEFAULT NULL,
    `st_principal`        TINYINT                                         NULL DEFAULT NULL,
    `nr_latitude`         DOUBLE                                          NULL DEFAULT NULL,
    `nr_longitude`        DOUBLE                                          NULL DEFAULT NULL,
    `fk_usuario_id`       INT                                             NOT NULL,
    `st_ativo`            TINYINT(1)                                      NULL DEFAULT NULL,
    `nm_apelido`          VARCHAR(80)                                     NULL DEFAULT NULL,
    `nr_rua`              INT                                             NULL DEFAULT NULL,
    PRIMARY KEY (`id_endereco_usuario`),
    CONSTRAINT `fk_Endereco_Usuario1`
    FOREIGN KEY (`fk_usuario_id`)
    REFERENCES `database_elo`.`usuario` (`id_usuario`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `fk_Endereco_Usuario1_idx` ON `database_elo`.`endereco_usuario` (`fk_usuario_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`orcamento_custos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`orcamento_custos`
(
    `id_orcamento_custos` INT         NOT NULL AUTO_INCREMENT,
    `fk_id_orcamento`     INT         NOT NULL,
    `ds_descricao`        VARCHAR(45) NULL DEFAULT NULL,
    `vl_valor`            DOUBLE      NULL DEFAULT NULL,
    PRIMARY KEY (`id_orcamento_custos`),
    CONSTRAINT `fk_Orcamento_Custos_Orcamento1`
    FOREIGN KEY (`fk_id_orcamento`)
    REFERENCES `database_elo`.`orcamento` (`id_orcamento`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `fk_Orcamento_Custos_Orcamento1_idx` ON `database_elo`.`orcamento_custos` (`fk_id_orcamento` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`orcamento_endereco`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`orcamento_endereco`
(
    `id_orcamento_endereco` INT         NOT NULL AUTO_INCREMENT,
    `fk_id_orcamento`       INT         NOT NULL,
    `nm_rua`                VARCHAR(200) NULL DEFAULT NULL,
    `nm_complemento`        VARCHAR(45) NULL DEFAULT NULL,
    `nm_bairro`             VARCHAR(45) NULL DEFAULT NULL,
    `nm_cidade`             VARCHAR(45) NULL DEFAULT NULL,
    `nm_estado`             VARCHAR(45) NULL DEFAULT NULL,
    `nr_cep`                VARCHAR(45) NULL DEFAULT NULL,
    `nr_rua`                INT         NULL DEFAULT NULL,
    `nr_latitude`           DOUBLE      NULL DEFAULT NULL,
    `nr_longitude`          DOUBLE      NULL DEFAULT NULL,
    PRIMARY KEY (`id_orcamento_endereco`),
    CONSTRAINT `uk_orcamento_endereco_orcamento`
    UNIQUE (`fk_id_orcamento`),
    CONSTRAINT `fk_Orcamento_endereco_Orcamento1`
    FOREIGN KEY (`fk_id_orcamento`)
    REFERENCES `database_elo`.`orcamento` (`id_orcamento`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `fk_Orcamento_endereco_Orcamento1_idx` ON `database_elo`.`orcamento_endereco` (`fk_id_orcamento` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`orcamento_imagem`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`orcamento_imagem`
(
    `id_orcamento_imagem` INT          NOT NULL AUTO_INCREMENT,
    `ds_chave_imagem`     VARCHAR(500) NOT NULL,
    `fk_id_orcamento`     INT          NOT NULL,
    PRIMARY KEY (`id_orcamento_imagem`),
    CONSTRAINT `fk_Orcamento_Imagem_Orcamento`
    FOREIGN KEY (`fk_id_orcamento`)
    REFERENCES `database_elo`.`orcamento` (`id_orcamento`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `fk_Orcamento_Imagem_Orcamento_idx` ON `database_elo`.`orcamento_imagem` (`fk_id_orcamento` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`publicacao`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`publicacao`
(
    `id_publicacao`              INT          NOT NULL AUTO_INCREMENT,
    `fk_profissional_usuario_id` INT          NOT NULL,
    `fk_categoria_Especifica_id` INT          NOT NULL,
    `ds_publicacao`              VARCHAR(100) NULL DEFAULT NULL,
    `dt_publicacao`              DATETIME     NULL DEFAULT NULL,
    `st_ativo`                   TINYINT      NULL DEFAULT NULL,
    PRIMARY KEY (`id_publicacao`),
    CONSTRAINT `fk_Publicacao_Categoria_Especifica1`
    FOREIGN KEY (`fk_categoria_Especifica_id`)
    REFERENCES `database_elo`.`categoria_especifica` (`id_categoria_especifica`),
    CONSTRAINT `fk_Publicacao_Profissional1`
    FOREIGN KEY (`fk_profissional_usuario_id`)
    REFERENCES `database_elo`.`profissional` (`usuario_id`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `fk_Publicacao_Profissional1_idx` ON `database_elo`.`publicacao` (`fk_profissional_usuario_id` ASC) VISIBLE;

CREATE INDEX `fk_Publicacao_Categoria_Especifica1_idx` ON `database_elo`.`publicacao` (`fk_categoria_Especifica_id` ASC) VISIBLE;

CREATE INDEX `idx_publicacao_feed` ON `database_elo`.`publicacao` (`st_ativo` ASC, `dt_publicacao` DESC, `id_publicacao` DESC) VISIBLE;

CREATE INDEX `idx_publicacao_feed_categoria` ON `database_elo`.`publicacao` (`fk_categoria_Especifica_id` ASC,
                                                                             `st_ativo` ASC, `dt_publicacao` DESC,
                                                                             `id_publicacao` DESC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`publicacao_comentario`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`publicacao_comentario`
(
    `id_publicacao_comentario` INT          NOT NULL AUTO_INCREMENT,
    `fk_publicacao_id`         INT          NOT NULL,
    `fk_usuario_id`            INT          NOT NULL,
    `fk_comentario_pai`        INT          NULL DEFAULT NULL,
    `ds_comentario`            VARCHAR(200) NULL DEFAULT NULL,
    `dt_comentario`            DATETIME     NULL DEFAULT NULL,
    `st_ativo`                 TINYINT      NULL DEFAULT NULL,
    PRIMARY KEY (`id_publicacao_comentario`),
    CONSTRAINT `fk_Publicacao_Comentario_Publicacao1`
    FOREIGN KEY (`fk_publicacao_id`)
    REFERENCES `database_elo`.`publicacao` (`id_publicacao`),
    CONSTRAINT `fk_Publicacao_Comentario_Publicacao_Comentario1`
    FOREIGN KEY (`fk_comentario_pai`)
    REFERENCES `database_elo`.`publicacao_comentario` (`id_publicacao_comentario`),
    CONSTRAINT `fk_Publicacao_Comentario_Usuario1`
    FOREIGN KEY (`fk_usuario_id`)
    REFERENCES `database_elo`.`usuario` (`id_usuario`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `fk_Publicacao_Comentario_Usuario1_idx` ON `database_elo`.`publicacao_comentario` (`fk_usuario_id` ASC) VISIBLE;

CREATE INDEX `fk_Publicacao_Comentario_Publicacao_Comentario_idx` ON `database_elo`.`publicacao_comentario` (`fk_comentario_pai` ASC) INVISIBLE;

CREATE INDEX `fk_Publicacao_Comentario_Publicacao_idx` ON `database_elo`.`publicacao_comentario` (`fk_publicacao_id` ASC, `dt_comentario` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`publicacao_curtida`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`publicacao_curtida`
(
    `id_publicacao` INT      NOT NULL,
    `id_usuario`    INT      NOT NULL,
    `dt_curtida`    DATETIME NULL DEFAULT NULL,
    PRIMARY KEY (`id_publicacao`, `id_usuario`),
    CONSTRAINT `fk_Publicacao_Curtida_Publicacao1`
    FOREIGN KEY (`id_publicacao`)
    REFERENCES `database_elo`.`publicacao` (`id_publicacao`),
    CONSTRAINT `fk_Publicacao_Curtida_Usuario1`
    FOREIGN KEY (`id_usuario`)
    REFERENCES `database_elo`.`usuario` (`id_usuario`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `fk_Publicacao_Curtida_Usuario1_idx` ON `database_elo`.`publicacao_curtida` (`id_usuario` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`publicacao_imagem`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`publicacao_imagem`
(
    `id_publicacao_Imagem` INT          NOT NULL AUTO_INCREMENT,
    `fk_publicacao_id`     INT          NOT NULL,
    `ds_chave_imagem`      VARCHAR(500) NULL DEFAULT NULL,
    `nr_ordem`             INT          NULL DEFAULT NULL,
    PRIMARY KEY (`id_publicacao_Imagem`),
    CONSTRAINT `fk_Publicacao_Imagem_Publicacao1`
    FOREIGN KEY (`fk_publicacao_id`)
    REFERENCES `database_elo`.`publicacao` (`id_publicacao`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `fk_Publicacao_Imagem_Publicacao1_idx` ON `database_elo`.`publicacao_imagem` (`fk_publicacao_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`search_outbox`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`search_outbox`
(
    `id_search_outbox`   BIGINT      NOT NULL AUTO_INCREMENT,
    `fk_profissional_id` INT         NOT NULL,
    `dt_criacao`         DATETIME(3) NOT NULL,
    `dt_processamento`   DATETIME(3) NULL     DEFAULT NULL,
    `nr_tentativas`      INT         NOT NULL DEFAULT '0',
    PRIMARY KEY (`id_search_outbox`),
    CONSTRAINT `fk_Search_Outbox_Profissional`
    FOREIGN KEY (`fk_profissional_id`)
    REFERENCES `database_elo`.`profissional` (`usuario_id`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `fk_Search_Outbox_Profissional` ON `database_elo`.`search_outbox` (`fk_profissional_id` ASC) VISIBLE;

CREATE INDEX `idx_search_outbox_pendente` ON `database_elo`.`search_outbox` (`dt_processamento` ASC, `nr_tentativas` ASC, `id_search_outbox` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`usuario_dispositivo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`usuario_dispositivo`
(
    `id_usuario_dispositivo` BIGINT       NOT NULL AUTO_INCREMENT,
    `fk_usuario_id`          INT          NOT NULL,
    `cd_dispositivo`         VARCHAR(100) NOT NULL,
    `ds_identificador_fcm`   VARCHAR(512) NOT NULL,
    `tp_identificador_fcm`   VARCHAR(10)  NOT NULL,
    `tp_plataforma`          VARCHAR(10)  NOT NULL,
    `st_ativo`               TINYINT(1)   NOT NULL DEFAULT 1,
    `dt_criacao`             DATETIME(3)  NOT NULL,
    `dt_atualizacao`         DATETIME(3)  NOT NULL,
    PRIMARY KEY (`id_usuario_dispositivo`),
    CONSTRAINT `fk_Usuario_Dispositivo_Usuario`
    FOREIGN KEY (`fk_usuario_id`)
    REFERENCES `database_elo`.`usuario` (`id_usuario`),
    CONSTRAINT `uk_usuario_dispositivo_codigo`
    UNIQUE (`fk_usuario_id`, `cd_dispositivo`),
    CONSTRAINT `uk_usuario_dispositivo_fcm`
    UNIQUE (`ds_identificador_fcm`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `idx_usuario_dispositivo_ativo` ON `database_elo`.`usuario_dispositivo` (`fk_usuario_id` ASC, `st_ativo` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`notificacao`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`notificacao`
(
    `id_notificacao`             BIGINT       NOT NULL AUTO_INCREMENT,
    `fk_usuario_destinatario_id` INT          NOT NULL,
    `fk_orcamento_id`            INT          NOT NULL,
    `tp_notificacao`             VARCHAR(60)  NOT NULL,
    `cd_chave_evento`            VARCHAR(160) NOT NULL,
    `ds_titulo`                  VARCHAR(120) NOT NULL,
    `ds_mensagem`                VARCHAR(500) NOT NULL,
    `dt_criacao`                 DATETIME(3)  NOT NULL,
    `dt_leitura`                 DATETIME(3)  NULL DEFAULT NULL,
    PRIMARY KEY (`id_notificacao`),
    CONSTRAINT `fk_Notificacao_Usuario`
    FOREIGN KEY (`fk_usuario_destinatario_id`)
    REFERENCES `database_elo`.`usuario` (`id_usuario`),
    CONSTRAINT `fk_Notificacao_Orcamento`
    FOREIGN KEY (`fk_orcamento_id`)
    REFERENCES `database_elo`.`orcamento` (`id_orcamento`),
    CONSTRAINT `uk_notificacao_chave_evento`
    UNIQUE (`cd_chave_evento`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `idx_notificacao_listagem` ON `database_elo`.`notificacao` (`fk_usuario_destinatario_id` ASC, `id_notificacao` DESC) VISIBLE;
CREATE INDEX `idx_notificacao_nao_lida` ON `database_elo`.`notificacao` (`fk_usuario_destinatario_id` ASC, `dt_leitura` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`notificacao_outbox`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`notificacao_outbox`
(
    `id_notificacao_outbox`     BIGINT        NOT NULL AUTO_INCREMENT,
    `fk_notificacao_id`         BIGINT        NOT NULL,
    `fk_usuario_dispositivo_id` BIGINT        NULL DEFAULT NULL,
    `tp_canal`                  VARCHAR(20)   NOT NULL,
    `tp_status`                 VARCHAR(20)   NOT NULL,
    `cd_idempotencia`           VARCHAR(200)  NOT NULL,
    `nr_tentativas`             INT           NOT NULL DEFAULT 0,
    `dt_proxima_tentativa`      DATETIME(3)   NOT NULL,
    `dt_processando_desde`      DATETIME(3)   NULL DEFAULT NULL,
    `dt_processamento`          DATETIME(3)   NULL DEFAULT NULL,
    `cd_mensagem_provedor`      VARCHAR(255)  NULL DEFAULT NULL,
    `ds_ultimo_erro`            VARCHAR(1000) NULL DEFAULT NULL,
    `nr_versao`                 BIGINT        NOT NULL DEFAULT 0,
    `dt_criacao`                DATETIME(3)   NOT NULL,
    PRIMARY KEY (`id_notificacao_outbox`),
    CONSTRAINT `fk_Notificacao_Outbox_Notificacao`
    FOREIGN KEY (`fk_notificacao_id`)
    REFERENCES `database_elo`.`notificacao` (`id_notificacao`),
    CONSTRAINT `fk_Notificacao_Outbox_Dispositivo`
    FOREIGN KEY (`fk_usuario_dispositivo_id`)
    REFERENCES `database_elo`.`usuario_dispositivo` (`id_usuario_dispositivo`),
    CONSTRAINT `uk_notificacao_outbox_idempotencia`
    UNIQUE (`cd_idempotencia`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `idx_notificacao_outbox_pendente` ON `database_elo`.`notificacao_outbox` (`tp_status` ASC, `dt_proxima_tentativa` ASC, `nr_tentativas` ASC, `id_notificacao_outbox` ASC) VISIBLE;
CREATE INDEX `idx_notificacao_outbox_processando` ON `database_elo`.`notificacao_outbox` (`tp_status` ASC, `dt_processando_desde` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`servico_disponibilidade`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`servico_disponibilidade`
(
    `id_servico_disponibilidade` INT      NOT NULL AUTO_INCREMENT,
    `fk_id_servico`              INT      NOT NULL,
    `nr_dia_semana`              INT      NULL DEFAULT NULL,
    `hr_inicio`                  TIME     NULL DEFAULT NULL,
    `hr_fim`                     TIME     NULL DEFAULT NULL,
    `st_ativo`                   TINYINT  NOT NULL DEFAULT 1,
    `dt_criacao`                 DATETIME NULL DEFAULT NULL,
    PRIMARY KEY (`id_servico_disponibilidade`),
    CONSTRAINT `ck_Servico_Disponibilidade_Dia_Semana`
    CHECK (`nr_dia_semana` BETWEEN 1 AND 7),
    CONSTRAINT `ck_Servico_Disponibilidade_Horario`
    CHECK (`hr_inicio` < `hr_fim`),
    CONSTRAINT `fk_Servico_Disponibilidade_Servico1`
    FOREIGN KEY (`fk_id_servico`)
    REFERENCES `database_elo`.`servico` (`id_servico`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `fk_Servico_Disponibilidade_Servico1_idx` ON `database_elo`.`servico_disponibilidade` (`fk_id_servico` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `database_elo`.`servico_imagem`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_elo`.`servico_imagem`
(
    `id_servico_imagem` INT          NOT NULL AUTO_INCREMENT,
    `fk_id_servico`     INT          NOT NULL,
    `ds_chave_imagem`   VARCHAR(500) NULL DEFAULT NULL,
    `nr_ordem`          INT          NULL DEFAULT NULL,
    PRIMARY KEY (`id_servico_imagem`),
    CONSTRAINT `fk_Servico_Imagem_Servico`
    FOREIGN KEY (`fk_id_servico`)
    REFERENCES `database_elo`.`servico` (`id_servico`)
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `fk_Servico_Imagem_Servico_idx` ON `database_elo`.`servico_imagem` (`fk_id_servico` ASC) VISIBLE;


CREATE TABLE IF NOT EXISTS `database_elo`.`avaliacao_analise_pln`
(
    `id_avaliacao_analise_pln` BIGINT                                NOT NULL AUTO_INCREMENT,
    `fk_id_avaliacao_reserva`  INT                                   NOT NULL,
    `fk_id_profissional`       INT                                   NOT NULL,
    `tp_sentimento`            ENUM ('POSITIVO','NEUTRO','NEGATIVO') NOT NULL,
    `nr_confianca`             DECIMAL(5, 4)                         NOT NULL,
    `st_possui_inconsistencia` TINYINT(1)                            NOT NULL DEFAULT 0,
    `js_aspectos`              JSON                                  NULL,
    `cd_versao_modelo`         VARCHAR(64)                           NOT NULL,
    `dt_processamento`         DATETIME(3)                           NOT NULL,
    PRIMARY KEY (`id_avaliacao_analise_pln`),
    CONSTRAINT `uk_avaliacao_analise_pln_avaliacao`
    UNIQUE (`fk_id_avaliacao_reserva`),
    CONSTRAINT `ck_avaliacao_analise_pln_confianca`
    CHECK (`nr_confianca` BETWEEN 0 AND 1),
    CONSTRAINT `fk_Avaliacao_Analise_Pln_Avaliacao_Reserva`
    FOREIGN KEY (`fk_id_avaliacao_reserva`)
    REFERENCES `database_elo`.`avaliacao_reserva` (`id_avaliacao_reserva`)
    ON DELETE CASCADE,
    CONSTRAINT `fk_Avaliacao_Analise_Pln_Profissional`
    FOREIGN KEY (`fk_id_profissional`)
    REFERENCES `database_elo`.`profissional` (`usuario_id`)
    ON DELETE CASCADE
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `idx_avaliacao_analise_pln_profissional`
    ON `database_elo`.`avaliacao_analise_pln` (`fk_id_profissional` ASC) VISIBLE;

CREATE INDEX `idx_avaliacao_analise_pln_versao`
    ON `database_elo`.`avaliacao_analise_pln` (`cd_versao_modelo` ASC) VISIBLE;


CREATE TABLE IF NOT EXISTS `database_elo`.`profissional_reputacao_pln`
(
    `id_profissional_reputacao_pln` BIGINT        NOT NULL AUTO_INCREMENT,
    `fk_id_profissional`            INT           NOT NULL,
    `qt_comentarios_processados`    INT           NOT NULL DEFAULT 0,
    `qt_positivo`                   INT           NOT NULL DEFAULT 0,
    `qt_neutro`                     INT           NOT NULL DEFAULT 0,
    `qt_negativo`                   INT           NOT NULL DEFAULT 0,
    `nr_percentual_positivo`        DECIMAL(5, 2) NOT NULL DEFAULT 0,
    `nr_percentual_neutro`          DECIMAL(5, 2) NOT NULL DEFAULT 0,
    `nr_percentual_negativo`        DECIMAL(5, 2) NOT NULL DEFAULT 0,
    `nr_sentimento_medio`           DECIMAL(5, 4) NOT NULL DEFAULT 0,
    `qt_inconsistencias`            INT           NOT NULL DEFAULT 0,
    `nr_taxa_inconsistencia`        DECIMAL(5, 2) NOT NULL DEFAULT 0,
    `js_pontos_fortes`              JSON          NULL,
    `js_pontos_fracos`              JSON          NULL,
    `ds_resumo`                     VARCHAR(500)  NULL,
    `cd_versao_modelo`              VARCHAR(64)   NOT NULL,
    `dt_atualizacao`                DATETIME(3)   NOT NULL,
    PRIMARY KEY (`id_profissional_reputacao_pln`),
    CONSTRAINT `uk_profissional_reputacao_pln_profissional`
    UNIQUE (`fk_id_profissional`),
    CONSTRAINT `fk_Profissional_Reputacao_Pln_Profissional`
    FOREIGN KEY (`fk_id_profissional`)
    REFERENCES `database_elo`.`profissional` (`usuario_id`)
    ON DELETE CASCADE
    )
    ENGINE = InnoDB
    DEFAULT CHARACTER SET = utf8mb3;

CREATE INDEX `idx_profissional_reputacao_pln_atualizacao`
    ON `database_elo`.`profissional_reputacao_pln` (`dt_atualizacao` ASC) VISIBLE;

SET SQL_MODE = @OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS = @OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS = @OLD_UNIQUE_CHECKS;