# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'meshprojectionwidget.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QSlider,
    QSpacerItem, QVBoxLayout, QWidget)

from cmlibs.widgets.basesceneviewerwidget import BaseSceneviewerWidget

class Ui_MeshProjectionWidget(object):
    def setupUi(self, MeshProjectionWidget):
        if not MeshProjectionWidget.objectName():
            MeshProjectionWidget.setObjectName(u"MeshProjectionWidget")
        MeshProjectionWidget.resize(884, 765)
        self.horizontalLayout_5 = QHBoxLayout(MeshProjectionWidget)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayoutHeader = QHBoxLayout()
        self.horizontalLayoutHeader.setObjectName(u"horizontalLayoutHeader")
        self.labelMeshProjection = QLabel(MeshProjectionWidget)
        self.labelMeshProjection.setObjectName(u"labelMeshProjection")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelMeshProjection.sizePolicy().hasHeightForWidth())
        self.labelMeshProjection.setSizePolicy(sizePolicy)

        self.horizontalLayoutHeader.addWidget(self.labelMeshProjection)

        self.labelMeshProjectionIdentifier = QLabel(MeshProjectionWidget)
        self.labelMeshProjectionIdentifier.setObjectName(u"labelMeshProjectionIdentifier")

        self.horizontalLayoutHeader.addWidget(self.labelMeshProjectionIdentifier)


        self.verticalLayout_2.addLayout(self.horizontalLayoutHeader)

        self.line = QFrame(MeshProjectionWidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_2.addWidget(self.line)

        self.groupBoxGraphics = QGroupBox(MeshProjectionWidget)
        self.groupBoxGraphics.setObjectName(u"groupBoxGraphics")
        self.verticalLayout_3 = QVBoxLayout(self.groupBoxGraphics)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.comboBoxNodeCoordinateField = QComboBox(self.groupBoxGraphics)
        self.comboBoxNodeCoordinateField.setObjectName(u"comboBoxNodeCoordinateField")

        self.gridLayout_3.addWidget(self.comboBoxNodeCoordinateField, 0, 1, 1, 1)

        self.labelNodeCoordinateField = QLabel(self.groupBoxGraphics)
        self.labelNodeCoordinateField.setObjectName(u"labelNodeCoordinateField")
        self.labelNodeCoordinateField.setMaximumSize(QSize(160, 16777215))

        self.gridLayout_3.addWidget(self.labelNodeCoordinateField, 0, 0, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout_3)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.labelDatapointCoordinateField = QLabel(self.groupBoxGraphics)
        self.labelDatapointCoordinateField.setObjectName(u"labelDatapointCoordinateField")
        self.labelDatapointCoordinateField.setMaximumSize(QSize(160, 16777215))

        self.horizontalLayout_6.addWidget(self.labelDatapointCoordinateField)

        self.comboBoxDatapointCoordinateField = QComboBox(self.groupBoxGraphics)
        self.comboBoxDatapointCoordinateField.setObjectName(u"comboBoxDatapointCoordinateField")

        self.horizontalLayout_6.addWidget(self.comboBoxDatapointCoordinateField)


        self.verticalLayout_3.addLayout(self.horizontalLayout_6)


        self.verticalLayout_2.addWidget(self.groupBoxGraphics)

        self.groupBoxProjection = QGroupBox(MeshProjectionWidget)
        self.groupBoxProjection.setObjectName(u"groupBoxProjection")
        self.verticalLayout = QVBoxLayout(self.groupBoxProjection)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.pushButtonAutoAlignPlane = QPushButton(self.groupBoxProjection)
        self.pushButtonAutoAlignPlane.setObjectName(u"pushButtonAutoAlignPlane")

        self.horizontalLayout_3.addWidget(self.pushButtonAutoAlignPlane)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_6)

        self.pushButtonProject = QPushButton(self.groupBoxProjection)
        self.pushButtonProject.setObjectName(u"pushButtonProject")

        self.horizontalLayout_3.addWidget(self.pushButtonProject)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.labelMinus180 = QLabel(self.groupBoxProjection)
        self.labelMinus180.setObjectName(u"labelMinus180")

        self.horizontalLayout_4.addWidget(self.labelMinus180)

        self.sliderFinalOrientation = QSlider(self.groupBoxProjection)
        self.sliderFinalOrientation.setObjectName(u"sliderFinalOrientation")
        self.sliderFinalOrientation.setMinimum(-180)
        self.sliderFinalOrientation.setMaximum(180)
        self.sliderFinalOrientation.setTracking(True)
        self.sliderFinalOrientation.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_4.addWidget(self.sliderFinalOrientation)

        self.labelPlus180 = QLabel(self.groupBoxProjection)
        self.labelPlus180.setObjectName(u"labelPlus180")

        self.horizontalLayout_4.addWidget(self.labelPlus180)


        self.verticalLayout.addLayout(self.horizontalLayout_4)


        self.verticalLayout_2.addWidget(self.groupBoxProjection)

        self.groupBoxVisibility = QGroupBox(MeshProjectionWidget)
        self.groupBoxVisibility.setObjectName(u"groupBoxVisibility")
        self.verticalLayout_6 = QVBoxLayout(self.groupBoxVisibility)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.checkBoxSurfacesVisibility = QCheckBox(self.groupBoxVisibility)
        self.checkBoxSurfacesVisibility.setObjectName(u"checkBoxSurfacesVisibility")
        self.checkBoxSurfacesVisibility.setChecked(True)

        self.verticalLayout_6.addWidget(self.checkBoxSurfacesVisibility)

        self.checkBoxMeshVisibility = QCheckBox(self.groupBoxVisibility)
        self.checkBoxMeshVisibility.setObjectName(u"checkBoxMeshVisibility")
        self.checkBoxMeshVisibility.setChecked(True)

        self.verticalLayout_6.addWidget(self.checkBoxMeshVisibility)

        self.checkBoxProjectedMeshVisibility = QCheckBox(self.groupBoxVisibility)
        self.checkBoxProjectedMeshVisibility.setObjectName(u"checkBoxProjectedMeshVisibility")
        self.checkBoxProjectedMeshVisibility.setEnabled(True)
        self.checkBoxProjectedMeshVisibility.setChecked(True)

        self.verticalLayout_6.addWidget(self.checkBoxProjectedMeshVisibility)

        self.checkBoxMarkersVisibility = QCheckBox(self.groupBoxVisibility)
        self.checkBoxMarkersVisibility.setObjectName(u"checkBoxMarkersVisibility")
        self.checkBoxMarkersVisibility.setChecked(True)

        self.verticalLayout_6.addWidget(self.checkBoxMarkersVisibility)

        self.checkBoxProjectedMarkersVisibility = QCheckBox(self.groupBoxVisibility)
        self.checkBoxProjectedMarkersVisibility.setObjectName(u"checkBoxProjectedMarkersVisibility")
        self.checkBoxProjectedMarkersVisibility.setChecked(True)

        self.verticalLayout_6.addWidget(self.checkBoxProjectedMarkersVisibility)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.spinBoxNodeSize = QDoubleSpinBox(self.groupBoxVisibility)
        self.spinBoxNodeSize.setObjectName(u"spinBoxNodeSize")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.spinBoxNodeSize.sizePolicy().hasHeightForWidth())
        self.spinBoxNodeSize.setSizePolicy(sizePolicy1)
        self.spinBoxNodeSize.setSingleStep(0.100000000000000)

        self.gridLayout.addWidget(self.spinBoxNodeSize, 0, 1, 1, 1)

        self.labelNodeSize = QLabel(self.groupBoxVisibility)
        self.labelNodeSize.setObjectName(u"labelNodeSize")
        sizePolicy2 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.labelNodeSize.sizePolicy().hasHeightForWidth())
        self.labelNodeSize.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.labelNodeSize, 0, 0, 1, 1)


        self.verticalLayout_6.addLayout(self.gridLayout)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.labelPlaneAlpha = QLabel(self.groupBoxVisibility)
        self.labelPlaneAlpha.setObjectName(u"labelPlaneAlpha")
        sizePolicy2.setHeightForWidth(self.labelPlaneAlpha.sizePolicy().hasHeightForWidth())
        self.labelPlaneAlpha.setSizePolicy(sizePolicy2)

        self.gridLayout_2.addWidget(self.labelPlaneAlpha, 0, 0, 1, 1)

        self.spinBoxPlaneAlpha = QDoubleSpinBox(self.groupBoxVisibility)
        self.spinBoxPlaneAlpha.setObjectName(u"spinBoxPlaneAlpha")
        self.spinBoxPlaneAlpha.setMaximum(1.000000000000000)
        self.spinBoxPlaneAlpha.setSingleStep(0.010000000000000)
        self.spinBoxPlaneAlpha.setValue(1.000000000000000)

        self.gridLayout_2.addWidget(self.spinBoxPlaneAlpha, 0, 1, 1, 1)


        self.verticalLayout_6.addLayout(self.gridLayout_2)


        self.verticalLayout_2.addWidget(self.groupBoxVisibility)

        self.groupBoxPreview = QGroupBox(MeshProjectionWidget)
        self.groupBoxPreview.setObjectName(u"groupBoxPreview")
        self.horizontalLayout_7 = QHBoxLayout(self.groupBoxPreview)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.widgetZincPreview = BaseSceneviewerWidget(self.groupBoxPreview)
        self.widgetZincPreview.setObjectName(u"widgetZincPreview")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy3.setHorizontalStretch(3)
        sizePolicy3.setVerticalStretch(1)
        sizePolicy3.setHeightForWidth(self.widgetZincPreview.sizePolicy().hasHeightForWidth())
        self.widgetZincPreview.setSizePolicy(sizePolicy3)

        self.horizontalLayout_7.addWidget(self.widgetZincPreview)


        self.verticalLayout_2.addWidget(self.groupBoxPreview)

        self.groupBoxView = QGroupBox(MeshProjectionWidget)
        self.groupBoxView.setObjectName(u"groupBoxView")
        self.horizontalLayout = QHBoxLayout(self.groupBoxView)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_4 = QSpacerItem(50, 17, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_4)

        self.pushButtonViewAll = QPushButton(self.groupBoxView)
        self.pushButtonViewAll.setObjectName(u"pushButtonViewAll")

        self.horizontalLayout.addWidget(self.pushButtonViewAll)

        self.horizontalSpacer_3 = QSpacerItem(50, 17, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)


        self.verticalLayout_2.addWidget(self.groupBoxView)

        self.groupBoxGeneral = QGroupBox(MeshProjectionWidget)
        self.groupBoxGeneral.setObjectName(u"groupBoxGeneral")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBoxGeneral)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.pushButtonContinue = QPushButton(self.groupBoxGeneral)
        self.pushButtonContinue.setObjectName(u"pushButtonContinue")

        self.horizontalLayout_2.addWidget(self.pushButtonContinue)

        self.horizontalSpacer_2 = QSpacerItem(46, 17, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addWidget(self.groupBoxGeneral)


        self.horizontalLayout_5.addLayout(self.verticalLayout_2)

        self.widgetZinc = BaseSceneviewerWidget(MeshProjectionWidget)
        self.widgetZinc.setObjectName(u"widgetZinc")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(3)
        sizePolicy4.setVerticalStretch(1)
        sizePolicy4.setHeightForWidth(self.widgetZinc.sizePolicy().hasHeightForWidth())
        self.widgetZinc.setSizePolicy(sizePolicy4)

        self.horizontalLayout_5.addWidget(self.widgetZinc)


        self.retranslateUi(MeshProjectionWidget)

        QMetaObject.connectSlotsByName(MeshProjectionWidget)
    # setupUi

    def retranslateUi(self, MeshProjectionWidget):
        MeshProjectionWidget.setWindowTitle(QCoreApplication.translate("MeshProjectionWidget", u"Mesh Projection", None))
        self.labelMeshProjection.setText(QCoreApplication.translate("MeshProjectionWidget", u"Mesh Projection - ", None))
        self.labelMeshProjectionIdentifier.setText("")
        self.groupBoxGraphics.setTitle(QCoreApplication.translate("MeshProjectionWidget", u"Graphics Coordinates", None))
        self.labelNodeCoordinateField.setText(QCoreApplication.translate("MeshProjectionWidget", u"Node coordinate Field:", None))
        self.labelDatapointCoordinateField.setText(QCoreApplication.translate("MeshProjectionWidget", u"Datapoint coordinate Field:", None))
        self.groupBoxProjection.setTitle(QCoreApplication.translate("MeshProjectionWidget", u"Projection", None))
        self.pushButtonAutoAlignPlane.setText(QCoreApplication.translate("MeshProjectionWidget", u"Auto Align Plane", None))
        self.pushButtonProject.setText(QCoreApplication.translate("MeshProjectionWidget", u"Project", None))
        self.labelMinus180.setText(QCoreApplication.translate("MeshProjectionWidget", u"-180 (deg)", None))
        self.labelPlus180.setText(QCoreApplication.translate("MeshProjectionWidget", u"180 (deg)", None))
        self.groupBoxVisibility.setTitle(QCoreApplication.translate("MeshProjectionWidget", u"Visibility", None))
        self.checkBoxSurfacesVisibility.setText(QCoreApplication.translate("MeshProjectionWidget", u"Surfaces", None))
        self.checkBoxMeshVisibility.setText(QCoreApplication.translate("MeshProjectionWidget", u"Mesh", None))
        self.checkBoxProjectedMeshVisibility.setText(QCoreApplication.translate("MeshProjectionWidget", u"Projected Mesh", None))
        self.checkBoxMarkersVisibility.setText(QCoreApplication.translate("MeshProjectionWidget", u"Markers", None))
        self.checkBoxProjectedMarkersVisibility.setText(QCoreApplication.translate("MeshProjectionWidget", u"Projected Markers", None))
        self.labelNodeSize.setText(QCoreApplication.translate("MeshProjectionWidget", u"Node Size:", None))
        self.labelPlaneAlpha.setText(QCoreApplication.translate("MeshProjectionWidget", u"Plane Alpha:", None))
        self.groupBoxPreview.setTitle(QCoreApplication.translate("MeshProjectionWidget", u"Preview", None))
        self.groupBoxView.setTitle(QCoreApplication.translate("MeshProjectionWidget", u"View", None))
        self.pushButtonViewAll.setText(QCoreApplication.translate("MeshProjectionWidget", u"View All", None))
        self.groupBoxGeneral.setTitle(QCoreApplication.translate("MeshProjectionWidget", u"General", None))
        self.pushButtonContinue.setText(QCoreApplication.translate("MeshProjectionWidget", u"Continue", None))
    # retranslateUi

