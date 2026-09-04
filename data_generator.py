# data_generator.py
from langchain_core.output_parsers import StrOutputParser
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
import re
import csv
import io
import os
import pandas as pd
from config import DEEPSEEK_API_KEY, OUTPUT_PATHS, CASE_GENERATE_TYPE

# 初始化大模型
llm = ChatDeepSeek(
    model="deepseek-v4-flash",
    api_key=DEEPSEEK_API_KEY,
    temperature=0.3,
    timeout=60,  # 超时60秒，防止无限等
    max_retries=2  # 失败重试2次
)



def _parse_md_table(md_text: str) -> str:
    """解析大模型返回的Markdown表格，转换为CSV字符串"""
    if not md_text:
        return ""
    lines = md_text.strip().splitlines()
    data = []
    for line in lines:
        line = line.strip()
        if not line.startswith("|") or re.match(r"^\|?\s*-+\s*(\|\s*-+\s*)*\|?$", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and "用例ID" in cells[0]:
            continue
        data.append(cells)
    if not data:
        return ""
    output = io.StringIO()
    csv.writer(output, lineterminator="\n").writerows(data)
    return output.getvalue()


def generate_cases(case_type: str, fields: dict, group_num: int = 10, output_path: str = None):
    """
    统一用例生成函数（纯LLM + 数据库记录）
    :return: (DataFrame, main_id)
    """
    field_rules = "\n".join([f"{k}：{v}" for k, v in fields.items()])
    table_headers = "用例ID," + ",".join(fields.keys()) + ",场景描述,用例类型,预期结果"

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""你是专业软件测试工程师，使用等价类划分法+健壮边界值法生成{case_type}测试用例。
字段规则：
{field_rules}
硬性要求：
1. 生成{group_num}组用例，所有输入字段互不重复；
2. 包含有效等价类、无效等价类、健壮边界值(合法边界)、健壮边界值(非法边界)四种类型；
3. 输出markdown表格，表头：{table_headers}；
4. 只输出表格，不要任何多余文字；
5. 表格每个单元格内容绝对不要包含英文逗号，否则会解析失败。"""),
        ("human", "生成测试用例")
    ])

    # 调用大模型
    chain = prompt | llm | StrOutputParser()
    res = chain.invoke({"group_num": group_num})
    csv_text = _parse_md_table(res)

    # 解析并验证
    cols = ["用例ID"] + list(fields.keys()) + ["场景描述", "用例类型", "预期结果"]
    rows = [r.split(",") for r in csv_text.strip().splitlines() if r.strip()]
    valid_rows = [r for r in rows if len(r) == len(cols)]
    if not valid_rows:
        raise ValueError("LLM返回格式异常，请重试")

    # 保存Excel
    df = pd.DataFrame(valid_rows, columns=cols)
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_excel(output_path, index=False)

    # ========== 写入数据库 ==========
    main_id = None
    try:
        from database import get_db_manager
        db = get_db_manager()
        if db.conn is not None:
            main_id = db.insert_test_case_main(
                case_type=case_type, group_num=group_num,
                case_title=f"{case_type}用例组_{group_num}条",
                case_content=str(fields), generate_type=CASE_GENERATE_TYPE["AI"]
            )
            if main_id:
                db.batch_insert_case_detail(main_id, df.to_dict("records"))
        else:
            print("⚠️ 数据库未连接，跳过数据库记录")
    except Exception as e:
        print(f"⚠️ 数据库写入失败（不影响Excel生成）：{e}")
    # ================================

    return df, main_id


# ========== 模块1：登录 ==========
def generate_login_case(group_num=10):
    return generate_cases(
        case_type="登录",
        fields={"账号": "字母数字，1-20位，不支持特殊字符和中文", "密码": "6-16位字母数字，区分大小写"},
        group_num=group_num,
        output_path=OUTPUT_PATHS["login"]
    )


# ========== 模块2：注册 ==========
def generate_register_case(group_num=10):
    return generate_cases(
        case_type="注册",
        fields={
            "账号": "字母开头，4-20位字母数字下划线，不可重复",
            "密码": "8-20位，必须包含大写字母、小写字母和数字",
            "确认密码": "与密码一致",
            "邮箱": "标准邮箱格式，如xxx@xx.com",
            "手机号": "1开头的11位中国大陆手机号"
        },
        group_num=group_num,
        output_path=OUTPUT_PATHS["register"]
    )


# ========== 模块3：修改个人信息 ==========
def generate_modify_profile_case(group_num=10):
    return generate_cases(
        case_type="修改个人信息",
        fields={
            "昵称": "2-15位，支持中文、字母、数字，不支持特殊符号",
            "手机号": "1开头的11位中国大陆手机号，不可与其他账号重复",
            "邮箱": "标准邮箱格式，修改后需要验证"
        },
        group_num=group_num,
        output_path=OUTPUT_PATHS["modify_profile"]
    )


# ========== 控制台调试入口 ==========
if __name__ == "__main__":
    print("=" * 40)
    print("  测试用例生成系统（控制台版）")
    print("=" * 40)
    print("  1. 生成登录测试用例")
    print("  2. 生成注册测试用例")
    print("  3. 生成修改个人信息测试用例")
    print("=" * 40)

    choice = input("请输入选项（1/2/3）：").strip()
    num = input("生成用例数量（默认10）：").strip()
    group_num = int(num) if num.isdigit() else 10

    if choice == "1":
        df, _ = generate_login_case(group_num)
        print(f"✅ 登录用例生成完成，共{len(df)}条")
    elif choice == "2":
        df, _ = generate_register_case(group_num)
        print(f"✅ 注册用例生成完成，共{len(df)}条")
    elif choice == "3":
        df, _ = generate_modify_profile_case(group_num)
        print(f"✅ 修改个人信息用例生成完成，共{len(df)}条")
    else:
        print("❌ 输入错误")
        exit()

    print("\n生成结果预览：")
    print(df)
