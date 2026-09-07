## Ch01 电商系统后台数据库(analysis_db)的设计与内容

### 课程目标：

1. 理解该数据库的设计目的（模拟电商系统）。
2. 掌握每个数据表的用途、主要字段及其含义。
3. 能够分析表与表之间的关系（外键、主键）。
4. 了解如何通过示例数据理解业务逻辑。

### 第一部分：数据库概览与核心业务

**1.1 数据库简介**

- **数据库名称：**analysis_db
- **字符集：** `utf8mb4` (支持emoji等特殊字符)
- **设计目的：** 模拟一个典型的电商平台数据存储系统，包含用户、商品、订单、评价、积分、访问日志等核心模块，为后续的业务分析和数据统计提供基础。

**1.2 核心业务模块**

- **用户管理：**存储用户注册信息、会员等级、账户状态等。
- **商品管理：** 管理商品分类、产品信息、库存与销售情况。
- **订单交易：** 记录完整的订单生命周期，从下单到完成。
- **用户互动：** 商品评价、会员积分系统。
- **用户行为：** 网站访问日志，用于分析用户行为。

### 第二部分：数据表详解

我们将按照从“主表”到“从表”的逻辑顺序，逐一讲解每个表。

#### 2.1 用户表 (users)

- **表名：** `users`
- **功能：** 存储所有注册用户的核心信息。这是整个系统的基石。
- **关键字段分析：**
  - id (INT, PRIMARY KEY): 用户的唯一标识，自动增长。
  - username (VARCHAR, NOT NULL): 用户登录名，不可为空。
  - real_name (VARCHAR): 真实姓名，可为空。
  - gender (ENUM): 性别，限定为 男/女/其他。
  - `city`, `province` (VARCHAR): 地理位置信息，可做地区分析。
  - membership_level (ENUM): 会员等级 (普通/银卡/金卡/钻石)，用于区分用户价值。
  - `account_balance` (DECIMAL): 账户余额，精确到小数点后两位。
  - `total_points` (INT): 总积分，与积分记录表关联。
  - status (ENUM): 账户状态 (正常/冻结/注销)，用于风控。
  - `created_at` / `updated_at` (TIMESTAMP): 记录创建和更新时间，自动维护。
- **示例数据解读：**
  - zhangsan (张三): 北京用户，金卡会员，余额5000，总积分12000。
  - huangsan (黄三): 长沙用户，钻石会员，余额50000，总积分50000，是高价值用户。

#### 2.2 产品分类表 (product_categories)

- **表名：** `product_categories`
- **功能：** 实现商品的层级分类（如：电子产品 -> 手机通讯）。
- **关键字段分析：**
  - `id` (INT, PRIMARY KEY): 分类ID。
  - category_name (VARCHAR): 分类名称。
  - `parent_id` (INT, SELF-REFERENCING): **核心字段**。指向父分类的ID，实现无限级分类。`NULL`表示顶级分类。
  - `sort_order` (INT): 排序字段，控制显示顺序。
- **表结构亮点：** 通过 `parent_id` 自引用，实现了树形结构，非常灵活。
- **示例数据解读：**
  - `电子产品` (ID:1) 是顶级分类。
  - 手机通讯 (ID:6) 的 parent_id 是1，表明它是电子产品的子分类。
  - `文具用品` (ID:16) 的 `parent_id` 是5，表明它是图书文具的子分类。

#### 2.3 产品表 (products)

- **表名：** `products`
- **功能：** 存储具体的商品信息。
- **关键字段分析：**
  - `id` (INT, PRIMARY KEY): 产品ID。
  - category_id (INT, FK -> product_categories.id): 外键，关联到产品分类表。
  - unit_price (DECIMAL): 销售单价。
  - `cost_price` (DECIMAL): 成本价，用于利润分析。
  - stock_quantity (INT): 库存数量。
  - `sales_volume` (INT): 累计销售数量。
  - `rating` (DECIMAL): 平均评分（如4.8）。
  - status (ENUM): 商品状态 (上架/下架/缺货)。
- **示例数据解读：**
  - iPhone 15 Pro Max (ID:1): 属于手机通讯分类，单价9999，成本7500，库存100，已售500，评分4.8。
  - `农夫山泉矿泉水` (ID:10): 属于`饮料冲调`分类，单价2元，销量巨大（50000），是典型的低价高销量商品。

#### 2.4 订单表 (orders)

- **表名：** `orders`
- **功能：** 记录每一笔订单的概要信息，是整个交易的核心。
- **关键字段分析：**
  - `id` (INT, PRIMARY KEY): 订单ID。
  - order_number (VARCHAR, UNIQUE): 订单编号，业务上的唯一标识。
  - user_id (INT, FK -> users.id): 外键，关联到用户表，表示谁下的单。
  - total_amount (DECIMAL): 订单总金额（折扣前）。
  - discount_amount (DECIMAL): 折扣金额。
  - actual_amount (DECIMAL): 实际支付金额。
  - order_status (ENUM): 订单状态 (待付款/已付款/待发货/已发货/已完成/已取消/已退款)。这是流程控制的关键字段。
  - order_date, payment_date, delivery_date, completion_date (DATETIME): 记录订单生命周期中的各个关键时间点。
