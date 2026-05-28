# -*- coding: utf-8 -*-
import urllib.request
import json
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.video import Video
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem

# عنوان السيرفر الافتراضي (سيقوم التطبيق بجلب البيانات منه فور تشغيله)
# ملاحظة: يمكنك تغيير هذا الـ IP ليتوافق مع السيرفر المحلي للشبكة
SERVER_IP = "your-server-ip-or-domain"
JSON_URL = f"http://{SERVER_IP}/api/channels.json"

class AlFyoushiApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        # الواجهة الرئيسية للتطبيق
        self.main_layout = BoxLayout(orientation='vertical')
        
        # 1. شريط العنوان العلوي المحترف
        self.toolbar = MDTopAppBar(
            title="شبكة الفيوشي الرقمية",
            anchor_title="right",
            right_action_items=[["menu", lambda x: None]]
        )
        self.toolbar.md_bg_color = self.theme_cls.primary_color
        self.main_layout.add_widget(self.toolbar)
        
        # 2. منطقة البث والفيديو الذكية (تتحمل الشعار والشريط المتحرك)
        self.video_container = FloatLayout(size_hint=(1, 0.40))
        
        # مشغل الفيديو الأساسي الداعم لـ m3u8 / mp4
        self.video_player = Video(
            source="http://server:port/live/1.m3u8", 
            state='play', 
            options={'eos': 'loop'},
            allow_stretch=True
        )
        self.video_container.add_widget(self.video_player)
        
        # زر التحكم بملء الشاشة (تكبير / تصغير) واجهة عصرية
        self.fullscreen_btn = MDIconButton(
            icon="fullscreen",
            pos_hint={"x": 0.02, "y": 0.05},
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            on_release=self.toggle_fullscreen
        )
        self.video_container.add_widget(self.fullscreen_btn)
        
        # شعار القنوات المباشرة (Logo Overlay) المتغير ديناميكياً
        self.logo_overlay = AsyncImage(
            source=f"http://{SERVER_IP}/images/logo.png",
            size_hint=(None, None),
            size=(80, 80),
            pos_hint={"right": 0.98, "top": 0.95}
        )
        self.video_container.add_widget(self.logo_overlay)
        
        # الشريط المتحرك العاجل فوق الفيديو (Ticker)
        self.ticker_label = Label(
            text="تغطية حصرية مباشرة لشبكة الفيوشي...",
            font_size='16sp',
            color=(1, 1, 0, 1), # لون أصفر ممتاز وعصري
            size_hint=(1, None),
            height=30,
            pos_hint={"x": 0, "y": 0.05}
        )
        self.video_container.add_widget(self.ticker_label)
        
        self.main_layout.add_widget(self.video_container)
        
        # 3. شريط التنقل السفلي السلس لتبديل المحطات الخمس بلمسة واحدة
        self.bottom_nav = MDBottomNavigation()
        
        # إنشاء الأزرار الخمسة للمحطات
        for i in range(1, 6):
            nav_item = MDBottomNavigationItem(
                name=f'ch{i}',
                text=f'المحطة {i}',
                icon='television-play',
                on_tab_press=lambda x, ch_num=i: self.change_channel(ch_num)
            )
            # إضافة حاوية داخلية لكل محطة لعرض بنر الإعلانات أسفلها
            ch_layout = BoxLayout(orientation='vertical', padding=10)
            if i == 1:
                self.ad_banner = AsyncImage(
                    source=f"http://{SERVER_IP}/images/banner.jpg",
                    size_hint=(1, 0.3)
                )
                ch_layout.add_widget(self.ad_banner)
                
                self.footer_label = Label(
                    text="جميع الحقوق محفوظة لشبكة الفيوشي © 2026",
                    color=(0,0,0,1),
                    size_hint=(1, 0.1)
                )
                ch_layout.add_widget(self.footer_label)
            
            nav_item.add_widget(ch_layout)
            self.bottom_nav.add_widget(nav_item)
            
        self.main_layout.add_widget(self.bottom_nav)
        
        # تشغيل مؤقت لتحديث النص المتحرك وجلب بيانات السيرفر تلقائياً بدون تعليق التطبيق
        Clock.schedule_once(self.load_server_data, 1)
        Clock.schedule_interval(self.animate_ticker, 0.1)
        
        self.is_fullscreen = False
        return self.main_layout

    def load_server_data(self, dt):
        # تشغيل الجلب في خيط مستقل (Thread) لضمان سلاسة فائقة للتطبيق وعدم تجمده
        threading.Thread(target=self.fetch_json_sync).start()

    def fetch_json_sync(self):
        try:
            response = urllib.request.urlopen(JSON_URL, timeout=5)
            config = json.loads(response.read().decode('utf-8'))
            
            # تحديث عناصر الواجهة في الخيط الرئيسي بشكل آمن
            Clock.schedule_once(lambda dt: self.apply_server_config(config), 0)
        except Exception as e:
            print(f"سيرفر الشبكة غير متصل حالياً أو الآي بي بحاجة لتعديل: {e}")

    def apply_server_config(self, config):
        # تطبيق اسم الشبكة المختار من لوحة التحكم ديناميكياً
        self.toolbar.title = config.get("network_name", "شبكة الفيوشي تي في")
        self.ticker_label.text = config.get("video_ticker_text", "")
        self.ticker_label.font_size = f"{config.get('video_ticker_size', 16)}sp"
        
        # تطبيق موقع وإحداثيات الشريط المتحرك
        t_pos = config.get("video_ticker_position", "bottom_left")
        if "top" in t_pos:
            self.ticker_label.pos_hint = {"x": 0, "top": 0.95}
        else:
            self.ticker_label.pos_hint = {"x": 0, "y": 0.05}
            
        # تطبيق رابط وإحداثيات وحجم الشعار
        self.logo_overlay.source = config.get("logo_url", "")
        l_size = config.get("logo_size", 80)
        self.logo_overlay.size = (l_size, l_size)
        
        l_pos = config.get("logo_position", "top_right")
        if l_pos == "top_right": self.logo_overlay.pos_hint = {"right": 0.98, "top": 0.95}
        elif l_pos == "top_left": self.logo_overlay.pos_hint = {"x": 0.02, "top": 0.95}
        elif l_pos == "bottom_right": self.logo_overlay.pos_hint = {"right": 0.98, "y": 0.1}
        elif l_pos == "bottom_left": self.logo_overlay.pos_hint = {"x": 0.02, "y": 0.1}
        
        # حفظ روابط القنوات الخمس المستلمة ديناميكياً للتبديل السريع
        self.channels_urls = [ch["url"] for ch in config.get("channels", [])]

    def change_channel(self, ch_num):
        # تبديل القنوات بشكل سريع وسلس جداً
        try:
            if hasattr(self, 'channels_urls') and len(self.channels_urls) >= ch_num:
                url = self.channels_urls[ch_num - 1]
                self.video_player.source = url
                self.video_player.state = 'play'
        except Exception as e:
            print(f"خطأ في الانتقال للمحطة: {e}")

    def animate_ticker(self, dt):
        # تحريك النص بشكل جانبي ناعم وسلس يحاكي القنوات التلفزيونية العالمية
        self.ticker_label.x -= 2
        if self.ticker_label.x < -Window.width / 2:
            self.ticker_label.x = Window.width / 2

    def toggle_fullscreen(self, instance):
        # ميزة ملء الشاشة الفورية لتجربة مشاهدة سينمائية للمشتركين واغلاقها بسهولة
        if not self.is_fullscreen:
            # تكبير شاشة البث وإخفاء القوائم الأخرى
            self.main_layout.remove_widget(self.toolbar)
            self.main_layout.remove_widget(self.bottom_nav)
            self.video_container.size_hint = (1, 1)
            self.fullscreen_btn.icon = "fullscreen-exit"
            self.is_fullscreen = True
        else:
            # العودة للوضع الطبيعي وإغلاق ملء الشاشة بلمسة واحدة
            self.video_container.size_hint = (1, 0.40)
            self.main_layout.clear_widgets()
            self.main_layout.add_widget(self.toolbar)
            self.main_layout.add_widget(self.video_container)
            self.main_layout.add_widget(self.bottom_nav)
            self.fullscreen_btn.icon = "fullscreen"
            self.is_fullscreen = False

if __name__ == '__main__':
    AlFyoushiApp().run()