from pandas.io.common import file_path_to_url
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchDriverException, NoSuchElementException
import pandas as pd
import os
if __name__ == "__main__":
    driver = webdriver.edge()
    file_path="files/testcase.xlsx"
    sheet_name="Sheet1"
    try:
        df=pd.read_excel(file_path,sheet_name=sheet_name)
        print(df)
    except Exception as e:
        print(e)
        driver.quit()
        exit()
    if '测试结果' not in df.columns:
        df['测试结果']=''
    else:
        df['测试结果']=''
    for index, row in df.iterrows():
        username=row[""]
        password=[""]
        result=""
        login_url=
        driver.get()
        try:
            username_field=driver.find_element(By.ID, "txtPwd")
            username_field.clear()
            username_field.send_keys(password)

            login_button=driver.find_element(By.ID, "btnSunbmit")
            login_button.click()
        #获取Alert消息框
        except Exception as e:
            print(f"错误信息{e}")

