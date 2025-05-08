from streamlit_cookies_controller import CookieController



class WebCookieController:
    cookie_controller = CookieController()

    @classmethod
    def get(cls, key: str):
        return cls.cookie_controller.get(key)

    @classmethod
    def set(cls, key: str, value: str, max_age: int = 3600):
        cls.cookie_controller.set(key, value, max_age=max_age)

    @classmethod
    def clear(cls):
        cookies = cls.cookie_controller.getAll()
        for cookie in list(cookies):
            print(f"Clearing cookie: {cookie}")
            cls.cookie_controller.remove(cookie)