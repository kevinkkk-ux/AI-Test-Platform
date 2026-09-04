from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import os

if __name__ == '__main__':
    driver=webdriver.Edge()
    file_path="files/testcases.xlsx"
    sheet_name="Sheet1"
    try:
        df=pd.read_excel(file_path,sheet_name=sheet_name)
        #print(df)
    except Exception as e:
        print(f"错误：无法读取Excel文件，请检查文件名及路径。错误信息：{e}")
        driver.quit()
        exit()

    if '测试结果' not in df.columns:
        df['测试结果']=''
    else:
        df['测试结果']=''

    for index,row in df.iterrows():
        username=row["admName"]
        password=row["admPwd"]
        result=""
        login_url="http://127.0.0.1:8848/login.html"
        driver.get(login_url)
        try:
            username_field=driver.find_element(By.ID,"txtName")
            username_field.clear()
            username_field.send_keys(username)

            password_field = driver.find_element(By.ID, "txtPwd")
            password_field.clear()
            password_field.send_keys(password)

            login_button=driver.find_element(By.ID,"btnSubmit")
            login_button.click()

            # ========== 下面是新增代码，获取alert消息 ==========
            wait = WebDriverWait(driver, 10)
            wait.until(EC.alert_is_present())
            alert = driver.switch_to.alert
            result = alert.text
            alert.accept()
            # ==================================================

        except Exception as e:
            print(f"错误信息：{e}")
            # ========== 新增：异常时把异常信息存入result ==========
            result = str(e)
            # ==================================================

        # ========== 新增：把result写入当前行的【测试结果】 ==========
        df.at[index, "测试结果"] = result
        # ==================================================

    # ========== 新增：循环结束后写回excel ==========
    df.to_excel(file_path, sheet_name=sheet_name, index=False)
    print("测试结果已写入Excel")
    # ==================================================

    # ========== 新增：关闭浏览器 ==========
    driver.quit()
    # ==================================================