- **示例数据解读：**
  - ORD20240101001 (用户ID:1): 状态为已完成，下单到完成共4天。
  - ORD20240801016 (用户ID:3): 状态为待发货，说明已付款但还未发货。
  - ORD20240808018 (用户ID:9): 状态为待付款，说明尚未付款。

#### 2.5 订单明细表 (order_details)

- **表名：** `order_details`
- **功能：** **多对多关系的中间表**。一个订单可以包含多个商品，一个商品可以出现在多个订单中。此表用于记录每个订单中具体包含了哪些商品及其数量、单价。
- **关键字段分析：**
  - `id` (INT, PRIMARY KEY): 明细ID。
  - order_id (INT, FK -> orders.id): 外键，属于哪个订单。
  - product_id (INT, FK -> products.id): 外键，购买了什么商品。
  - `quantity` (INT): 购买数量。
  - unit_price (DECIMAL): 购买时的单价（商品价格可能变动）。
  - subtotal (DECIMAL): 小计金额 (= quantity * unit_price)。
- **示例数据解读：**
  - 订单ID `15` 有4条明细，说明该订单购买了4种不同的商品，总共10+50+30+50=140件商品，这是一个批量采购订单。

#### 2.6 商品评价表 (reviews)

- **表名：** `reviews`
- **功能：** 存储用户对已购商品的评价。
- **关键字段分析：**
  - `id` (INT, PRIMARY KEY): 评价ID。
  - user_id, product_id, order_id (INT, FK): 关联到用户、商品和订单，确保评价来源于真实的购买。
  - `rating` (INT): 评分（1-5分）。
  - `content` (TEXT): 评价内容。
  - is_recommend (ENUM): 是否推荐。
- **示例数据解读：**
  - 用户`zhangsan` (ID:1) 对订单1中的iPhone 15 Pro Max给出了5分好评，并推荐。

#### 2.7 积分记录表 (points_records)

- **表名：** `points_records`
- **功能：** 记录用户积分的每一次变动（获得、消费、过期），是积分系统的核心流水表。
- **关键字段分析：**
  - `id` (INT, PRIMARY KEY): 记录ID。
  - `user_id` (INT, FK -> users.id): 用户ID。
  - points (INT): 积分变动值（正数表示获得，负数表示消费）。
  - record_type (ENUM): 变动类型 (获得/消费/过期)。
  - source (VARCHAR): 积分来源 (购物/签到/评价/活动 等)。
- **示例数据解读：**
  - 用户huangsan (ID:11) 有16000积分：通过购物获得3000，生日获得500，然后消费了1000用于兑换。

#### 2.8 访问日志表 (visit_logs)

- **表名：** `visit_logs`
- **功能：** 记录用户访问网站的行为，用于用户行为分析。
- **关键字段分析：**
  - `id` (INT, PRIMARY KEY): 日志ID。
  - user_id (INT, FK -> users.id): 访问用户，可为空（匿名访问）。
  - `page_url` (VARCHAR): 访问的页面URL。
  - visit_time (DATETIME): 访问时间。
  - `ip_address` (VARCHAR): 用户IP地址。
  - device_type (ENUM): 设备类型 (手机/电脑/平板)。
  - duration_seconds (INT): 页面停留时长。
- **示例数据解读：**
  - 用户zhangsan (ID:1) 在2024年1月1日上午，使用电脑先后浏览了/product/1、/product/2，然后进入了购物车，总共停留了245秒。

### 第三部分：表关系与数据完整性

- 一对一关系：没有显式的一对一关系，但users表的total_points字段与points_records表的记录是逻辑上的“一对多”汇总关系。
- 一对多关系：
  - `users` (1) -> `orders` (N): 一个用户可以有多个订单。
  - `users` (1) -> `reviews` (N): 一个用户可以写多个评价。
  - product_categories (1) -> products (N): 一个分类下有多个商品。
  - orders (1) -> order_details (N): 一个订单包含多个商品明细。
  - products (1) -> order_details (N): 一个商品可以出现在多个订单明细中。
- 多对多关系：orders 和 products 通过 order_details 表实现了多对多关系。
- 数据完整性：
  - **主键 (PRIMARY KEY):** 确保每行数据的唯一性。
  - **外键 (FOREIGN KEY):** 确保引用的有效性。例如，`orders.user_id` 的值必须在 `users.id` 中存在。这保证了数据的一致性。
  - **非空约束 (NOT NULL):** 关键字段（如`username`, `order_number`）不能为空。
  - **唯一约束 (UNIQUE):** `order_number` 字段不能重复。
  - **枚举约束 (ENUM):**限制字段只能取指定的值，如gender只能在男/女/其他中选择。

### 第四部分：视图与索引

- 索引 (Indexes):为了提高查询效率而创建。 
  - idx_user_id 等：加速按用户ID、订单日期、商品ID等字段的查询。
  - **作用：** 就像书的目录，让数据库能快速找到数据，而不必全表扫描。
- 视图 (Views): 虚拟表，基于SQL查询结果，方便复杂查询的复用。 
  - v_user_order_stats: 用户订单统计，可以快速查看每个用户的订单数、总消费额等。
  - v_product_sales_stats: 产品销售统计，可以查看每个商品的销量、收入、购买人数等。
  - v_daily_sales: 每日销售统计，分析每日的订单量、收入等趋势。
  - **作用：** 简化复杂查询，提供数据安全（只暴露必要字段）。