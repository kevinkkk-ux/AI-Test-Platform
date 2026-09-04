/*
 Navicat Premium Data Transfer

 Source Server         : softtest_db
 Source Server Type    : MySQL
 Source Server Version : 80403 (8.4.3)
 Source Host           : localhost:3306
 Source Schema         : softtest_db

 Target Server Type    : MySQL
 Target Server Version : 80403 (8.4.3)
 File Encoding         : 65001

 Date: 19/08/2026 14:44:57
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- 1. 系统用户表
-- ----------------------------
DROP TABLE IF EXISTS `sys_user`;
CREATE TABLE `sys_user` (
  `user_id` int NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '用户名',
  `password` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '密码',
  `nickname` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT '用户昵称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `is_deleted` tinyint DEFAULT 0 COMMENT '逻辑删除：0 未删除，1 已删除',
  PRIMARY KEY (`user_id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin COMMENT = '系统用户';

-- ----------------------------
-- 2. 文件表
-- ----------------------------
DROP TABLE IF EXISTS `file`;
CREATE TABLE `file` (
  `file_id` bigint NOT NULL AUTO_INCREMENT COMMENT '文件ID',
  `file_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '文件原始名称',
  `file_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '文件存储路径',
  `file_type` tinyint NOT NULL COMMENT '文件业务类型（1: 脚本, 2: 接口文档, 3: 需求文档）',
  `file_size` bigint DEFAULT NULL COMMENT '文件大小 (字节)',
  `file_create_time` datetime DEFAULT NULL COMMENT '上传时间',
  `file_is_deleted` tinyint DEFAULT 0 COMMENT '逻辑删除：0 未删除，1 已删除',
  PRIMARY KEY (`file_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin COMMENT = '文件';

-- ----------------------------
-- 3. 自动化脚本表
-- ----------------------------
DROP TABLE IF EXISTS `auto_script`;
CREATE TABLE `auto_script` (
  `script_id` bigint NOT NULL AUTO_INCREMENT COMMENT '脚本ID',
  `script_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '脚本名称',
  `script_content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '脚本源码内容',
  `script_create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `script_is_deleted` tinyint DEFAULT 0 COMMENT '逻辑删除：0 未删除，1 已删除',
  PRIMARY KEY (`script_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin COMMENT = '自动化脚本';

-- ----------------------------
-- 4. 自动化执行记录表
-- ----------------------------
DROP TABLE IF EXISTS `auto_execute`;
CREATE TABLE `auto_execute` (
  `exec_id` bigint NOT NULL AUTO_INCREMENT COMMENT '执行记录ID',
  `task_name` varchar(200) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '任务名称',
  `task_type` varchar(50) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '任务类型 (login_auto, register_auto, custom_auto, api_auto)',
  `exec_status` tinyint NOT NULL COMMENT '执行状态：0 待执行，1 运行中，2 成功，3 失败',
  `total_cases` int DEFAULT 0 COMMENT '总用例数',
  `pass_cases` int DEFAULT 0 COMMENT '通过用例数',
  `fail_cases` int DEFAULT 0 COMMENT '失败用例数',
  `exec_log` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT '运行输出日志',
  `exec_result` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT '执行返回结果',
  `exec_start_time` datetime DEFAULT NULL COMMENT '开始时间',
  `exec_end_time` datetime DEFAULT NULL COMMENT '结束时间',
  PRIMARY KEY (`exec_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin COMMENT = '自动化执行记录';

-- ----------------------------
-- 5. 测试用例表
-- ----------------------------
DROP TABLE IF EXISTS `test_case`;
CREATE TABLE `test_case` (
  `case_ID` bigint NOT NULL AUTO_INCREMENT COMMENT '用例ID',
  `case_title` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL COMMENT '用例标题',
  `case_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '测试用例详细内容',
  `case_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT '' COMMENT '用例类型 (login, register, 接口测试等)',
  `case_generate_type` tinyint NOT NULL COMMENT '用例来源：0 手动，1 AI生成，2 RAG生成，4 接口解析',
  `case_create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `case_is_deleted` tinyint DEFAULT 0 COMMENT '逻辑删除：0 未删除，1 已删除',
  `user_id` int NOT NULL COMMENT '用户ID',
  PRIMARY KEY (`case_ID`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin COMMENT = '测试用例';

-- ----------------------------
-- 6. 数据分析任务表
-- ----------------------------
DROP TABLE IF EXISTS `analysis_task`;
CREATE TABLE `analysis_task` (
  `task_id` bigint NOT NULL AUTO_INCREMENT COMMENT '任务ID',
  `user_id` bigint DEFAULT NULL COMMENT '发起任务的用户ID',
  `task_natural_query` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '用户输入的自然语言查询',
  `task_sql_text` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'AI生成的SQL查询',
  `task_status` tinyint NOT NULL COMMENT '任务状态：0 待执行，1 执行中，2 成功，3 失败',
  `task_result` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT '查询返回的分析结果',
  `task_create_time` datetime DEFAULT NULL COMMENT '任务创建时间',
  PRIMARY KEY (`task_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin COMMENT = '数据分析任务';

-- ----------------------------
-- 7. 操作日志表
-- ----------------------------
DROP TABLE IF EXISTS `operate_log`;
CREATE TABLE `operate_log` (
  `log_id` bigint NOT NULL AUTO_INCREMENT COMMENT '日志ID',
  `user_id` bigint DEFAULT NULL COMMENT '操作用户ID',
  `log_operate_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '操作类型',
  `log_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT '操作详细描述',
  `log_related_taskid` bigint DEFAULT NULL COMMENT '关联业务任务编号',
  `log_operate_time` datetime DEFAULT NULL COMMENT '操作时间',
  PRIMARY KEY (`log_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin COMMENT = '操作日志';

SET FOREIGN_KEY_CHECKS = 1;

-- ----------------------------
-- Table structure for test_case_detail
-- ----------------------------
DROP TABLE IF EXISTS `test_case_detail`;
CREATE TABLE `test_case_detail`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `case_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用例编号TC001',
  `case_main_id` int NOT NULL DEFAULT 0 COMMENT '兼容旧代码',
  `scene_desc` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '' COMMENT '场景描述',
  `pre_condition` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '' COMMENT '前置条件',
  `test_step` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '测试步骤',
  `expect_result` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '预期结果',
  `account` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '' COMMENT '账号',
  `password` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '' COMMENT '密码',
  `confirm_pwd` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '' COMMENT '确认密码',
  `email` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '' COMMENT '邮箱',
  `phone` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '' COMMENT '手机号',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `case_category` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用例类型',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_case_id`(`case_id` ASC) USING BTREE,
  INDEX `idx_case_main_id`(`case_main_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 659 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '测试用例明细表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for test_execute_result
-- ----------------------------
DROP TABLE IF EXISTS `test_execute_result`;
CREATE TABLE `test_execute_result`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `case_main_id` int NOT NULL COMMENT '测试用例主表ID',
  `detail_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用例编号',
  `execute_url` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '被测页面地址',
  `actual_result` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '实际执行结果',
  `execute_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '成功/失败',
  `execute_log` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '执行完整日志',
  `create_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '执行时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 299 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '自动化测试执行结果表' ROW_FORMAT = Dynamic;
