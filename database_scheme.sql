CREATE TABLE `tool` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `version` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `benchmarks_set` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `tool_run` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tool_id` int(11) DEFAULT NULL,
  `options` text,
  `memlimit` varchar(100) DEFAULT NULL,
  `cpulimit` varchar(100) DEFAULT NULL,
  `date` DATETIME DEFAULT NULL,
  `description` VARCHAR(255) DEFAULT NULL,
  `tags` TEXT DEFAULT NULL,
  `outputs` VARCHAR(512) DEFAULT NULL,
  `name` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`tool_id`) REFERENCES `tool` (`id`)
);

CREATE TABLE `run` (
  `status` varchar(255) DEFAULT NULL,
  `cputime` float DEFAULT NULL,
  `walltime` float DEFAULT NULL,
  `memusage` int(64) DEFAULT NULL,
  `classification` varchar(50) DEFAULT NULL,
  `exitcode` int(11) DEFAULT NULL,
  `exitsignal` int(11) DEFAULT NULL,
  `terminationreason` varchar(100) DEFAULT NULL,
  `tool_run_id` int(11) NOT NULL,
  `benchmarks_set_id` int(11) NOT NULL,
  `property` varchar(100) DEFAULT NULL,
  `options` text,
  `file` text,
  FOREIGN KEY (`tool_run_id`) REFERENCES `tool_run` (`id`),
  FOREIGN KEY (`benchmarks_set_id`) REFERENCES `benchmarks_set` (`id`)
);

