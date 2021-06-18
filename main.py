# Python file "main.py".
# Is used to develop the functional side of the <Planer> application.
# The app is designed for a graduation project

# Kivy Libraries
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty

# Kivy Layouts
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.stacklayout import StackLayout

# KivyMD Libraries
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.picker import MDDatePicker
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem, TwoLineAvatarIconListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.screen import Screen

# Auxiliary libraries
import shelve
from datetime import datetime
import time

Window.size = (300, 500)


class MainScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def clear_fields(self):
        self.ids.task_name.text = ""
        self.ids.task_about_me.text = ""
        self.ids.task_interests.text = ""


class TaskDetailDialog(BoxLayout):
    # Opens a dialog box with detailed information about the task
    def __init__(self, widget=None, **kwargs):
        super().__init__(**kwargs)

        self.widget = widget
        self.ids.task_detail_text.text = str(self.widget.text)
        self.ids.task_detail_date.text = str(self.widget.secondary_text)

    def open_edit_dialog(self):
        self.edit_dialog = MDDialog(title='EDIT TASK',
                                    type="custom",
                                    content_cls=TaskEditDialog(widget=self.widget),
                                    size_hint=[.95, .5],
        )
        self.edit_dialog.open()

    def close_edit_dialog(self):
        self.edit_dialog.dismiss()

    def delete_task_dialog(self):
        self.delete_dialog = MDDialog(title='DELETE TASK',
                                      type="custom",
                                      content_cls=ConfirmDelete(widget=self.widget),
                                      size_hint=[.95, .5],
        )
        self.delete_dialog.open()

    def close_delete_dialog(self):
        self.delete_dialog.dismiss()


class TaskEditDialog(BoxLayout):
    # Opens a dialog box for editing the selected task
    def __init__(self, widget=None, **kwargs):
        super().__init__(**kwargs)
        self.widget = widget
        self.ids.edit_task_text.text = self.widget.text
        self.ids.edit_date_text.text = self.widget.secondary_text
        self.pk = int(self.widget.pk)

    # Opens the date selection window
    def show_date_picker(self):
        date_dialog = MDDatePicker(callback=self.get_date)
        date_dialog.open()

    # This function gets the date and converts it to a more
    # user-friendly view. Also, it changes the date label in the dialog box.
    def get_date(self, date):
        date = date.strftime('%A %d %B %Y')
        self.ids.edit_date_text.text = str(date)
        print(date)

    # Saves the task values
    def save_task_data(self):
        self.widget.text = str(self.ids.edit_task_text.text)
        self.widget.secondary_text = str(self.ids.edit_date_text.text)
        self.save_edit_data_to_file()

        Snackbar(text='Task Saved!').show()

    # Saves the changed task values
    def save_edit_data_to_file(self):
        shelf_file = shelve.open('planer_data')
        todo = shelf_file['planer']

        print(self.pk)

        for k in todo:
            print(k['pk'])
            try:
                if k['pk'] == self.pk:
                    k['task'] = str(self.ids.edit_task_text.text)
                    k['date'] = str(self.ids.edit_date_text.text)
            except TypeError:
                continue
        shelf_file['planer'] = todo

        shelf_file.close()


class DialogFeedback(BoxLayout):
    # Opens a dialog box where the user can add a task
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.date_text.text = str(datetime.now().strftime('%A %d %B %Y'))

    # Opens the date picker
    def show_date_picker(self):
        date_dialog = MDDatePicker(callback=self.get_date)
        date_dialog.open()

    # This functions gets the date from the date picker and converts its it a
    # more friendly form then changes the date label on the dialog to that
    def get_date(self, date):
        date = date.strftime('%A %d %B %Y')
        self.ids.date_text.text = str(date)
        print(date)


class DialogContent(BoxLayout):
    # Opens a dialog box where the user can add a task
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.date_text.text = str(datetime.now().strftime('%A %d %B %Y'))

    # Save task
    def save_task(self, value):
        the_task = Task(value)
        the_task.save_data_to_shelf()

    # Opens the date picker
    def show_date_picker(self):
        date_dialog = MDDatePicker(callback=self.get_date)
        date_dialog.open()

    # This functions gets the date from the date picker and converts its it a
    # more friendly form then changes the date label on the dialog to that
    def get_date(self, date):
        date = date.strftime('%A %d %B %Y')
        self.ids.date_text.text = str(date)
        print(date)


