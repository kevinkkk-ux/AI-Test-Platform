# rag_generator.py
import os
import pandas as pd
from typing import List, Tuple
from langchain_core.output_parsers import StrOutputParser
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from data_generator import _parse_md_table
from database import get_db_manager
from config import CASE_GENERATE_TYPE, PATH_CONFIG

llm = ChatDeepSeek(model="deepseek-v4-flash", temperature=0.3)

def load_documents(file_paths: List[str]) -> List[dict]:
    """
    加载多种格式的文档文件
    :param file_paths: 文件路径列表
    :return: 文档内容列表，每项包含content和source
    """
    docs = []
    for path in file_paths:
        if not os.path.exists(path):
            continue
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == '.txt':
                loaded = TextLoader(path, encoding='utf-8').load()
            elif ext == '.pdf':
                loaded = PyPDFLoader(path).load()
            elif ext == '.docx':
                from langchain_community.document_loaders import Docx2txtLoader
                loaded = Docx2txtLoader(path).load()
            else:
                continue
            for doc in loaded:
                docs.append({"content": doc.page_content, "source": os.path.basename(path)})
        except Exception as e:
            print(f"加载失败 {path}: {e}")
    return docs
# rag_generator.py
def build_vector_store(chunks: List[dict], store_path: str = None, user_id: int = None):
    """
    构建FAISS向量存储
    :param chunks: 文档切片列表
    :param store_path: 存储路径
    :param user_id: 用户ID
    """
    store_path = store_path or PATH_CONFIG["faiss_vector_store"]
    os.makedirs(store_path, exist_ok=True)
    embeddings = HuggingFaceEmbeddings(
        model_name=PATH_CONFIG["embed_model_path"],
        model_kwargs={'device': 'cpu'}
    )
    texts = [c["content"] for c in chunks]
    metadatas = [{"source": c["source"]} for c in chunks]
    FAISS.from_texts(texts=texts, embedding=embeddings, metadatas=metadatas).save_local(store_path)

def load_vector_store(store_path: str = None) -> FAISS:
    """
    加载本地FAISS向量存储
    """
    store_path = store_path or PATH_CONFIG["faiss_vector_store"]
    embeddings = HuggingFaceEmbeddings(
        model_name=PATH_CONFIG["embed_model_path"],
        model_kwargs={'device': 'cpu'}
    )
    return FAISS.load_local(store_path, embeddings, allow_dangerous_deserialization=True)
# rag_generator.py
def retrieve_context(query: str, top_k: int = 5) -> str:
    """
    从向量库检索相关文档
    :param query: 查询文本
    :param top_k: 返回最相似的文档数量
    :return: 检索到的文档文本
    """
    try:
        vs = load_vector_store()
        docs = vs.similarity_search(query, k=top_k)
        return "\n\n".join([f"[{i+1}] {d.page_content}" for i, d in enumerate(docs)])
    except:
        return ""


