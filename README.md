# SVM-gesture  
Motion detection of gesture sensor (APDS9960) by using machine learning (Support Vector Machine).  
Original library can detect 6motions(not using machine learning).
<https://www.sparkfun.com/products/12787>

Refered page tried to detect 10 motions by using machine learning.       
But failed to scaling fetched data and didn't optimize hyper parameter of SVM(use linear-SVM).  
(but thanks too much this previous research)
<https://github.com/flaket/gesture-machine-learning>

Also I modified above problem,and add GUI to convenient controll.
This can detect 14 motions.

AVR refered:<http://makezine.jp/blog/2015/10/apds-9960.html>
#how to use
1.Write gesture_sensing.ino to your AVR or Arduino,use modified library uploaded.  
2.Adjust "COM port" in gesture_detect_ML.py,and compile below.  
`python gesture_detect_ML.py`

<img src="picture/gesture_GUI.jpg" width="320px">
3.If you want to add original motion,use below code to fetch data.
`python window_gesture_fin.py`

<img src="picture/gesture_window.png" width="320px">
