-- ============================================
-- 电商系统后台数据库 analysis_db
-- 包含8张表 + 示例数据
-- ============================================

-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS analysis_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE analysis_db;

-- ============================================
-- 2. 创建表
-- ============================================

-- 表1：用户表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    real_name VARCHAR(50) COMMENT '真实姓名',
    gender ENUM('男','女','其他') DEFAULT '其他' COMMENT '性别',
    city VARCHAR(50) COMMENT '城市',
    province VARCHAR(50) COMMENT '省份',
    membership_level ENUM('普通','银卡','金卡','钻石') DEFAULT '普通' COMMENT '会员等级',
    account_balance DECIMAL(10,2) DEFAULT 0.00 COMMENT '账户余额',
    total_points INT DEFAULT 0 COMMENT '总积分',
    status ENUM('正常','冻结','注销') DEFAULT '正常' COMMENT '账户状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 表2：产品分类表
CREATE TABLE IF NOT EXISTS product_categories (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '分类ID',
    category_name VARCHAR(100) NOT NULL COMMENT '分类名称',
    parent_id INT NULL COMMENT '父分类ID，NULL表示顶级分类',
    sort_order INT DEFAULT 0 COMMENT '排序',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='产品分类表';

-- 表3：产品表
CREATE TABLE IF NOT EXISTS products (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '产品ID',
    category_id INT NOT NULL COMMENT '分类ID',
    product_name VARCHAR(200) NOT NULL COMMENT '产品名称',
    unit_price DECIMAL(10,2) NOT NULL COMMENT '销售单价',
    cost_price DECIMAL(10,2) DEFAULT 0.00 COMMENT '成本价',
    stock_quantity INT DEFAULT 0 COMMENT '库存数量',
    sales_volume INT DEFAULT 0 COMMENT '累计销量',
    rating DECIMAL(2,1) DEFAULT 5.0 COMMENT '平均评分',
    status ENUM('上架','下架','缺货') DEFAULT '上架' COMMENT '商品状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (category_id) REFERENCES product_categories(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='产品表';

-- 表4：订单表
CREATE TABLE IF NOT EXISTS orders (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单ID',
    order_number VARCHAR(50) NOT NULL UNIQUE COMMENT '订单编号',
    user_id INT NOT NULL COMMENT '用户ID',
    total_amount DECIMAL(10,2) DEFAULT 0.00 COMMENT '订单总金额（折扣前）',
    discount_amount DECIMAL(10,2) DEFAULT 0.00 COMMENT '折扣金额',
    actual_amount DECIMAL(10,2) DEFAULT 0.00 COMMENT '实际支付金额',
    order_status ENUM('待付款','已付款','待发货','已发货','已完成','已取消','已退款') DEFAULT '待付款' COMMENT '订单状态',
    order_date DATETIME COMMENT '下单时间',
    payment_date DATETIME COMMENT '付款时间',
    delivery_date DATETIME COMMENT '发货时间',
    completion_date DATETIME COMMENT '完成时间',
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- 表5：订单明细表
CREATE TABLE IF NOT EXISTS order_details (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '明细ID',
    order_id INT NOT NULL COMMENT '订单ID',
    product_id INT NOT NULL COMMENT '产品ID',
    quantity INT NOT NULL DEFAULT 1 COMMENT '购买数量',
    unit_price DECIMAL(10,2) NOT NULL COMMENT '购买时单价',
    subtotal DECIMAL(10,2) NOT NULL COMMENT '小计金额',
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单明细表';

-- 表6：商品评价表
CREATE TABLE IF NOT EXISTS reviews (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '评价ID',
    user_id INT NOT NULL COMMENT '用户ID',
    product_id INT NOT NULL COMMENT '产品ID',
    order_id INT NOT NULL COMMENT '订单ID',
    rating INT NOT NULL COMMENT '评分（1-5分）',
    content TEXT COMMENT '评价内容',
    is_recommend ENUM('是','否') DEFAULT '是' COMMENT '是否推荐',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '评价时间',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品评价表';

-- 表7：积分记录表
CREATE TABLE IF NOT EXISTS points_records (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    user_id INT NOT NULL COMMENT '用户ID',
    points INT NOT NULL COMMENT '积分变动值（正=获得，负=消费）',
    record_type ENUM('获得','消费','过期') DEFAULT '获得' COMMENT '变动类型',
    source VARCHAR(100) COMMENT '积分来源',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='积分记录表';

-- 表8：访问日志表
CREATE TABLE IF NOT EXISTS visit_logs (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
    user_id INT NULL COMMENT '访问用户ID，NULL表示匿名访问',
    page_url VARCHAR(500) NOT NULL COMMENT '访问页面URL',
    visit_time DATETIME NOT NULL COMMENT '访问时间',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    device_type ENUM('手机','电脑','平板') DEFAULT '电脑' COMMENT '设备类型',
    duration_seconds INT DEFAULT 0 COMMENT '页面停留时长（秒）',
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='访问日志表';

-- ============================================
-- 3. 插入示例数据
-- ============================================

-- 插入用户数据
INSERT INTO users (username, real_name, gender, city, province, membership_level, account_balance, total_points, status) VALUES
('zhangsan', '张三', '男', '北京', '北京', '金卡', 5000.00, 12000, '正常'),
('lisi', '李四', '女', '上海', '上海', '银卡', 2000.00, 5000, '正常'),
('wangwu', '王五', '男', '广州', '广东', '普通', 500.00, 800, '正常'),
('zhaoliu', '赵六', '女', '深圳', '广东', '钻石', 80000.00, 80000, '正常'),
('huangsan', '黄三', '男', '长沙', '湖南', '钻石', 50000.00, 50000, '正常'),
('zhouqi', '周七', '女', '杭州', '浙江', '金卡', 8000.00, 15000, '正常'),
('wuba', '吴八', '男', '成都', '四川', '银卡', 3000.00, 6000, '正常'),
('zhengjiu', '郑九', '女', '武汉', '湖北', '普通', 200.00, 300, '冻结'),
('sunshi', '孙十', '男', '南京', '江苏', '金卡', 6000.00, 18000, '正常'),
('qianyi', '钱一', '女', '西安', '陕西', '普通', 100.00, 100, '正常');

-- 插入产品分类数据
INSERT INTO product_categories (category_name, parent_id, sort_order) VALUES
('电子产品', NULL, 1),
('服装鞋帽', NULL, 2),
('食品饮料', NULL, 3),
('图书文具', NULL, 4),
('家居用品', NULL, 5),
('手机通讯', 1, 1),
('电脑办公', 1, 2),
('数码配件', 1, 3),
('男装', 2, 1),
('女装', 2, 2),
('休闲零食', 3, 1),
('饮料冲调', 3, 2),
('图书', 4, 1),
('文具用品', 4, 2);

-- 插入产品数据
INSERT INTO products (category_id, product_name, unit_price, cost_price, stock_quantity, sales_volume, rating, status) VALUES
(6, 'iPhone 15 Pro Max', 9999.00, 7500.00, 100, 500, 4.8, '上架'),
(6, '华为Mate 60 Pro', 6999.00, 5000.00, 200, 800, 4.9, '上架'),
(6, '小米14 Ultra', 5999.00, 4000.00, 150, 600, 4.7, '上架'),
(7, 'MacBook Pro 14寸', 14999.00, 11000.00, 50, 200, 4.9, '上架'),
(7, '联想拯救者Y9000P', 8999.00, 6500.00, 80, 300, 4.6, '上架'),
(8, 'AirPods Pro 2', 1899.00, 1200.00, 300, 1500, 4.8, '上架'),
(9, '男士纯棉T恤', 99.00, 30.00, 500, 2000, 4.5, '上架'),
(10, '女士连衣裙', 299.00, 80.00, 300, 1200, 4.7, '上架'),
(11, '三只松鼠坚果大礼包', 89.00, 40.00, 1000, 5000, 4.6, '上架'),
(12, '农夫山泉矿泉水550ml*24瓶', 39.90, 20.00, 2000, 10000, 4.9, '上架'),
(13, 'Python编程从入门到实践', 89.00, 45.00, 400, 800, 4.8, '上架'),
(14, '晨光中性笔10支装', 15.00, 5.00, 2000, 8000, 4.7, '上架'),
(5, '小米扫地机器人', 1999.00, 1200.00, 100, 400, 4.6, '缺货'),
(6, 'OPPO Find X7', 4999.00, 3500.00, 0, 350, 4.5, '缺货');

-- 插入订单数据
INSERT INTO orders (order_number, user_id, total_amount, discount_amount, actual_amount, order_status, order_date, payment_date, delivery_date, completion_date) VALUES
('ORD20240101001', 1, 9999.00, 200.00, 9799.00, '已完成', '2024-01-01 10:00:00', '2024-01-01 10:05:00', '2024-01-02 09:00:00', '2024-01-05 14:00:00'),
('ORD20240102001', 2, 299.00, 0.00, 299.00, '已完成', '2024-01-02 15:30:00', '2024-01-02 15:35:00', '2024-01-03 10:00:00', '2024-01-06 11:00:00'),
('ORD20240103001', 3, 128.90, 10.00, 118.90, '已完成', '2024-01-03 20:00:00', '2024-01-03 20:05:00', '2024-01-04 08:00:00', '2024-01-07 16:00:00'),
('ORD20240105001', 4, 14999.00, 500.00, 14499.00, '已完成', '2024-01-05 12:00:00', '2024-01-05 12:10:00', '2024-01-06 09:00:00', '2024-01-09 10:00:00'),
('ORD20240108001', 5, 6999.00, 0.00, 6999.00, '已完成', '2024-01-08 14:00:00', '2024-01-08 14:05:00', '2024-01-09 10:00:00', '2024-01-12 15:00:00'),
('ORD20240110001', 6, 1899.00, 100.00, 1799.00, '已完成', '2024-01-10 09:00:00', '2024-01-10 09:05:00', '2024-01-11 08:00:00', '2024-01-14 12:00:00'),
('ORD20240115001', 7, 198.00, 0.00, 198.00, '已发货', '2024-01-15 16:00:00', '2024-01-15 16:05:00', '2024-01-16 09:00:00', NULL),
('ORD20240118001', 8, 89.00, 0.00, 89.00, '待发货', '2024-01-18 11:00:00', '2024-01-18 11:05:00', NULL, NULL),
('ORD20240120001', 9, 5999.00, 200.00, 5799.00, '待付款', '2024-01-20 13:00:00', NULL, NULL, NULL),
('ORD20240122001', 10, 15.00, 0.00, 15.00, '已取消', '2024-01-22 10:00:00', NULL, NULL, NULL),
('ORD20240201001', 1, 1899.00, 0.00, 1899.00, '已完成', '2024-02-01 10:00:00', '2024-02-01 10:05:00', '2024-02-02 09:00:00', '2024-02-05 14:00:00'),
('ORD20240205001', 2, 99.00, 0.00, 99.00, '已完成', '2024-02-05 15:00:00', '2024-02-05 15:05:00', '2024-02-06 10:00:00', '2024-02-09 11:00:00'),
('ORD20240210001', 3, 39.90, 0.00, 39.90, '已完成', '2024-02-10 20:00:00', '2024-02-10 20:05:00', '2024-02-11 08:00:00', '2024-02-14 16:00:00'),
('ORD20240215001', 4, 8999.00, 300.00, 8699.00, '已完成', '2024-02-15 12:00:00', '2024-02-15 12:10:00', '2024-02-16 09:00:00', '2024-02-19 10:00:00'),
('ORD20240220001', 5, 5999.00, 0.00, 5999.00, '已退款', '2024-02-20 14:00:00', '2024-02-20 14:05:00', '2024-02-21 10:00:00', NULL);

-- 插入订单明细数据
INSERT INTO order_details (order_id, product_id, quantity, unit_price, subtotal) VALUES
(1, 1, 1, 9999.00, 9999.00),
(2, 8, 1, 299.00, 299.00),
(3, 11, 1, 89.00, 89.00),
(3, 12, 1, 39.90, 39.90),
(4, 4, 1, 14999.00, 14999.00),
(5, 2, 1, 6999.00, 6999.00),
(6, 6, 1, 1899.00, 1899.00),
(7, 7, 2, 99.00, 198.00),
(8, 11, 1, 89.00, 89.00),
(9, 3, 1, 5999.00, 5999.00),
(10, 14, 1, 15.00, 15.00),
(11, 6, 1, 1899.00, 1899.00),
(12, 7, 1, 99.00, 99.00),
(13, 12, 1, 39.90, 39.90),
(14, 5, 1, 8999.00, 8999.00),
(15, 3, 1, 5999.00, 5999.00);

-- 插入商品评价数据
INSERT INTO reviews (user_id, product_id, order_id, rating, content, is_recommend) VALUES
(1, 1, 1, 5, '手机非常好用，拍照清晰，续航给力，推荐购买！', '是'),
(2, 8, 2, 4, '裙子质量不错，尺码标准，就是颜色比图片深一点。', '是'),
(3, 11, 3, 5, '书的内容很详细，适合初学者，纸张质量也很好。', '是'),
(4, 4, 4, 5, 'MacBook性能强劲，屏幕显示效果一流，办公神器！', '是'),
(5, 2, 5, 5, '华为手机信号好，充电快，系统流畅，支持国产！', '是'),
(6, 6, 6, 4, '耳机音质不错，降噪效果好，就是价格有点贵。', '是'),
(1, 6, 11, 5, '第二次购买了，音质依然很棒，降噪效果好。', '是'),
(2, 7, 12, 3, 'T恤质量一般，洗了一次有点变形，不推荐。', '否'),
(4, 5, 14, 4, '笔记本性能不错，散热一般，游戏本都这样。', '是');

-- 插入积分记录数据
INSERT INTO points_records (user_id, points, record_type, source) VALUES
(1, 980, '获得', '购物'),
(1, 200, '获得', '签到'),
(1, -500, '消费', '兑换优惠券'),
(2, 30, '获得', '购物'),
(2, 50, '获得', '评价'),
(3, 12, '获得', '购物'),
(4, 1450, '获得', '购物'),
(4, 500, '获得', '生日礼包'),
(4, -1000, '消费', '兑换礼品'),
(5, 700, '获得', '购物'),
(5, 300, '获得', '邀请好友'),
(6, 180, '获得', '购物'),
(7, 20, '获得', '购物'),
(9, 580, '获得', '购物'),
(10, 10, '获得', '注册');

-- 插入访问日志数据
INSERT INTO visit_logs (user_id, page_url, visit_time, ip_address, device_type, duration_seconds) VALUES
(1, '/product/1', '2024-01-01 09:30:00', '192.168.1.100', '电脑', 120),
(1, '/product/2', '2024-01-01 09:35:00', '192.168.1.100', '电脑', 80),
(1, '/cart', '2024-01-01 09:40:00', '192.168.1.100', '电脑', 45),
(2, '/product/8', '2024-01-02 15:00:00', '192.168.1.101', '手机', 200),
(3, '/product/11', '2024-01-03 19:30:00', '192.168.1.102', '电脑', 150),
(4, '/product/4', '2024-01-05 11:30:00', '192.168.1.103', '电脑', 300),
(5, '/product/2', '2024-01-08 13:30:00', '192.168.1.104', '手机', 180),
(6, '/product/6', '2024-01-10 08:30:00', '192.168.1.105', '平板', 90),
(7, '/product/7', '2024-01-15 15:30:00', '192.168.1.106', '手机', 60),
(8, '/product/11', '2024-01-18 10:30:00', '192.168.1.107', '电脑', 45),
(NULL, '/index', '2024-01-20 12:00:00', '192.168.1.108', '手机', 30),
(9, '/product/3', '2024-01-20 12:30:00', '192.168.1.109', '电脑', 210),
(10, '/product/14', '2024-01-22 09:30:00', '192.168.1.110', '手机', 20),
(1, '/product/6', '2024-02-01 09:30:00', '192.168.1.100', '电脑', 100),
(2, '/product/7', '2024-02-05 14:30:00', '192.168.1.101', '手机', 70),
(3, '/product/12', '2024-02-10 19:30:00', '192.168.1.102', '电脑', 50),
(4, '/product/5', '2024-02-15 11:30:00', '192.168.1.103', '电脑', 250),
(5, '/product/3', '2024-02-20 13:30:00', '192.168.1.104', '手机', 160);

-- ============================================
-- 完成
-- ============================================
SELECT '数据库创建完成，共8张表，示例数据已插入' AS 提示;