class ListItemWithCheckbox_OnStart(TwoLineAvatarIconListItem):
    pass


class ListItemWithCheckbox_default(TwoLineAvatarIconListItem):
    def __init__(self, check=False, pk=1, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ListItemWithCheckbox(TwoLineAvatarIconListItem):
    # Custom list item
    icon = StringProperty('calendar-check')

    def __init__(self,check = False, pk=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ids.check.active = check
        self.pk = pk


# Custom right container
class RightCheckbox(IRightBodyTouch, MDCheckbox):
    pass


class ConfirmDelete(BoxLayout):
    def __init__(self, widget=None, **kwargs):
        super().__init__(**kwargs)
        self.widget = widget

    # Delete task
    def delete_the_task(self):
        self.widget.parent.remove_widget(self.widget)
        self.delete_data_in_file()

        Snackbar(text= 'Task Deleted!').show()

    # Deleting data in the Planer application file
    def delete_data_in_file(self):
        # --------- Update the information in the shelve file ---------
        shelf_file = shelve.open('planer_data')
        todo = shelf_file['planer']
        for k in todo:
            try:
                if k['pk'] == self.widget.pk:
                    todo[todo.index(k)] = 'deleted'
                    k['completed'] = True
                    k['today'] = True

            except TypeError:
                continue

        shelf_file['planer'] = todo
        shelf_file.close()
        # -------------------------------------------------------------

    def close_confirm_dialog(self):
        # Closes the task feedback dialog
        self.confirm_dialog.dismiss()


# Logic task
# This class is responsible for creating a task
class Task:
    def __init__(self, task=None, date=None, completed=False, pk=1):
        self.task = str(task)
        self.completed = completed
        self.date = date
        self.pk = pk

    # By saving data to a shelve file, a task is successfully created, the task are loaded from the
    # shelve file
    def save_data_to_shelf(self):

        shelf_file = shelve.open('planer_data')

        # Exception Handler
        try:
            todo = shelf_file['planer']
            todo.append({'pk':self.pk,'task': self.task, 'completed': self.completed, 'date': self.date})
            print(todo)
            shelf_file['planer'] = todo
            shelf_file.close()
        
        except  KeyError:
            todo = []
            todo.append({'pk':1,'task': self.task, 'completed': self.completed, 'date': self.date})
            print(todo)
            shelf_file['planer'] = todo
            shelf_file.close()
        # End of the exception handler

    # Repeat function
    def retrive_everything(self):
        # Exception Handler
        try:
            shelf_file = shelve.open('planer_data')
            todo = shelf_file['planer']
            print(todo)
            shelf_file.close()
            
            return True
        
        except KeyError:
            print('Nothing in the shelf file yet')
            return False
        # End of the exception handler


# End task logic
class MainApp(MDApp):

    dialog = None

    def build(self):
        self.root = root = MainScreen()

        # ---------------- To avoid the error of adding a task behind the toolbar ---------------
        self.root.ids.container.add_widget(
            ListItemWithCheckbox_default(text="", secondary_text="")
        )

        self.root.ids.completed_container.add_widget(
            ListItemWithCheckbox_default(text="", secondary_text="")
        )
        # ---------------- To avoid the error of adding a task behind the toolbar ---------------

        return root

    # Date function
    def callback_clock(self):
        picker = MDDatePicker(callback=self.got_date)
        picker.open()

    # Checking the code health in the project console
    def got_date(self, the_date):
        print(the_date.year)
        print(the_date.month)
        print(the_date.day)

    def on_start(self):
        if Task().retrive_everything() == True:
            shelf_file = shelve.open('planer_data')
            todo = shelf_file['planer']

            for k in todo:
                try:
                    if k['completed'] == True:
                        self.root.ids.completed_container.add_widget(
                                ListItemWithCheckbox(text=k['task'], secondary_text="Due: "+k['date'], check=True, pk=k['pk'])
                            )
                    
                    elif k['completed'] == False:
                        self.root.ids.container.add_widget(
                                ListItemWithCheckbox(text=k['task'], secondary_text="Due: "+k['date'], pk=k['pk'])
                            )


                    shelf_file.close()
            
                except TypeError:
                    continue

    def show_feedback_dialog(self):
        self.feedback_dialog = MDDialog(title="FEEDBACK",
                              type="custom",
                              content_cls=DialogFeedback(),
                              size_hint=[.95, .60],
                              auto_dismiss=False,
                              )
        self.feedback_dialog.open()

    def close_feedback_dialog(self):
        # Closes the task feedback dialog
        self.feedback_dialog.dismiss()

    def feedback_sent(self):
        Snackbar(text='Message Sent').show()

    # Shows the task creation dialog
    def show_task_dialog(self):
        self.dialog = MDDialog(title="CREATE A NEW TASK",
                               type="custom",
                               content_cls=DialogContent(),
                               size_hint=[.95, .8],
                               auto_dismiss=False,
                               )
        self.dialog.open()

    # Closes the task creation dialog
    def close_dialog(self):
        self.dialog.dismiss()

    # Saves tasks by creating a list item and adding it to the container
    def save_task(self, value, date):
        # We want to generate a primary key for each widget from the number of items
        # in the shelf file list
        try:
            # Open shelf file
            shelf_file = shelve.open('planer_data')
            print("Getting planer list")
            todo = shelf_file['planer']
            print(todo)
            pk = len(todo)+1
            print(pk)

            ListItemWithCheckbox(text=".", secondary_text=".", pk=pk)

            shelf_file.close()

            if value and date:
                self.root.ids.container.add_widget(
                            ListItemWithCheckbox(text=value, secondary_text="Due: "+date, pk=pk)
                        )
                Task(value, date, pk=pk).save_data_to_shelf()
                Snackbar(text="Your task has been saved").show()
            else:
                MDDialog(title="ALERT",
                    text='Please add a task name',
                    size_hint=[.9, None]
                ).open()

        except KeyError:
            if value and date:
                self.root.ids.container.add_widget(
                            ListItemWithCheckbox(text=value, secondary_text="Due: "+date, pk=1)
                        )
                Task(value, date).save_data_to_shelf()
                Snackbar(text="Your task has been saved").show()
            else:
                MDDialog(title="ALERT",
                    text='Please add a task name!',
                    size_hint=[.9, None]
                ).open()

    def confirm_delete_task(self, widget):
        self.root.ids.container.remove_widget(widget)

    def mark(self, instance_check, widget):
        # Does something when the task checkbox is marked or unmarked
        if instance_check.active == True:
            print(True)
            print(widget.text)
            print(widget.secondary_text)
            self.root.ids.container.remove_widget(widget)
            self.root.ids.completed_container.add_widget(widget)
            Snackbar(text="Task Complete").show()

            # --------- Update the information in the shelve file ---------
            shelf_file = shelve.open('planer_data')
            todo = shelf_file['planer']
            for k in todo:
                try:
                    if k['pk'] == widget.pk:
                        k['completed'] = True

                except TypeError:
                    continue

            shelf_file['planer'] = todo
            shelf_file.close()
            # -------------------------------------------------------------

        if instance_check.active == False:
            print(False)
            
            self.root.ids.completed_container.remove_widget(widget)
            self.root.ids.container.add_widget(widget)
            Snackbar(text="TASK UNMARKED!").show()

            # --------- Update the information in the shelve file ---------
            shelf_file = shelve.open('planer_data')
            todo = shelf_file['planer']
            for k in todo:
                try:
                    if k['pk'] == widget.pk:
                        k['completed'] = False
                except TypeError:
                    continue
            
            shelf_file['planer'] = todo
            shelf_file.close()
            # -------------------------------------------------------------

    def show_detail(self, widget):
        # Shows the details of a selected task
        self.detail_dialog = MDDialog(
            title="TASK DETAIL",
            type="custom",
            content_cls=TaskDetailDialog(widget=widget),
            size_hint=[.8, .8],
            auto_dismiss=True,
        )

        self.detail_dialog.open()

    def close_detail_dialog(self):
        # Closes the task detail dialog
        self.detail_dialog.dismiss()

    def user_information_saved(self):
        Snackbar(text="Information Saved").show()

    def user_fields_cleared_saved(self):
        Snackbar(text="Fields Cleared").show()

    def night_mode(self):
        self.theme_cls.theme_style = "Dark" or "Light"

    def light_mode(self):
        self.theme_cls.theme_style = "Light" or "Dark"


MainApp().run()