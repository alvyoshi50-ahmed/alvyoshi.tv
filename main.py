import json
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.network.urlrequest import UrlRequest

class StationsApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.scroll = ScrollView()
        self.container = BoxLayout(orientation='vertical', size_hint_y=None)
        self.container.bind(minimum_height=self.container.setter('height'))
        
        self.scroll.add_widget(self.container)
        self.layout.add_widget(self.scroll)
        
        # الاتصال بالـ IP الخاص بكمبيوتر البث
        url = "http://10.10.10.2/get_stations"
        req = UrlRequest(url, self.got_stations)
        
        return self.layout

    def got_stations(self, request, result):
        stations = json.loads(result)
        for station in stations:
            btn = Button(text=station['name'], size_hint_y=None, height=50)
            btn.bind(on_press=lambda x, url=station['url']: self.play_stream(url))
            self.container.add_widget(btn)

    def play_stream(self, url):
        print("تشغيل البث من الرابط:", url)

if __name__ == '__main__':
    StationsApp().run()
