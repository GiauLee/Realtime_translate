# core/translator_engine.py

import argostranslate.package
import argostranslate.translate
from deep_translator import GoogleTranslator

class MyTranslator:
    # Các engine có sẵn
    ENGINE_ARGOS = "argos"
    ENGINE_GOOGLE = "google"

    def __init__(self, engine=None):
        self.current_engine = engine or self.ENGINE_ARGOS
        
        # --- Khởi tạo Argos Translate (offline) ---
        self._init_argos()
        
        # --- Khởi tạo Google Translate (online) ---
        self.google_translator = GoogleTranslator(source='en', target='vi')

    def _init_argos(self):
        """Tải và cài gói ngôn ngữ EN→VI cho Argos nếu chưa có"""
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        
        # Tìm package en→vi
        package_to_install = next(
            (pkg for pkg in available_packages 
             if pkg.from_code == "en" and pkg.to_code == "vi"),
            None
        )
        
        if package_to_install:
            # Chỉ cài nếu chưa có
            installed_languages = argostranslate.translate.get_installed_languages()
            en_lang = next((l for l in installed_languages if l.code == "en"), None)
            vi_lang = next((l for l in installed_languages if l.code == "vi"), None)
            
            if not en_lang or not vi_lang:
                argostranslate.package.install_from_path(
                    package_to_install.download()
                )
        
        # Lấy reference đến installed languages
        installed_languages = argostranslate.translate.get_installed_languages()
        self.en_lang = next(l for l in installed_languages if l.code == "en")
        self.vi_lang = next(l for l in installed_languages if l.code == "vi")
        self.argos_translation = self.en_lang.get_translation(self.vi_lang)

    def set_engine(self, engine_name):
        """Chuyển đổi engine dịch"""
        if engine_name in (self.ENGINE_ARGOS, self.ENGINE_GOOGLE):
            self.current_engine = engine_name

    def get_engine(self):
        """Trả về engine hiện tại"""
        return self.current_engine

    def translate(self, text):
        """Dịch text bằng engine đang được chọn"""
        if not text or not text.strip():
            return ""
        
        try:
            if self.current_engine == self.ENGINE_GOOGLE:
                return self._translate_google(text)
            else:
                return self._translate_argos(text)
        except Exception as e:
            return f"(Lỗi khi dịch: {e})"

    def _translate_argos(self, text):
        """Dịch bằng Argos Translate (offline)"""
        return self.argos_translation.translate(text)

    def _translate_google(self, text):
        """Dịch bằng Google Translate (online)"""
        return self.google_translator.translate(text)