import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QAction, QFileDialog,
                             QMessageBox, QTabWidget)
from PyQt5.QtGui import QFont

# To handle multiple windows
notepad_instances = []

class Notepad(QMainWindow):
    def __init__(self):
        super().__init__()
        # Store the initial font to allow zoom reset
        self.default_font = QFont("Consolas", 11)
        self.initUI()

    def initUI(self):
        # --- Window Properties ---
        self.setGeometry(100, 100, 800, 600)

        # --- Tab Widget ---
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tab_widget)

        # --- Initial Tab ---
        self.add_new_tab()

        # --- Actions ---
        self.create_actions()

        # --- Menu Bar ---
        self.create_menu_bar()

        # Connect signal for window title updates
        self.tab_widget.currentChanged.connect(self.update_window_title)
        self.update_window_title() # Set initial title

    def create_actions(self):
        # --- File Actions ---
        self.new_tab_action = QAction("새 탭", self, shortcut="Ctrl+T", triggered=lambda: self.add_new_tab())
        self.new_window_action = QAction("새 창", self, shortcut="Ctrl+Shift+N", triggered=self.new_window)
        self.open_action = QAction("열기(&O)...", self, shortcut="Ctrl+O", triggered=self.open_file)
        self.save_action = QAction("저장(&S)", self, shortcut="Ctrl+S", triggered=self.save_file)
        self.save_as_action = QAction("다른 이름으로 저장(&A)...", shortcut="Ctrl+Shift+S", triggered=self.save_file_as)
        self.exit_action = QAction("종료", self, shortcut="Ctrl+Q", triggered=self.close)

        # --- Edit Actions ---
        self.undo_action = QAction("실행 취소(&U)", self, shortcut="Ctrl+Z")
        self.undo_action.triggered.connect(lambda: self.get_current_editor() and self.get_current_editor().undo())

        # --- View Actions ---
        self.zoom_in_action = QAction("확대", self, shortcut="Ctrl+=", triggered=self.zoom_in)
        self.zoom_out_action = QAction("축소", self, shortcut="Ctrl+-", triggered=self.zoom_out)
        self.restore_zoom_action = QAction("확대/축소 배율 기본값으로 복원", self, shortcut="Ctrl+0", triggered=self.restore_zoom)

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("파일(&F)")
        file_menu.addAction(self.new_tab_action)
        file_menu.addAction(self.new_window_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # Edit Menu
        edit_menu = menu_bar.addMenu("편집(&E)")
        edit_menu.addAction(self.undo_action)

        # View Menu
        view_menu = menu_bar.addMenu("보기(&V)")
        zoom_menu = view_menu.addMenu("확대/축소")
        zoom_menu.addAction(self.zoom_in_action)
        zoom_menu.addAction(self.zoom_out_action)
        zoom_menu.addAction(self.restore_zoom_action)

    def get_current_editor(self):
        if self.tab_widget.count() == 0:
            return None
        return self.tab_widget.currentWidget()

    def on_modification_changed(self, is_modified):
        current_index = self.tab_widget.currentIndex()
        if current_index == -1:
            return
        
        tab_text = self.tab_widget.tabText(current_index)
        # Remove existing asterisk if present
        if tab_text.endswith('*'):
            tab_text = tab_text[:-1]

        if is_modified:
            self.tab_widget.setTabText(current_index, tab_text + '*')
        else:
            self.tab_widget.setTabText(current_index, tab_text)
        
        self.update_window_title()

    def add_new_tab(self, file_path=None, content=''):
        editor = QTextEdit()
        editor.setFont(self.default_font)
        editor.setProperty("file_path", file_path)
        editor.setPlainText(content)
        editor.document().modificationChanged.connect(self.on_modification_changed)
        
        tab_name = "제목 없음" if file_path is None else os.path.basename(file_path)
        index = self.tab_widget.addTab(editor, tab_name)
        self.tab_widget.setCurrentIndex(index)
        # on_modification_changed(False) will be called automatically, removing the '*'
        editor.document().setModified(False)

    def new_window(self):
        new_win = Notepad()
        notepad_instances.append(new_win)
        new_win.show()

    def open_file(self):
        editor = self.get_current_editor()
        # If current tab is modified, ask to save
        if editor and editor.document().isModified():
             if not self.maybe_save():
                 return

        paths, _ = QFileDialog.getOpenFileNames(self, "열기", "", "텍스트 문서 (*.txt);;모든 파일 (*.*)")
        if paths:
            for path in paths:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        text = f.read()
                except Exception as e:
                    QMessageBox.warning(self, "오류", f"'{os.path.basename(path)}' 파일을 열 수 없습니다: {e}")
                    continue
                
                # Check if an empty, unmodified tab is available
                current_editor = self.get_current_editor()
                is_new_and_empty = current_editor and not current_editor.property("file_path") and not current_editor.toPlainText() and not current_editor.document().isModified()

                if is_new_and_empty and len(paths) == 1:
                    # Use the current empty tab only if opening a single file
                    current_index = self.tab_widget.currentIndex()
                    current_editor.setPlainText(text)
                    current_editor.setProperty("file_path", path)
                    self.tab_widget.setTabText(current_index, os.path.basename(path))
                    current_editor.document().setModified(False)
                else:
                    # Otherwise, open in a new tab
                    self.add_new_tab(file_path=path, content=text)

    def save_file(self):
        editor = self.get_current_editor()
        if not editor:
            return False
            
        path = editor.property("file_path")
        if path is None:
            return self.save_file_as()
        else:
            return self._save_to_path(path)

    def save_file_as(self):
        editor = self.get_current_editor()
        if not editor:
            return False

        path, _ = QFileDialog.getSaveFileName(self, "다른 이름으로 저장", "제목 없음.txt", "텍스트 문서 (*.txt);;모든 파일 (*.*)")
        if path:
            return self._save_to_path(path)
        return False

    def _save_to_path(self, path):
        editor = self.get_current_editor()
        if not editor:
            return False
            
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(editor.toPlainText())
        except Exception as e:
            QMessageBox.warning(self, "오류", f"파일을 저장할 수 없습니다: {e}")
            return False
        else:
            editor.setProperty("file_path", path)
            editor.document().setModified(False) # This will trigger on_modification_changed
            current_index = self.tab_widget.currentIndex()
            self.tab_widget.setTabText(current_index, os.path.basename(path)) # Update tab text
            self.update_window_title()
            return True

    def maybe_save(self):
        editor = self.get_current_editor()
        if not editor or not editor.document().isModified():
            return True
        
        tab_name = self.tab_widget.tabText(self.tab_widget.currentIndex()).replace('*','')
        ret = QMessageBox.question(self, "메모장",
                                   f"'{tab_name}'의 내용을 저장하시겠습니까?",
                                   QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

        if ret == QMessageBox.Save:
            return self.save_file()
        elif ret == QMessageBox.Cancel:
            return False
        return True

    def close_tab(self, index):
        self.tab_widget.setCurrentIndex(index)
        if not self.maybe_save():
            return

        # If it's the last tab, close the window.
        if self.tab_widget.count() == 1:
            self.close()
        else:
            self.tab_widget.removeTab(index)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '메모장',
                                     "정말로 닫으시겠습니까?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Iterate through all tabs and ask to save if modified
            # We must iterate backwards when removing items
            for i in range(self.tab_widget.count() - 1, -1, -1):
                self.tab_widget.setCurrentIndex(i)
                if not self.maybe_save():
                    event.ignore()
                    return
                # No need to remove tab here, as the whole window is closing
            
            event.accept()
            # Remove the instance from the global list to allow Python to exit
            if self in notepad_instances:
                notepad_instances.remove(self)
        else:
            event.ignore()

    def update_window_title(self):
        editor = self.get_current_editor()
        if not editor:
            self.setWindowTitle("메모장")
            return

        path = editor.property("file_path")
        title = "제목 없음"
        if path:
            title = os.path.basename(path)
        
        if editor.document().isModified():
            title += "*"
            
        self.setWindowTitle(f"{title} - 메모장")

    def zoom_in(self):
        editor = self.get_current_editor()
        if editor:
            editor.zoomIn(2)

    def zoom_out(self):
        editor = self.get_current_editor()
        if editor:
            editor.zoomOut(2)

    def restore_zoom(self):
        editor = self.get_current_editor()
        if editor:
            editor.setFont(self.default_font)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Keep a reference to the window to prevent it from being garbage collected
    main_window = Notepad()
    notepad_instances.append(main_window)
    main_window.show()
    sys.exit(app.exec_())