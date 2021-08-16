# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Reinh\OneDrive\Dokumente\python\MzChess\MzChess\chessMainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(973, 753)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtWidgets.QSplitter(self.centralWidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.boardGraphicsView = QBoardViewClass(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.boardGraphicsView.sizePolicy().hasHeightForWidth())
        self.boardGraphicsView.setSizePolicy(sizePolicy)
        self.boardGraphicsView.setMinimumSize(QtCore.QSize(100, 100))
        self.boardGraphicsView.setObjectName("boardGraphicsView")
        self.verticalLayout.addWidget(self.boardGraphicsView)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.materialLabel = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.materialLabel.sizePolicy().hasHeightForWidth())
        self.materialLabel.setSizePolicy(sizePolicy)
        self.materialLabel.setMinimumSize(QtCore.QSize(0, 30))
        self.materialLabel.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Chess Leipzig")
        font.setPointSize(20)
        self.materialLabel.setFont(font)
        self.materialLabel.setText("")
        self.materialLabel.setObjectName("materialLabel")
        self.horizontalLayout.addWidget(self.materialLabel)
        self.turnFrame = QtWidgets.QFrame(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.turnFrame.sizePolicy().hasHeightForWidth())
        self.turnFrame.setSizePolicy(sizePolicy)
        self.turnFrame.setMinimumSize(QtCore.QSize(30, 30))
        self.turnFrame.setAutoFillBackground(True)
        self.turnFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.turnFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.turnFrame.setObjectName("turnFrame")
        self.horizontalLayout.addWidget(self.turnFrame)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tabWidget = QtWidgets.QTabWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMinimumSize(QtCore.QSize(100, 0))
        self.tabWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.tabWidget.setObjectName("tabWidget")
        self.tabGame = QtWidgets.QWidget()
        self.tabGame.setObjectName("tabGame")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tabGame)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.gameTreeViewWidget = GameTreeView(self.tabGame)
        self.gameTreeViewWidget.setObjectName("gameTreeViewWidget")
        self.gameTreeViewWidget.headerItem().setText(0, "1")
        self.verticalLayout_3.addWidget(self.gameTreeViewWidget)
        self.tabWidget.addTab(self.tabGame, "")
        self.tabHeader = QtWidgets.QWidget()
        self.tabHeader.setObjectName("tabHeader")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tabHeader)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.gameHeaderTableView = GameHeaderView(self.tabHeader)
        self.gameHeaderTableView.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed)
        self.gameHeaderTableView.setColumnCount(2)
        self.gameHeaderTableView.setObjectName("gameHeaderTableView")
        self.gameHeaderTableView.setRowCount(0)
        self.gameHeaderTableView.horizontalHeader().setVisible(False)
        self.gameHeaderTableView.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout_4.addWidget(self.gameHeaderTableView)
        self.tabWidget.addTab(self.tabHeader, "")
        self.tabDatabase = QtWidgets.QWidget()
        self.tabDatabase.setObjectName("tabDatabase")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.tabDatabase)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.gameListTableView = GameListTableView(self.tabDatabase)
        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setPointSize(10)
        self.gameListTableView.setFont(font)
        self.gameListTableView.setObjectName("gameListTableView")
        self.horizontalLayout_3.addWidget(self.gameListTableView)
        self.tabWidget.addTab(self.tabDatabase, "")
        self.tabScorePlot = QtWidgets.QWidget()
        self.tabScorePlot.setObjectName("tabScorePlot")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.tabScorePlot)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.scorePlotGraphicsView = ScorePlot(self.tabScorePlot)
        self.scorePlotGraphicsView.setObjectName("scorePlotGraphicsView")
        self.horizontalLayout_2.addWidget(self.scorePlotGraphicsView)
        self.tabWidget.addTab(self.tabScorePlot, "")
        self.tabLog = QtWidgets.QWidget()
        self.tabLog.setObjectName("tabLog")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.tabLog)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.uciTextEdit = QUCIEdit(self.tabLog)
        self.uciTextEdit.setObjectName("uciTextEdit")
        self.horizontalLayout_4.addWidget(self.uciTextEdit)
        self.tabWidget.addTab(self.tabLog, "")
        self.verticalLayout_2.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 973, 21))
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        self.menuRecent_PGN = QtWidgets.QMenu(self.menuFile)
        self.menuRecent_PGN.setObjectName("menuRecent_PGN")
        self.menuEncoding = QtWidgets.QMenu(self.menuFile)
        self.menuEncoding.setObjectName("menuEncoding")
        self.menuEdit = QtWidgets.QMenu(self.menuBar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuGame = QtWidgets.QMenu(self.menuBar)
        self.menuGame.setObjectName("menuGame")
        self.menuEnd_Game = QtWidgets.QMenu(self.menuGame)
        self.menuEnd_Game.setObjectName("menuEnd_Game")
        self.menuEngine = QtWidgets.QMenu(self.menuBar)
        self.menuEngine.setObjectName("menuEngine")
        self.menuSelect_Engine = QtWidgets.QMenu(self.menuEngine)
        self.menuSelect_Engine.setObjectName("menuSelect_Engine")
        self.menuSearch_Depth = QtWidgets.QMenu(self.menuEngine)
        self.menuSearch_Depth.setObjectName("menuSearch_Depth")
        self.menuBlunder_Limit = QtWidgets.QMenu(self.menuEngine)
        self.menuBlunder_Limit.setObjectName("menuBlunder_Limit")
        self.menuAnnotate_Variants = QtWidgets.QMenu(self.menuEngine)
        self.menuAnnotate_Variants.setObjectName("menuAnnotate_Variants")
        self.menuNumber_of_Annotations = QtWidgets.QMenu(self.menuEngine)
        self.menuNumber_of_Annotations.setObjectName("menuNumber_of_Annotations")
        self.menuDatabase = QtWidgets.QMenu(self.menuBar)
        self.menuDatabase.setObjectName("menuDatabase")
        self.menuHelp = QtWidgets.QMenu(self.menuBar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menuBar)
        self.actionCopy_FEN = QtWidgets.QAction(MainWindow)
        self.actionCopy_FEN.setObjectName("actionCopy_FEN")
        self.actionPaste_FEN = QtWidgets.QAction(MainWindow)
        self.actionPaste_FEN.setObjectName("actionPaste_FEN")
        self.actionCopy_PGN = QtWidgets.QAction(MainWindow)
        self.actionCopy_PGN.setObjectName("actionCopy_PGN")
        self.actionPaste_PGN = QtWidgets.QAction(MainWindow)
        self.actionPaste_PGN.setObjectName("actionPaste_PGN")
        self.actionNew_Game = QtWidgets.QAction(MainWindow)
        self.actionNew_Game.setObjectName("actionNew_Game")
        self.actionWhite_wins = QtWidgets.QAction(MainWindow)
        self.actionWhite_wins.setObjectName("actionWhite_wins")
        self.action0_1 = QtWidgets.QAction(MainWindow)
        self.action0_1.setObjectName("action0_1")
        self.action1_2_1_2 = QtWidgets.QAction(MainWindow)
        self.action1_2_1_2.setObjectName("action1_2_1_2")
        self.actionShow_Options = QtWidgets.QAction(MainWindow)
        self.actionShow_Options.setCheckable(True)
        self.actionShow_Options.setObjectName("actionShow_Options")
        self.action5_Moves = QtWidgets.QAction(MainWindow)
        self.action5_Moves.setCheckable(True)
        self.action5_Moves.setObjectName("action5_Moves")
        self.action10_Moves = QtWidgets.QAction(MainWindow)
        self.action10_Moves.setCheckable(True)
        self.action10_Moves.setObjectName("action10_Moves")
        self.action15_Moves = QtWidgets.QAction(MainWindow)
        self.action15_Moves.setCheckable(True)
        self.action15_Moves.setChecked(False)
        self.action15_Moves.setObjectName("action15_Moves")
        self.action20_Moves = QtWidgets.QAction(MainWindow)
        self.action20_Moves.setCheckable(True)
        self.action20_Moves.setObjectName("action20_Moves")
        self.action25_Moves = QtWidgets.QAction(MainWindow)
        self.action25_Moves.setCheckable(True)
        self.action25_Moves.setObjectName("action25_Moves")
        self.actionShow_Hints = QtWidgets.QAction(MainWindow)
        self.actionShow_Hints.setCheckable(True)
        self.actionShow_Hints.setObjectName("actionShow_Hints")
        self.actionNext_Move = QtWidgets.QAction(MainWindow)
        self.actionNext_Move.setShortcutContext(QtCore.Qt.WindowShortcut)
        self.actionNext_Move.setObjectName("actionNext_Move")
        self.actionPrevious_Move = QtWidgets.QAction(MainWindow)
        self.actionPrevious_Move.setShortcutContext(QtCore.Qt.WindowShortcut)
        self.actionPrevious_Move.setObjectName("actionPrevious_Move")
        self.actionOpen_PGN = QtWidgets.QAction(MainWindow)
        self.actionOpen_PGN.setObjectName("actionOpen_PGN")
        self.actionSave_PGN = QtWidgets.QAction(MainWindow)
        self.actionSave_PGN.setObjectName("actionSave_PGN")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionbla = QtWidgets.QAction(MainWindow)
        self.actionbla.setObjectName("actionbla")
        self.actionAdd_To_DB = QtWidgets.QAction(MainWindow)
        self.actionAdd_To_DB.setObjectName("actionAdd_To_DB")
        self.actionAppend_to_DB = QtWidgets.QAction(MainWindow)
        self.actionAppend_to_DB.setCheckable(True)
        self.actionAppend_to_DB.setObjectName("actionAppend_to_DB")
        self.actionSave_Game = QtWidgets.QAction(MainWindow)
        self.actionSave_Game.setObjectName("actionSave_Game")
        self.actionClose_PGN = QtWidgets.QAction(MainWindow)
        self.actionClose_PGN.setObjectName("actionClose_PGN")
        self.actionAdd_Game = QtWidgets.QAction(MainWindow)
        self.actionAdd_Game.setObjectName("actionAdd_Game")
        self.actionRemove_Games = QtWidgets.QAction(MainWindow)
        self.actionRemove_Games.setObjectName("actionRemove_Games")
        self.actionNew_PGN = QtWidgets.QAction(MainWindow)
        self.actionNew_PGN.setObjectName("actionNew_PGN")
        self.actionFlip_Board = QtWidgets.QAction(MainWindow)
        self.actionFlip_Board.setCheckable(True)
        self.actionFlip_Board.setObjectName("actionFlip_Board")
        self.actionNext_Variant = QtWidgets.QAction(MainWindow)
        self.actionNext_Variant.setObjectName("actionNext_Variant")
        self.actionPrevious_Variant = QtWidgets.QAction(MainWindow)
        self.actionPrevious_Variant.setObjectName("actionPrevious_Variant")
        self.actionShow_Scores = QtWidgets.QAction(MainWindow)
        self.actionShow_Scores.setCheckable(True)
        self.actionShow_Scores.setObjectName("actionShow_Scores")
        self.actionWarn_of_Danger = QtWidgets.QAction(MainWindow)
        self.actionWarn_of_Danger.setCheckable(True)
        self.actionWarn_of_Danger.setObjectName("actionWarn_of_Danger")
        self.actionUndo_Last_Move = QtWidgets.QAction(MainWindow)
        self.actionUndo_Last_Move.setObjectName("actionUndo_Last_Move")
        self.actionAnnotate_Last_Move = QtWidgets.QAction(MainWindow)
        self.actionAnnotate_Last_Move.setObjectName("actionAnnotate_Last_Move")
        self.actionBlNone = QtWidgets.QAction(MainWindow)
        self.actionBlNone.setCheckable(True)
        self.actionBlNone.setChecked(False)
        self.actionBlNone.setObjectName("actionBlNone")
        self.action0_5_pawns = QtWidgets.QAction(MainWindow)
        self.action0_5_pawns.setCheckable(True)
        self.action0_5_pawns.setObjectName("action0_5_pawns")
        self.action1_pawn = QtWidgets.QAction(MainWindow)
        self.action1_pawn.setCheckable(True)
        self.action1_pawn.setObjectName("action1_pawn")
        self.action1_5_pawns = QtWidgets.QAction(MainWindow)
        self.action1_5_pawns.setCheckable(True)
        self.action1_5_pawns.setObjectName("action1_5_pawns")
        self.action2_0_pawns = QtWidgets.QAction(MainWindow)
        self.action2_0_pawns.setCheckable(True)
        self.action2_0_pawns.setObjectName("action2_0_pawns")
        self.action2_5_pawns = QtWidgets.QAction(MainWindow)
        self.action2_5_pawns.setCheckable(True)
        self.action2_5_pawns.setObjectName("action2_5_pawns")
        self.action3_0_pawns = QtWidgets.QAction(MainWindow)
        self.action3_0_pawns.setCheckable(True)
        self.action3_0_pawns.setObjectName("action3_0_pawns")
        self.actionAvNone = QtWidgets.QAction(MainWindow)
        self.actionAvNone.setCheckable(True)
        self.actionAvNone.setChecked(False)
        self.actionAvNone.setObjectName("actionAvNone")
        self.action2_Halfmoves = QtWidgets.QAction(MainWindow)
        self.action2_Halfmoves.setCheckable(True)
        self.action2_Halfmoves.setObjectName("action2_Halfmoves")
        self.action4_Halfmoves = QtWidgets.QAction(MainWindow)
        self.action4_Halfmoves.setCheckable(True)
        self.action4_Halfmoves.setObjectName("action4_Halfmoves")
        self.action6_Halfmoves = QtWidgets.QAction(MainWindow)
        self.action6_Halfmoves.setCheckable(True)
        self.action6_Halfmoves.setObjectName("action6_Halfmoves")
        self.actionAll = QtWidgets.QAction(MainWindow)
        self.actionAll.setCheckable(True)
        self.actionAll.setObjectName("actionAll")
        self.actionConfigureEngine = QtWidgets.QAction(MainWindow)
        self.actionConfigureEngine.setObjectName("actionConfigureEngine")
        self.actionDebugEngine = QtWidgets.QAction(MainWindow)
        self.actionDebugEngine.setCheckable(True)
        self.actionDebugEngine.setObjectName("actionDebugEngine")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionPromote_Variant = QtWidgets.QAction(MainWindow)
        self.actionPromote_Variant.setObjectName("actionPromote_Variant")
        self.actionDelete_Variant = QtWidgets.QAction(MainWindow)
        self.actionDelete_Variant.setObjectName("actionDelete_Variant")
        self.actionAnnotate_All = QtWidgets.QAction(MainWindow)
        self.actionAnnotate_All.setObjectName("actionAnnotate_All")
        self.action1 = QtWidgets.QAction(MainWindow)
        self.action1.setCheckable(True)
        self.action1.setObjectName("action1")
        self.action2 = QtWidgets.QAction(MainWindow)
        self.action2.setCheckable(True)
        self.action2.setObjectName("action2")
        self.action3 = QtWidgets.QAction(MainWindow)
        self.action3.setCheckable(True)
        self.action3.setObjectName("action3")
        self.actionAll_2 = QtWidgets.QAction(MainWindow)
        self.actionAll_2.setObjectName("actionAll_2")
        self.actionUTF_8 = QtWidgets.QAction(MainWindow)
        self.actionUTF_8.setCheckable(True)
        self.actionUTF_8.setChecked(True)
        self.actionUTF_8.setObjectName("actionUTF_8")
        self.actionISO_8859_1 = QtWidgets.QAction(MainWindow)
        self.actionISO_8859_1.setCheckable(True)
        self.actionISO_8859_1.setObjectName("actionISO_8859_1")
        self.actionASCII = QtWidgets.QAction(MainWindow)
        self.actionASCII.setCheckable(True)
        self.actionASCII.setObjectName("actionASCII")
        self.actionHelp = QtWidgets.QAction(MainWindow)
        self.actionHelp.setObjectName("actionHelp")
        self.actionDemote_Variant = QtWidgets.QAction(MainWindow)
        self.actionDemote_Variant.setObjectName("actionDemote_Variant")
        self.actionPromote_Variant_to_Main = QtWidgets.QAction(MainWindow)
        self.actionPromote_Variant_to_Main.setObjectName("actionPromote_Variant_to_Main")
        self.actionSelect_Header_Elements = QtWidgets.QAction(MainWindow)
        self.actionSelect_Header_Elements.setObjectName("actionSelect_Header_Elements")
        self.actionRunning_Game = QtWidgets.QAction(MainWindow)
        self.actionRunning_Game.setObjectName("actionRunning_Game")
        self.actionFEN_Builder = QtWidgets.QAction(MainWindow)
        self.actionFEN_Builder.setObjectName("actionFEN_Builder")
        self.menuRecent_PGN.addAction(self.actionbla)
        self.menuEncoding.addAction(self.actionUTF_8)
        self.menuEncoding.addAction(self.actionISO_8859_1)
        self.menuEncoding.addAction(self.actionASCII)
        self.menuFile.addAction(self.menuEncoding.menuAction())
        self.menuFile.addAction(self.actionOpen_PGN)
        self.menuFile.addAction(self.menuRecent_PGN.menuAction())
        self.menuFile.addAction(self.actionAppend_to_DB)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave_PGN)
        self.menuFile.addAction(self.actionSave_Game)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuEdit.addAction(self.actionFEN_Builder)
        self.menuEdit.addAction(self.actionCopy_PGN)
        self.menuEdit.addAction(self.actionPaste_PGN)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionCopy_FEN)
        self.menuEdit.addAction(self.actionPaste_FEN)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionNext_Move)
        self.menuEdit.addAction(self.actionPrevious_Move)
        self.menuEdit.addAction(self.actionUndo_Last_Move)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionNext_Variant)
        self.menuEdit.addAction(self.actionPrevious_Variant)
        self.menuEdit.addAction(self.actionPromote_Variant)
        self.menuEdit.addAction(self.actionPromote_Variant_to_Main)
        self.menuEdit.addAction(self.actionDemote_Variant)
        self.menuEdit.addAction(self.actionDelete_Variant)
        self.menuEnd_Game.addAction(self.actionRunning_Game)
        self.menuEnd_Game.addAction(self.actionWhite_wins)
        self.menuEnd_Game.addAction(self.action0_1)
        self.menuEnd_Game.addAction(self.action1_2_1_2)
        self.menuGame.addAction(self.actionNew_Game)
        self.menuGame.addAction(self.actionSelect_Header_Elements)
        self.menuGame.addAction(self.menuEnd_Game.menuAction())
        self.menuGame.addSeparator()
        self.menuGame.addAction(self.actionFlip_Board)
        self.menuGame.addSeparator()
        self.menuGame.addAction(self.actionShow_Options)
        self.menuGame.addAction(self.actionWarn_of_Danger)
        self.menuSelect_Engine.addSeparator()
        self.menuSearch_Depth.addAction(self.action5_Moves)
        self.menuSearch_Depth.addAction(self.action10_Moves)
        self.menuSearch_Depth.addAction(self.action15_Moves)
        self.menuSearch_Depth.addAction(self.action20_Moves)
        self.menuSearch_Depth.addAction(self.action25_Moves)
        self.menuBlunder_Limit.addAction(self.actionBlNone)
        self.menuBlunder_Limit.addSeparator()
        self.menuBlunder_Limit.addAction(self.action0_5_pawns)
        self.menuBlunder_Limit.addAction(self.action1_pawn)
        self.menuBlunder_Limit.addAction(self.action1_5_pawns)
        self.menuBlunder_Limit.addAction(self.action2_0_pawns)
        self.menuBlunder_Limit.addAction(self.action2_5_pawns)
        self.menuBlunder_Limit.addAction(self.action3_0_pawns)
        self.menuAnnotate_Variants.addAction(self.actionAvNone)
        self.menuAnnotate_Variants.addAction(self.actionAll)
        self.menuAnnotate_Variants.addSeparator()
        self.menuAnnotate_Variants.addAction(self.action2_Halfmoves)
        self.menuAnnotate_Variants.addAction(self.action4_Halfmoves)
        self.menuAnnotate_Variants.addAction(self.action6_Halfmoves)
        self.menuNumber_of_Annotations.addAction(self.action1)
        self.menuNumber_of_Annotations.addAction(self.action2)
        self.menuNumber_of_Annotations.addAction(self.action3)
        self.menuEngine.addAction(self.menuSelect_Engine.menuAction())
        self.menuEngine.addAction(self.menuSearch_Depth.menuAction())
        self.menuEngine.addSeparator()
        self.menuEngine.addAction(self.actionAnnotate_Last_Move)
        self.menuEngine.addAction(self.actionAnnotate_All)
        self.menuEngine.addAction(self.menuNumber_of_Annotations.menuAction())
        self.menuEngine.addAction(self.menuBlunder_Limit.menuAction())
        self.menuEngine.addAction(self.menuAnnotate_Variants.menuAction())
        self.menuEngine.addSeparator()
        self.menuEngine.addAction(self.actionShow_Scores)
        self.menuEngine.addAction(self.actionShow_Hints)
        self.menuEngine.addSeparator()
        self.menuEngine.addAction(self.actionConfigureEngine)
        self.menuEngine.addAction(self.actionDebugEngine)
        self.menuDatabase.addAction(self.actionNew_PGN)
        self.menuDatabase.addAction(self.actionClose_PGN)
        self.menuDatabase.addSeparator()
        self.menuDatabase.addAction(self.actionAdd_Game)
        self.menuDatabase.addAction(self.actionRemove_Games)
        self.menuHelp.addAction(self.actionHelp)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout)
        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuEdit.menuAction())
        self.menuBar.addAction(self.menuDatabase.menuAction())
        self.menuBar.addAction(self.menuGame.menuAction())
        self.menuBar.addAction(self.menuEngine.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MzChess"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabGame), _translate("MainWindow", "Game"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabHeader), _translate("MainWindow", "Header"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabDatabase), _translate("MainWindow", "Database"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabScorePlot), _translate("MainWindow", "Score Plot"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabLog), _translate("MainWindow", "Log"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuRecent_PGN.setTitle(_translate("MainWindow", "Recent"))
        self.menuEncoding.setTitle(_translate("MainWindow", "Encoding"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuGame.setTitle(_translate("MainWindow", "Game"))
        self.menuEnd_Game.setTitle(_translate("MainWindow", "End Game"))
        self.menuEngine.setTitle(_translate("MainWindow", "Engine"))
        self.menuSelect_Engine.setTitle(_translate("MainWindow", "Select Engine"))
        self.menuSearch_Depth.setTitle(_translate("MainWindow", "Search Depth"))
        self.menuBlunder_Limit.setTitle(_translate("MainWindow", "Blunder Limit"))
        self.menuAnnotate_Variants.setTitle(_translate("MainWindow", "Annotate Variants"))
        self.menuNumber_of_Annotations.setTitle(_translate("MainWindow", "# Annotations"))
        self.menuDatabase.setTitle(_translate("MainWindow", "Database"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionCopy_FEN.setText(_translate("MainWindow", "Copy FEN"))
        self.actionCopy_FEN.setShortcut(_translate("MainWindow", "Ctrl+Shift+C"))
        self.actionPaste_FEN.setText(_translate("MainWindow", "Paste FEN"))
        self.actionPaste_FEN.setShortcut(_translate("MainWindow", "Ctrl+Shift+V"))
        self.actionCopy_PGN.setText(_translate("MainWindow", "Copy PGN"))
        self.actionCopy_PGN.setShortcut(_translate("MainWindow", "Ctrl+C"))
        self.actionPaste_PGN.setText(_translate("MainWindow", "Paste PGN"))
        self.actionPaste_PGN.setShortcut(_translate("MainWindow", "Ctrl+V"))
        self.actionNew_Game.setText(_translate("MainWindow", "New"))
        self.actionWhite_wins.setText(_translate("MainWindow", "1-0"))
        self.action0_1.setText(_translate("MainWindow", "0-1"))
        self.action1_2_1_2.setText(_translate("MainWindow", "1/2-1/2"))
        self.actionShow_Options.setText(_translate("MainWindow", "Show Move Options"))
        self.action5_Moves.setText(_translate("MainWindow", "5 Moves"))
        self.action10_Moves.setText(_translate("MainWindow", "10 Moves"))
        self.action15_Moves.setText(_translate("MainWindow", "15 Moves"))
        self.action20_Moves.setText(_translate("MainWindow", "20 Moves"))
        self.action25_Moves.setText(_translate("MainWindow", "25 Moves"))
        self.actionShow_Hints.setText(_translate("MainWindow", "Show Hints"))
        self.actionNext_Move.setText(_translate("MainWindow", "Next Move"))
        self.actionNext_Move.setShortcut(_translate("MainWindow", "Down"))
        self.actionPrevious_Move.setText(_translate("MainWindow", "Previous Move"))
        self.actionPrevious_Move.setShortcut(_translate("MainWindow", "Up"))
        self.actionOpen_PGN.setText(_translate("MainWindow", "Open DB ..."))
        self.actionSave_PGN.setText(_translate("MainWindow", "Save DB ..."))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionbla.setText(_translate("MainWindow", "bla"))
        self.actionAdd_To_DB.setText(_translate("MainWindow", "Add to DB"))
        self.actionAppend_to_DB.setText(_translate("MainWindow", "Append to DB"))
        self.actionSave_Game.setText(_translate("MainWindow", "Save Game ..."))
        self.actionClose_PGN.setText(_translate("MainWindow", "Close"))
        self.actionAdd_Game.setText(_translate("MainWindow", "Add Game"))
        self.actionRemove_Games.setText(_translate("MainWindow", "Remove Games"))
        self.actionNew_PGN.setText(_translate("MainWindow", "New"))
        self.actionFlip_Board.setText(_translate("MainWindow", "Rotate Board"))
        self.actionFlip_Board.setShortcut(_translate("MainWindow", "Ctrl+F"))
        self.actionNext_Variant.setText(_translate("MainWindow", "Next Variant"))
        self.actionNext_Variant.setShortcut(_translate("MainWindow", "Right"))
        self.actionPrevious_Variant.setText(_translate("MainWindow", "Previous Variant"))
        self.actionPrevious_Variant.setShortcut(_translate("MainWindow", "Left"))
        self.actionShow_Scores.setText(_translate("MainWindow", "Show Scores"))
        self.actionWarn_of_Danger.setText(_translate("MainWindow", "Warn of Danger"))
        self.actionWarn_of_Danger.setShortcut(_translate("MainWindow", "Ctrl+W"))
        self.actionUndo_Last_Move.setText(_translate("MainWindow", "Undo Last Move"))
        self.actionUndo_Last_Move.setShortcut(_translate("MainWindow", "Ctrl+Z"))
        self.actionAnnotate_Last_Move.setText(_translate("MainWindow", "Annotate Last Move"))
        self.actionBlNone.setText(_translate("MainWindow", "None"))
        self.action0_5_pawns.setText(_translate("MainWindow", "0.5 pawns"))
        self.action1_pawn.setText(_translate("MainWindow", "1 pawn"))
        self.action1_5_pawns.setText(_translate("MainWindow", "1.5 pawns"))
        self.action2_0_pawns.setText(_translate("MainWindow", "2 pawns"))
        self.action2_5_pawns.setText(_translate("MainWindow", "2.5 pawns"))
        self.action3_0_pawns.setText(_translate("MainWindow", "3 pawns"))
        self.actionAvNone.setText(_translate("MainWindow", "None"))
        self.action2_Halfmoves.setText(_translate("MainWindow", "2 Halfmoves"))
        self.action4_Halfmoves.setText(_translate("MainWindow", "4 Halfmoves"))
        self.action6_Halfmoves.setText(_translate("MainWindow", "6 Halfmoves"))
        self.actionAll.setText(_translate("MainWindow", "All"))
        self.actionConfigureEngine.setText(_translate("MainWindow", "Configure ..."))
        self.actionDebugEngine.setText(_translate("MainWindow", "Debug"))
        self.actionAbout.setText(_translate("MainWindow", "About ..."))
        self.actionPromote_Variant.setText(_translate("MainWindow", "Promote Variant"))
        self.actionPromote_Variant.setShortcut(_translate("MainWindow", "Ctrl+P"))
        self.actionDelete_Variant.setText(_translate("MainWindow", "Delete Variant"))
        self.actionDelete_Variant.setShortcut(_translate("MainWindow", "Ctrl+R"))
        self.actionAnnotate_All.setText(_translate("MainWindow", "Annotate All"))
        self.action1.setText(_translate("MainWindow", "1 variant"))
        self.action2.setText(_translate("MainWindow", "2 variants"))
        self.action3.setText(_translate("MainWindow", "3 variants"))
        self.actionAll_2.setText(_translate("MainWindow", "All"))
        self.actionUTF_8.setText(_translate("MainWindow", "UTF-8"))
        self.actionISO_8859_1.setText(_translate("MainWindow", "ISO 8859/1"))
        self.actionASCII.setText(_translate("MainWindow", "ASCII"))
        self.actionHelp.setText(_translate("MainWindow", "Help ..."))
        self.actionDemote_Variant.setText(_translate("MainWindow", "Demote Variant"))
        self.actionDemote_Variant.setShortcut(_translate("MainWindow", "Ctrl+D"))
        self.actionPromote_Variant_to_Main.setText(_translate("MainWindow", "Promote Variant to Main"))
        self.actionPromote_Variant_to_Main.setShortcut(_translate("MainWindow", "Ctrl+M"))
        self.actionSelect_Header_Elements.setText(_translate("MainWindow", "Select Header Elements ..."))
        self.actionRunning_Game.setText(_translate("MainWindow", "*"))
        self.actionFEN_Builder.setText(_translate("MainWindow", "FEN Builder ..."))
from gameheaderview import GameHeaderView
from gamelisttableview import GameListTableView
from gametreeview import GameTreeView
from qboardviewclass import QBoardViewClass
from scoreplotgraphicsview import ScorePlot
from uciedit import QUCIEdit


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
