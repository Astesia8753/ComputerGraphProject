# -*- coding: utf-8 -*-
"""
Created on Sat Sep 26 23:32:37 2020

@author: ZQY
"""

#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    if len(p_list)==0:
        return []
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
    elif algorithm == 'DDA':
        if abs(x1-x0)<=abs(y1-y0):
            length=abs(y1-y0)
        else :
            length=abs(x1-x0)
        
        if length==0:
            return []
        
        dx=(x1-x0)/length
        dy=(y1-y0)/length
        x=x0+0.5
        y=y0+0.5
        for  i in range(length):
             result.append((int(x), int(y)))
             x+=dx
             y+=dy
             
            
    elif algorithm == 'Bresenham':
        # 我们已经知道了对于斜率小于1时直线的生成方法
        # 对于斜率大于等于1的直线，我们只需要把x y对调，设置像素时再对调一次即可
        
        
        # 设置一个swap_flag变量来记录对调情况
        dx=abs(x1-x0)
        dy=abs(y1-y0)
        swap_flag=False
        if dy>=dx:
            x0,x1,dx,y0,y1,dy=y0,y1,dy,x0,x1,dx
            swap_flag=True
            
        #初始化x,y,p
        x,y=x0,y0
        if swap_flag:
            result.append((int(y),int(x)))
        result.append((int(x),int(y)))
        p=2*dy-dx
        
        
        #direct表示增长方向
        direct_x=(1 if x1>x0 else -1)
        direct_y=(1 if y1>y0 else -1)
        
        
        for i in range(dx):
            x+=direct_x
            if p<0:
                p+=2*dy
            else:
                y+=direct_y
                p+=2*dy-2*dx
            
            if swap_flag:
                result.append((int(y),int(x)))
            else:
                result.append((int(x),int(y)))
            
        
    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    
    return result
def draw_free(p_list):
    
    result = []
    
    for i in range(len(p_list)-1):
        line = draw_line([p_list[i], p_list[i+1]], 'DDA')
        result += line
    
    return result


def draw_ellipse(p_list,algorithm):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result=[]
    x0,y0=p_list[0]
    x1,y1=p_list[1]
    
    
    xc=(x0+x1)/2
    yc=(y0+y1)/2
    
    a=abs(x1-x0)/2
    b=abs(y0-y1)/2
    
    x=0
    y=b
    
    sqra=a*a
    sqrb=b*b
    
    
    p1=sqrb-sqra*b+sqra/4
    result.append((int(x+xc),int(y+yc)))
    result.append((int(x+xc),int(yc-y)))
    
    while sqrb*(x+1)<sqra*(y-0.5):
        if p1<0:
            p1+=2*sqrb*x+3*sqrb
            x+=1
        else:
            p1+=2*sqrb*x-2*sqra*y+2*sqra+3*sqrb
            x+=1
            y-=1
       
        result.append((int(x+xc),int(y+yc)))
        result.append((int(x+xc),int(yc-y)))
        result.append((int(xc-x),int(y+yc)))
        result.append((int(xc-x),int(yc-y)))
    
    
    p2=sqrb*(x+0.5)*(x+0.5)+sqra*(y-1)*(y-1)-sqra*sqrb
    
    while y>=0 :
        if p2<0:
            p2+=(2*sqrb*x-2*sqra*y+2*sqrb+3*sqra)
            x+=1
            y-=1
           
        else:
            p2+=(-2*sqra*y+3*sqra)
            y-=1
           
        result.append((int(x+xc),int(y+yc)))
        result.append((int(x+xc),int(yc-y)))
        result.append((int(xc-x),int(y+yc)))
        result.append((int(xc-x),int(yc-y)))
        
    return result
            
            
            
dt =0.001  ## dt 为t每次增加的步长

def vector_dot(v1,v2):
    rst=0
    v_len =len(v1)
    for i in range(v_len):
        rst+=v1[i]*v2[i]
    return rst
        
def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    if len(p_list)<=3:
        return []
    result_point=[]
    result=[]
    p_len=len(p_list)
    
    if algorithm == 'Bezier':
        t=0
        while t<=1:
            ###########################################
            #   该部分计算为 给定t值，计算出P(t)点坐标   #
            ########################################### 
            
            p_Bezier=[]
            
            ## 初始化p_Bezier
            for i in range(p_len):
                p_Bezier.append(p_list[i])
                
            ## 对于n个控制点，我们需要n-1次迭代才能得到P(t)的坐标
            ## 每次迭代都会减少一个点
            for i in range(p_len-1):
                p_tmp=[]
                for j in range(p_len-i-1):
                    px1,py1=p_Bezier[j]
                    px2,py2=p_Bezier[j+1]
                    x=(1-t)*px1+t*px2
                    y=(1-t)*py1+t*py2
                    p_tmp.append((x,y))
                    
                for j in range(p_len-i-1):
                    p_Bezier[j]=p_tmp[j]
            
            ## 在 len-1次迭代之后，p_Bezier中只剩下了一个点就是P(t)
            result_point.append((int(p_Bezier[0][0]),int(p_Bezier[0][1])))
        
           
            ##此后我们只需要慢慢增大t即可，这样就能生成一组非常密集的点
            t+=dt
    
    elif algorithm=='B-spline':
        for i in range(p_len-3):
            vc0=(-1,3,-3,1)
            vc1=(3,-6,3,0)
            vc2=(-3,0,3,0)
            vc3=(1,4,1,0)
            vpx=(p_list[i][0],p_list[i+1][0],p_list[i+2][0],p_list[i+3][0])
            vpy=(p_list[i][1],p_list[i+1][1],p_list[i+2][1],p_list[i+3][1])
            ax0=vector_dot(vc0,vpx)/6
            ax1=vector_dot(vc1,vpx)/6
            ax2=vector_dot(vc2,vpx)/6
            ax3=vector_dot(vc3,vpx)/6
            ay0=vector_dot(vc0,vpy)/6
            ay1=vector_dot(vc1,vpy)/6
            ay2=vector_dot(vc2,vpy)/6
            ay3=vector_dot(vc3,vpy)/6
            vax=(ax0,ax1,ax2,ax3)
            vay=(ay0,ay1,ay2,ay3)
            t=0
            while t<=1:
                vt=(t*t*t,t*t,t,1)
                x=vector_dot(vt,vax)
                y=vector_dot(vt,vay)
                t+=dt
                result_point.append((int(x),int(y)))
              
    for i in range (len(result_point)-1):
        if(result_point[i]!=result_point[i+1]):
            subline=draw_line((result_point[i],result_point[i+1]),'DDA')
            result+=subline
        
    return result
            
       


