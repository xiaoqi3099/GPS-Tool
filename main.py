"""
GPS经纬度转换工具 - Android应用
基于Kivy框架开发

主要功能:
1. 单个地址转经纬度
2. 批量地址转经纬度 (从文件)
3. 坐标系转换 (BD-09 -> GCJ-02 -> WGS84)
4. 生成Excel报告
"""

import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.clock import Clock

import os
import threading
from datetime import datetime

# 导入自定义模块
from coordinate转换 import convert_bd09_to_wgs84
from baidu_api import BaiduGeocodingAPI
from excel_handler import ExcelHandler


class GPSToolApp(App):
    """GPS经纬度转换工具主应用"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = BaiduGeocodingAPI()
        self.excel_handler = ExcelHandler()
        self.report_data = []
        self.is_converting = False
    
    def build(self):
        """构建应用界面"""
        Window.softinput_mode = 'pan'
        
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # 标题
        title = Label(text='[b]标准地址转经纬度[/b]', font_size='22sp', 
                      size_hint_y=None, height=60, markup=True)
        main_layout.add_widget(title)
        
        # 模式选择
        mode_layout = BoxLayout(size_hint_y=None, height=50)
        self.mode_spinner = Spinner(
            text='单个转换',
            values=('单个转换', '批量转换'),
            size_hint_x=0.5,
            font_size='16sp'
        )
        self.mode_spinner.bind(text=self.on_mode_change)
        mode_layout.add_widget(self.mode_spinner)
        main_layout.add_widget(mode_layout)
        
        # 单个转换区域
        self.single_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=180)
        self.single_layout.add_widget(Label(text='输入标准地址：', size_hint_y=None, height=30, font_size='14sp'))
        self.address_input = TextInput(hint_text='例如：北京市朝阳区某某路10号', 
                                       multiline=False, 
                                       size_hint_y=None, height=45,
                                       font_size='14sp')
        self.single_layout.add_widget(self.address_input)
        
        self.convert_btn = Button(text='开始转换', 
                                  size_hint_y=None, height=50,
                                  background_color=(0.2, 0.6, 1, 1),
                                  font_size='16sp')
        self.convert_btn.bind(on_press=self.start_single_conversion)
        self.single_layout.add_widget(self.convert_btn)
        main_layout.add_widget(self.single_layout)
        
        # 批量转换区域（默认隐藏）
        self.batch_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=0)
        self.batch_layout.opacity = 0
        
        file_layout = BoxLayout(size_hint_y=None, height=45)
        file_layout.add_widget(Label(text='文件：', size_hint_x=0.2, font_size='14sp'))
        self.file_input = TextInput(readonly=True, size_hint_x=0.5, font_size='12sp')
        file_layout.add_widget(self.file_input)
        
        self.select_file_btn = Button(text='选择', size_hint_x=0.3, font_size='12sp')
        self.select_file_btn.bind(on_press=self.show_file_chooser)
        file_layout.add_widget(self.select_file_btn)
        self.batch_layout.add_widget(file_layout)
        
        save_layout = BoxLayout(size_hint_y=None, height=45)
        save_layout.add_widget(Label(text='保存：', size_hint_x=0.2, font_size='14sp'))
        self.save_input = TextInput(readonly=True, size_hint_x=0.5, font_size='12sp')
        save_layout.add_widget(self.save_input)
        
        self.select_save_btn = Button(text='选择', size_hint_x=0.3, font_size='12sp')
        self.select_save_btn.bind(on_press=self.show_save_chooser)
        save_layout.add_widget(self.select_save_btn)
        self.batch_layout.add_widget(save_layout)
        
        self.batch_convert_btn = Button(text='开始批量转换', 
                                         size_hint_y=None, height=45,
                                         background_color=(0.2, 0.8, 0.4, 1),
                                         font_size='14sp')
        self.batch_convert_btn.bind(on_press=self.start_batch_conversion)
        self.batch_layout.add_widget(self.batch_convert_btn)
        
        main_layout.add_widget(self.batch_layout)
        
        # 进度条
        progress_label = Label(text='转换进度：', size_hint_y=None, height=25, font_size='12sp', halign='left')
        main_layout.add_widget(progress_label)
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=20)
        main_layout.add_widget(self.progress_bar)
        
        # 结果显示区域
        scroll = ScrollView(size_hint=(1, 0.45))
        self.result_label = Label(text='转换结果将显示在这里\n', 
                                   valign='top', 
                                   text_size=(None, None),
                                   font_size='13sp')
        self.result_label.bind(texture_size=self.result_label.setter('texture_size'))
        scroll.add_widget(self.result_label)
        main_layout.add_widget(scroll)
        
        # 底部按钮
        btn_layout = BoxLayout(size_hint_y=None, height=50)
        
        self.clear_btn = Button(text='清空', background_color=(0.8, 0.3, 0.3, 1), font_size='14sp')
        self.clear_btn.bind(on_press=self.clear_results)
        btn_layout.add_widget(self.clear_btn)
        
        self.export_btn = Button(text='导出报告', background_color=(0.3, 0.8, 0.3, 1), font_size='14sp')
        self.export_btn.bind(on_press=self.export_report)
        btn_layout.add_widget(self.export_btn)
        
        main_layout.add_widget(btn_layout)
        
        return main_layout
    
    def on_mode_change(self, spinner, text):
        """切换转换模式"""
        if text == '单个转换':
            self.single_layout.height = 180
            self.single_layout.opacity = 1
            self.batch_layout.height = 0
            self.batch_layout.opacity = 0
        else:
            self.single_layout.height = 0
            self.single_layout.opacity = 0
            self.batch_layout.height = 190
            self.batch_layout.opacity = 1
    
    def show_file_chooser(self, instance):
        """显示文件选择器"""
        # 尝试多个可能的路径
        paths_to_try = ['/storage/emulated/0/', '/sdcard/', os.path.expanduser('~')]
        default_path = paths_to_try[0]
        
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserIconView(path=default_path, 
                                           filters=['*.xlsx', '*.xls', '*.txt', '*.csv'])
        content.add_widget(filechooser)
        
        btn_layout = BoxLayout(size_hint_y=None, height=50)
        btn = Button(text='选择')
        btn.bind(on_press=lambda x: self.select_file(filechooser.path, filechooser.selection, popup))
        btn_layout.add_widget(btn)
        btn_layout.add_widget(Button(text='取消', on_press=lambda x: popup.dismiss()))
        content.add_widget(btn_layout)
        
        popup = Popup(title='选择文件', content=content, size_hint=(0.9, 0.9))
        popup.open()
        self.current_popup = popup
    
    def select_file(self, path, selection, popup):
        """选择文件"""
        popup.dismiss()
        if selection:
            self.file_path = selection[0]
            self.file_input.text = os.path.basename(self.file_path)
    
    def show_save_chooser(self, instance):
        """显示保存路径选择器"""
        paths_to_try = ['/storage/emulated/0/', '/sdcard/', os.path.expanduser('~')]
        default_path = paths_to_try[0]
        
        content = BoxLayout(orientation='vertical')
        dirchooser = FileChooserIconView(path=default_path, dirselect=True)
        content.add_widget(dirchooser)
        
        btn_layout = BoxLayout(size_hint_y=None, height=50)
        btn = Button(text='选择')
        btn.bind(on_press=lambda x: self.select_save_path(dirchooser.path, popup))
        btn_layout.add_widget(btn)
        btn_layout.add_widget(Button(text='取消', on_press=lambda x: popup.dismiss()))
        content.add_widget(btn_layout)
        
        popup = Popup(title='选择保存目录', content=content, size_hint=(0.9, 0.9))
        popup.open()
        self.current_popup = popup
    
    def select_save_path(self, path, popup):
        """选择保存路径"""
        popup.dismiss()
        self.save_path = path
        self.save_input.text = path
    
    def start_single_conversion(self, instance):
        """开始单个地址转换"""
        address = self.address_input.text.strip()
        
        if not address:
            self.result_label.text += "请输入地址！\n"
            return
        
        if self.is_converting:
            self.result_label.text += "正在转换中，请稍候...\n"
            return
        
        self.is_converting = True
        self.result_label.text = ""
        self.report_data = []
        
        # 在后台线程执行转换
        threading.Thread(target=self.convert_single_address, args=(address,), daemon=True).start()
    
    def convert_single_address(self, address):
        """执行单个地址转换"""
        try:
            lon, lat = self.api.geocode(address)
            
            if lon is not None and lat is not None:
                # 坐标系转换
                lon_wgs84, lat_wgs84 = convert_bd09_to_wgs84(lon, lat)
                
                lon_str = "{:.6f}".format(lon_wgs84)
                lat_str = "{:.6f}".format(lat_wgs84)
                
                # 保存数据
                self.report_data.append({
                    'address': address,
                    'lon': lon_wgs84,
                    'lat': lat_wgs84
                })
                
                # 更新UI
                Clock.schedule_once(lambda dt: self.update_result(
                    f"地址: {address}\n经度: {lon_str}\n纬度: {lat_str}\n{'-'*25}\n"))
            else:
                Clock.schedule_once(lambda dt: self.update_result(
                    f"地址: {address}\n转换失败，请检查地址是否正确\n{'-'*25}\n"))
        
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_result(
                f"地址: {address}\n错误: {str(e)}\n{'-'*25}\n"))
        
        finally:
            self.is_converting = False
    
    def start_batch_conversion(self, instance):
        """开始批量转换"""
        if not hasattr(self, 'file_path') or not self.file_path:
            self.result_label.text += "请先选择文件！\n"
            return
        
        if not hasattr(self, 'save_path') or not self.save_path:
            self.result_label.text += "请先选择保存路径！\n"
            return
        
        self.is_converting = True
        self.report_data = []
        self.result_label.text = "开始批量转换...\n"
        
        threading.Thread(target=self.convert_batch_addresses, daemon=True).start()
    
    def convert_batch_addresses(self):
        """执行批量地址转换"""
        try:
            # 读取地址
            addresses = self.excel_handler.read_addresses_from_file(self.file_path)
            
            if not addresses:
                Clock.schedule_once(lambda dt: self.update_result("文件中未找到地址！\n"))
                return
            
            total = len(addresses)
            completed = 0
            
            for address in addresses:
                if not address:
                    continue
                
                try:
                    lon, lat = self.api.geocode(address)
                    
                    if lon is not None and lat is not None:
                        lon_wgs84, lat_wgs84 = convert_bd09_to_wgs84(lon, lat)
                        
                        self.report_data.append({
                            'address': address,
                            'lon': lon_wgs84,
                            'lat': lat_wgs84
                        })
                        
                        completed += 1
                        progress = (completed / total) * 100
                        
                        Clock.schedule_once(lambda dt, p=progress: self.update_progress(p))
                        Clock.schedule_once(lambda dt, a=address, l=lon_wgs84, 
                                           la=lat_wgs84: self.update_result(
                            f"✓ {a}\n  经度:{l:.6f} 纬度:{la:.6f}\n"))
                    else:
                        Clock.schedule_once(lambda dt, a=address: 
                                            self.update_result(f"✗ {a} - 转换失败\n"))
                
                except Exception as e:
                    Clock.schedule_once(lambda dt, a=address, e=str(e): 
                                        self.update_result(f"✗ {a} - 错误\n"))
            
            Clock.schedule_once(lambda dt: self.update_result(
                f"\n批量转换完成！共 {completed}/{total} 个\n"))
            
            # 自动导出报告
            self.auto_export_report()
        
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_result(f"批量转换错误: {str(e)}\n"))
        
        finally:
            self.is_converting = False
    
    def update_result(self, text):
        """更新结果显示"""
        self.result_label.text += text
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.value = value
    
    def clear_results(self, instance):
        """清空结果"""
        self.result_label.text = ""
        self.progress_bar.value = 0
        self.report_data = []
    
    def export_report(self, instance):
        """导出报告"""
        if not self.report_data:
            self.result_label.text += "没有可导出的数据！\n"
            return
        
        if not hasattr(self, 'save_path') or not self.save_path:
            self.result_label.text += "请先选择保存路径！\n"
            return
        
        self.auto_export_report()
    
    def auto_export_report(self):
        """自动导出报告"""
        if not hasattr(self, 'save_path') or not self.save_path:
            return
            
        try:
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"经纬度报告_{timestamp}.xlsx"
            output_path = os.path.join(self.save_path, file_name)
            
            # 保存Excel
            success, msg = self.excel_handler.save_to_excel(self.report_data, output_path)
            
            if success:
                Clock.schedule_once(lambda dt: self.update_result(f"\n报告已保存: {file_name}\n"))
            else:
                # 尝试保存为CSV
                csv_path = output_path.replace('.xlsx', '.csv')
                success, msg = self.excel_handler.save_to_csv(self.report_data, csv_path)
                if success:
                    Clock.schedule_once(lambda dt: self.update_result(f"\n报告已保存: {os.path.basename(csv_path)}\n"))
                else:
                    Clock.schedule_once(lambda dt: self.update_result(f"\n保存失败: {msg}\n"))
        
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_result(f"\n导出错误: {str(e)}\n"))


if __name__ == '__main__':
    GPSToolApp().run()
