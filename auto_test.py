# auto_test.py
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoAlertPresentException
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from config import CASE_PATH


def _clean_val(v):
    """清理取值，处理None和NaN"""
    if v is None:
        return ""
    try:
        return "" if pd.isna(v) else str(v).strip()
    except:
        return str(v).strip() if v else ""


def _find_element(driver, selector):
    """
    智能元素查找，支持id和name两种定位方式
    """
    s = str(selector).strip()
    if not s:
        raise NoSuchElementException("空选择器")
    if s.startswith("name="):
        return driver.find_element(By.NAME, s[5:])
    try:
        return driver.find_element(By.ID, s)
    except:
        return driver.find_element(By.NAME, s)


def _get_alert_text(driver):
    """尝试获取alert弹窗的文字，没有则返回空"""
    try:
        alert = driver.switch_to.alert
        text = alert.text
        alert.accept()  # 点击确定关闭弹窗
        return text
    except NoAlertPresentException:
        return ""
    except:
        return ""


def execute_cases(
    case_type: str,
    url: str,
    field_map: dict,
    submit_id: str,
    success_keyword: str,
    case_file: str = None,
    headless: bool = True
):
    """
    统一测试执行引擎
    :param case_type: 测试类型（登录/注册/自定义）
    :param url: 目标页面URL
    :param field_map: 字段名到元素ID的映射字典
    :param submit_id: 提交按钮的元素ID
    :param success_keyword: 成功关键字
    :param case_file: 测试用例Excel文件路径
    :param headless: 是否无头模式
    :return: (结果摘要, 详细日志)
    """
    case_file = case_file or CASE_PATH
    if not os.path.exists(case_file):
        return f"错误：未找到用例文件 {case_file}", ""

    df = pd.read_excel(case_file, dtype=str)
    total = len(df)
    if total == 0:
        return "错误：测试用例文件为空", ""

    logs = []
    logs.append(f"===== {case_type}自动化测试开始 =====")
    logs.append(f"目标URL: {url}")
    logs.append(f"用例数量: {total}")
    logs.append(f"字段映射: {field_map}")
    logs.append("-" * 50)

    # 启动浏览器
    try:
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        # 禁用alert弹窗在无头模式下的问题
        options.add_argument("--disable-popup-blocking")
        service = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
        driver.implicitly_wait(5)
    except Exception as e:
        return f"浏览器启动失败: {e}", "\n".join(logs)

    results = []
    passed = 0
    failed = 0

    for idx, row in df.iterrows():
        case_id = _clean_val(row.get("用例ID", f"用例{idx+1}"))
        expected = _clean_val(row.get("预期结果", ""))
        logs.append(f"\n执行用例: {case_id}")

        try:
            driver.get(url)
            time.sleep(1)

            # 填充表单字段
            for field_name, elem_id in field_map.items():
                val = _clean_val(row.get(field_name, ""))
                try:
                    elem = _find_element(driver, elem_id)
                    elem.clear()
                    if val:
                        elem.send_keys(val)
                    logs.append(f"  填充 [{field_name}] = {val}")
                except Exception as e:
                    logs.append(f"  填充 [{field_name}] 失败: {e}")

            # 点击提交按钮
            try:
                submit_btn = _find_element(driver, submit_id)
                submit_btn.click()
                logs.append(f"  点击提交按钮")
            except Exception as e:
                logs.append(f"  点击提交按钮失败: {e}")

            # 等待页面响应
            time.sleep(1)

            # ===== 关键改动：先尝试获取alert弹窗，再看页面文字 =====
            alert_text = _get_alert_text(driver)
            page_text = driver.find_element(By.TAG_NAME, "body").text

            if alert_text:
                result_text = alert_text
                logs.append(f"  Alert弹窗: {alert_text}")
            else:
                result_text = page_text
                logs.append(f"  页面文字(前50字): {page_text[:50]}")

            # 判断结果
            expect_success = ("成功" in expected) or ("通过" in expected)
            actual_success = success_keyword in result_text

            if expect_success and actual_success:
                result = "通过"
                passed += 1
            elif not expect_success and not actual_success:
                result = "通过"
                passed += 1
            else:
                if expect_success:
                    result = f"失败(预期成功但实际失败)"
                else:
                    result = f"失败(预期失败但实际成功)"
                failed += 1

            logs.append(f"  结果: {result}")

        except Exception as e:
            result = f"失败({str(e)[:50]})"
            failed += 1
            logs.append(f"  异常: {e}")

        results.append(result)

    driver.quit()

    # 统计
    pass_rate = round(passed / total * 100, 2) if total > 0 else 0
    summary = f"执行完成！总{total}条，通过{passed}条，失败{failed}条，通过率{pass_rate}%"

    logs.append("\n" + "=" * 50)
    logs.append(summary)
    logs.append("=" * 50)

    # 写回Excel
    try:
        df["实际结果"] = results
        df.to_excel(case_file, index=False)
        logs.append(f"结果已写回: {case_file}")
    except Exception as e:
        logs.append(f"写回Excel失败: {e}")

    return summary, "\n".join(logs)


def execute_login_cases(url=None, username_selector="txtName",
                        password_selector="txtPwd", submit_selector="btnSubmit",
                        case_file=None, headless=True):
    """执行登录测试用例（默认选择器匹配你的login.html）"""
    return execute_cases(
        "登录",
        url or "about:blank",
        {"账号": username_selector, "密码": password_selector},
        submit_selector,
        "登录成功",
        case_file,
        headless
    )


def execute_register_cases(url=None, case_file=None, headless=True):
    """执行注册测试用例"""
    return execute_cases(
        "注册",
        url or "about:blank",
        {
            "账号": "username",
            "密码": "password",
            "确认密码": "confirmPassword",
            "邮箱": "email",
            "手机号": "phone"
        },
        "registerBtn",
        "注册成功",
        case_file,
        headless
    )


# 控制台测试
if __name__ == "__main__":
    local_html = r"file:///C:/Users/hp/PycharmProjects/PythonProject6/login.html"
    summary, logs = execute_login_cases(
        url=local_html,
        case_file="files/login_testcases.xlsx",
        headless=False  # 显示浏览器窗口，方便看效果
    )
    print(summary)
    print("-" * 50)
    print(logs)
