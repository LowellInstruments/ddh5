# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'designer_main.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QFrame, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QTabWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(818, 498)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tabs = QTabWidget(self.centralwidget)
        self.tabs.setObjectName(u"tabs")
        sizePolicy.setHeightForWidth(self.tabs.sizePolicy().hasHeightForWidth())
        self.tabs.setSizePolicy(sizePolicy)
        self.tabs.setMinimumSize(QSize(800, 480))
        font = QFont()
        font.setPointSize(18)
        self.tabs.setFont(font)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        sizePolicy.setHeightForWidth(self.tab.sizePolicy().hasHeightForWidth())
        self.tab.setSizePolicy(sizePolicy)
        self.horizontalLayout_10 = QHBoxLayout(self.tab)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_5 = QSpacerItem(10, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_5)

        self.verticalLayout_main_left_column = QVBoxLayout()
        self.verticalLayout_main_left_column.setObjectName(u"verticalLayout_main_left_column")
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.lbl_boat_img = QLabel(self.tab)
        self.lbl_boat_img.setObjectName(u"lbl_boat_img")
        self.lbl_boat_img.setMinimumSize(QSize(50, 50))
        self.lbl_boat_img.setMaximumSize(QSize(50, 50))
        self.lbl_boat_img.setFrameShape(QFrame.Shape.Box)
        self.lbl_boat_img.setScaledContents(True)

        self.horizontalLayout_9.addWidget(self.lbl_boat_img)

        self.lbl_boat_txt = QLabel(self.tab)
        self.lbl_boat_txt.setObjectName(u"lbl_boat_txt")
        sizePolicy.setHeightForWidth(self.lbl_boat_txt.sizePolicy().hasHeightForWidth())
        self.lbl_boat_txt.setSizePolicy(sizePolicy)
        self.lbl_boat_txt.setFrameShape(QFrame.Shape.Box)
        self.lbl_boat_txt.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_9.addWidget(self.lbl_boat_txt)


        self.verticalLayout_main_left_column.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.lbl_brightness_img = QLabel(self.tab)
        self.lbl_brightness_img.setObjectName(u"lbl_brightness_img")
        self.lbl_brightness_img.setMinimumSize(QSize(50, 50))
        self.lbl_brightness_img.setMaximumSize(QSize(50, 50))
        self.lbl_brightness_img.setFrameShape(QFrame.Shape.Box)
        self.lbl_brightness_img.setScaledContents(True)

        self.horizontalLayout_11.addWidget(self.lbl_brightness_img)

        self.lbl_brightness_txt = QLabel(self.tab)
        self.lbl_brightness_txt.setObjectName(u"lbl_brightness_txt")
        sizePolicy.setHeightForWidth(self.lbl_brightness_txt.sizePolicy().hasHeightForWidth())
        self.lbl_brightness_txt.setSizePolicy(sizePolicy)
        self.lbl_brightness_txt.setFrameShape(QFrame.Shape.Box)
        self.lbl_brightness_txt.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_11.addWidget(self.lbl_brightness_txt)


        self.verticalLayout_main_left_column.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.lbl_gps_antenna_img = QLabel(self.tab)
        self.lbl_gps_antenna_img.setObjectName(u"lbl_gps_antenna_img")
        self.lbl_gps_antenna_img.setMinimumSize(QSize(50, 50))
        self.lbl_gps_antenna_img.setMaximumSize(QSize(50, 50))
        self.lbl_gps_antenna_img.setFrameShape(QFrame.Shape.Box)
        self.lbl_gps_antenna_img.setScaledContents(True)

        self.horizontalLayout_22.addWidget(self.lbl_gps_antenna_img)

        self.lbl_gps_antenna_txt = QLabel(self.tab)
        self.lbl_gps_antenna_txt.setObjectName(u"lbl_gps_antenna_txt")
        sizePolicy.setHeightForWidth(self.lbl_gps_antenna_txt.sizePolicy().hasHeightForWidth())
        self.lbl_gps_antenna_txt.setSizePolicy(sizePolicy)
        self.lbl_gps_antenna_txt.setFrameShape(QFrame.Shape.Box)
        self.lbl_gps_antenna_txt.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_22.addWidget(self.lbl_gps_antenna_txt)


        self.verticalLayout_main_left_column.addLayout(self.horizontalLayout_22)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.lbl_ble_antenna_img = QLabel(self.tab)
        self.lbl_ble_antenna_img.setObjectName(u"lbl_ble_antenna_img")
        self.lbl_ble_antenna_img.setMinimumSize(QSize(50, 50))
        self.lbl_ble_antenna_img.setMaximumSize(QSize(50, 50))
        self.lbl_ble_antenna_img.setFrameShape(QFrame.Shape.Box)
        self.lbl_ble_antenna_img.setScaledContents(True)

        self.horizontalLayout_12.addWidget(self.lbl_ble_antenna_img)

        self.lbl_ble_antenna_txt = QLabel(self.tab)
        self.lbl_ble_antenna_txt.setObjectName(u"lbl_ble_antenna_txt")
        sizePolicy.setHeightForWidth(self.lbl_ble_antenna_txt.sizePolicy().hasHeightForWidth())
        self.lbl_ble_antenna_txt.setSizePolicy(sizePolicy)
        self.lbl_ble_antenna_txt.setFrameShape(QFrame.Shape.Box)
        self.lbl_ble_antenna_txt.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.lbl_ble_antenna_txt.setWordWrap(True)

        self.horizontalLayout_12.addWidget(self.lbl_ble_antenna_txt)


        self.verticalLayout_main_left_column.addLayout(self.horizontalLayout_12)

        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.lbl_cell_wifi_img = QLabel(self.tab)
        self.lbl_cell_wifi_img.setObjectName(u"lbl_cell_wifi_img")
        self.lbl_cell_wifi_img.setMinimumSize(QSize(50, 50))
        self.lbl_cell_wifi_img.setMaximumSize(QSize(50, 50))
        self.lbl_cell_wifi_img.setFrameShape(QFrame.Shape.Box)
        self.lbl_cell_wifi_img.setScaledContents(True)

        self.horizontalLayout_20.addWidget(self.lbl_cell_wifi_img)

        self.lbl_cell_wifi_txt = QLabel(self.tab)
        self.lbl_cell_wifi_txt.setObjectName(u"lbl_cell_wifi_txt")
        sizePolicy.setHeightForWidth(self.lbl_cell_wifi_txt.sizePolicy().hasHeightForWidth())
        self.lbl_cell_wifi_txt.setSizePolicy(sizePolicy)
        self.lbl_cell_wifi_txt.setFrameShape(QFrame.Shape.Box)
        self.lbl_cell_wifi_txt.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_20.addWidget(self.lbl_cell_wifi_txt)


        self.verticalLayout_main_left_column.addLayout(self.horizontalLayout_20)

        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.lbl_cloud_img = QLabel(self.tab)
        self.lbl_cloud_img.setObjectName(u"lbl_cloud_img")
        self.lbl_cloud_img.setMinimumSize(QSize(50, 50))
        self.lbl_cloud_img.setMaximumSize(QSize(50, 50))
        self.lbl_cloud_img.setFrameShape(QFrame.Shape.Box)
        self.lbl_cloud_img.setScaledContents(True)

        self.horizontalLayout_21.addWidget(self.lbl_cloud_img)

        self.lbl_cloud_txt = QLabel(self.tab)
        self.lbl_cloud_txt.setObjectName(u"lbl_cloud_txt")
        sizePolicy.setHeightForWidth(self.lbl_cloud_txt.sizePolicy().hasHeightForWidth())
        self.lbl_cloud_txt.setSizePolicy(sizePolicy)
        self.lbl_cloud_txt.setFrameShape(QFrame.Shape.Box)
        self.lbl_cloud_txt.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_21.addWidget(self.lbl_cloud_txt)


        self.verticalLayout_main_left_column.addLayout(self.horizontalLayout_21)

        self.horizontalLayout_24 = QHBoxLayout()
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.lbl_last_dl_img = QLabel(self.tab)
        self.lbl_last_dl_img.setObjectName(u"lbl_last_dl_img")
        self.lbl_last_dl_img.setMinimumSize(QSize(50, 50))
        self.lbl_last_dl_img.setMaximumSize(QSize(50, 50))
        self.lbl_last_dl_img.setFrameShape(QFrame.Shape.Box)
        self.lbl_last_dl_img.setScaledContents(True)

        self.horizontalLayout_24.addWidget(self.lbl_last_dl_img)

        self.lbl_last_dl_txt = QLabel(self.tab)
        self.lbl_last_dl_txt.setObjectName(u"lbl_last_dl_txt")
        sizePolicy.setHeightForWidth(self.lbl_last_dl_txt.sizePolicy().hasHeightForWidth())
        self.lbl_last_dl_txt.setSizePolicy(sizePolicy)
        self.lbl_last_dl_txt.setFrameShape(QFrame.Shape.Box)
        self.lbl_last_dl_txt.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_24.addWidget(self.lbl_last_dl_txt)


        self.verticalLayout_main_left_column.addLayout(self.horizontalLayout_24)

        self.lbl_date_txt = QLabel(self.tab)
        self.lbl_date_txt.setObjectName(u"lbl_date_txt")
        sizePolicy.setHeightForWidth(self.lbl_date_txt.sizePolicy().hasHeightForWidth())
        self.lbl_date_txt.setSizePolicy(sizePolicy)
        self.lbl_date_txt.setFrameShape(QFrame.Shape.Box)
        self.lbl_date_txt.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.lbl_date_txt.setWordWrap(True)

        self.verticalLayout_main_left_column.addWidget(self.lbl_date_txt)

        self.verticalLayout_main_left_column.setStretch(0, 1)
        self.verticalLayout_main_left_column.setStretch(3, 1)
        self.verticalLayout_main_left_column.setStretch(4, 1)
        self.verticalLayout_main_left_column.setStretch(5, 1)
        self.verticalLayout_main_left_column.setStretch(7, 1)

        self.horizontalLayout_4.addLayout(self.verticalLayout_main_left_column)

        self.horizontalSpacer_6 = QSpacerItem(10, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_6)

        self.verticalLayout_main_right_column = QVBoxLayout()
        self.verticalLayout_main_right_column.setObjectName(u"verticalLayout_main_right_column")
        self.lbl_ble_txt = QLabel(self.tab)
        self.lbl_ble_txt.setObjectName(u"lbl_ble_txt")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lbl_ble_txt.sizePolicy().hasHeightForWidth())
        self.lbl_ble_txt.setSizePolicy(sizePolicy1)
        font1 = QFont()
        font1.setPointSize(36)
        font1.setBold(False)
        self.lbl_ble_txt.setFont(font1)
        self.lbl_ble_txt.setFrameShape(QFrame.Shape.Box)
        self.lbl_ble_txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_ble_txt.setWordWrap(True)

        self.verticalLayout_main_right_column.addWidget(self.lbl_ble_txt)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.lbl_testmode = QLabel(self.tab)
        self.lbl_testmode.setObjectName(u"lbl_testmode")
        self.lbl_testmode.setMaximumSize(QSize(100, 16777215))
        font2 = QFont()
        font2.setPointSize(18)
        font2.setBold(True)
        self.lbl_testmode.setFont(font2)
        self.lbl_testmode.setAutoFillBackground(False)
        self.lbl_testmode.setStyleSheet(u"background-color: pink")
        self.lbl_testmode.setTextFormat(Qt.TextFormat.PlainText)
        self.lbl_testmode.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_8.addWidget(self.lbl_testmode)

        self.lbl_ble_img = QLabel(self.tab)
        self.lbl_ble_img.setObjectName(u"lbl_ble_img")
        sizePolicy1.setHeightForWidth(self.lbl_ble_img.sizePolicy().hasHeightForWidth())
        self.lbl_ble_img.setSizePolicy(sizePolicy1)
        self.lbl_ble_img.setMaximumSize(QSize(300, 300))
        self.lbl_ble_img.setFont(font1)
        self.lbl_ble_img.setFrameShape(QFrame.Shape.Box)
        self.lbl_ble_img.setPixmap(QPixmap(u"res/img_info_blue.png"))
        self.lbl_ble_img.setScaledContents(True)
        self.lbl_ble_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_ble_img.setWordWrap(True)

        self.horizontalLayout_8.addWidget(self.lbl_ble_img)

        self.lbl_summary_dl = QLabel(self.tab)
        self.lbl_summary_dl.setObjectName(u"lbl_summary_dl")
        self.lbl_summary_dl.setMaximumSize(QSize(200, 16777215))
        font3 = QFont()
        font3.setPointSize(14)
        font3.setBold(False)
        self.lbl_summary_dl.setFont(font3)
        self.lbl_summary_dl.setAutoFillBackground(False)
        self.lbl_summary_dl.setStyleSheet(u"")
        self.lbl_summary_dl.setFrameShape(QFrame.Shape.Box)
        self.lbl_summary_dl.setTextFormat(Qt.TextFormat.PlainText)
        self.lbl_summary_dl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_8.addWidget(self.lbl_summary_dl)

        self.horizontalLayout_8.setStretch(0, 1)
        self.horizontalLayout_8.setStretch(1, 3)
        self.horizontalLayout_8.setStretch(2, 2)

        self.verticalLayout_main_right_column.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setSpacing(6)
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.horizontalSpacer_18 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_23.addItem(self.horizontalSpacer_18)

        self.bar_dl = QProgressBar(self.tab)
        self.bar_dl.setObjectName(u"bar_dl")
        sizePolicy.setHeightForWidth(self.bar_dl.sizePolicy().hasHeightForWidth())
        self.bar_dl.setSizePolicy(sizePolicy)
        self.bar_dl.setMaximumSize(QSize(16777215, 50))
        self.bar_dl.setValue(24)

        self.horizontalLayout_23.addWidget(self.bar_dl)

        self.horizontalSpacer_19 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_23.addItem(self.horizontalSpacer_19)

        self.horizontalLayout_23.setStretch(0, 1)
        self.horizontalLayout_23.setStretch(1, 5)
        self.horizontalLayout_23.setStretch(2, 1)

        self.verticalLayout_main_right_column.addLayout(self.horizontalLayout_23)

        self.verticalLayout_main_right_column.setStretch(0, 1)
        self.verticalLayout_main_right_column.setStretch(1, 5)
        self.verticalLayout_main_right_column.setStretch(2, 1)

        self.horizontalLayout_4.addLayout(self.verticalLayout_main_right_column)

        self.horizontalSpacer_13 = QSpacerItem(10, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_13)

        self.horizontalLayout_4.setStretch(1, 1)
        self.horizontalLayout_4.setStretch(3, 3)

        self.horizontalLayout_10.addLayout(self.horizontalLayout_4)

        self.tabs.addTab(self.tab, "")
        self.tab_setup = QWidget()
        self.tab_setup.setObjectName(u"tab_setup")
        self.horizontalLayout_6 = QHBoxLayout(self.tab_setup)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(18, -1, 18, -1)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.btn_see_all = QPushButton(self.tab_setup)
        self.btn_see_all.setObjectName(u"btn_see_all")
        self.btn_see_all.setMaximumSize(QSize(75, 16777215))

        self.horizontalLayout_3.addWidget(self.btn_see_all)

        self.btn_see_cur = QPushButton(self.tab_setup)
        self.btn_see_cur.setObjectName(u"btn_see_cur")

        self.horizontalLayout_3.addWidget(self.btn_see_cur)

        self.btn_known_clear = QPushButton(self.tab_setup)
        self.btn_known_clear.setObjectName(u"btn_known_clear")
        self.btn_known_clear.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout_3.addWidget(self.btn_known_clear)

        self.line_sn = QLineEdit(self.tab_setup)
        self.line_sn.setObjectName(u"line_sn")
        self.line_sn.setMaxLength(7)
        self.line_sn.setClearButtonEnabled(False)

        self.horizontalLayout_3.addWidget(self.line_sn)

        self.horizontalLayout_3.setStretch(0, 2)
        self.horizontalLayout_3.setStretch(1, 2)
        self.horizontalLayout_3.setStretch(2, 1)
        self.horizontalLayout_3.setStretch(3, 2)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.lst_mac_org = QListWidget(self.tab_setup)
        self.lst_mac_org.setObjectName(u"lst_mac_org")
        font4 = QFont()
        font4.setFamilies([u"Open Sans"])
        font4.setPointSize(18)
        self.lst_mac_org.setFont(font4)
        self.lst_mac_org.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.verticalLayout.addWidget(self.lst_mac_org)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_3)

        self.btn_arrow = QPushButton(self.tab_setup)
        self.btn_arrow.setObjectName(u"btn_arrow")

        self.horizontalLayout_5.addWidget(self.btn_arrow)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_4)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.lst_mac_dst = QListWidget(self.tab_setup)
        self.lst_mac_dst.setObjectName(u"lst_mac_dst")

        self.verticalLayout.addWidget(self.lst_mac_dst)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 10)
        self.verticalLayout.setStretch(2, 1)
        self.verticalLayout.setStretch(3, 10)

        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.horizontalSpacer_2 = QSpacerItem(144, 397, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, -1, 6, 6)
        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.btn_load_current = QPushButton(self.tab_setup)
        self.btn_load_current.setObjectName(u"btn_load_current")

        self.gridLayout_4.addWidget(self.btn_load_current, 0, 1, 1, 1)

        self.label_3 = QLabel(self.tab_setup)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_4.addWidget(self.label_3, 2, 0, 1, 1)

        self.label_11 = QLabel(self.tab_setup)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout_4.addWidget(self.label_11, 5, 0, 1, 1)

        self.cb_skip_in_port = QComboBox(self.tab_setup)
        self.cb_skip_in_port.setObjectName(u"cb_skip_in_port")

        self.gridLayout_4.addWidget(self.cb_skip_in_port, 5, 1, 1, 1)

        self.label_8 = QLabel(self.tab_setup)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_4.addWidget(self.label_8, 4, 0, 1, 1)

        self.label_5 = QLabel(self.tab_setup)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_4.addWidget(self.label_5, 0, 0, 1, 1)

        self.label = QLabel(self.tab_setup)
        self.label.setObjectName(u"label")

        self.gridLayout_4.addWidget(self.label, 1, 0, 1, 1)

        self.cb_s3_uplink_type = QComboBox(self.tab_setup)
        self.cb_s3_uplink_type.setObjectName(u"cb_s3_uplink_type")

        self.gridLayout_4.addWidget(self.cb_s3_uplink_type, 4, 1, 1, 1)

        self.lne_forget = QLineEdit(self.tab_setup)
        self.lne_forget.setObjectName(u"lne_forget")

        self.gridLayout_4.addWidget(self.lne_forget, 2, 1, 1, 1)

        self.label_4 = QLabel(self.tab_setup)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_4.addWidget(self.label_4, 6, 0, 1, 1)

        self.lne_vessel = QLineEdit(self.tab_setup)
        self.lne_vessel.setObjectName(u"lne_vessel")

        self.gridLayout_4.addWidget(self.lne_vessel, 1, 1, 1, 1)

        self.label_2 = QLabel(self.tab_setup)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_4.addWidget(self.label_2, 3, 0, 1, 1)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.btn_close_wo_save = QPushButton(self.tab_setup)
        self.btn_close_wo_save.setObjectName(u"btn_close_wo_save")

        self.horizontalLayout_15.addWidget(self.btn_close_wo_save)

        self.btn_setup_apply = QPushButton(self.tab_setup)
        self.btn_setup_apply.setObjectName(u"btn_setup_apply")

        self.horizontalLayout_15.addWidget(self.btn_setup_apply)

        self.horizontalLayout_15.setStretch(0, 1)
        self.horizontalLayout_15.setStretch(1, 1)

        self.gridLayout_4.addLayout(self.horizontalLayout_15, 6, 1, 1, 1)

        self.cbox_gear_type = QComboBox(self.tab_setup)
        self.cbox_gear_type.setObjectName(u"cbox_gear_type")

        self.gridLayout_4.addWidget(self.cbox_gear_type, 3, 1, 1, 1)

        self.gridLayout_4.setColumnStretch(0, 1)

        self.verticalLayout_2.addLayout(self.gridLayout_4)

        self.lbl_setup_result = QLabel(self.tab_setup)
        self.lbl_setup_result.setObjectName(u"lbl_setup_result")
        self.lbl_setup_result.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout_2.addWidget(self.lbl_setup_result)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_3)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.btn_dl_purge = QPushButton(self.tab_setup)
        self.btn_dl_purge.setObjectName(u"btn_dl_purge")

        self.horizontalLayout_16.addWidget(self.btn_dl_purge)

        self.btn_his_purge = QPushButton(self.tab_setup)
        self.btn_his_purge.setObjectName(u"btn_his_purge")

        self.horizontalLayout_16.addWidget(self.btn_his_purge)


        self.verticalLayout_2.addLayout(self.horizontalLayout_16)

        self.verticalLayout_2.setStretch(0, 7)
        self.verticalLayout_2.setStretch(1, 1)
        self.verticalLayout_2.setStretch(2, 1)
        self.verticalLayout_2.setStretch(3, 1)

        self.horizontalLayout_2.addLayout(self.verticalLayout_2)

        self.horizontalLayout_2.setStretch(0, 12)
        self.horizontalLayout_2.setStretch(1, 1)
        self.horizontalLayout_2.setStretch(2, 10)

        self.horizontalLayout_6.addLayout(self.horizontalLayout_2)

        self.tabs.addTab(self.tab_setup, "")
        self.tab_note = QWidget()
        self.tab_note.setObjectName(u"tab_note")
        self.verticalLayout_6 = QVBoxLayout(self.tab_note)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer_8, 0, 1, 1, 1)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer_7, 0, 4, 1, 1)

        self.btn_note_no = QPushButton(self.tab_note)
        self.btn_note_no.setObjectName(u"btn_note_no")

        self.gridLayout_3.addWidget(self.btn_note_no, 7, 2, 1, 1)

        self.btn_note_yes = QPushButton(self.tab_note)
        self.btn_note_yes.setObjectName(u"btn_note_yes")

        self.gridLayout_3.addWidget(self.btn_note_yes, 3, 2, 1, 1)

        self.lbl_note = QLabel(self.tab_note)
        self.lbl_note.setObjectName(u"lbl_note")
        self.lbl_note.setStyleSheet(u"color: rgb(239, 41, 41);\n"
"font: 19pt \"DejaVu Sans\";")
        self.lbl_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_note.setWordWrap(True)

        self.gridLayout_3.addWidget(self.lbl_note, 1, 1, 1, 3)

        self.verticalSpacer_10 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_10, 4, 2, 1, 1)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer_10, 0, 3, 1, 1)

        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_7, 6, 2, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer, 0, 0, 1, 1)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_5, 2, 2, 1, 1)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_6, 0, 2, 1, 1)

        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer_8, 8, 2, 1, 1)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.btn_note_yes_specific = QPushButton(self.tab_note)
        self.btn_note_yes_specific.setObjectName(u"btn_note_yes_specific")

        self.horizontalLayout_14.addWidget(self.btn_note_yes_specific)

        self.lst_macs_note_tab = QListWidget(self.tab_note)
        self.lst_macs_note_tab.setObjectName(u"lst_macs_note_tab")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.lst_macs_note_tab.sizePolicy().hasHeightForWidth())
        self.lst_macs_note_tab.setSizePolicy(sizePolicy2)
        self.lst_macs_note_tab.setMaximumSize(QSize(16777215, 150))
        self.lst_macs_note_tab.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.horizontalLayout_14.addWidget(self.lst_macs_note_tab)


        self.gridLayout_3.addLayout(self.horizontalLayout_14, 5, 2, 1, 1)

        self.gridLayout_3.setRowStretch(0, 1)
        self.gridLayout_3.setRowStretch(1, 1)
        self.gridLayout_3.setRowStretch(2, 1)
        self.gridLayout_3.setRowStretch(3, 1)
        self.gridLayout_3.setRowStretch(4, 1)
        self.gridLayout_3.setRowStretch(5, 1)
        self.gridLayout_3.setRowStretch(6, 1)
        self.gridLayout_3.setRowStretch(7, 1)
        self.gridLayout_3.setRowStretch(8, 1)
        self.gridLayout_3.setColumnStretch(0, 1)
        self.gridLayout_3.setColumnStretch(1, 1)
        self.gridLayout_3.setColumnStretch(2, 4)
        self.gridLayout_3.setColumnStretch(3, 1)
        self.gridLayout_3.setColumnStretch(4, 1)

        self.verticalLayout_6.addLayout(self.gridLayout_3)

        self.tabs.addTab(self.tab_note, "")
        self.tab_more_info = QWidget()
        self.tab_more_info.setObjectName(u"tab_more_info")
        self.verticalLayout_3 = QVBoxLayout(self.tab_more_info)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.verticalSpacer_9 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.gridLayout_5.addItem(self.verticalSpacer_9, 0, 1, 1, 1)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_5.addItem(self.horizontalSpacer_9, 1, 0, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(6, -1, 6, -1)
        self.lbl_uptime = QLabel(self.tab_more_info)
        self.lbl_uptime.setObjectName(u"lbl_uptime")
        self.lbl_uptime.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_7.addWidget(self.lbl_uptime)

        self.lbl_cnv = QLabel(self.tab_more_info)
        self.lbl_cnv.setObjectName(u"lbl_cnv")
        self.lbl_cnv.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_7.addWidget(self.lbl_cnv)

        self.btn_sms = QPushButton(self.tab_more_info)
        self.btn_sms.setObjectName(u"btn_sms")
        self.btn_sms.setEnabled(False)

        self.horizontalLayout_7.addWidget(self.btn_sms)

        self.lbl_commit = QLabel(self.tab_more_info)
        self.lbl_commit.setObjectName(u"lbl_commit")
        sizePolicy.setHeightForWidth(self.lbl_commit.sizePolicy().hasHeightForWidth())
        self.lbl_commit.setSizePolicy(sizePolicy)
        self.lbl_commit.setFrameShape(QFrame.Shape.NoFrame)
        self.lbl_commit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_commit.setWordWrap(True)

        self.horizontalLayout_7.addWidget(self.lbl_commit)

        self.horizontalLayout_7.setStretch(0, 1)
        self.horizontalLayout_7.setStretch(1, 1)
        self.horizontalLayout_7.setStretch(2, 1)
        self.horizontalLayout_7.setStretch(3, 1)

        self.gridLayout_5.addLayout(self.horizontalLayout_7, 3, 0, 1, 3)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.lbl_gps = QLabel(self.tab_more_info)
        self.lbl_gps.setObjectName(u"lbl_gps")
        self.lbl_gps.setFrameShape(QFrame.Shape.NoFrame)
        self.lbl_gps.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_gps.setWordWrap(True)

        self.horizontalLayout_13.addWidget(self.lbl_gps)

        self.lbl_gps_sat = QLabel(self.tab_more_info)
        self.lbl_gps_sat.setObjectName(u"lbl_gps_sat")
        self.lbl_gps_sat.setFrameShape(QFrame.Shape.NoFrame)
        self.lbl_gps_sat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_gps_sat.setWordWrap(True)

        self.horizontalLayout_13.addWidget(self.lbl_gps_sat)

        self.lbl_box_sn = QLabel(self.tab_more_info)
        self.lbl_box_sn.setObjectName(u"lbl_box_sn")
        self.lbl_box_sn.setFrameShape(QFrame.Shape.NoFrame)
        self.lbl_box_sn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_box_sn.setWordWrap(True)

        self.horizontalLayout_13.addWidget(self.lbl_box_sn)


        self.gridLayout_5.addLayout(self.horizontalLayout_13, 2, 1, 1, 1)

        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_5.addItem(self.horizontalSpacer_11, 1, 2, 1, 1)

        self.tbl_his = QTableWidget(self.tab_more_info)
        if (self.tbl_his.columnCount() < 3):
            self.tbl_his.setColumnCount(3)
        if (self.tbl_his.rowCount() < 25):
            self.tbl_his.setRowCount(25)
        self.tbl_his.setObjectName(u"tbl_his")
        sizePolicy.setHeightForWidth(self.tbl_his.sizePolicy().hasHeightForWidth())
        self.tbl_his.setSizePolicy(sizePolicy)
        self.tbl_his.setStyleSheet(u"font: 12pt \"DejaVu Sans\";")
        self.tbl_his.setFrameShape(QFrame.Shape.Box)
        self.tbl_his.setFrameShadow(QFrame.Shadow.Plain)
        self.tbl_his.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tbl_his.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_his.setTabKeyNavigation(False)
        self.tbl_his.setDragDropOverwriteMode(False)
        self.tbl_his.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tbl_his.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl_his.setSortingEnabled(True)
        self.tbl_his.setWordWrap(False)
        self.tbl_his.setRowCount(25)
        self.tbl_his.setColumnCount(3)
        self.tbl_his.horizontalHeader().setHighlightSections(True)
        self.tbl_his.verticalHeader().setVisible(False)

        self.gridLayout_5.addWidget(self.tbl_his, 1, 1, 1, 1)

        self.gridLayout_5.setRowStretch(0, 1)
        self.gridLayout_5.setRowStretch(1, 4)
        self.gridLayout_5.setRowStretch(2, 1)
        self.gridLayout_5.setRowStretch(3, 1)
        self.gridLayout_5.setColumnStretch(0, 1)
        self.gridLayout_5.setColumnStretch(1, 10)
        self.gridLayout_5.setColumnStretch(2, 1)

        self.verticalLayout_3.addLayout(self.gridLayout_5)

        self.tabs.addTab(self.tab_more_info, "")
        self.tab_advanced = QWidget()
        self.tab_advanced.setObjectName(u"tab_advanced")
        self.verticalLayout_5 = QVBoxLayout(self.tab_advanced)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.verticalSpacer_11 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_6.addItem(self.verticalSpacer_11, 0, 1, 1, 1)

        self.chk_b_maps = QCheckBox(self.tab_advanced)
        self.chk_b_maps.setObjectName(u"chk_b_maps")

        self.gridLayout_6.addWidget(self.chk_b_maps, 2, 1, 1, 1)

        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_6.addItem(self.horizontalSpacer_12, 0, 0, 1, 1)

        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.label_6 = QLabel(self.tab_advanced)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFont(font)
        self.label_6.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_17.addWidget(self.label_6)

        self.cbox_scf = QComboBox(self.tab_advanced)
        self.cbox_scf.setObjectName(u"cbox_scf")

        self.horizontalLayout_17.addWidget(self.cbox_scf)


        self.gridLayout_6.addLayout(self.horizontalLayout_17, 4, 1, 1, 1)

        self.btn_adv_purge_lo = QPushButton(self.tab_advanced)
        self.btn_adv_purge_lo.setObjectName(u"btn_adv_purge_lo")

        self.gridLayout_6.addWidget(self.btn_adv_purge_lo, 6, 1, 1, 1)

        self.horizontalSpacer_22 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_6.addItem(self.horizontalSpacer_22, 0, 2, 1, 1)

        self.chk_rerun = QCheckBox(self.tab_advanced)
        self.chk_rerun.setObjectName(u"chk_rerun")

        self.gridLayout_6.addWidget(self.chk_rerun, 1, 1, 1, 1)

        self.verticalSpacer_13 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_6.addItem(self.verticalSpacer_13, 7, 1, 1, 1)

        self.chk_ow = QCheckBox(self.tab_advanced)
        self.chk_ow.setObjectName(u"chk_ow")

        self.gridLayout_6.addWidget(self.chk_ow, 3, 1, 1, 1)


        self.verticalLayout_5.addLayout(self.gridLayout_6)

        self.tabs.addTab(self.tab_advanced, "")
        self.tab_graph = QWidget()
        self.tab_graph.setObjectName(u"tab_graph")
        self.verticalLayout_7 = QVBoxLayout(self.tab_graph)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.lay_g_h1 = QHBoxLayout()
        self.lay_g_h1.setSpacing(18)
        self.lay_g_h1.setObjectName(u"lay_g_h1")
        self.btn_g_reset = QPushButton(self.tab_graph)
        self.btn_g_reset.setObjectName(u"btn_g_reset")

        self.lay_g_h1.addWidget(self.btn_g_reset)

        self.cb_g_paint_zones = QComboBox(self.tab_graph)
        self.cb_g_paint_zones.addItem("")
        self.cb_g_paint_zones.addItem("")
        self.cb_g_paint_zones.setObjectName(u"cb_g_paint_zones")

        self.lay_g_h1.addWidget(self.cb_g_paint_zones)

        self.cb_g_switch_tp = QComboBox(self.tab_graph)
        self.cb_g_switch_tp.addItem("")
        self.cb_g_switch_tp.addItem("")
        self.cb_g_switch_tp.setObjectName(u"cb_g_switch_tp")
        self.cb_g_switch_tp.setMaximumSize(QSize(110, 16777215))

        self.lay_g_h1.addWidget(self.cb_g_switch_tp)

        self.cb_g_sn = QComboBox(self.tab_graph)
        self.cb_g_sn.setObjectName(u"cb_g_sn")
        self.cb_g_sn.setMaximumSize(QSize(200, 16777215))

        self.lay_g_h1.addWidget(self.cb_g_sn)

        self.label_9 = QLabel(self.tab_graph)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.lay_g_h1.addWidget(self.label_9)

        self.cb_g_cycle_haul = QComboBox(self.tab_graph)
        self.cb_g_cycle_haul.addItem("")
        self.cb_g_cycle_haul.addItem("")
        self.cb_g_cycle_haul.addItem("")
        self.cb_g_cycle_haul.setObjectName(u"cb_g_cycle_haul")

        self.lay_g_h1.addWidget(self.cb_g_cycle_haul)

        self.btn_g_next_haul = QPushButton(self.tab_graph)
        self.btn_g_next_haul.setObjectName(u"btn_g_next_haul")
        self.btn_g_next_haul.setMaximumSize(QSize(100, 16777215))

        self.lay_g_h1.addWidget(self.btn_g_next_haul)

        self.lay_g_h1.setStretch(0, 1)
        self.lay_g_h1.setStretch(1, 2)
        self.lay_g_h1.setStretch(2, 1)
        self.lay_g_h1.setStretch(3, 2)
        self.lay_g_h1.setStretch(4, 1)
        self.lay_g_h1.setStretch(5, 1)
        self.lay_g_h1.setStretch(6, 1)

        self.verticalLayout_7.addLayout(self.lay_g_h1)

        self.lay_g_h1_2 = QHBoxLayout()
        self.lay_g_h1_2.setSpacing(0)
        self.lay_g_h1_2.setObjectName(u"lay_g_h1_2")
        self.lbl_graph_busy = QLabel(self.tab_graph)
        self.lbl_graph_busy.setObjectName(u"lbl_graph_busy")
        self.lbl_graph_busy.setMaximumSize(QSize(9000, 200))
        font5 = QFont()
        font5.setPointSize(48)
        font5.setBold(False)
        font5.setUnderline(False)
        font5.setStrikeOut(False)
        font5.setKerning(True)
        self.lbl_graph_busy.setFont(font5)
        self.lbl_graph_busy.setStyleSheet(u"color: rgb(0, 0, 255)")
        self.lbl_graph_busy.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lay_g_h1_2.addWidget(self.lbl_graph_busy)


        self.verticalLayout_7.addLayout(self.lay_g_h1_2)

        self.lay_g_h2 = QHBoxLayout()
        self.lay_g_h2.setObjectName(u"lay_g_h2")
        self.lay_g_h2.setContentsMargins(-1, 3, -1, -1)

        self.verticalLayout_7.addLayout(self.lay_g_h2)

        self.verticalLayout_7.setStretch(0, 1)
        self.verticalLayout_7.setStretch(2, 8)
        self.tabs.addTab(self.tab_graph, "")
        self.tab_map = QWidget()
        self.tab_map.setObjectName(u"tab_map")
        self.verticalLayout_4 = QVBoxLayout(self.tab_map)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.lay_g_h2_3 = QHBoxLayout()
        self.lay_g_h2_3.setObjectName(u"lay_g_h2_3")
        self.lay_g_h2_3.setContentsMargins(-1, 3, -1, -1)
        self.horizontalSpacer_23 = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.lay_g_h2_3.addItem(self.horizontalSpacer_23)

        self.lbl_map = QLabel(self.tab_map)
        self.lbl_map.setObjectName(u"lbl_map")
        self.lbl_map.setScaledContents(True)

        self.lay_g_h2_3.addWidget(self.lbl_map)

        self.btn_map_next = QPushButton(self.tab_map)
        self.btn_map_next.setObjectName(u"btn_map_next")
        self.btn_map_next.setMaximumSize(QSize(50, 16777215))
        font6 = QFont()
        font6.setPointSize(22)
        font6.setItalic(False)
        self.btn_map_next.setFont(font6)

        self.lay_g_h2_3.addWidget(self.btn_map_next)

        self.horizontalSpacer_24 = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.lay_g_h2_3.addItem(self.horizontalSpacer_24)

        self.lay_g_h2_3.setStretch(0, 1)
        self.lay_g_h2_3.setStretch(1, 10)
        self.lay_g_h2_3.setStretch(2, 1)
        self.lay_g_h2_3.setStretch(3, 1)

        self.verticalLayout_4.addLayout(self.lay_g_h2_3)

        self.verticalLayout_4.setStretch(0, 10)
        self.tabs.addTab(self.tab_map, "")

        self.horizontalLayout.addWidget(self.tabs)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.lbl_boat_img.setText("")
        self.lbl_boat_txt.setText("")
        self.lbl_brightness_img.setText("")
        self.lbl_brightness_txt.setText("")
        self.lbl_gps_antenna_img.setText("")
        self.lbl_gps_antenna_txt.setText("")
        self.lbl_ble_antenna_img.setText("")
        self.lbl_ble_antenna_txt.setText("")
        self.lbl_cell_wifi_img.setText("")
        self.lbl_cell_wifi_txt.setText("")
        self.lbl_cloud_img.setText("")
        self.lbl_cloud_txt.setText("")
        self.lbl_last_dl_img.setText("")
        self.lbl_last_dl_txt.setText("")
        self.lbl_date_txt.setText("")
        self.lbl_ble_txt.setText("")
        self.lbl_testmode.setText(QCoreApplication.translate("MainWindow", u"TEST", None))
        self.lbl_ble_img.setText("")
        self.bar_dl.setFormat(QCoreApplication.translate("MainWindow", u"%p %", None))
        self.tabs.setTabText(self.tabs.indexOf(self.tab), QCoreApplication.translate("MainWindow", u" Information", None))
        self.btn_see_all.setText(QCoreApplication.translate("MainWindow", u"all", None))
        self.btn_see_cur.setText(QCoreApplication.translate("MainWindow", u"current", None))
        self.btn_known_clear.setText(QCoreApplication.translate("MainWindow", u"x", None))
        self.btn_arrow.setText(QCoreApplication.translate("MainWindow", u"\u2193", None))
        self.btn_load_current.setText(QCoreApplication.translate("MainWindow", u"load", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"forget (s)", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"skip in port", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"S3 uplink", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"load values", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"vessel", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"save values", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"gear type", None))
        self.btn_close_wo_save.setText(QCoreApplication.translate("MainWindow", u"cancel", None))
        self.btn_setup_apply.setText(QCoreApplication.translate("MainWindow", u"save", None))
        self.lbl_setup_result.setText("")
        self.btn_dl_purge.setText(QCoreApplication.translate("MainWindow", u"purge files", None))
        self.btn_his_purge.setText(QCoreApplication.translate("MainWindow", u"purge history", None))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_setup), QCoreApplication.translate("MainWindow", u" Setup", None))
        self.btn_note_no.setText(QCoreApplication.translate("MainWindow", u"cancel", None))
        self.btn_note_yes.setText(QCoreApplication.translate("MainWindow", u"OK", None))
        self.lbl_note.setText(QCoreApplication.translate("MainWindow", u"Skipping this logger until a valid GPS fix is obtained", None))
        self.btn_note_yes_specific.setText(QCoreApplication.translate("MainWindow", u"selective OK", None))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_note), QCoreApplication.translate("MainWindow", u"Note", None))
        self.lbl_uptime.setText("")
        self.lbl_cnv.setText("")
        self.btn_sms.setText(QCoreApplication.translate("MainWindow", u"tech support", None))
        self.lbl_commit.setText("")
        self.lbl_gps.setText("")
        self.lbl_gps_sat.setText("")
        self.lbl_box_sn.setText("")
        self.tabs.setTabText(self.tabs.indexOf(self.tab_more_info), QCoreApplication.translate("MainWindow", u" Details", None))
        self.chk_b_maps.setText(QCoreApplication.translate("MainWindow", u" Show bottom Temperature maps", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"TDO profiling", None))
        self.btn_adv_purge_lo.setText(QCoreApplication.translate("MainWindow", u"Open loggers lock-out tab", None))
        self.chk_rerun.setText(QCoreApplication.translate("MainWindow", u" Run logger after download", None))
        self.chk_ow.setText(QCoreApplication.translate("MainWindow", u" Graphs show out-of-water data", None))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_advanced), QCoreApplication.translate("MainWindow", u" Advanced", None))
        self.btn_g_reset.setText(QCoreApplication.translate("MainWindow", u"reset", None))
        self.cb_g_paint_zones.setItemText(0, QCoreApplication.translate("MainWindow", u"zones ON", None))
        self.cb_g_paint_zones.setItemText(1, QCoreApplication.translate("MainWindow", u"zones OFF", None))

        self.cb_g_switch_tp.setItemText(0, QCoreApplication.translate("MainWindow", u"x-time", None))
        self.cb_g_switch_tp.setItemText(1, QCoreApplication.translate("MainWindow", u"x-Temp", None))

        self.cb_g_switch_tp.setCurrentText(QCoreApplication.translate("MainWindow", u"x-time", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"hauls", None))
        self.cb_g_cycle_haul.setItemText(0, QCoreApplication.translate("MainWindow", u"last", None))
        self.cb_g_cycle_haul.setItemText(1, QCoreApplication.translate("MainWindow", u"all", None))
        self.cb_g_cycle_haul.setItemText(2, QCoreApplication.translate("MainWindow", u"single", None))

        self.btn_g_next_haul.setText(QCoreApplication.translate("MainWindow", u"<", None))
        self.lbl_graph_busy.setText(QCoreApplication.translate("MainWindow", u"LOADING...", None))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_graph), QCoreApplication.translate("MainWindow", u" Graphs", None))
        self.lbl_map.setText("")
        self.btn_map_next.setText(QCoreApplication.translate("MainWindow", u">", None))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_map), QCoreApplication.translate("MainWindow", u" Models", None))
    # retranslateUi

