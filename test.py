from selenium import webdriver
from selenium.webdriver.common.by import By
import time
if __name__ == "__main__":
    driver = webdriver.Edge()
    driver.get("http://www.baidu.com")
    input_elem = driver.find_element(By.ID, "kw")
    input_elem.send_keys("湖南农业大学 双一流")
    time.sleep(5)