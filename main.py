from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import QLabel
from plyer import filechooser
import gpxpy
import webbrowser

class GPXApp(App):
    def build(self):
        self.title = "GPX to Google Maps"
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        self.label = QLabel(text="Chưa chọn file GPX nào", halign='center')
        layout.add_widget(self.label)
        
        btn = Button(text="Chọn file GPX & Mở Bản Đồ", size_hint=(1, 0.3), background_color=(0.1, 0.5, 0.8, 1))
        btn.bind(on_press=self.show_file_chooser)
        layout.add_widget(btn)
        
        return layout

    def show_file_chooser(self, instance):
        # Mở bộ chọn file trên Android hoặc máy tính
        filechooser.open_file(on_selection=self.process_gpx)

    def process_gpx(self, selection):
        if not selection:
            return
        
        file_path = selection[0]
        self.label.text = f"Đang đọc: {file_path.split('/')[-1]}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                gpx = gpxpy.parse(f)

            points = []
            for track in gpx.tracks:
                for segment in track.segments:
                    for p in segment.points:
                        points.append((p.latitude, p.longitude))
            
            if not points:
                self.label.text = "File GPX không có tọa độ!"
                return

            start_lat, start_lng = points[0]
            end_lat, end_lng = points[-1]

            # Xử lý waypoint giống bản Python trước
            intermediate_points = []
            if len(points) > 2:
                step = max(1, len(points) // 9)
                intermediate_points = points[step:-step:step]

            base_url = "https://www.google.com/maps/dir/?api=1"
            origin_param = f"&origin={start_lat},{start_lng}"
            destination_param = f"&destination={end_lat},{end_lng}"
            
            waypoints_param = ""
            if intermediate_points:
                wp_encoded = "%7C".join([f"{p[0]},{p[1]}" for p in intermediate_points])
                waypoints_param = f"&waypoints={wp_encoded}"

            google_maps_url = base_url + origin_param + destination_param + waypoints_param

            # Mở Google Maps trên điện thoại
            webbrowser.open(google_maps_url)
            self.label.text = "Đã mở Google Maps thành công!"

        except Exception as e:
            self.label.text = f"Lỗi: {str(e)}"

if __name__ == '__main__':
    GPXApp().run()
