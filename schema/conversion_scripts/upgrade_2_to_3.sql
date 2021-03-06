# MySQL script to upgrade the database schema from version 2 to 3.
ALTER TABLE `version` ADD COLUMN `schema_version` int(11) unsigned NOT NULL AFTER `version`;
ALTER TABLE `phage` ADD COLUMN `Subcluster2` varchar(5) DEFAULT NULL AFTER `AnnotationAuthor`;
ALTER TABLE `phage` ADD COLUMN `Cluster2` varchar(5) DEFAULT NULL AFTER `AnnotationAuthor`;
ALTER TABLE `phage` ADD COLUMN `TempCluster2` varchar(5) DEFAULT NULL;
UPDATE `phage` SET `Subcluster2` = `Cluster` WHERE `Cluster` REGEXP '[0-9]$';
DROP PROCEDURE IF EXISTS split_subcluster;
DELIMITER //
CREATE PROCEDURE split_subcluster()
BEGIN
    DECLARE Counter INT DEFAULT 8;
    WHILE Counter > -1 DO
        UPDATE `phage` SET `TempCluster2` = SUBSTRING(`Subcluster2`, 1, LENGTH(`Subcluster2`)-Counter);
        UPDATE `phage` SET `Cluster2` = `TempCluster2` WHERE `TempCluster2` NOT REGEXP '[0-9]$' and `TempCluster2` != '';
        SET Counter = Counter - 1;
    END WHILE;
END //
DELIMITER;
CALL split_subcluster;
DROP PROCEDURE split_subcluster;
UPDATE `phage` SET `Cluster2` = `Cluster` WHERE `Cluster` NOT REGEXP '[0-9]$';
ALTER TABLE `phage` DROP COLUMN `TempCluster2`;
ALTER TABLE `phage` DROP COLUMN `Program`;
ALTER TABLE `gene` ADD COLUMN `LocusTag` varchar(50) DEFAULT NULL AFTER `cdd_status`;
UPDATE `version` SET `schema_version` = 3;

### DATA_LOSS_SUMMARY
# LOST_COLUMN:phage.Program
# INACCURATE_COLUMN:gene.LocusTag
