import os
import re
import sys
from datetime import datetime
import requests
from tqdm import tqdm
from playwright.sync_api import sync_playwright

# 将项目根目录加入 sys.path，使得直接运行此脚本时也能导入 src 包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.config import CONFIG_DIR,get_account,DATA_DIR

STATE_FILE=CONFIG_DIR / "state.json"
accountinfo=get_account()
# 支持中文终端打印
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def fetch_mp4_url_and_download(page_url, coursename="Unnamed"):

    captured_mp4_url = None
    request_headers = {}

    print(f"🚀 正在启动后台浏览器，准备解析页面: {page_url}")

    with sync_playwright() as p:
        # 使用无头模式（不弹出浏览器界面）
        browser = p.chromium.launch(headless=True)
        
        if os.path.exists(STATE_FILE) :
            context = browser.new_context(storage_state=STATE_FILE)
        else:
            context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
          
        page = context.new_page()

        # 3. 监听网络请求
        def handle_request(request):
            nonlocal captured_mp4_url, request_headers
            url = request.url
            if ".mp4" in url.lower() and request.method == "GET":
                if not captured_mp4_url:
                    captured_mp4_url = url
                    request_headers = request.headers
                    print(f"🎯 成功拦截到视频 MP4 直链!")

        page.on("request", handle_request)
        
        # 4. 访问页面
        try:
            # 已经注入了 Cookie，这里应该能直接绕过登录进入播放页
            page.goto(page_url, wait_until="networkidle", timeout=30000)
            print("⏳ 页面加载完成，检查是否需要登录...")

            # 新增：检查页面中是否有 "Login" 文本，若有则执行登录流程
            try:
                if page.get_by_text("Login").count() > 0:
                    print("🔑 检测到登录页面，准备填写登录信息...")
                    irre2_locator = page.locator('xpath=//*[@id="root"]/div/div/div/div[4]')
                    irre2_locator.wait_for(state="visible", timeout=10000)
                    irre2_locator.click()

                    page.wait_for_load_state("networkidle", timeout=30000)
                    print("已经点击登录按钮")
                    if page.get_by_text("Login").count() > 0:
                        print("需要账号密码登录,从config中读取并输入……")

                        username_locator = page.locator('xpath=//*[@id="Username"]')
                        username_locator.wait_for(state="visible", timeout=10000)
                        username_locator.fill(accountinfo[0])

                        password_locator = page.locator('xpath=//*[@id="Password"]')
                        password_locator.wait_for(state="visible", timeout=10000)
                        password_locator.fill(accountinfo[1])

                        remember_login_locator = page.locator('xpath=//*[@id="RememberLogin"]')
                        remember_login_locator.click()

                        submit_locator = page.locator(
                            'xpath=/html/body/div/div/div/div/div[2]/div/form/div[3]/button'
                        )
                        submit_locator.click()

                        print("✅ 登录信息已提交，等待页面跳转...")
                else:
                    print("ℹ️ 未检测到登录页面，跳过登录步骤")
            except Exception as e:
                print(f"⚠️ 登录流程处理失败: {e}")
                
                print("继续尝试后续操作...")

            print("⏳ 准备点击指定按钮...")
            '''
            # 新增：点击指定的按钮
            xpath = "/html/body/div/div[1]/div/div/div[1]/div[2]/div[3]/div/div[2]/div[1]/div/p[1]"
                     
            try:
                # 等待按钮可见
                button_locator = page.locator(f"xpath={xpath}")
                button_locator.wait_for(state="visible", timeout=10000)
                print(f"✅ 找到目标按钮，准备点击: {xpath}")
                
                # 点击按钮
                button_locator.click()
                print("✅ 按钮点击成功")
                
                # 点击后等待一段时间，让后续内容加载
                page.wait_for_timeout(2000)
                
            except Exception as e:
                print(f"⚠️ 点击按钮失败: {e}")
                print("继续尝试捕获 MP4 链接...")
            '''
            print("⏳ 正在等待页面流媒体加载...")
            # 检查是否已经捕获到 MP4 链接
            if not captured_mp4_url:
                page.wait_for_timeout(4000)  # 等待 4 秒确保视频组件加载并发出 MP4 请求
            else:
                page.wait_for_timeout(1000)  # 如果已经捕获到，只等待 1 秒

        except Exception as e:
            print(f"❌ 页面加载超时或出错: {e}")
        #保存当前state
        context.storage_state(path=STATE_FILE)
        browser.close()

    # 5. 下载逻辑
    if captured_mp4_url:
        date_str = datetime.now().strftime("%Y%m%d_%H%M")
        output_dir = DATA_DIR / coursename
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{coursename}_{date_str}.mp4"
        file_path = output_dir / f"{coursename}_{date_str}" / filename

        print(f"\n🔗 视频直链: {captured_mp4_url}")
        download_file(captured_mp4_url, str(file_path), request_headers)
        return file_path
    else:
        print("❌ 未能在网络请求中捕获到 .mp4 链接！")

def download_file(url, save_path, headers):
    print(f"📥 开始下载视频，保存路径: {save_path}")
    if 'host' in headers: del headers['host']
    
    response = requests.get(url, headers=headers, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024 * 1024  # 1MB buffer
    
    with open(save_path, 'wb') as f, tqdm(
        total=total_size, unit='iB', unit_scale=True, desc="下载进度"
    ) as progress_bar:
        for data in response.iter_content(block_size):
            f.write(data)
            progress_bar.update(len(data))
            
    print("🎉 下载完成！")

#if __name__ == "__main__":
#    target_url = input("请输入 TRMS 课程播放页网址: ").strip()
            
#    fetch_mp4_url_and_download(target_url,"test")