-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: localhost    Database: accredita_docs
-- ------------------------------------------------------
-- Server version	8.0.34

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accreditions`
--

DROP TABLE IF EXISTS `accreditions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accreditions` (
  `accredition_id` int NOT NULL AUTO_INCREMENT,
  `accredition` varchar(50) NOT NULL,
  PRIMARY KEY (`accredition_id`),
  UNIQUE KEY `accredition` (`accredition`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accreditions`
--

LOCK TABLES `accreditions` WRITE;
/*!40000 ALTER TABLE `accreditions` DISABLE KEYS */;
INSERT INTO `accreditions` VALUES (8,'NAAC');
/*!40000 ALTER TABLE `accreditions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `activities`
--

DROP TABLE IF EXISTS `activities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activities` (
  `file_id` int NOT NULL,
  `activity_type` enum('Uploaded','Reviewed','Changes','Renamed','Trashed','Deleted','Restored','Re-Uploaded') NOT NULL,
  `activity_timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `performed_by` int NOT NULL,
  `description` varchar(100) DEFAULT NULL,
  KEY `idx_performed_by` (`performed_by`),
  KEY `idx_activity_timestamp` (`activity_timestamp`),
  CONSTRAINT `activities_ibfk_1` FOREIGN KEY (`performed_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activities`
--

LOCK TABLES `activities` WRITE;
/*!40000 ALTER TABLE `activities` DISABLE KEYS */;
/*!40000 ALTER TABLE `activities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_email`
--

DROP TABLE IF EXISTS `admin_email`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_email` (
  `email` varchar(250) NOT NULL,
  PRIMARY KEY (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_email`
--

LOCK TABLES `admin_email` WRITE;
/*!40000 ALTER TABLE `admin_email` DISABLE KEYS */;
INSERT INTO `admin_email` VALUES ('manan.agarwal@bca.christuniversity.in');
/*!40000 ALTER TABLE `admin_email` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `category` (
  `category_id` int NOT NULL AUTO_INCREMENT,
  `definition` varchar(100) NOT NULL,
  `category` varchar(5) NOT NULL,
  PRIMARY KEY (`category_id`),
  UNIQUE KEY `category` (`category`),
  CONSTRAINT `category_chk_1` CHECK ((length(`category`) between 3 and 5))
) ENGINE=InnoDB AUTO_INCREMENT=166 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `category`
--

LOCK TABLES `category` WRITE;
/*!40000 ALTER TABLE `category` DISABLE KEYS */;
INSERT INTO `category` VALUES (87,'Syllabus Revisions','SYLR'),(88,'Course plan','COPL'),(89,'Feedback','FDBK'),(90,'Cross cutting issues','CCIS'),(91,'LRNG needs','LRNG'),(92,'Program outcome','PEOC'),(93,'Course Outcome','COUC'),(94,'New program','NEPR'),(95,'Value added courses','VADC'),(96,'Employability','EMPL'),(97,'Entrepreneurship','ENTR'),(98,'Skill development','SKDT'),(99,'Internship','INTN'),(100,'Consultancy Project','CONS'),(101,'Mou s','MOUS'),(102,'Extension activity','EXTA'),(103,'Department Fest UG','DFTU'),(104,'Department Fest PG','DFTP'),(105,'Fest outside CHRIST','FSTO'),(106,'Alumni meet','ALME'),(107,'Alumni Connect','ALCO'),(108,'FDP conducted inhouse','IFDP'),(109,'QIP conducted inhouse','IQIP'),(110,'FPD conducted by others','EFDP'),(111,'QIP conducted by others','EQIP'),(112,'Corporate Connect','COCO'),(113,'Conference Publication','CPUB'),(114,'Conference Presentation','CPRS'),(115,'Conference Attended','CATT'),(116,'Conference Keynote','CKEY'),(117,'Conference Session Chair','CSCH'),(118,'Conference Convenor','CCON'),(119,'Seminar Organized','SORG'),(120,'Seminar Attended','SATT'),(121,'Journal Publication (Indexed)','JPUI'),(122,'Journal Publication (Non Indexed)','JPUN'),(123,'Book Chapter','BCHP'),(124,'Book','BOOK'),(125,'Patent Filed','PFIL'),(126,'Patent Granted','PGRA'),(127,'Research Project (Internal Funding)','RPIF'),(128,'Research Project (External Funding)','RPEF'),(129,'Consultancy Project (Internal)','CONI'),(130,'Consultancy Project (External)','CONE'),(131,'MoU Industry','MOIY'),(132,'MoU Institution','MOIN'),(133,'Workshop Organized','WORG'),(134,'Orientation Attended','OATT'),(135,'Orientation Presentation','OPRE'),(136,'Fee concession','FEEC'),(137,'Scholorship','SCHL'),(138,'Capability','CAPA'),(139,'International program','INTL'),(140,'Placements','PLAM'),(141,'Cell Programs','PROG'),(142,'Other exams','OTEX'),(143,'Alumni support','ALSP'),(144,'fdp','FDP'),(145,'qip','QIP'),(146,'workshop','WOSP'),(147,'professional development program','PDPR'),(148,'seminar','SEMR'),(149,'symposium','SYMP'),(150,'conference','CONF'),(151,'finance incentives','FIIN'),(152,'Choice Based Credit System','CBCS'),(153,'Achievements','ACHS'),(154,'Fellowship','FELL'),(155,'Ph.d Awarded','PHDA'),(156,'Collaboration','COLL'),(157,'Memorandum of Understanding External,','MOUE'),(158,'Memorandum of Understanding Internal,','MOUI'),(159,'State level examination','STLE'),(160,'International level examination','ITLE'),(161,'National level examination','NTLE'),(162,'Gender Sensetisation','GENS'),(163,'Service Learning','SELE'),(164,'Prefessional Ethics','PRET'),(165,'Event fest organised by department','FEST');
/*!40000 ALTER TABLE `category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `criteria`
--

DROP TABLE IF EXISTS `criteria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `criteria` (
  `criteria_id` int NOT NULL AUTO_INCREMENT,
  `criteria_number` varchar(15) NOT NULL,
  `definition` varchar(500) DEFAULT NULL,
  `accredition_id` int NOT NULL,
  PRIMARY KEY (`criteria_id`),
  UNIQUE KEY `criteria_number` (`criteria_number`),
  KEY `accredition_id` (`accredition_id`),
  CONSTRAINT `criteria_ibfk_1` FOREIGN KEY (`accredition_id`) REFERENCES `accreditions` (`accredition_id`)
) ENGINE=InnoDB AUTO_INCREMENT=95 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `criteria`
--

LOCK TABLES `criteria` WRITE;
/*!40000 ALTER TABLE `criteria` DISABLE KEYS */;
INSERT INTO `criteria` VALUES (66,'1.1.2 ','Percentage of Programmes where syllabus revision was carried out during the last five years (20)',8),(67,'1.1.3','Average percentage of courses having focus on employability/ entrepreneurship/ skill development during the last five years (10)',8),(68,'1.2.1','Percentage of new courses introduced of the total number of courses across all programmes offered during the last five years (30)',8),(69,'1.2.2','Percentage of programs in which Choice Based Credit System (CBCS)/elective course system has been implemented (20)',8),(70,'1.3.2','Number of value-added courses for imparting transferable and life skills offered during last five years (10)',8),(71,'1.3.3','Average Percentage of students enrolled in the courses under 1.3.2 above (10)',8),(72,'1.3.4','Percentage of students undertaking field projects / research projects / internships ',8),(73,'1.4.1','Structured feedback for design and review of syllabus semester wise / year wise is received from 1) Students 2) Teachers 3) Employers 4) Alumni 5) Parents for design and review of syllabus',8),(74,'1.4.2','Feedback processes of the institution may be classified as follows: (10)',8),(75,'2.3.3','Ratio of students to mentor for academic and other related issues   ',8),(76,'2.4.2','Average percentage of full time teachers with Ph.D./D.M/M.Ch./D.N.B Superspeciality/D.Sc./D.Lit. during the last five years',8),(77,'2.4.4','Average percentage of full time teachers who received awards, recognition, fellowships at State, National, International level from Government/Govt. recognized bodies during the last five years (10)',8),(78,'3.1.3','Percentage of teachers receiving national/ international fellowship/financial support by various agencies for advanced studies/ research during the last five years (3)',8),(79,'3.2.1','Extramural funding for Research (Grants sponsored by the non-government sources such as industry, corporate houses, international bodies for research projects) endowments, Chairs in the University during the last five years (INR in Lakhs) (5)',8),(80,'3.2.2','Grants for research projects sponsored by the government agencies during the last five years (INR in Lakhs) (10)',8),(81,'3.2.3','Number of research projects per teacher funded by government and non-government agencies during the last five years (5)',8),(82,'3.3.3','Number of awards / recognitions received for research/innovations by the institution/teachers/research scholars/students during the last five years (10)',8),(83,'3.4.3',' Number of Patents published/awarded during the last five years (10)',8),(84,'3.4.4','Number of Ph.D\'s awarded per teacher during the last five years (10)',8),(85,'3.4.5','Number of research papers per teacher in the Journals notified on UGC website during the last five years (15)',8),(86,'3.4.6','Number of books and chapters in edited volumes published per teacher during the last five years (15)',8),(87,'3.5.2','Revenue generated from consultancy and corporate training during the last five years (INR in Lakhs) (15)',8),(88,'3.7.1','Number of collaborative activities with other institutions/ research establishment/industry for research and academic development of faculty and students per year (10)',8),(89,'3.7.2','Number of functional MoUs with institutions/ industries in India and abroad for internship, on-the-job training, project work, student / faculty exchange and collaborative research during the last five years',8),(90,'5.1.1','Average percentage of students benefited by scholarships, freeships, etc. provided by the institution, Government and non-government agencies (NGOs) during the last five years (other than the students',8),(91,'5.1.3','Following Capacity development and skills enhancement initiatives are taken by the institution (5)',8),(92,'5.2.1','Average percentage of students qualifying in state/ national/ international level examinations during the last five years',8),(93,'5.2.3','Percentage of recently graduated students who have progressed to higher education (previous graduating batch) (15)',8),(94,'6.3.4','Average percentage of teachers undergoing online/ face-to-face Faculty Development Programmes (FDP)during the last five years (Professional Development Programmes, Orientation / Induction',8);
/*!40000 ALTER TABLE `criteria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `criteria_category`
--

DROP TABLE IF EXISTS `criteria_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `criteria_category` (
  `criteria_id` int NOT NULL,
  `category_id` int NOT NULL,
  PRIMARY KEY (`criteria_id`,`category_id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `criteria_category_ibfk_1` FOREIGN KEY (`criteria_id`) REFERENCES `criteria` (`criteria_id`),
  CONSTRAINT `criteria_category_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `category` (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `criteria_category`
--

LOCK TABLES `criteria_category` WRITE;
/*!40000 ALTER TABLE `criteria_category` DISABLE KEYS */;
INSERT INTO `criteria_category` VALUES (66,87),(73,89),(74,89),(68,94),(70,95),(71,95),(67,96),(67,97),(67,98),(72,99),(72,102),(85,121),(85,122),(86,123),(86,124),(83,125),(83,126),(80,127),(81,127),(79,128),(80,128),(81,128),(87,129),(87,130),(90,136),(90,137),(91,138),(91,139),(93,141),(94,144),(94,145),(90,151),(69,152),(77,153),(82,153),(78,154),(84,155),(88,156),(89,157),(89,158),(92,159),(92,160),(92,161);
/*!40000 ALTER TABLE `criteria_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `department`
--

DROP TABLE IF EXISTS `department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `department` (
  `dept_id` int NOT NULL AUTO_INCREMENT,
  `dept_name` varchar(50) NOT NULL,
  `owner` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`dept_id`),
  UNIQUE KEY `dept_name` (`dept_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `department`
--

LOCK TABLES `department` WRITE;
/*!40000 ALTER TABLE `department` DISABLE KEYS */;
INSERT INTO `department` VALUES (1,'Computer Science','manan.agarwal@bca.christuniversity.in');
/*!40000 ALTER TABLE `department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `file_category`
--

DROP TABLE IF EXISTS `file_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `file_category` (
  `file_id` int NOT NULL,
  `category_id` int NOT NULL,
  PRIMARY KEY (`file_id`,`category_id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `file_category_ibfk_1` FOREIGN KEY (`file_id`) REFERENCES `files` (`file_id`),
  CONSTRAINT `file_category_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `category` (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `file_category`
--

LOCK TABLES `file_category` WRITE;
/*!40000 ALTER TABLE `file_category` DISABLE KEYS */;
/*!40000 ALTER TABLE `file_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `files`
--

DROP TABLE IF EXISTS `files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `files` (
  `file_id` int NOT NULL AUTO_INCREMENT,
  `unique_id` varchar(100) NOT NULL,
  `file_name` varchar(100) NOT NULL,
  `period_date` date NOT NULL,
  `size` bigint DEFAULT NULL,
  `dept_id` int NOT NULL,
  `owner_id` int NOT NULL,
  `mimeType_id` int DEFAULT NULL,
  `description` varchar(100) DEFAULT NULL,
  `last_modified` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `reviewed` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`file_id`),
  UNIQUE KEY `unique_id` (`unique_id`),
  KEY `mimeType_id` (`mimeType_id`),
  KEY `idx_dept_files` (`dept_id`),
  KEY `idx_owner_id` (`owner_id`),
  CONSTRAINT `files_ibfk_1` FOREIGN KEY (`dept_id`) REFERENCES `department` (`dept_id`),
  CONSTRAINT `files_ibfk_2` FOREIGN KEY (`owner_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `files_ibfk_3` FOREIGN KEY (`mimeType_id`) REFERENCES `mimetype` (`mimeType_id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `files`
--

LOCK TABLES `files` WRITE;
/*!40000 ALTER TABLE `files` DISABLE KEYS */;
/*!40000 ALTER TABLE `files` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mimetype`
--

DROP TABLE IF EXISTS `mimetype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mimetype` (
  `mimeType_id` int NOT NULL AUTO_INCREMENT,
  `mimeType_name` varchar(100) DEFAULT NULL,
  `link` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`mimeType_id`),
  UNIQUE KEY `mimType_name` (`mimeType_name`),
  UNIQUE KEY `link` (`link`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mimetype`
--

LOCK TABLES `mimetype` WRITE;
/*!40000 ALTER TABLE `mimetype` DISABLE KEYS */;
INSERT INTO `mimetype` VALUES (1,'others','/static?file_name=file-regular-24.png'),(2,'image/jpeg','https://drive-thirdparty.googleusercontent.com/16/type/image/jpeg'),(3,'image/png','https://drive-thirdparty.googleusercontent.com/16/type/image/png'),(4,'application/vnd.ms-excel','https://drive-thirdparty.googleusercontent.com/16/type/application/vnd.ms-excel'),(5,'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','https://drive-thirdparty.googleusercontent.com/16/type/application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),(6,'application/vnd.google-apps.document','https://drive-thirdparty.googleusercontent.com/16/type/application/vnd.google-apps.document'),(7,'application/vnd.google-apps.spreadsheet','https://drive-thirdparty.googleusercontent.com/16/type/application/vnd.google-apps.spreadsheet'),(8,'application/pdf','https://drive-thirdparty.googleusercontent.com/16/type/application/pdf');
/*!40000 ALTER TABLE `mimetype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `privilage` enum('admin','editor','viewer','waitlist','denied') DEFAULT NULL,
  `dept_id` int DEFAULT NULL,
  `otp` int DEFAULT NULL,
  `unique_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `unique_id` (`unique_id`),
  KEY `idx_dept_owners` (`dept_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`dept_id`) REFERENCES `department` (`dept_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (5,'mananagarwal1784@gmail.com','hellotime1234','Manan Agarwal','admin',1,NULL,'4511adfe-eb93-404c-ab65-9950dcf53ab5'),(6,'manan.agarwal@bca.christuniversity.in','hellotime1234','MANAN AGARWAL','admin',1,NULL,'f074a39e-82fc-4cb7-ac34-a76f349ad9ff'),(8,'hello@gmail.com','hello1234','Manan Agarwal',NULL,NULL,417554,'f3a94262-aa1c-48ee-b991-110e841e5758'),(9,'agamjot.dua@bca.christuniversity.in','hello1234','Agamjot Dua',NULL,NULL,NULL,'45d2c400-b09d-483c-95d2-d28ca8b1b337');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-10-21  2:31:38
