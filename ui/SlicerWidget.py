"""
SlicerWidget

Class that shows a slicer with controls for loading data, etc.

@author: Berend Klein Haneveld 2013
"""

try:
	from PySide.QtGui import QWidget
	from PySide.QtGui import QPushButton
	from PySide.QtGui import QIcon
	from PySide.QtGui import QVBoxLayout
	from PySide.QtGui import QFileDialog
	from PySide.QtGui import QLabel
	from PySide import QtCore
	from PySide.QtCore import Signal
	from vtk import *
except ImportError, e:
	raise e

from core.AppVars import AppVars
from ButtonContainer import ButtonContainer
from UAHCore.UAHViewer.BaseViewer import BaseViewer
from UAHCore.UAHViewer.slicer import Slicer

class SlicerWidget(QWidget):
	loadedFileName = Signal(basestring)

	def __init__(self, title=""):
		"""
		Sets up the slicer widget.
		"""
		super(SlicerWidget, self).__init__()
		self._baseTitle = title
		self.initUI()

		self._slicer = Slicer(self._viewer.rwi, self._viewer.ren)
		self._imageReader = vtkMetaImageReader()
		self._imageData = None
		self._fileName = None
		pass

	# Public methods

	def fileName(self):
		"""
		Returns the file name of the current loaded set
		@rtype: basestring
		"""
		return self._fileName

	def setFileName(self, fileName):
		"""
		Sets the file name and loads the data for it into the slicer
		@type fileName: basestring
		"""
		# TODO: check if it is sane? Project controller should probably do that
		self._fileName = fileName
		self._imageReader.SetFileName(self._fileName)
		self._imageData = self._imageReader.GetOutput()

		self._slicer.set_input(self._imageData)
		self._slicer.set_perspective()
		self._slicer.reset_to_default_view(2)
		self._slicer.reset_camera()

		# Update the title with the last path component
		# TODO: check to see if this works on Windows...
		index = self._fileName.rfind("/")
		self.setTitle(self._fileName[index+1:])

	# UI methods

	def initUI(self):
		"""
		Sets up the UI. Creates vertical layout and adds
		a list widget.
		"""
		# Create container for action buttons
		self._actionButtons = ButtonContainer()
		button = QPushButton()
		button.setIcon(QIcon(AppVars.imagePath() + "AddButton.png"))
		button.clicked.connect(self.loadFile)
		self._actionButtons.addButton(button)

		# Create a main layout (vertical) for this widget
		self._layout = QVBoxLayout()
		self._layout.setSpacing(0)
		self._layout.setContentsMargins(0, 0, 0, 0)
		
		# Create label with title
		self._titleLabel = QLabel(self._baseTitle)
		font = self._titleLabel.font()
		font.setPixelSize(11)
		self._titleLabel.setFont(font)
		self._titleLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.setTitle(None)

		# Create the base viewer in which the slices will be shown
		self._viewer = BaseViewer(BaseViewer.TypeSlice)

		# Put actions underneath the main part of the widget
		# Just like in XCode/Finder
		self._layout.addWidget(self._titleLabel)
		self._layout.addWidget(self._viewer)
		self._layout.addWidget(self._actionButtons)
		
		self.setLayout(self._layout)
		pass

	def setTitle(self, title):
		"""
		Sets the title on the top of the viewer
		@type title: basestring
		"""
		if title is None:
			self._title = "No data loaded"
		else:
			self._title = title
		self._titleLabel.setText(self._baseTitle + ": " + self._title)
		pass

	# UI actions / callbacks

	def loadFile(self):
		"""
		Open file dialog to search for data files. If valid data is given, it will
		pass the data file location on to the slicer and the project controller.
		"""
		fileName, other = QFileDialog.getOpenFileName(self, "Open fixed data set", "", "Images (*.mhd)")
		if len(fileName) > 0:
			# Send signal that new file name is available
			self.loadedFileName.emit(fileName)
		pass

