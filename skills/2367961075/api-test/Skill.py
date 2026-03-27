import requests
import json

class Skill:
    def __init__(self):
        self.name = "API 数据获取"
        self.description = "调用外部 API 获取数据，支持 GET/POST/JSON"
        self.version = "1.0.0"
        self.author = "ClawHub"
        self.type = "tool"

    def run(self, params):
        try:
            url = params.get("url")
            if not url:
                return self.fail("缺少 url 参数")

            method = params.get("method", "GET").upper()
            headers = params.get("headers", {})
            url_params = params.get("params", {})
            data = params.get("data", {})
            timeout = params.get("timeout", 10)

            default_headers = {
                "User-Agent": "ClawHub-Skill/1.0",
                "Content-Type": "application/json"
            }
            headers = {**default_headers, **headers}

            if method == "GET":
                resp = requests.get(url, headers=headers, params=url_params, timeout=timeout)
            elif method == "POST":
                resp = requests.post(url, headers=headers, params=url_params, json=data, timeout=timeout)
            else:
                return self.fail(f"不支持的方法 {method}")

            resp.raise_for_status()

            try:
                result = resp.json()
            except:
                result = resp.text[:1000]

            return self.success({
                "status_code": resp.status_code,
                "url": url,
                "method": method,
                "data": result
            })

        except requests.exceptions.Timeout:
            return self.fail("请求超时")
        except requests.exceptions.ConnectionError:
            return self.fail("连接失败")
        except requests.HTTPError as e:
            return self.fail(f"HTTP 错误: {str(e)}")
        except Exception as e:
            return self.fail(f"异常: {str(e)}")

    def success(self, data):
        return {"status": "success", "data": data, "error": ""}

    def fail(self, error):
        return {"status": "fail", "data": None, "error": error}