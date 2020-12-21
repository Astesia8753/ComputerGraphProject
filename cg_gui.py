# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 18:11:05 2020

@author: ZQY
"""

#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys,time
import cg_algorithms as alg
import math
import os
from PIL import Image

from PyQt5 import QtCore
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication,
    QColorDialog,
    QMainWindow,
    qApp,
    QFileDialog,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QStyleOptionGraphicsItem,
    QSplashScreen )

from PyQt5.QtGui import QPainter, QMouseEvent, QColor,QPixmap,QPalette , QBrush
from PyQt5.QtCore import QRectF
import numpy as np

def get_center_point(p_list):
    if p_list==[]:
        return 
    x_list=[]
    y_list=[]
    
    len_p_list=len(p_list)
    for i in range(len_p_list):
        x_list.append(p_list[i][0])
        y_list.append(p_list[i][1])
    
    x_max=max(x_list)
    x_min=min(x_list)
    y_max=max(y_list)
    y_min=min(y_list)
    return [int((x_max+x_min)/2),int((y_min+y_max)/2)]



    
def get_rotate_angle(x1,y1,x_c,y_c,x2,y2):
    dx1,dy1=x1-x_c,y1-y_c
    dx2,dy2=x2-x_c,y2-y_c
    len1=math.sqrt(dx1**2+dy1**2)
    len2=math.sqrt(dx2**2+dy2**2)
    if len1==0 or len2==0:
   
        return 0
    sin1=dy1/len1
    cos1=dx1/len1
    sin2=dy2/len2
    cos2=dx2/len2
    dsin=sin2*cos1-cos2*sin1
    dcos=cos2*cos1+sin2*sin1
    ra=0
    if dcos>=0:
        ra=math.asin(dsin)
    else:
        ra=math.pi-math.asin(dsin)
    return -ra* 360 / 2 / np.pi
        
        
class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        
        self.temp_point_list=[]  ##用于暂存曲线或多边形的已有控制点
        self.color=QColor(0,0,0)
        self.change_para_list=[] ##对于变换，建立一个参数列表来保存不同鼠标操作产生的参数
        self.clip_temp_item=None ##对于裁剪过程中，我们显示的是一个被剪裁的副本
        self.ori_item_pl=None
        
        self.rect_item=None      ##在裁剪时显示裁剪边框
        
    def set_pen(self, color):
        self.color = color
        
    def clear_tmp_var(self):
        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.temp_point_list=[]  
        self.change_para_list=[]
        self.clip_temp_item=None 
        self.ori_item_pl=None
        self.rect_item=None  
        
        
    def clear_canvas(self):
        #print('进入画布的重置函数')
        #删除场景中所有图元并更新
        for item in self.item_dict:
            self.scene().removeItem(self.item_dict[item])
        self.updateScene([self.sceneRect()])
        ### 重置所有画布变量
        self.item_dict = {}
        self.selected_id = ''
        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.temp_point_list=[]
        self.color=QColor(0,0,0)
        #print('已删除所有图元，结束画布重置函数')
        self.change_para_list=[] ##用于记录一些变换过程的点数据
        self.clip_temp_item=None
        
        
    def save_canvas_picture(self,path):
        canvas = np.zeros([600, 600, 3], np.uint8)
        canvas.fill(255)
        
        for item in self.item_dict.values():
            pixels=[]
            RGB=[item.color.red(),item.color.green(),item.color.blue()]
            if item.item_type == 'line':
                pixels = alg.draw_line(item.p_list, item.algorithm)
            elif item.item_type == 'polygon':
                pixels = alg.draw_polygon(item.p_list, item.algorithm)
            elif item.item_type == 'ellipse':
                pixels = alg.draw_ellipse(item.p_list,'')
            elif item.item_type == 'curve':
                pixels = alg.draw_curve(item.p_list, item.algorithm)
            elif item.item_type=='free':
                pixels = alg.draw_free(item.p_list)
            for x, y in pixels:
                if 0<=x<600 and 0<=y<600:
                    canvas[y, x] = RGB
        Image.fromarray(canvas).save(os.path.join(path))
    
    def save_canvas_file(self,path):
        file=open(path,'w')
        for item in self.item_dict.values():
            file.write(str([item.color.red(),item.color.green(),item.color.blue()])+'#')
            file.write(str(item.item_type))
            file.write(' '+str(item.id))
            if(item.algorithm==''):
                file.write('#')
            else:
                file.write(' '+str(item.algorithm)+'#')
            file.write(str(item.p_list)+'\n')
        file.close()
        
    ##def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '', color:QColor=QColor(0,0,0,), parent: QGraphicsItem = None):
    def load_canvas_file(self,path):
        rst=''
        with open(path, 'r') as fp:
            line = fp.readline()
            while line:
                str_list=line.split('#')
                cur_str=str_list[0]
                color_list=eval(cur_str)
                cur_str=str_list[1]
                info_list=cur_str.split(' ')
                rst=info_list[1]
                alg=''
                if len(info_list)==3:
                    alg=info_list[2]
                cur_str=str_list[2]
                point_list=eval(cur_str)
                new_item=MyItem(info_list[1],info_list[0],point_list,alg,QColor(color_list[0],color_list[1],color_list[2]))
                self.item_dict[info_list[1]]=new_item
                self.scene().addItem(new_item)
                self.list_widget.addItem(info_list[1])
                line=fp.readline()
        self.updateScene([self.sceneRect()])   
        return rst       
        
        
        
    def start_translate(self,item_id):
        if item_id=='':
            return
        self.status='translate'
        self.temp_algorithm=''
        self.temp_id=item_id
    
    def start_rotate(self,item_id):
        if item_id=='' :
            return
        center_point=get_center_point(self.item_dict[item_id].p_list)
        self.change_para_list.append(center_point)
        self.status='rotate'
        self.temp_algorithm=''
        self.temp_id=item_id
        self.ori_item_pl=self.item_dict[item_id].p_list
        
    def start_scale(self,item_id):
        if item_id=='':
            return
        center_point=get_center_point(self.item_dict[item_id].p_list)
        self.change_para_list.append(center_point)
        self.status='scale'
        self.temp_algorithm=''
        self.temp_id=item_id
        self.ori_item_pl=self.item_dict[item_id].p_list
    
    def start_clip(self,algorithm,item_id):
        if item_id=='' or self.item_dict[item_id].item_type!='line':
            return
        self.status='clip'
        self.temp_algorithm=algorithm
        self.temp_id=item_id
        
        self.clip_temp_item = MyItem(-1, 'line', [[0, 0], [0, 0]], self.temp_algorithm,self.color)
        
   
    
    def start_free_draw(self,item_id):
        self.status='free'
        self.algorithm=''
        self.temp_id=item_id
        
    def start_draw_line(self, algorithm, item_id):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
    
    def start_draw_polygon(self, algorithm, item_id):
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        

    def start_draw_ellipse(self,item_id):
        self.status = 'ellipse'
        self.temp_algorithm=''
        self.temp_id=item_id
        
    
    def start_draw_curve(self, algorithm, item_id):
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        
    def start_delete(self,item_id):
        if item_id=='':
            return 
        
        item_to_delete=self.list_widget.findItems(item_id,QtCore.Qt.MatchContains)
        self.clear_selection()
        self.list_widget.clearSelection()
        self.scene().removeItem(self.item_dict[item_id])
        self.item_dict.pop(item_id)
        
        if len(item_to_delete)==0:
            return 
        
        connect=self.list_widget.row(item_to_delete[0])
        self.list_widget.removeItemWidget(item_to_delete[0])
        self.list_widget.takeItem(connect)
        
    def finish_draw(self):
        if self.status=='curve':
            if len(self.temp_item.p_list)<=3:
                self.clear_tmp_var()
                return 
        self.item_dict[self.temp_id] = self.temp_item
        self.list_widget.addItem(self.temp_id)
        self.status=''
        self.temp_id = self.main_window.get_id()
        self.clear_tmp_var();
        

    
    def finish_change(self):
        self.clear_tmp_var()
        

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''
            self.rotate_scale_flag=0

    def selection_changed(self, selected):
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        if selected !='':
            self.selected_id = selected
            self.item_dict[selected].selected = True
            self.item_dict[selected].update()
            self.status = ''
            self.updateScene([self.sceneRect()])
            self.rotate_scale_flag=0

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line' or self.status=='ellipse':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm,self.color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'polygon' or self.status == 'curve':
            if event.buttons()== QtCore.Qt.LeftButton:
                if self.temp_point_list == [] :
                    self.temp_item = MyItem(self.temp_id, self.status, self.temp_point_list, self.temp_algorithm,self.color)
                    self.scene().addItem(self.temp_item)
                self.temp_point_list.append([x, y])
            elif event.buttons()==QtCore.Qt.RightButton:
                self.finish_draw()
        elif self.status=='free':
            self.temp_item=MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm,self.color)
            self.scene().addItem(self.temp_item)
            self.temp_point_list.append([x,y])
            
        elif self.status=='translate' or self.status=='rotate' or self.status=='scale':
            self.change_para_list.append([x,y])
            
        elif self.status=='clip':
            self.change_para_list.append([x,y])
            self.scene().addItem(self.clip_temp_item)
            self.rect_item=MyItem(-1,'rect',[[x,y],[x,y]])
            self.scene().addItem(self.rect_item)
            
          
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line' or self.status=='ellipse':
            
            self.temp_item.p_list[1] = [x, y]
            
        elif self.status == 'polygon' or self.status == 'curve':
            
            self.temp_point_list[len(self.temp_point_list)-1]=([x, y])
        
        elif self.status=='free':
            self.temp_item.p_list.append([x,y])
            
        elif self.status=='translate':
            if len(self.change_para_list)==0:
                print('operate too fast')
                self.clear_tmp_var()
                return
            dx=x-self.change_para_list[0][0]
            dy=y-self.change_para_list[0][1]
            self.change_para_list[0][0]=x
            self.change_para_list[0][1]=y
            point_list=self.item_dict[self.temp_id].p_list
            self.item_dict[self.temp_id].p_list=alg.translate(point_list,[dx,dy],'')
            
        elif self.status=='scale':
            if len(self.change_para_list)<2:
                print('operate too fast')
                self.clear_tmp_var()
                return
            dx1=self.change_para_list[1][0]-self.change_para_list[0][0]
            dy1=self.change_para_list[1][1]-self.change_para_list[0][1]
            norm_len=math.sqrt(dx1*dx1+dy1*dy1)
                
            dx2=x-self.change_para_list[0][0]
            dy2=y-self.change_para_list[0][1]
            change_len=math.sqrt(dx2*dx2+dy2*dy2)
            if norm_len!=0:
                scale=float(change_len/norm_len)               
                tmp_para_list=[self.change_para_list[0][0],self.change_para_list[0][1],scale]
                self.item_dict[self.temp_id].p_list=alg.scale(self.ori_item_pl,tmp_para_list,'')
            else :
                pass
        elif self.status=='rotate':
            if len(self.change_para_list)<2:
                print('operate too fast')
                self.clear_tmp_var()
                return
            cx,cy=self.change_para_list[0][0],self.change_para_list[0][1]
            lx,ly=self.change_para_list[1][0],self.change_para_list[1][1]
            a=get_rotate_angle(lx,ly,cx,cy,x,y)
            tmp_para_list=[cx,cy,a]
            self.item_dict[self.temp_id].p_list=alg.rotate(self.ori_item_pl,tmp_para_list,'')
            
        elif self.status=='clip':
            point_list=self.item_dict[self.temp_id].p_list
            if len(self.change_para_list)==0:
                print('operate too fast')
                self.clear_tmp_var()
                return
            tmp_para_list=[self.change_para_list[0][0],self.change_para_list[0][1],x,y]
            self.clip_temp_item.p_list=alg.clip(point_list,tmp_para_list,self.temp_algorithm)
            self.rect_item.p_list[1]=[x,y]
            
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.status == 'line' or self.status=='ellipse' or self.status=='free':
            self.finish_draw()
        elif self.status == 'polygon' or self.status == 'curve':
            pass
        elif self.status=='translate'or self.status=='rotate'or self.status=='scale':
            self.finish_change()
            
        elif self.status=='clip':
            if self.item_dict[self.temp_id].item_type!='line':
                return
            self.item_dict[self.temp_id].p_list=self.clip_temp_item.p_list
            if self.item_dict[self.temp_id].p_list==[]:
                
                self.start_delete(self.temp_id)
            self.scene().removeItem(self.clip_temp_item)
            self.scene().removeItem(self.rect_item)
            self.finish_change()
        self.updateScene([self.sceneRect()])
            
        super().mouseReleaseEvent(event)


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '', color:QColor=QColor(0,0,0,), parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list        # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.color=color
   
        
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        
        painter.setPen(self.color)
        item_pixels=[]
        
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)   
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)  
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list, self.algorithm)
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
        elif self.item_type=='free':
            item_pixels=alg.draw_free(self.p_list)
        elif self.item_type=='rect':
            painter.setPen(QColor.blue())
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            rect_p_list=[[x-1,y-1],[w+2,y-1],[w+2,h+2],[x-1,h+2]]
            item_pixels=alg.draw_polygon(rect_p_list,'DDA')
        
        
        for p in item_pixels:
            painter.drawPoint(*p)
        if self.selected:
            painter.setPen(QColor(255, 0, 0))
            painter.drawRect(self.boundingRect())

    def boundingRect(self) -> QRectF:
        if self.item_type == 'line' or self.item_type=='ellipse' :
            if len(self.p_list)==0 :
                return QRectF(0,0,0,0)
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'polygon' or self.item_type=='curve'or self.item_type=='free':
            x_min, y_min = self.p_list[0]
            x_max, y_max = x_min, y_min
            for x, y in self.p_list:
                if(x < x_min):
                    x_min = x
                if(x > x_max):
                    x_max = x
                if(y < y_min):
                    y_min = y
                if (y > y_max):
                    y_max = y
            return QRectF(x_min-1, y_min-1, x_max-x_min+2, y_max-y_min+2)
        elif self.item_type=='rect':
            return QRectF(0,0,0,0)
       


class MainWindow(QMainWindow):
    """
    主窗口类
    """
    def __init__(self):
        super().__init__()
        self.item_cnt = 0

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 600, 600)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(600, 600)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')

        set_pen_act = file_menu.addAction('设置画笔')
        set_pen_act.setShortcut(str('ctrl+p'))
        reset_canvas_act = file_menu.addAction('重置画布')
        reset_canvas_act.setShortcut(str('ctrl+r'))
        save_canvas_picture_act=file_menu.addAction('保存画布(图片)')
        save_canvas_picture_act.setShortcut(str('ctrl+s'))
        save_canvas_file_act=file_menu.addAction('保存画布(文件)')
        save_canvas_file_act.setShortcut(str('ctrl+f'))
        load_canvas_file_act=file_menu.addAction('加载画布文件')
        load_canvas_file_act.setShortcut(str('ctrl+o'))
        exit_act = file_menu.addAction('退出')
        exit_act.setShortcut(str('ctrl+q'))
        
        
        draw_menu = menubar.addMenu('绘制')
    
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_naive_act.setShortcut(str('ctrl+1'))
        line_dda_act = line_menu.addAction('DDA')
        line_dda_act.setShortcut(str('ctrl+2'))
        line_bresenham_act = line_menu.addAction('Bresenham')
        line_bresenham_act.setShortcut(str('ctrl+3'))
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_dda_act.setShortcut(str('ctrl+4'))
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        polygon_bresenham_act.setShortcut(str('ctrl+5'))
        ellipse_act = draw_menu.addAction('椭圆')
        ellipse_act.setShortcut(str('ctrl+6'))
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_bezier_act.setShortcut(str('ctrl+7'))
        curve_b_spline_act = curve_menu.addAction('B-spline')
        curve_b_spline_act.setShortcut(str('ctrl+8'))
        free_draw_act=draw_menu.addAction('自由绘图')
        free_draw_act.setShortcut('ctrl+9')
        
        
        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        translate_act.setShortcut('shift+t')
        rotate_act = edit_menu.addAction('旋转')
        rotate_act.setShortcut('shift+r')
        scale_act = edit_menu.addAction('缩放')
        scale_act.setShortcut('shift+s')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_cohen_sutherland_act.setShortcut('shift+1')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')
        clip_liang_barsky_act.setShortcut('shift+2')
        delete_item_act=edit_menu.addAction('删除')
        delete_item_act.setShortcut(str('ctrl+z'))
        
        layout_menu=menubar.addMenu('设置')
        set_theme_act=layout_menu.addAction('设置')
        set_theme_act.setShortcut('alt+t')
        

        # 连接信号和槽函数
        exit_act.triggered.connect(qApp.quit)
        '''画布设置'''
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        save_canvas_picture_act.triggered.connect(self.save_canvas_picture_action)
        save_canvas_file_act.triggered.connect(self.save_canvas_file_action)
        load_canvas_file_act.triggered.connect(self.load_canvas_file_action)
        set_pen_act.triggered.connect(self.set_pen_action)
        '''图元生成'''
        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        ellipse_act.triggered.connect(self.ellipse_action)
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)
        free_draw_act.triggered.connect(self.free_draw_action)
        '''图元变换'''
        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)
        delete_item_act.triggered.connect(self.delete_item_action)
        '''图元选择'''
        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)
        
        
        '''主题设置'''
        set_theme_act.triggered.connect(self.set_theme_action)
        
        
        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)
        self.setWindowTitle('ZQY\'s canva ')

    def terminate_p_c(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        
    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id
    
    def set_theme_action(self):
        palette = QPalette()
        col = QColorDialog.getColor()
        if col.isValid(): 
            palette.setColor(QPalette.Background , col)
            self.setPalette(palette)

           
        
    def set_pen_action(self):
        self.terminate_p_c()
        col = QColorDialog.getColor()
        if col.isValid(): 
            self.canvas_widget.set_pen(col)
            
    def reset_canvas_action(self):
        self.terminate_p_c()
        self.statusBar().showMessage('重置画布')
        self.item_cnt=0
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        self.canvas_widget.clear_canvas()
        
        self.list_widget.clear()
        return        
        

    def save_canvas_picture_action(self):
        self.terminate_p_c()
        path = QFileDialog.getSaveFileName(
            filter='Images (*.png *.jpg *.bmp)')
        if path[0]=='':
            return 
        self.canvas_widget.save_canvas_picture(path[0])
        self.statusBar().showMessage('保存画布(图片形式)')
    
    def save_canvas_file_action(self):
        self.terminate_p_c()
        path = QFileDialog.getSaveFileName(
            filter='Images (*.txt)')
        if path[0]=='':
            return 
        self.canvas_widget.save_canvas_file(path[0])
        self.statusBar().showMessage('保存画布(文件形式)')
    
    def load_canvas_file_action(self):
        self.reset_canvas_action()
        path = QFileDialog.getOpenFileName(
            filter='Images (*.txt)')
        if path[0]=='':
            return 
        now_id=self.canvas_widget.load_canvas_file(path[0])
        self.item_cnt=int(now_id)+1
        self.statusBar().showMessage('加载画布文件')
        
    
    def free_draw_action(self):
        self.terminate_p_c()
        self.canvas_widget.start_free_draw(self.get_id())
        self.statusBar().showMessage('自由绘图')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        
    def line_naive_action(self):
        self.terminate_p_c()
        self.canvas_widget.start_draw_line('Naive', self.get_id())
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    
    def line_dda_action(self):
        self.terminate_p_c()
        self.canvas_widget.start_draw_line('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    
    def line_bresenham_action(self):
        self.terminate_p_c()
        self.canvas_widget.start_draw_line('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    
    def polygon_dda_action(self):
        self.terminate_p_c()
        self.canvas_widget.start_draw_polygon('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        self.terminate_p_c()
        self.canvas_widget.start_draw_polygon('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        self.terminate_p_c()
        self.canvas_widget.start_draw_ellipse(self.get_id())
        self.statusBar().showMessage('椭圆绘制')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    
    def curve_bezier_action(self):
        self.terminate_p_c()
        self.canvas_widget.start_draw_curve('Bezier', self.get_id())
        self.statusBar().showMessage('Bezier算法绘制曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_b_spline_action(self):
        self.terminate_p_c()
        self.canvas_widget.start_draw_curve('B-spline', self.get_id())
        self.statusBar().showMessage('B-spline算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        
        
    def translate_action(self):
        self.terminate_p_c()
        self.canvas_widget.start_translate(self.canvas_widget.selected_id)
        
    def rotate_action(self):
        self.terminate_p_c()
        self.canvas_widget.start_rotate(self.canvas_widget.selected_id)
        
    def scale_action(self):
        self.terminate_p_c()
        self.canvas_widget.start_scale(self.canvas_widget.selected_id)
        
    def clip_cohen_sutherland_action(self):
        self.terminate_p_c()
        self.canvas_widget.start_clip('Cohen-Sutherland',self.canvas_widget.selected_id)
        
    def clip_liang_barsky_action(self):
        self.terminate_p_c()
        self.canvas_widget.start_clip('Liang-Barsky',self.canvas_widget.selected_id)
    
    def delete_item_action(self):
        self.terminate_p_c()
        self.canvas_widget.start_delete(self.canvas_widget.selected_id)
        

class SplashScreen(QSplashScreen):
    def __init__(self):
        super(SplashScreen, self).__init__(QPixmap("./source/start.jpg"))  
   
    def effect(self):
        self.setWindowOpacity(0)
       
        while True:
            newOpacity = self.windowOpacity() + 0.05     #设置淡入
            if newOpacity > 1:
                break
            self.setWindowOpacity(newOpacity)
            self.show()
            time.sleep(0.04)
        time.sleep(0.2)
  
        while True:
            newOpacity = self.windowOpacity() - 0.05       #设置淡出
            if newOpacity < 0:
                break
            self.setWindowOpacity(newOpacity)
            time.sleep(0.02)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.processEvents()
    mw = MainWindow()
    
    splash = SplashScreen()
    splash.effect()
    mw.show()
    splash.finish(mw)
    sys.exit(app.exec_())
