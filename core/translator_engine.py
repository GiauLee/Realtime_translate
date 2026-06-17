# core/translator_engine.py

import argostranslate.package
import argostranslate.translate

class MyTranslator:
    def __init__(self):
        # Tải và cài gói ngôn ngữ EN→VI nếu chưa có
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
        self.translation = self.en_lang.get_translation(self.vi_lang)

    def translate(self, text):
        try:
            return self.translation.translate(text)
        except Exception:
            return "(Lỗi khi dịch)"