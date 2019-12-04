# MySQL script to upgrade Phamerator database schema from version 5 to 6.
# No loss in data.
ALTER TABLE `domain` CHANGE `id` `ID` int(10) unsigned NOT NULL AUTO_INCREMENT;
ALTER TABLE `domain` CHANGE `description` `Description` blob;
ALTER TABLE `gene_domain` CHANGE `id` `ID` int(10) unsigned NOT NULL AUTO_INCREMENT;
ALTER TABLE `gene_domain` CHANGE `expect` `Expect` double unsigned NOT NULL;
ALTER TABLE `phage` CHANGE `status` `Status` enum('unknown','draft','final') DEFAULT NULL;
ALTER TABLE `pham` CHANGE `name` `Name` int(10) unsigned DEFAULT NULL;
ALTER TABLE `pham_color` CHANGE `id` `ID` int(10) unsigned NOT NULL AUTO_INCREMENT;
ALTER TABLE `pham_color` CHANGE `name` `Name` int(10) unsigned NOT NULL;
ALTER TABLE `pham_color` CHANGE `color` `Color` char(7) NOT NULL;
ALTER TABLE `version` CHANGE `version` `Version` int(11) unsigned NOT NULL;
ALTER TABLE `gene` CHANGE `translation` `Translation` varchar(5000) DEFAULT NULL;
ALTER TABLE `gene` CHANGE `id` `ID` int(10) unsigned NOT NULL AUTO_INCREMENT;
ALTER TABLE `gene` CHANGE `cdd_status` `DomainStatus` tinyint(1) NOT NULL DEFAULT '0';
ALTER TABLE `version` CHANGE `schema_version` `SchemaVersion` int(11) unsigned NOT NULL;
ALTER TABLE `domain` CHANGE `hit_id` `HitID` varchar(25) NOT NULL;
ALTER TABLE `gene_domain` CHANGE `hit_id` `HitID` varchar(25) NOT NULL;
ALTER TABLE `gene_domain` CHANGE `query_start` `QueryStart` int(10) unsigned NOT NULL;
ALTER TABLE `gene_domain` CHANGE `query_end` `QueryEnd` int(10) unsigned NOT NULL;
UPDATE `version` SET `SchemaVersion` = 6;
