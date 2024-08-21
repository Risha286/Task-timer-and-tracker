from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import csv

# TaskTimerTracker class definition
class TaskTimerTracker:
    def __init__(self):
        self.tasks = {}
    
    def add_task(self, task_name):
        task_id = len(self.tasks) + 1
        self.tasks[task_id] = {
            'name': task_name,
            'sessions': [],
            'total_time': timedelta()
        }
        return task_id
    
    def start_timer(self, task_id):
        if task_id in self.tasks and (not self.tasks[task_id]['sessions'] or self.tasks[task_id]['sessions'][-1]['end'] is not None):
            start_time = datetime.now()
            self.tasks[task_id]['sessions'].append({'start': start_time, 'end': None})
        else:
            raise Exception("Timer is already running for this task or the task does not exist.")
    
    def stop_timer(self, task_id):
        if task_id in self.tasks and self.tasks[task_id]['sessions'][-1]['end'] is None:
            end_time = datetime.now()
            self.tasks[task_id]['sessions'][-1]['end'] = end_time
            session_time = end_time - self.tasks[task_id]['sessions'][-1]['start']
            self.tasks[task_id]['total_time'] += session_time
        else:
            raise Exception("No active timer found for this task.")
    
    def pause_timer(self, task_id):
        self.stop_timer(task_id)

    def resume_timer(self, task_id):
        self.start_timer(task_id)
    
    def delete_task(self, task_id):
        if task_id in self.tasks:
            del self.tasks[task_id]
        else:
            raise Exception("Task not found.")

    def edit_task_name(self, task_id, new_name):
        if task_id in self.tasks:
            self.tasks[task_id]['name'] = new_name
        else:
            raise Exception("Task not found.")
    
    def view_task_summary(self, task_id):
        if task_id in self.tasks:
            task = self.tasks[task_id]
            summary = f"Summary for Task: {task['name']}\n"
            for idx, session in enumerate(task['sessions'], 1):
                start = session['start'].strftime('%Y-%m-%d %H:%M:%S')
                end = session['end'].strftime('%Y-%m-%d %H:%M:%S') if session['end'] else 'Ongoing'
                summary += f"  Session {idx}: {start} - {end}\n"
            summary += f"Total Time Spent: {task['total_time']}\n"
            return summary
        else:
            raise Exception("Task not found.")
    
    def view_all_tasks_summary(self):
        summary = "All Tasks Summary:\n"
        for task_id, task in self.tasks.items():
            summary += f"Task ID: {task_id}, Task Name: {task['name']}, Total Time: {task['total_time']}\n"
        return summary

    def generate_report(self, time_frame):
        report = "Task Report:\n"
        time_frame_start = datetime.now() - timedelta(days=time_frame)
        for task_id, task in self.tasks.items():
            total_time_within_frame = timedelta()
            for session in task['sessions']:
                if session['end'] and session['end'] >= time_frame_start:
                    total_time_within_frame += session['end'] - session['start']
            report += f"Task ID: {task_id}, Task Name: {task['name']}, Time Spent: {total_time_within_frame}\n"
        return report

    def backup_data(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filename:
            with open(filename, 'w') as f:
                json.dump(self.tasks, f, default=str)

    def restore_data(self, backup_file):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            with open(filename, 'r') as f:
                data = json.load(f)
                for task_id, task in data.items():
                    task['total_time'] = timedelta(seconds=task['total_time'])
                    for session in task['sessions']:
                        session['start'] = datetime.strptime(session['start'], '%Y-%m-%d %H:%M:%S')
                        if session['end']:
                            session['end'] = datetime.strptime(session['end'], '%Y-%m-%d %H:%M:%S')
                self.tasks = data
    
    def export_summary(self, task_id, file_format):
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if file_format == 'CSV':
                filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
                if filename:
                    with open(filename, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Session', 'Start Time', 'End Time'])
                        for idx, session in enumerate(task['sessions'], 1):
                            start = session['start'].strftime('%Y-%m-%d %H:%M:%S')
                            end = session['end'].strftime('%Y-%m-%d %H:%M:%S') if session['end'] else 'Ongoing'
                            writer.writerow([idx, start, end])
            elif file_format == 'TXT':
                filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
                if filename:
                    with open(filename, 'w') as f:
                        f.write(f"Summary for Task: {task['name']}\n")
                        for idx, session in enumerate(task['sessions'], 1):
                            start = session['start'].strftime('%Y-%m-%d %H:%M:%S')
                            end = session['end'].strftime('%Y-%m-%d %H:%M:%S') if session['end'] else 'Ongoing'
                            f.write(f"  Session {idx}: {start} - {end}\n")
                        f.write(f"Total Time Spent: {task['total_time']}\n")
        else:
            raise Exception("Task not found.")


# TaskTimerApp class definition
class TaskTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Timer and Tracker")
        self.tracker = TaskTimerTracker()
        
        # GUI Elements
        self.task_name_label = tk.Label(root, text="Task Name:")
        self.task_name_label.grid(row=0, column=0)
        self.task_name_entry = tk.Entry(root)
        self.task_name_entry.grid(row=0, column=1)
        
        self.add_task_button = tk.Button(root, text="Add Task", command=self.add_task)
        self.add_task_button.grid(row=0, column=2)
        
        self.task_id_label = tk.Label(root, text="Task ID:")
        self.task_id_label.grid(row=1, column=0)
        self.task_id_entry = tk.Entry(root)
        self.task_id_entry.grid(row=1, column=1)
        
        self.start_button = tk.Button(root, text="Start Timer", command=self.start_timer)
        self.start_button.grid(row=1, column=2)
        
        self.stop_button = tk.Button(root, text="Stop Timer", command=self.stop_timer)
        self.stop_button.grid(row=1, column=3)
        
        self.pause_button = tk.Button(root, text="Pause Timer", command=self.pause_timer)
        self.pause_button.grid(row=1, column=4)
        
        self.resume_button = tk.Button(root, text="Resume Timer", command=self.resume_timer)
        self.resume_button.grid(row=1, column=5)
        
        self.view_summary_button = tk.Button(root, text="View Task Summary", command=self.view_task_summary)
        self.view_summary_button.grid(row=2, column=1)
        
        self.view_all_summary_button = tk.Button(root, text="View All Tasks Summary", command=self.view_all_tasks_summary)
        self.view_all_summary_button.grid(row=2, column=2)
        
        self.delete_task_button = tk.Button(root, text="Delete Task", command=self.delete_task)
        self.delete_task_button.grid(row=2, column=3)
        
        self.edit_task_name_button = tk.Button(root, text="Edit Task Name", command=self.edit_task_name)
        self.edit_task_name_button.grid(row=2, column=4)
        
        self.generate_report_button = tk.Button(root, text="Generate Report", command=self.generate_report)
        self.generate_report_button.grid(row=2, column=5)
        
        self.backup_data_button = tk.Button(root, text="Backup Data", command=self.backup_data)
        self.backup_data_button.grid(row=3, column=1)
        
        self.restore_data_button = tk.Button(root, text="Restore Data", command=self.restore_data)
        self.restore_data_button.grid(row=3, column=2)
        
        self.export_summary_button = tk.Button(root, text="Export Summary", command=self.export_summary)
        self.export_summary_button.grid(row=3, column=3)
    
    def add_task(self):
        task_name = self.task_name_entry.get()
        if task_name:
            task_id = self.tracker.add_task(task_name)
            messagebox.showinfo("Task Added", f"Task '{task_name}' added with ID {task_id}.")
        else:
            messagebox.showerror("Error", "Task name cannot be empty.")
    
    def start_timer(self):
        task_id = int(self.task_id_entry.get())
        try:
            self.tracker.start_timer(task_id)
            messagebox.showinfo("Timer Started", f"Timer started for task ID {task_id}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def stop_timer(self):
        task_id = int(self.task_id_entry.get())
        try:
            self.tracker.stop_timer(task_id)
            messagebox.showinfo("Timer Stopped", f"Timer stopped for task ID {task_id}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def pause_timer(self):
        task_id = int(self.task_id_entry.get())
        try:
            self.tracker.pause_timer(task_id)
            messagebox.showinfo("Timer Paused", f"Timer paused for task ID {task_id}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def resume_timer(self):
        task_id = int(self.task_id_entry.get())
        try:
            self.tracker.resume_timer(task_id)
            messagebox.showinfo("Timer Resumed", f"Timer resumed for task ID {task_id}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def delete_task(self):
        task_id = int(self.task_id_entry.get())
        try:
            self.tracker.delete_task(task_id)
            messagebox.showinfo("Task Deleted", f"Task ID {task_id} deleted.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def edit_task_name(self):
        task_id = int(self.task_id_entry.get())
        new_name = self.task_name_entry.get()
        try:
            self.tracker.edit_task_name(task_id, new_name)
            messagebox.showinfo("Task Updated", f"Task ID {task_id} name changed to '{new_name}'.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def view_task_summary(self):
        task_id = int(self.task_id_entry.get())
        try:
            summary = self.tracker.view_task_summary(task_id)
            messagebox.showinfo("Task Summary", summary)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def view_all_tasks_summary(self):
        summary = self.tracker.view_all_tasks_summary()
        messagebox.showinfo("All Tasks Summary", summary)
    
    def generate_report(self):
        time_frame = int(self.task_name_entry.get())
        report = self.tracker.generate_report(time_frame)
        messagebox.showinfo("Task Report", report)
    
    def backup_data(self):
        self.tracker.backup_data()
        messagebox.showinfo("Backup", "Data backed up successfully.")
    
    def restore_data(self):
        self.tracker.restore_data()
        messagebox.showinfo("Restore", "Data restored successfully.")
    
    def export_summary(self):
        task_id = int(self.task_id_entry.get())
        file_format = self.task_name_entry.get()
        try:
            self.tracker.export_summary(task_id, file_format.upper())
            messagebox.showinfo("Export", f"Task summary exported as {file_format.upper()}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# Running the GUI application
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskTimerApp(root)
    root.mainloop()