def translate(p_list, paraList,algorithm):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    rst=[]
    for i in range(len(p_list)):
        xnew=p_list[i][0]+int(paraList[0])
        ynew=p_list[i][1]+int(paraList[1])
        rst.append([int(xnew),int(ynew)])
    return rst


def rotate(p_list, paraList,algorithm):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    r=-math.pi*float(paraList[2])/180
    sinr=math.sin(r)
    cosr=math.cos(r)
    x=int(paraList[0])
    y=int(paraList[1])

  
    result = []
    for i in range(len(p_list)):
        x0 = p_list[i][0]
        y0 = p_list[i][1]
        tempx = x + (x0 - x) * cosr - (y0 - y) * sinr
        tempy = y + (x0 - x) * sinr + (y0 - y) * cosr
        result.append([int(tempx), int(tempy)])
    return result



def scale(p_list, paraList,algorithm):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    
    rst=[]
    x=int(paraList[0])
    y=int(paraList[1])
    s=float(paraList[2])
  
    for i in range(len(p_list)):
        xnew=int((p_list[i][0]-x)*s+x)
        ynew=int((p_list[i][1]-y)*s+y)   
        rst.append([int(xnew),int(ynew)])
    return rst


def encode(x, y, x_min, y_min, x_max, y_max) -> int:
    result = 0
    INSIDE = 0  # 0000
    LEFT = 1  # 0001
    RIGHT = 2  # 0010
    BOTTOM = 4  # 0100
    TOP = 8  # 1000

    result = INSIDE

    if x < x_min:
        result = result | LEFT
    elif x > x_max:
        result = result | RIGHT
    if y < y_min:
        result = result | BOTTOM
    elif y > y_max:
        result = result | TOP
    return result


def clip(p_list, paraList, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    
    x_min=min(paraList[0],paraList[2])
    x_max=max(paraList[0],paraList[2])
    y_min=min(paraList[1],paraList[3])
    y_max=max(paraList[1],paraList[3])
    
    x0,y0 = int(p_list[0][0]),int(p_list[0][1])
    x1,y1 = int(p_list[1][0]),int(p_list[1][1])
    result=[]
    if algorithm == 'Cohen-Sutherland':
        LEFT = 1  # 0001
        RIGHT = 2  # 0010
        BOTTOM = 4  # 0100
        TOP = 8  # 1000
        x0, y0 = p_list[0]
        x1, y1 = p_list[1]
        outcode0 = encode(x0, y0, x_min, y_min, x_max, y_max)
        outcode1 = encode(x1, y1, x_min, y_min, x_max, y_max)
        
        success=False
        
        while (1):
          
            if bool((outcode0 | outcode1)) == 0:
                success = True 
                break
            elif bool(outcode0 & outcode1) == 1:  
                success = False  
                break
            else:
             
                x = 0
                y = 0
                if outcode0 == 0:
                    outcode = outcode1
                else:
                    outcode = outcode0
              
                if outcode & TOP:
                    rk = (x1 - x0) / (y1 - y0)
                    y = y_max
                    x = x0 + rk * (y - y0)
                elif outcode & BOTTOM:
                    rk = (x1 - x0) / (y1 - y0)
                    y = y_min
                    x = x0 + rk * (y - y0)
                elif outcode & RIGHT:
                    k = (y1 - y0) / (x1 - x0)
                    x = x_max
                    y = y0 + k * (x - x0)
                elif outcode & LEFT:
                    k = (y1 - y0) / (x1 - x0)
                    x = x_min
                    y = y0 + k * (x - x0)
                if outcode == outcode1:
                    x1 = x
                    y1 = y
                    outcode1 = encode(x1, y1, x_min, y_min, x_max, y_max)
                else:
                    x0 = x
                    y0 = y
                    outcode0 = encode(x0, y0, x_min, y_min, x_max, y_max)
        if success == True:
            result.append((int(x0), int(y0)))
            result.append((int(x1), int(y1)))
    
        return result
    elif algorithm=='Liang-Barsky':
        dx=x1-x0
        dy=y1-y0
        p=[-dx,dx,-dy,dy]
        q=[x0-x_min,x_max-x0,y0-y_min,y_max-y0]
        u_in,u_out=0,1
        for i in range(4):
            if p[i]==0:
                if q[i]<0:
                    return result
            elif p[i]<0:
                u_in=max(u_in,q[i]/p[i])
            else:
                u_out=min(u_out,q[i]/p[i])
                
            if u_in>u_out:
                return result
        
        result.append((int(x0+u_in*dx),int(y0+u_in*dy)))
        result.append((int(x0+u_out*dx),int(y0+u_out*dy)))
        return result
    
   