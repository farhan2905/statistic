import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

class FitnessTracker:
    def __init__(self, csv_path='fitness_activities.csv'):
        self.csv_path = csv_path
        self.columns = ['date', 'activity_type', 'duration', 'calories_burned']
        self.df = self._load_data()

    def _load_data(self):
        if not os.path.exists(self.csv_path):
            print(f"No file found at '{self.csv_path}'. Starting new tracker.")
            return pd.DataFrame(columns=self.columns)
        try:
            df = pd.read_csv(self.csv_path)
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df['duration'] = pd.to_numeric(df['duration'], errors='coerce')
            df['calories_burned'] = pd.to_numeric(df['calories_burned'], errors='coerce')
            return df.dropna(subset=self.columns)
        except Exception as e:
            print(f"Failed to load data: {e}")
            return pd.DataFrame(columns=self.columns)

    def _save(self):
        try:
            self.df.to_csv(self.csv_path, index=False)
        except Exception as e:
            print(f"Failed to save data: {e}")

    def add_activity(self, date_str, activity_type, duration, calories):
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD.")
            return

        new_row = {
            'date': date,
            'activity_type': activity_type.strip(),
            'duration': int(duration),
            'calories_burned': int(calories)
        }
        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
        self._save()
        print("Activity added.")

    def daily_summary(self):
        if self.df.empty:
            print("No data available.")
            return pd.DataFrame()
        return self.df.groupby('date').agg(
            total_duration=('duration', 'sum'),
            total_calories=('calories_burned', 'sum')
        ).reset_index()

    def activity_trends(self):
        if self.df.empty:
            print("No data available.")
            return pd.DataFrame()
        return self.df.groupby('activity_type').agg(
            avg_duration=('duration', 'mean'),
            avg_calories=('calories_burned', 'mean')
        ).reset_index()

    def filter_by_date(self, start_date, end_date):
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format.")
            return pd.DataFrame()
        return self.df[(self.df['date'] >= start) & (self.df['date'] <= end)]

    def filter_by_type(self, activity_type):
        return self.df[self.df['activity_type'].str.lower() == activity_type.lower()]

    def plot_activity_distribution(self):
        if self.df.empty:
            print("No data to plot.")
            return
        plt.figure(figsize=(8, 5))
        sns.countplot(data=self.df, y='activity_type', order=self.df['activity_type'].value_counts().index)
        plt.title("Activity Frequency")
        plt.tight_layout()
        plt.show()

    def plot_calories_over_time(self):
        summary = self.daily_summary()
        if summary.empty:
            print("No data to plot.")
            return
        plt.figure(figsize=(10, 5))
        sns.lineplot(data=summary, x='date', y='total_calories', marker='o')
        plt.title("Calories Burned Over Time")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_duration_vs_calories(self):
        if self.df.empty:
            print("No data to plot.")
            return
        plt.figure(figsize=(8, 5))
        sns.scatterplot(data=self.df, x='duration', y='calories_burned', hue='activity_type', s=100)
        plt.title("Duration vs Calories Burned")
        plt.tight_layout()
        plt.show()


def get_input(prompt, cast_func=str, condition=lambda x: True, error="Invalid input."):
    while True:
        val = input(prompt)
        try:
            val = cast_func(val)
            if condition(val):
                return val
        except Exception:
            pass
        print(error)


def prompt_activity(tracker):
    date = get_input("Date (YYYY-MM-DD): ", str, lambda d: datetime.strptime(d, "%Y-%m-%d"), "Invalid date.")
    activity = get_input("Activity type: ", str, lambda x: x.strip() != "", "Activity can't be empty.")
    duration = get_input("Duration (minutes): ", int, lambda x: x > 0, "Must be a positive number.")
    calories = get_input("Calories burned: ", int, lambda x: x >= 0, "Must be zero or more.")
    tracker.add_activity(date, activity, duration, calories)


def main_menu():
    tracker = FitnessTracker()

    while True:
        print("\n--- Fitness Tracker ---")
        print("1. Add Activity")
        print("2. View Daily Summary")
        print("3. View Activity Trends")
        print("4. Filter by Date")
        print("5. Filter by Activity Type")
        print("6. Visualizations")
        print("7. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            prompt_activity(tracker)

        elif choice == '2':
            summary = tracker.daily_summary()
            if not summary.empty:
                print(summary)

        elif choice == '3':
            trends = tracker.activity_trends()
            if not trends.empty:
                print(trends)

        elif choice == '4':
            start = input("Start date (YYYY-MM-DD): ")
            end = input("End date (YYYY-MM-DD): ")
            filtered = tracker.filter_by_date(start, end)
            if not filtered.empty:
                print(filtered)
            else:
                print("No activities found in that range.")

        elif choice == '5':
            activity = input("Activity type to filter by: ")
            filtered = tracker.filter_by_type(activity)
            if not filtered.empty:
                print(filtered)
            else:
                print(f"No entries for activity type '{activity}'.")

        elif choice == '6':
            print("\n1. Activity Distribution")
            print("2. Calories Over Time")
            print("3. Duration vs Calories")
            viz = input("Choose visualization: ")
            if viz == '1':
                tracker.plot_activity_distribution()
            elif viz == '2':
                tracker.plot_calories_over_time()
            elif viz == '3':
                tracker.plot_duration_vs_calories()
            else:
                print("Invalid option.")

        elif choice == '7':
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main_menu()
