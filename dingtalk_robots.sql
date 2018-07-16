
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for config
-- ----------------------------
DROP TABLE IF EXISTS `config`;
CREATE TABLE `config`  (
  `id` int(60) NOT NULL AUTO_INCREMENT,
  `processName` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `jenkinsUrl` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `jenkinsToken` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 20 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;

-- ----------------------------
-- Table structure for run_log
-- ----------------------------
DROP TABLE IF EXISTS `run_log`;
CREATE TABLE `run_log`  (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ProcessInstanceID` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `businessID` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `Name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `User` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `DingTalkResult` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `JenkinsResult` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`ID`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 110 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `phone` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;

SET FOREIGN_KEY_CHECKS = 1;