# rag_generator.py
def _rag_generate(case_type: str, fields: dict, group_num: int, query: str, user_id: int = None) -> Tuple[
    pd.DataFrame, int]:
    """
    RAG增强生成测试用例核心函数
    :param case_type: 用例类型
    :param fields: 字段规则
    :param group_num: 生成数量
    :param query: 检索查询
    :param user_id: 用户ID
    """
    # 第一步：从向量库检索相关文档
    context = retrieve_context(query)

    field_rules = "\n".join([f"{k}：{v}" for k, v in fields.items()])
    table_headers = "用例ID," + ",".join(fields.keys()) + ",场景描述,用例类型,预期结果"

    # 第二步：构建增强提示词（将检索结果作为上下文注入）
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""你是专业测试工程师，参考需求文档生成{case_type}测试用例。
需求文档参考：
{context}  # ← 注入检索到的相关文档
字段规则：
{field_rules}
硬性要求：
1. 生成{group_num}组用例，所有输入字段互不重复；
2. 包含有效等价类、无效等价类、健壮边界值(合法边界)、健壮边界值(非法边界)四种类型；
3. 输出markdown表格，表头：{table_headers}；
4. 只输出表格，不要任何多余文字。"""),
        ("human", "生成测试用例")
    ])

    # 第三步：LLM生成
    res = (prompt | llm | StrOutputParser()).invoke({})
    csv_text = _parse_md_table(res)

    # 第四步：解析并保存结果
    cols = ["用例ID"] + list(fields.keys()) + ["场景描述", "用例类型", "预期结果"]
    rows = [r.split(",") for r in csv_text.strip().splitlines() if r.strip()]
    valid_rows = [r for r in rows if len(r) == len(cols)]
    if not valid_rows:
        raise ValueError("格式异常")

    df = pd.DataFrame(valid_rows, columns=cols)
    db = get_db_manager()
    main_id = db.insert_test_case_main(
        case_type=case_type, group_num=group_num,
        case_title=f"RAG{case_type}用例组{group_num}条",
        case_content=str(fields), generate_type=CASE_GENERATE_TYPE["RAG"]
    )
    db.batch_insert_case_detail(main_id, df.to_dict("records"))
    if user_id:
        db.add_operation_log(user_id, "RAG用例生成", f"生成{case_type}用例{len(df)}条", main_id)
    return df, main_id
# rag_generator.py
def rag_generate_login_case(account_rule, pwd_rule, group_num=20, doc_paths=None, query="登录功能", user_id=None):
    """
    RAG增强生成登录测试用例
    :param doc_paths: 上传的需求文档路径列表
    """
    if doc_paths:
        # 如果有上传文档，先加载并构建向量库
        docs = load_documents(doc_paths)
        chunks = [{"content": d["content"], "source": d["source"]} for d in docs]
        build_vector_store(chunks, user_id=user_id)
    return _rag_generate("登录", {"账号": account_rule, "密码": pwd_rule}, group_num, query, user_id)

def rag_generate_register_case(account_rule, pwd_rule, email_rule, phone_rule, group_num=20, doc_paths=None, query="注册功能", user_id=None):
    """
    RAG增强生成注册测试用例
    """
    if doc_paths:
        docs = load_documents(doc_paths)
        chunks = [{"content": d["content"], "source": d["source"]} for d in docs]
        build_vector_store(chunks, user_id=user_id)
    return _rag_generate("注册", {
        "账号": account_rule,
        "密码": pwd_rule,
        "确认密码": "与密码一致",
        "邮箱": email_rule,
        "手机号": phone_rule
    }, group_num, query, user_id)
if __name__ == "__main__":
    print("=" * 50)
    print("  RAG增强生成测试用例系统")
    print("=" * 50)
    print("  1. RAG生成登录测试用例")
    print("  2. RAG生成注册测试用例")
    print("=" * 50)

    choice = input("请输入选项（1/2）：").strip()

    # 询问是否上传需求文档
    use_doc = input("是否上传需求文档构建向量库？(y/n)：").strip().lower()
    doc_paths = None
    if use_doc == "y":
        doc_input = input("请输入需求文档路径（多个用逗号分隔）：").strip()
        doc_paths = [p.strip() for p in doc_input.split(",") if p.strip()]
        print(f"将加载 {len(doc_paths)} 个文档...")
    else:
        print("将使用已有的向量库（如果没有则检索为空）")

    if choice == "1":
        print("\n正在RAG生成登录测试用例...")
        try:
            df, main_id = rag_generate_login_case(
                account_rule="账号：字母数字，1-20位",
                pwd_rule="密码：6-16位字母数字",
                group_num=10,
                doc_paths=doc_paths,
                query="登录功能 账号密码验证"
            )
            output_path = PATH_CONFIG["output_excel"]
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_excel(output_path, index=False)
            print(f"✅ 登录用例生成完成，共{len(df)}条")
            print(f"📁 Excel已保存到：{output_path}")
            print("\n预览：")
            print(df)
        except Exception as e:
            print(f"❌ 生成失败：{e}")
            print("提示：如果是数据库报错，把_rag_generate里的数据库代码注释掉")

    elif choice == "2":
        print("\n正在RAG生成注册测试用例...")
        try:
            df, main_id = rag_generate_register_case(
                account_rule="账号：字母数字，1-20位",
                pwd_rule="密码：6-16位字母数字",
                email_rule="邮箱：标准邮箱格式",
                phone_rule="手机号：1开头的11位数字",
                group_num=10,
                doc_paths=doc_paths,
                query="注册功能 用户注册 账号邮箱手机号验证"
            )
            output_path = PATH_CONFIG["output_excel"]
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_excel(output_path, index=False)
            print(f"✅ 注册用例生成完成，共{len(df)}条")
            print(f"📁 Excel已保存到：{output_path}")
            print("\n预览：")
            print(df)
        except Exception as e:
            print(f"❌ 生成失败：{e}")

    else:
        print("❌ 输入错误，请输入1或2")
