import tkinter as tk
from tkinter import ttk, StringVar, PhotoImage
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from datetime import datetime
import warnings
from PIL import Image, ImageTk
from scipy.stats import ttest_ind, chi2_contingency
warnings.filterwarnings("ignore")

plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['figure.facecolor'] = '#ffffff'
sns.set_style("whitegrid", {'axes.grid': False, 'axes.linewidth': 1.5})

class IPLDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("IPL Dashboard 2025")
        self.root.state('zoomed')  
        self.root.configure(bg="#001133")

        # Team colors
        self.team_colors = {
            "Chennai Super Kings": "#ffd633",
            "Mumbai Indians": "#004BA0",
            "Royal Challengers Bengaluru": "#EC1C24",
            "Kolkata Knight Riders": "#3A225D",
            "Delhi Capitals": "#0078BC",
            "Sunrisers Hyderabad": "#F7A721",
            "Punjab Kings": "#ED1B24",
            "Rajasthan Royals": "#ff007c",
            "Gujarat Titans": "#1C1C1C",
            "Lucknow Super Giants": "#A72056"
        }

        # Light variants of team colors for backgrounds
        self.team_colors_light = {
            "Chennai Super Kings": "#FFFF99",
            "Mumbai Indians": "#6699CC",
            "Royal Challengers Bengaluru": "#F4A6A9",
            "Kolkata Knight Riders": "#AFA6C5",
            "Delhi Capitals": "#66B2D8",
            "Sunrisers Hyderabad": "#FBCF94",
            "Punjab Kings": "#F4A6A9",
            "Rajasthan Royals": "#90A8D0",
            "Gujarat Titans": "#666666",
            "Lucknow Super Giants": "#C77F9A"
        }

        # Player Performance section color theme
        self.player_section_colors = {
            "header": "#6A0DAD", 
            "background": "#E6E6FA",  
            "text": "#4B0082"  
        }

        # Team logos (placeholders for paths)
        self.team_logos = {
            "Chennai Super Kings": "Csk.png",
            "Mumbai Indians": "MI.png",
            "Royal Challengers Bengaluru": "RCB.png",
            "Kolkata Knight Riders": "kkr.png",
            "Delhi Capitals": "DC.png",
            "Sunrisers Hyderabad": "SRH.png",
            "Punjab Kings": "punjB.png",
            "Rajasthan Royals": "RR.png",
            "Gujarat Titans": "GT.png",
            "Lucknow Super Giants": "LSG.png"
        }

        # Placeholder for IPL logo path 
        self.ipl_logo_path = "ipllogo.png"

        # Placeholder for trophy image path 
        self.trophy_image_path = "trophy.png"

        # Trophy counts for teams
        self.trophy_count = {
            "Mumbai Indians": 5,
            "Chennai Super Kings": 5,
            "Kolkata Knight Riders": 3,
            "Gujarat Titans": 1,
            "Rajasthan Royals": 1,
            "Sunrisers Hyderabad": 1,
            "Royal Challengers Bengaluru": 0,
            "Delhi Capitals": 0,
            "Punjab Kings": 0,
            "Lucknow Super Giants": 0
        }

        # Initialize filter variables
        self.selected_team1 = StringVar(value=list(self.team_colors.keys())[0])
        self.selected_team2 = StringVar(value=list(self.team_colors.keys())[1])
        self.selected_season = StringVar(value="All")  # Default to 'All'
        self.selected_player = StringVar(value="")

        self.load_data()
        self.create_layout()
        self.create_sidebar()
        self.show_frame("home")

    def load_data(self):
        try:
            self.schedule_df = pd.read_csv('IPL_2025_Match_Schedule_Full.csv')
            self.matches_df = pd.read_csv('ipl_all_matches (1).csv')
            self.players_df = pd.read_csv('Player_Performance (1).csv')
            self.points_df = pd.read_csv('points_table_historic (1).csv')
            self.process_data()
            self.selected_player.set(self.players_df['Player'].iloc[0] if not self.players_df.empty else "")
        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def process_data(self):
        team_name_map = {
            "Chennai Super Kings": ["Chennai Super Kings", "CSK"],
            "Mumbai Indians": ["Mumbai Indians", "MI"],
            "Royal Challengers Bengaluru": ["Royal Challengers Bangalore", "Royal Challengers Bengaluru", "RCB"],
            "Kolkata Knight Riders": ["Kolkata Knight Riders", "KKR"],
            "Delhi Capitals": ["Delhi Capitals", "Delhi Daredevils", "DC", "DD"],
            "Sunrisers Hyderabad": ["Sunrisers Hyderabad", "SRH"],
            "Punjab Kings": ["Punjab Kings", "Kings XI Punjab", "PBKS", "KXIP"],
            "Rajasthan Royals": ["Rajasthan Royals", "RR"],
            "Gujarat Titans": ["Gujarat Titans", "GT"],
            "Lucknow Super Giants": ["Lucknow Super Giants", "LSG"]
        }

        def standardize_team_name(name):
            if pd.isna(name):
                return name
            for std_name, variations in team_name_map.items():
                if name in variations:
                    return std_name
            return name

        self.matches_df['team1'] = self.matches_df['team1'].apply(standardize_team_name)
        self.matches_df['team2'] = self.matches_df['team2'].apply(standardize_team_name)
        self.matches_df['winner'] = self.matches_df['winner'].apply(standardize_team_name)
        self.matches_df['toss_winner'] = self.matches_df['toss_winner'].apply(standardize_team_name)
        self.points_df['team'] = self.points_df['team'].apply(standardize_team_name)
        self.schedule_df['Home'] = self.schedule_df['Home'].apply(standardize_team_name)
        self.schedule_df['Away'] = self.schedule_df['Away'].apply(standardize_team_name)

        self.players = self.players_df['Player'].dropna().unique().tolist()
        self.seasons = ['All'] + sorted(self.matches_df['season'].dropna().unique().tolist())
        self.calculate_points_table()

    def calculate_points_table(self, season=None):
        if season is None:
            season = self.selected_season.get() or "All"

        teams = list(self.team_colors.keys())
        points_data = []

        if season == "All":
            season_matches = self.matches_df
        else:
            season_matches = self.matches_df[self.matches_df['season'] == season]

        for team in teams:
            team_matches = season_matches[(season_matches['team1'] == team) | (season_matches['team2'] == team)]
            matches_played = len(team_matches)
            matches_won = len(season_matches[season_matches['winner'] == team])
            matches_lost = matches_played - matches_won

            runs_scored = 0
            overs_faced = 0
            runs_conceded = 0
            overs_bowled = 0

            for _, match in team_matches.iterrows():
                if match['team1'] == team:
                    if not pd.isna(match['target_runs']):
                        runs_scored += match['target_runs']
                        overs_faced += match['target_overs']
                    if match['team2'] == team:
                        runs_conceded += match['target_runs']
                        overs_bowled += match['target_overs']
                else:
                    if not pd.isna(match['target_runs']):
                        runs_conceded += match['target_runs']
                        overs_bowled += match['target_overs']
                    if match['team1'] == team:
                        runs_scored += match['target_runs']
                        overs_faced += match['target_overs']

            nrr = ((runs_scored / overs_faced) - (runs_conceded / overs_bowled)) if overs_faced > 0 and overs_bowled > 0 else 0

            points_data.append({
                'year': season,
                'team': team,
                'matchs played': matches_played,
                'Won': matches_won,
                'Lost': matches_lost,
                'Net Run Rate': round(nrr, 3),
                'points': matches_won * 2
            })

        self.current_points_table = pd.DataFrame(points_data)
        self.current_points_table = self.current_points_table.sort_values(by=['points', 'Net Run Rate'], ascending=[False, False])
        self.current_points_table['pos'] = range(1, len(self.current_points_table) + 1)

    def create_layout(self):
        self.main_container = tk.Frame(self.root, bg="#ffffff")
        self.main_container.pack(side="right", fill="both", expand=True)

        self.frames = {}
        self.canvas = {}
        self.scrollable_frame = {}
        self.v_scrollbar = {}

        for section in ["home", "team_comparison", "team_performance", "player_performance", "season_trends"]:
            self.frames[section] = tk.Frame(self.main_container, bg="#ffffff")
            self.frames[section].pack(fill="both", expand=True)
            self.frames[section].pack_forget()

            self.canvas[section] = tk.Canvas(self.frames[section], bg="#ffffff", highlightthickness=0)
            self.canvas[section].pack(side="left", fill="both", expand=True)

            self.v_scrollbar[section] = ttk.Scrollbar(self.frames[section], orient="vertical", command=self.canvas[section].yview)
            self.v_scrollbar[section].pack(side="right", fill="y")

            self.canvas[section].configure(yscrollcommand=self.v_scrollbar[section].set)

            self.scrollable_frame[section] = tk.Frame(self.canvas[section], bg="#ffffff")
            self.canvas[section].create_window((0, 0), window=self.scrollable_frame[section], anchor="nw")

            self.scrollable_frame[section].bind("<Configure>", lambda e, s=section: self.canvas[s].configure(scrollregion=self.canvas[s].bbox("all")))

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.root, width=300, bg="#001133", padx=20, pady=20) 
        self.sidebar.pack(side="left", fill="y")

        title_label = tk.Label(self.sidebar, text="IPL DASHBOARD", font=("Arial", 18, "bold"), bg="#001133", fg="#ffffff")
        title_label.pack(pady=15)

        season_label = tk.Label(self.sidebar, text="2025 Season", font=("Arial", 12), bg="#001133", fg="#7f8fa6")
        season_label.pack(pady=15)

        nav_buttons = [
            ("Home", lambda: self.show_frame("home")),
            ("Team Comparison", lambda: self.show_frame("team_comparison")),
            ("Team Performance", lambda: self.show_frame("team_performance")),
            ("Player Performance", lambda: self.show_frame("player_performance")),
            ("Season Trends", lambda: self.show_frame("season_trends"))
        ]
        icon_dict = {
            "Home": "🏡",
            "Team Comparison": "🆚",
            "Team Performance": "💪",
            "Player Performance": "🏏",
            "Season Trends": "📈"
        }

        for text, command in nav_buttons:
            frame = tk.Frame(self.sidebar, bg="#001133", pady=5)
            frame.pack(fill="x", pady=5)

            icon = icon_dict[text]
            icon_label = tk.Label(frame, text=icon, font=("Arial", 14), bg="#001133", fg="#ffffff")
            icon_label.pack(side="left", padx=8)

            button = tk.Button(frame, text=text, font=("Arial", 12), bg="#001133", fg="#ffffff", bd=0,
                               activebackground="#162955", activeforeground="#ffffff", command=command)
            button.pack(fill="x", padx=8)



        filter_label = tk.Label(self.sidebar, text="FILTERS", font=("Arial", 14, "bold"), bg="#001133", fg="#ffffff")
        filter_label.pack(pady=(10, 5), anchor="w")

        teams_label = tk.Label(self.sidebar, text="Teams", font=("Arial", 12), bg="#001133", fg="#7f8fa6")
        teams_label.pack(pady=(10, 5), anchor="w")

        teams = list(self.team_colors.keys())
        team1_dropdown = ttk.Combobox(self.sidebar, textvariable=self.selected_team1, values=teams, state="readonly", font=("Arial", 12))
        team1_dropdown.pack(fill="x", pady=5, padx=10)

        team1_frame = tk.Frame(self.sidebar, bg="#162955", pady=5)
        team1_frame.pack(fill="x", pady=5)
        team1_label = tk.Label(team1_frame, textvariable=self.selected_team1, bg="#162955", fg="#ffffff", padx=10, font=("Arial", 12))
        team1_label.pack(side="left")
        team1_remove = tk.Button(team1_frame, text="✕", bg="#162955", fg="#ffffff", bd=0, command=lambda: self.remove_team(1), font=("Arial", 12))
        team1_remove.pack(side="right")

        team2_dropdown = ttk.Combobox(self.sidebar, textvariable=self.selected_team2, values=teams, state="readonly", font=("Arial", 12))
        team2_dropdown.pack(fill="x", pady=5, padx=10)

        team2_frame = tk.Frame(self.sidebar, bg="#162955", pady=5)
        team2_frame.pack(fill="x", pady=5)
        team2_label = tk.Label(team2_frame, textvariable=self.selected_team2, bg="#162955", fg="#ffffff", padx=10, font=("Arial", 12))
        team2_label.pack(side="left")
        team2_remove = tk.Button(team2_frame, text="✕", bg="#162955", fg="#ffffff", bd=0, command=lambda: self.remove_team(2), font=("Arial", 12))
        team2_remove.pack(side="right")

        seasons_label = tk.Label(self.sidebar, text="Seasons", font=("Arial", 12), bg="#001133", fg="#7f8fa6")
        seasons_label.pack(pady=(10, 5), anchor="w")
        season_dropdown = ttk.Combobox(self.sidebar, textvariable=self.selected_season, values=self.seasons, state="readonly", font=("Arial", 12))
        season_dropdown.pack(fill="x", pady=5, padx=5)

        player_label = tk.Label(self.sidebar, text="Player", font=("Arial", 12), bg="#001133", fg="#7f8fa6")
        player_label.pack(pady=(10, 5), anchor="w")
        player_dropdown = ttk.Combobox(self.sidebar, textvariable=self.selected_player, values=self.players, state="readonly", font=("Arial", 12))
        player_dropdown.pack(fill="x", pady=5, padx=5)

        apply_button = tk.Button(self.sidebar, text="Apply Filters", bg="#4cd137", fg="#ffffff", font=("Arial", 12),
                                 command=self.update_dashboard)
        apply_button.pack(fill="x", pady=5)

        reset_button = tk.Button(self.sidebar, text="Reset Filters", bg="#e84118", fg="#ffffff", font=("Arial", 12),
                                 command=self.reset_filters)
        reset_button.pack(fill="x", pady=5)

    def remove_team(self, team_num):
        if team_num == 1:
            self.selected_team1.set("")
        else:
            self.selected_team2.set("")
        self.update_dashboard()

    def reset_filters(self):
        self.selected_team1.set("Chennai Super Kings")
        self.selected_team2.set("Mumbai Indians")
        self.selected_season.set("All")
        self.selected_player.set(self.players[0] if self.players else "")
        self.update_dashboard()

    def show_frame(self, frame_name):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[frame_name].pack(fill="both", expand=True)

        if frame_name == "home":
            self.update_home_section()
        elif frame_name == "team_comparison":
            self.update_team_comparison_section()
        elif frame_name == "team_performance":
            self.update_team_performance_section()
        elif frame_name == "player_performance":
            self.update_player_performance_section()
        elif frame_name == "season_trends":
            self.update_season_trends_section()

    def update_dashboard(self):
        self.calculate_points_table()
        for frame_name, frame in self.frames.items():
            if frame.winfo_ismapped():
                self.show_frame(frame_name)
                break

    def create_stat_box(self, parent, title, value, color="#4cd137", font_size=18):
        box = tk.Frame(parent, bg="#D4EFDF", bd=2, relief="solid") 
        box.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        title_label = tk.Label(box, text=title, font=("Arial", 12, "bold"), bg="#D4EFDF", fg="#2f3542")
        title_label.pack(pady=(10, 0))

        text_color = "#0000FF" if self.selected_team1.get() == "Chennai Super Kings" else color
        value_label = tk.Label(box, text=value, font=("Arial", font_size, "bold"), bg="#D4EFDF", fg=text_color)
        value_label.pack(pady=(0, 10))

        return box

    def create_logo_space(self, parent, team_name, width=180, height=180): 
        logo_frame = tk.Frame(parent, width=width, height=height, bg="#ffffff")
        logo_frame.pack_propagate(False)
        logo_path = self.team_logos.get(team_name, "")
        if logo_path:
            try:
                image = Image.open(logo_path)
                image = image.resize((180, 180), Image.LANCZOS)
                logo_image = ImageTk.PhotoImage(image)
                logo_label = tk.Label(logo_frame, image=logo_image, bg="#ffffff")
                logo_label.image = logo_image
                logo_label.pack(fill="both", expand=True)
            except Exception as e:
                print(f"Error loading logo for {team_name}: {e}")
                logo_label = tk.Label(logo_frame, text=f"{team_name}\nLogo", font=("Arial", 12), bg="#f1f2f6")
                logo_label.pack(fill="both", expand=True)
        else:
            logo_label = tk.Label(logo_frame, text=f"{team_name}\nLogo", font=("Arial", 12), bg="#f1f2f6")
            logo_label.pack(fill="both", expand=True)
        return logo_frame

    def create_trophy_space(self, parent, count, width=72, height=72, bg_color="#ffffff"):
        trophy_frame = tk.Frame(parent, bg=bg_color)
        trophy_frame.pack(side="left", padx=5)
        if count == 0:
            text_color = "#0000FF" if self.selected_team1.get() == "Chennai Super Kings" else "#95a5a6"
            label = tk.Label(trophy_frame, text="[No Trophies]", font=("Arial", 10), bg=bg_color, fg=text_color)
            label.pack()
        else:
            for _ in range(count):
                trophy_space = tk.Frame(trophy_frame, width=width, height=height, bg=bg_color)
                trophy_space.pack_propagate(False)
                trophy_space.pack(side="left", padx=2)
                if self.trophy_image_path:
                    try:
                        image = Image.open(self.trophy_image_path)
                        image = image.resize((72, 72), Image.LANCZOS)
                        trophy_image = ImageTk.PhotoImage(image)
                        trophy_label = tk.Label(trophy_space, image=trophy_image, bg=bg_color)
                        trophy_label.image = trophy_image
                        trophy_label.pack(fill="both", expand=True)
                    except Exception as e:
                        print(f"Error loading trophy image: {e}")
                        trophy_label = tk.Label(trophy_space, text="Trophy", font=("Arial", 10), bg=bg_color)
                        trophy_label.pack(fill="both", expand=True)
                else:
                    trophy_label = tk.Label(trophy_space, text="Trophy", font=("Arial", 10), bg=bg_color)
                    trophy_label.pack(fill="both", expand=True)
        return trophy_frame

    def update_home_section(self):
        for widget in self.scrollable_frame["home"].winfo_children():
            widget.destroy()

        team_color = "#004BA0"
        text_color = "#0000FF" if self.selected_team1.get() == "Chennai Super Kings" else team_color
        background_color = "#F0F4F8"  

        header_frame = tk.Frame(self.scrollable_frame["home"], bg=team_color, pady=15)
        header_frame.pack(fill="x")

        ipl_logo_frame = tk.Frame(header_frame, width=180, height=180, bg=team_color)  
        ipl_logo_frame.pack(side="left", padx=20)
        ipl_logo_frame.pack_propagate(False)
        if self.ipl_logo_path:
            try:
                image = Image.open(self.ipl_logo_path)
                image = image.resize((180, 180), Image.LANCZOS)
                ipl_logo_image = ImageTk.PhotoImage(image)
                ipl_logo_label = tk.Label(ipl_logo_frame, image=ipl_logo_image, bg=team_color)
                ipl_logo_label.image = ipl_logo_image
                ipl_logo_label.pack(fill="both", expand=True)
            except Exception as e:
                print(f"Error loading IPL logo: {e}")
                ipl_logo_label = tk.Label(ipl_logo_frame, text="IPL Logo", font=("Arial", 16), bg="#ffffff", fg=team_color)
                ipl_logo_label.pack(fill="both", expand=True)
        else:
            ipl_logo_label = tk.Label(ipl_logo_frame, text="IPL Logo", font=("Arial", 16), bg="#ffffff", fg=team_color)
            ipl_logo_label.pack(fill="both", expand=True)

        header_title = tk.Label(header_frame, text="INDIAN PREMIER LEAGUE", font=("Arial", 24, "bold"), bg=team_color, fg="#ffffff")
        header_title.pack(side="left", expand=True)

        content_frame = tk.Frame(self.scrollable_frame["home"], bg=background_color, padx=20, pady=10)
        content_frame.pack(fill="both", expand=True)

        fixtures_frame = tk.Frame(content_frame, bg="#ffffff", bd=2, relief="solid")
        fixtures_frame.pack(fill="x")

        fixtures_title = tk.Label(fixtures_frame, text="Today's Fixtures", font=("Arial", 16, "bold"), bg="#ffffff", fg=text_color)
        fixtures_title.pack(fill="x")

        today = datetime.now().strftime("%d-%b-%y")
        today_matches = self.schedule_df[self.schedule_df['Date'].str.contains(today[:5], case=False, regex=False)]

        if len(today_matches) == 0:
            first_match = self.schedule_df.iloc[0]
            match_text = f"{first_match['Home']} vs {first_match['Away']} - {first_match['Start']} - {first_match['Venue']}"
            match_label = tk.Label(fixtures_frame, text=match_text, font=("Arial", 28, "bold"), bg="#ffffff", fg=text_color, bd=2, relief="solid")
            match_label.pack(fill="x", expand=True)
        else:
            for _, row in today_matches.iterrows():
                match_text = f"{row['Home']} vs {row['Away']} - {row['Start']} - {row['Venue']}"
                match_label = tk.Label(fixtures_frame, text=match_text, font=("Arial", 28, "bold"), bg="#ffffff", fg=text_color, bd=2, relief="solid")
                match_label.pack(fill="x", expand=True)

        main_content = tk.Frame(content_frame, bg=background_color)
        main_content.pack(fill="both", expand=True)

        # Row 0: Stats Boxes with Variance
        stats_frame = tk.Frame(main_content, bg=background_color, pady=10)
        stats_frame.pack(fill="x")

        season_matches = self.matches_df if self.selected_season.get() == "All" else self.matches_df[self.matches_df['season'] == self.selected_season.get()]
        total_matches = len(season_matches)
        total_runs = season_matches['target_runs'].sum()
        avg_runs = season_matches['target_runs'].mean() if not season_matches['target_runs'].empty else 0
        runs_variance = season_matches['target_runs'].var() if not season_matches['target_runs'].empty else 0

        box1 = self.create_stat_box(stats_frame, "Total Matches", str(total_matches), team_color)
        box2 = self.create_stat_box(stats_frame, "Total Runs", f"{total_runs:.0f}", team_color)
        box3 = self.create_stat_box(stats_frame, "Avg Runs", f"{avg_runs:.1f}", team_color)
        box4 = self.create_stat_box(stats_frame, "Runs Variance", f"{runs_variance:.1f}", team_color)

        # Row 1: Points Table and Pie Chart
        row1_frame = tk.Frame(main_content, bg=background_color)
        row1_frame.pack(fill="both", expand=True, pady=10)

        # Left:Points Table
        left_frame = tk.Frame(row1_frame, bg=background_color)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        points_title = tk.Label(left_frame, text=f"Points Table {self.selected_season.get()}", font=("Arial", 16, "bold"), bg=background_color, fg=text_color, pady=10)
        points_title.pack(fill="x")

        points_table_frame = tk.Frame(left_frame, bg="#ffffff", bd=2, relief="solid")
        points_table_frame.pack(fill="both", expand=True, pady=10)

        # Calculating points table and sorting by pos
        self.calculate_points_table(self.selected_season.get())
        # Converting 'pos' column to integer for proper numerical sorting
        self.current_points_table['pos'] = self.current_points_table['pos'].astype(int)
        # Sorting just before rendering to ensure order is maintained
        self.current_points_table = self.current_points_table.sort_values(by='pos', ascending=True)
        print("Sorted Points Table:", self.current_points_table) 

        columns = ["Pos", "Team", "M", "W", "L", "NRR", "Pts"]
        for i, col in enumerate(columns):
            header = tk.Label(points_table_frame, text=col, font=("Arial", 12, "bold"), bg=team_color, fg="#ffffff",
                              padx=10, pady=10, borderwidth=1, relief="solid", width=5 if col != "Team" else 15)
            header.grid(row=0, column=i, sticky="nsew")

        for i, row in self.current_points_table.iterrows():
            bg_color = "#e6f0fa" if i % 2 == 0 else "#f0f8ff"
            tk.Label(points_table_frame, text=str(row['pos']), font=("Arial", 12), bg=bg_color, fg=text_color, padx=10, pady=10,
                     borderwidth=1, relief="solid").grid(row=i+1, column=0, sticky="nsew")
            tk.Label(points_table_frame, text=row['team'], font=("Arial", 12), bg=bg_color, fg=text_color, padx=10, pady=10,
                     borderwidth=1, relief="solid", anchor="w").grid(row=i+1, column=1, sticky="nsew")
            tk.Label(points_table_frame, text=str(row['matchs played']), font=("Arial", 12), bg=bg_color, fg=text_color, padx=10, pady=10,
                     borderwidth=1, relief="solid").grid(row=i+1, column=2, sticky="nsew")
            tk.Label(points_table_frame, text=str(row['Won']), font=("Arial", 12), bg=bg_color, fg=text_color, padx=10, pady=10,
                     borderwidth=1, relief="solid").grid(row=i+1, column=3, sticky="nsew")
            tk.Label(points_table_frame, text=str(row['Lost']), font=("Arial", 12), bg=bg_color, fg=text_color, padx=10, pady=10,
                     borderwidth=1, relief="solid").grid(row=i+1, column=4, sticky="nsew")
            tk.Label(points_table_frame, text=str(row['Net Run Rate']), font=("Arial", 12), bg=bg_color, fg=text_color, padx=10, pady=10,
                     borderwidth=1, relief="solid").grid(row=i+1, column=5, sticky="nsew")
            tk.Label(points_table_frame, text=str(row['points']), font=("Arial", 12, "bold"), bg=bg_color, fg=text_color, padx=10, pady=10,
                     borderwidth=1, relief="solid").grid(row=i+1, column=6, sticky="nsew")

        for i in range(7):
            points_table_frame.grid_columnconfigure(i, weight=1 if i != 1 else 3)

        # Right: Pie Chart
        right_frame = tk.Frame(row1_frame, bg=background_color)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        chart_frame_wrapper = tk.Frame(right_frame, bg=background_color)
        chart_frame_wrapper.pack(fill="both", expand=True)

        chart_title = tk.Label(chart_frame_wrapper, text="Most Successful Teams (Top 5)", font=("Arial", 16, "bold"), bg=background_color, fg=text_color, pady=10)
        chart_title.pack(fill="x")

        chart_inner_frame = tk.Frame(chart_frame_wrapper, bg=background_color)
        chart_inner_frame.pack(fill="both", expand=True)

        chart_frame = tk.Frame(chart_inner_frame, bg="#E3F2FD", bd=2, relief="solid") 
        chart_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        fig, ax = plt.subplots(figsize=(6, 4))
        team_success = {}
        for team in self.current_points_table['team'].unique():
            team_matches = season_matches[(season_matches['team1'] == team) | (season_matches['team2'] == team)]
            team_wins = season_matches[season_matches['winner'] == team]
            win_percentage = (len(team_wins) / len(team_matches) * 100) if len(team_matches) > 0 else 0
            team_success[team] = win_percentage

        team_success = {k: v for k, v in sorted(team_success.items(), key=lambda item: item[1], reverse=True)[:5]}
        colors = [self.team_colors.get(team, '#3498db') for team in team_success.keys()]
        ax.pie(list(team_success.values()), labels=list(team_success.keys()), autopct='%1.1f%%', startangle=90,
               colors=colors, wedgeprops=dict(width=0.5, edgecolor='white'))
        centre_circle = plt.Circle((0, 0), 0.3, fc='white')
        ax.add_artist(centre_circle)
        ax.set_aspect('equal')

        chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        chart_canvas.draw()
        chart_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Blank space where stats box was
        blank_space = tk.Frame(chart_inner_frame, bg=background_color)
        blank_space.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Row 2: Bar Chart and Trophy Table
        row2_frame = tk.Frame(main_content, bg=background_color)
        row2_frame.pack(fill="both", expand=True, pady=10)

        # Left: Bar Chart
        left_frame2 = tk.Frame(row2_frame, bg=background_color)
        left_frame2.pack(side="left", fill="both", expand=True, padx=(0, 10))

        bar_frame_wrapper = tk.Frame(left_frame2, bg=background_color)
        bar_frame_wrapper.pack(fill="both", expand=True)

        bar_title = tk.Label(bar_frame_wrapper, text="Top 5 Teams by Win %", font=("Arial", 16, "bold"), bg=background_color, fg=text_color, pady=10)
        bar_title.pack(fill="x")

        bar_inner_frame = tk.Frame(bar_frame_wrapper, bg=background_color)
        bar_inner_frame.pack(fill="both", expand=True)

        bar_frame = tk.Frame(bar_inner_frame, bg="#E3F2FD", bd=2, relief="solid") 
        bar_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        fig2, ax2 = plt.subplots(figsize=(6, 4))
        win_data = pd.Series(team_success).head(5)
        sns.barplot(x=win_data.index, y=win_data.values, ax=ax2, palette=[self.team_colors.get(team, '#3498db') for team in win_data.index])
        ax2.set_xlabel('Team')
        ax2.set_ylabel('Win %')
        ax2.tick_params(axis='x', rotation=45)
        ax2.set_title('Top 5 Teams by Win Percentage')

        bar_canvas = FigureCanvasTkAgg(fig2, master=bar_frame)
        bar_canvas.draw()
        bar_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Blank space where stats box was
        blank_space = tk.Frame(bar_inner_frame, bg=background_color)
        blank_space.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Right: Trophy Table
        right_frame2 = tk.Frame(row2_frame, bg=background_color)
        right_frame2.pack(side="right", fill="both", expand=True, padx=(10, 0))

        trophy_title = tk.Label(right_frame2, text="Trophy Count", font=("Arial", 16, "bold"), bg=background_color, fg=text_color, pady=10)
        trophy_title.pack(fill="x")

        trophy_frame = tk.Frame(right_frame2, bg="#ffffff", bd=2, relief="solid")
        trophy_frame.pack(fill="both", expand=True)

        trophy_count = {
            "Mumbai Indians": 5,
            "Chennai Super Kings": 5,
            "Kolkata Knight Riders": 3,
            "Gujarat Titans": 1,
            "Rajasthan Royals": 1,
            "Sunrisers Hyderabad": 1,
            "Royal Challengers Bengaluru": 0,
            "Delhi Capitals": 0,
            "Punjab Kings": 0,
            "Lucknow Super Giants": 0
        }
        trophy_count = {k: v for k, v in sorted(trophy_count.items(), key=lambda item: item[1], reverse=True)}

        trophy_columns = ["Team", "Trophies"]
        for i, col in enumerate(trophy_columns):
            header = tk.Label(trophy_frame, text=col, font=("Arial", 12, "bold"), bg=team_color, fg="#ffffff",
                              padx=10, pady=10, borderwidth=1, relief="solid", width=15 if col == "Team" else 10)
            header.grid(row=0, column=i, sticky="nsew")

        for i, (team, count) in enumerate(trophy_count.items()):
            bg_color = "#e6f0fa" if i % 2 == 0 else "#f0f8ff"
            tk.Label(trophy_frame, text=team, font=("Arial", 12), bg=bg_color, fg=text_color, padx=10, pady=10,
                     borderwidth=1, relief="solid", anchor="w").grid(row=i+1, column=0, sticky="nsew")
            tk.Label(trophy_frame, text=str(count), font=("Arial", 12, "bold"), bg=bg_color, fg=text_color, padx=10, pady=10,
                     borderwidth=1, relief="solid").grid(row=i+1, column=1, sticky="nsew")

        trophy_frame.grid_columnconfigure(0, weight=3)
        trophy_frame.grid_columnconfigure(1, weight=1)

        # Row 3: Trophy Images
        row3_frame = tk.Frame(main_content, bg=background_color)
        row3_frame.pack(fill="both", expand=True, pady=10)

        trophy_images_title = tk.Label(row3_frame, text="Trophies Won by Teams", font=("Arial", 16, "bold"), bg=background_color, fg=text_color, pady=10)
        trophy_images_title.pack(fill="x")

        trophy_images_frame = tk.Frame(row3_frame, bg="#ffffff", bd=2, relief="solid")
        trophy_images_frame.pack(fill="both", expand=True)

        for team, count in trophy_count.items():
            team_frame = tk.Frame(trophy_images_frame, bg="#ffffff")
            team_frame.pack(fill="x", pady=5)

            team_label = tk.Label(team_frame, text=team, font=("Arial", 12), bg="#ffffff", fg=text_color, width=20, anchor="w")
            team_label.pack(side="left", padx=10)

            self.create_trophy_space(team_frame, count)
    def update_team_comparison_section(self):
        for widget in self.scrollable_frame["team_comparison"].winfo_children():
            widget.destroy()

        team1 = self.selected_team1.get()
        team2 = self.selected_team2.get()
        team_color = self.team_colors.get(team1, "#3498db")
        text_color = "#cccccc" if self.selected_team1.get() == "Chennai Super Kings" else team_color

        if not team1 or not team2:
            msg_label = tk.Label(self.scrollable_frame["team_comparison"], text="Please select two teams to compare",
                                 font=("Arial", 16, "bold"), bg="#ffffff", fg="#7f8fa6", pady=50)
            msg_label.pack(fill="both", expand=True)
            return

        filtered_matches = self.matches_df if self.selected_season.get() == "All" else self.matches_df[self.matches_df['season'] == self.selected_season.get()]

        header_frame = tk.Frame(self.scrollable_frame["team_comparison"], bg=team_color, pady=15)
        header_frame.pack(fill="x")

        team1_frame = tk.Frame(header_frame, bg=team_color)
        team1_frame.pack(side="left", padx=20)
        team1_logo_frame = self.create_logo_space(team1_frame, team1)
        team1_logo_frame.pack()
        team1_name = tk.Label(team1_frame, text=team1, font=("Arial", 16, "bold"), bg=team_color, fg="#cffff7")
        team1_name.pack(pady=5)

        vs_label = tk.Label(header_frame, text="VS", font=("Arial", 30, "bold"), bg=team_color, fg="#ffffff")
        vs_label.pack(side="left", expand=True)

        team2_frame = tk.Frame(header_frame, bg=team_color)
        team2_frame.pack(side="right", padx=20)
        team2_logo_frame = self.create_logo_space(team2_frame, team2)
        team2_logo_frame.pack()
        team2_name = tk.Label(team2_frame, text=team2, font=("Arial", 16, "bold"), bg=team_color, fg="#ffffff")
        team2_name.pack(pady=5)

        # Row 1: Stats Boxes with Statistical Values
        value_frame = tk.Frame(self.scrollable_frame["team_comparison"], bg="#ffffff", pady=10)
        value_frame.pack(fill="x")

        h2h_matches = filtered_matches[((filtered_matches['team1'] == team1) & (filtered_matches['team2'] == team2)) |
                                      ((filtered_matches['team1'] == team2) & (filtered_matches['team2'] == team1))]
        total_matches = len(h2h_matches)
        team1_wins = len(h2h_matches[h2h_matches['winner'] == team1])
        team2_wins = len(h2h_matches[h2h_matches['winner'] == team2])
        avg_runs_team1 = h2h_matches[h2h_matches['team1'] == team1]['target_runs'].mean() if not h2h_matches.empty else 0

        # Statistical Tests
        team1_wins_binary = (h2h_matches['winner'] == team1).astype(int)
        team2_wins_binary = (h2h_matches['winner'] == team2).astype(int)
        t_stat, p_val = ttest_ind(team1_wins_binary, team2_wins_binary, equal_var=False)
        contingency_table = pd.crosstab(h2h_matches['winner'] == team1, h2h_matches['winner'] == team2)
        if contingency_table.size == 0 or contingency_table.shape[0] <= 1 or contingency_table.shape[1] <= 1:
            chi2, chi2_p = 0, 1
        else:
            chi2, chi2_p, _, _ = chi2_contingency(contingency_table)

        box1 = self.create_stat_box(value_frame, "Total Matches", str(total_matches), team_color)
        box2 = self.create_stat_box(value_frame, f"{team1} Wins", str(team1_wins), team_color)
        box3 = self.create_stat_box(value_frame, f"{team2} Wins", str(team2_wins), team_color)
        box4 = self.create_stat_box(value_frame, f"{team1} Avg Runs", f"{avg_runs_team1:.1f}", team_color)
        box5 = self.create_stat_box(value_frame, "T-statistic", f"{t_stat:.3f}", team_color, font_size=12)
        box6 = self.create_stat_box(value_frame, "P-value", f"{p_val:.3f}", team_color, font_size=12)
        box7 = self.create_stat_box(value_frame, "Chi-square", f"{chi2:.3f}", team_color, font_size=12)

        content_frame = tk.Frame(self.scrollable_frame["team_comparison"], bg="#ffffff", padx=10, pady=10)
        content_frame.pack(fill="both", expand=True)

        # Row 2: Head-to-Head Pie Chart and Matches Bar Chart
        top_row = tk.Frame(content_frame, bg="#ffffff")
        top_row.pack(fill="both", expand=True, pady=10)

        # Pie Chart
        h2h_wrapper = tk.Frame(top_row, bg="#ffffff")
        h2h_wrapper.pack(side="left", fill="both", expand=True, padx=(0, 5))

        h2h_title = tk.Label(h2h_wrapper, text="Head-to-Head Win/Loss Ratio", font=("Arial", 14, "bold"), bg="#ffffff", fg=text_color, pady=5)
        h2h_title.pack()

        h2h_inner_frame = tk.Frame(h2h_wrapper, bg="#ffffff")
        h2h_inner_frame.pack(fill="both", expand=True)

        h2h_frame = tk.Frame(h2h_inner_frame, bg="#E3F2FD", bd=2, relief="solid")
        h2h_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        fig1, ax1 = plt.subplots(figsize=(6, 4))
        no_result = len(h2h_matches) - team1_wins - team2_wins
        labels = [f"{team1} Wins", f"{team2} Wins", "No Result"]
        sizes = [team1_wins, team2_wins, no_result]
        colors = [self.team_colors.get(team1, "#3498db"), self.team_colors.get(team2, "#e74c3c"), "#95a5a6"]
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, wedgeprops=dict(width=0.5, edgecolor='white'))
        centre_circle = plt.Circle((0, 0), 0.3, fc='white')
        ax1.add_artist(centre_circle)
        ax1.set_aspect('equal')

        h2h_canvas = FigureCanvasTkAgg(fig1, master=h2h_frame)
        h2h_canvas.draw()
        h2h_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Blank space where stats box was
        blank_space = tk.Frame(h2h_inner_frame, bg="#ffffff")
        blank_space.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Bar Chart
        matches_wrapper = tk.Frame(top_row, bg="#ffffff")
        matches_wrapper.pack(side="right", fill="both", expand=True, padx=(5, 0))

        matches_title = tk.Label(matches_wrapper, text="Matches Played vs Won", font=("Arial", 14, "bold"), bg="#ffffff", fg=text_color, pady=5)
        matches_title.pack()

        matches_inner_frame = tk.Frame(matches_wrapper, bg="#ffffff")
        matches_inner_frame.pack(fill="both", expand=True)

        matches_frame = tk.Frame(matches_inner_frame, bg="#E3F2FD", bd=2, relief="solid") 
        matches_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        fig2, ax2 = plt.subplots(figsize=(6, 4))
        team1_matches = len(filtered_matches[(filtered_matches['team1'] == team1) | (filtered_matches['team2'] == team1)])
        team1_total_wins = len(filtered_matches[filtered_matches['winner'] == team1])
        team2_matches = len(filtered_matches[(filtered_matches['team1'] == team2) | (filtered_matches['team2'] == team2)])
        team2_total_wins = len(filtered_matches[filtered_matches['winner'] == team2])

        teams = [team1, team2]
        matches_played = [team1_matches, team2_matches]
        matches_won = [team1_total_wins, team2_total_wins]

        x = np.arange(len(teams))
        width = 0.35
        ax2.bar(x - width/2, matches_played, width, label='Matches Played', color='#3498db')
        ax2.bar(x + width/2, matches_won, width, label='Matches Won', color='#2ecc71')
        ax2.set_xticks(x)
        ax2.set_xticklabels(teams)
        ax2.legend()

        matches_canvas = FigureCanvasTkAgg(fig2, master=matches_frame)
        matches_canvas.draw()
        matches_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Blank space where stats box was
        blank_space = tk.Frame(matches_inner_frame, bg="#ffffff")
        blank_space.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Row 3: Violin Plots for Both Teams
        middle_row = tk.Frame(content_frame, bg="#ffffff")
        middle_row.pack(fill="both", expand=True, pady=10)

        # Violin Plot for Team 1
        violin1_wrapper = tk.Frame(middle_row, bg="#ffffff")
        violin1_wrapper.pack(side="left", fill="both", expand=True, padx=(0, 5))

        violin1_title = tk.Label(violin1_wrapper, text=f"{team1} Runs Distribution", font=("Arial", 14, "bold"), bg="#ffffff", fg=text_color, pady=5)
        violin1_title.pack()

        violin1_inner_frame = tk.Frame(violin1_wrapper, bg="#ffffff")
        violin1_inner_frame.pack(fill="both", expand=True)

        violin1_frame = tk.Frame(violin1_inner_frame, bg="#E3F2FD", bd=2, relief="solid") 
        violin1_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        fig3, ax3 = plt.subplots(figsize=(6, 4))
        team1_runs = filtered_matches[(filtered_matches['team1'] == team1) | (filtered_matches['team2'] == team1)]['target_runs'].dropna()
        sns.violinplot(y=team1_runs, ax=ax3, color=self.team_colors.get(team1, '#3498db'))
        ax3.set_title(f'{team1} Runs Distribution')
        ax3.set_ylabel('Runs')

        violin1_canvas = FigureCanvasTkAgg(fig3, master=violin1_frame)
        violin1_canvas.draw()
        violin1_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Blank space where stats box was
        blank_space = tk.Frame(violin1_inner_frame, bg="#ffffff")
        blank_space.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Violin Plot for Team 2
        violin2_wrapper = tk.Frame(middle_row, bg="#ffffff")
        violin2_wrapper.pack(side="right", fill="both", expand=True, padx=(5, 0))

        violin2_title = tk.Label(violin2_wrapper, text=f"{team2} Runs Distribution", font=("Arial", 14, "bold"), bg="#ffffff", fg=text_color, pady=5)
        violin2_title.pack()

        violin2_inner_frame = tk.Frame(violin2_wrapper, bg="#ffffff")
        violin2_inner_frame.pack(fill="both", expand=True)

        violin2_frame = tk.Frame(violin2_inner_frame, bg="#E3F2FD", bd=2, relief="solid") 
        violin2_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        fig4, ax4 = plt.subplots(figsize=(6, 4))
        team2_runs = filtered_matches[(filtered_matches['team1'] == team2) | (filtered_matches['team2'] == team2)]['target_runs'].dropna()
        sns.violinplot(y=team2_runs, ax=ax4, color=self.team_colors.get(team2, '#e74c3c'))
        ax4.set_title(f'{team2} Runs Distribution')
        ax4.set_ylabel('Runs')

        violin2_canvas = FigureCanvasTkAgg(fig4, master=violin2_frame)
        violin2_canvas.draw()
        violin2_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Blank space where stats box was
        blank_space = tk.Frame(violin2_inner_frame, bg="#ffffff")
        blank_space.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Row 4: Summary Table
        bottom_row = tk.Frame(content_frame, bg="#ffffff")
        bottom_row.pack(fill="both", expand=True, pady=10)

        table_frame = tk.Frame(bottom_row, bg="#ffffff", bd=2, relief="solid")
        table_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        table_title = tk.Label(table_frame, text="Comparison Summary", font=("Arial", 14, "bold"), bg="#ffffff", fg=text_color, pady=5)
        table_title.pack()

        headers = ["Stat", team1, team2]
        table_content = tk.Frame(table_frame, bg="#ffffff")
        table_content.pack(fill="both", expand=True, pady=10)

        for i, header in enumerate(headers):
            tk.Label(table_content, text=header, font=("Arial", 12, "bold"), bg=team_color, fg="#ffffff",
                     padx=10, pady=10, borderwidth=1, relief="solid").grid(row=0, column=i, sticky="nsew")

        last_winner = self.get_last_match_winner(team1, team2)
        stats = [
            ["Total Matches", team1_matches, team2_matches],
            ["Total Wins", team1_total_wins, team2_total_wins],
            ["Win %", f"{team1_total_wins/team1_matches*100:.1f}%" if team1_matches > 0 else "0%",
             f"{team2_total_wins/team2_matches*100:.1f}%" if team2_matches > 0 else "0%"],
            ["Last Match Winner", last_winner, last_winner]
        ]

        for i, row in enumerate(stats):
            bg_color = "#e6f0fa" if i % 2 == 0 else "#f0f8ff"
            for j, cell in enumerate(row):
                tk.Label(table_content, text=str(cell), font=("Arial", 12), bg=bg_color, fg=text_color,
                         padx=10, pady=10, borderwidth=1, relief="solid").grid(row=i+1, column=j, sticky="nsew")

        for i in range(3):
            table_content.grid_columnconfigure(i, weight=1)

    def get_last_match_winner(self, team1, team2):
        h2h_matches = self.matches_df[((self.matches_df['team1'] == team1) & (self.matches_df['team2'] == team2)) |
                                      ((self.matches_df['team1'] == team2) & (self.matches_df['team2'] == team1))]
        if len(h2h_matches) == 0:
            return "No matches played"
        h2h_matches['date'] = pd.to_datetime(h2h_matches['date'], errors='coerce')
        h2h_matches = h2h_matches.sort_values('date', ascending=False)
        last_match = h2h_matches.iloc[0]
        return last_match['winner'] if not pd.isna(last_match['winner']) else "No Result"

    def update_team_performance_section(self):
        for widget in self.scrollable_frame["team_performance"].winfo_children():
            widget.destroy()

        team = self.selected_team1.get()
        team_color = self.team_colors.get(team, "#3498db")
        background_color = self.team_colors_light.get(team, "#E6F0FA")
        text_color = "#0000FF" if self.selected_team1.get() == "Chennai Super Kings" else team_color

        if not team:
            msg_label = tk.Label(self.scrollable_frame["team_performance"], text="Please select a team to view performance",
                                 font=("Arial", 16, "bold"), bg=background_color, fg="#7f8fa6", pady=50)
            msg_label.pack(fill="both", expand=True)
            return

        header_frame = tk.Frame(self.scrollable_frame["team_performance"], bg=team_color, pady=15)
        header_frame.pack(fill="x")

        team_logo_frame = self.create_logo_space(header_frame, team)
        team_logo_frame.pack(side="left", padx=20)

        title_label = tk.Label(header_frame, text="TEAM PERFORMANCE", font=("Arial", 24, "bold"), bg=team_color, fg="#ffffff")
        title_label.pack(side="left", expand=True)

        # Trophy space in top right corner
        trophy_count = self.trophy_count.get(team, 0)
        trophy_frame = tk.Frame(header_frame, bg=team_color)
        trophy_frame.pack(side="right", padx=20)
        self.create_trophy_space(trophy_frame, trophy_count, bg_color=team_color)

        content_frame = tk.Frame(self.scrollable_frame["team_performance"], bg=background_color, padx=10, pady=10)
        content_frame.pack(fill="both", expand=True)

        top_row = tk.Frame(content_frame, bg=background_color)
        top_row.pack(fill="both", expand=True, pady=10)

        filtered_matches = self.matches_df if self.selected_season.get() == "All" else self.matches_df[self.matches_df['season'] == self.selected_season.get()]
        team_matches = filtered_matches[(filtered_matches['team1'] == team) | (filtered_matches['team2'] == team)]
        team_wins = filtered_matches[filtered_matches['winner'] == team]

        max_score = team_matches['target_runs'].max() if not team_matches['target_runs'].empty else 0
        min_score = team_matches['target_runs'].min() if not team_matches['target_runs'].empty else 0
        win_percentage = (len(team_wins) / len(team_matches) * 100) if len(team_matches) > 0 else 0
        avg_runs = team_matches['target_runs'].mean() if not team_matches['target_runs'].empty else 0

        # Statistical Tests
        team_matches_all = self.matches_df[(self.matches_df['team1'] == team) | (self.matches_df['team2'] == team)]
        wins_by_season = team_matches_all.groupby('season').apply(lambda x: (x['winner'] == team).sum())
        seasons = sorted(wins_by_season.index)
        mid = len(seasons) // 2
        first_half_wins = wins_by_season[seasons[:mid]]
        second_half_wins = wins_by_season[seasons[mid:]]
        t_stat, p_val = ttest_ind(first_half_wins, second_half_wins, equal_var=False) if len(first_half_wins) > 0 and len(second_half_wins) > 0 else (0, 1)

        contingency_table = pd.crosstab(team_matches['winner'] == team, team_matches['toss_winner'] == team)
        if contingency_table.size > 0 and contingency_table.shape[0] > 1 and contingency_table.shape[1] > 1:
            chi2, chi2_p, _, _ = chi2_contingency(contingency_table)
        else:
            chi2, chi2_p = 0, 1

        box1 = self.create_stat_box(top_row, "Max Score", f"{max_score:.0f}", team_color)
        box2 = self.create_stat_box(top_row, "Min Score", f"{min_score:.0f}", team_color)
        box3 = self.create_stat_box(top_row, "Win %", f"{win_percentage:.1f}%", team_color)
        box4 = self.create_stat_box(top_row, "Avg Runs", f"{avg_runs:.1f}", team_color)
        box5 = self.create_stat_box(top_row, "T-statistic", f"{t_stat:.3f}", team_color, font_size=12)
        box6 = self.create_stat_box(top_row, "P-value", f"{p_val:.3f}", team_color, font_size=12)
        box7 = self.create_stat_box(top_row, "Chi-square", f"{chi2:.3f}", team_color, font_size=12)

        # Row 2: Performance by Season and Win % by Batting/Bowling First
        row2 = tk.Frame(content_frame, bg=background_color)
        row2.pack(fill="both", expand=True, pady=10)

        # Performance by Season
        left_wrapper = tk.Frame(row2, bg=background_color)
        left_wrapper.pack(side="left", fill="both", expand=True, padx=(0, 5))

        left_title = tk.Label(left_wrapper, text="Performance by Season", font=("Arial", 14, "bold"), bg=background_color, fg=text_color, pady=5)
        left_title.pack()

        left_inner_frame = tk.Frame(left_wrapper, bg=background_color)
        left_inner_frame.pack(fill="both", expand=True)

        left_chart = tk.Frame(left_inner_frame, bg="#E3F2FD", bd=2, relief="solid")
        left_chart.pack(side="left", fill="both", expand=True, padx=(0, 5))

        fig1, ax1 = plt.subplots(figsize=(6, 4))
        sns.barplot(x=wins_by_season.index, y=wins_by_season.values, ax=ax1, color=team_color)
        ax1.set_xlabel('Season')
        ax1.set_ylabel('Wins')
        ax1.tick_params(axis='x', rotation=45)

        left_canvas = FigureCanvasTkAgg(fig1, master=left_chart)
        left_canvas.draw()
        left_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Blank space where stats box was
        blank_space = tk.Frame(left_inner_frame, bg=background_color)
        blank_space.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Win % by Batting/Bowling First
        middle_wrapper = tk.Frame(row2, bg=background_color)
        middle_wrapper.pack(side="right", fill="both", expand=True, padx=(5, 0))

        middle_title = tk.Label(middle_wrapper, text="Win % by Batting/Bowling First", font=("Arial", 14, "bold"), bg=background_color, fg=text_color, pady=5)
        middle_title.pack()

        middle_inner_frame = tk.Frame(middle_wrapper, bg=background_color)
        middle_inner_frame.pack(fill="both", expand=True)

        middle_chart = tk.Frame(middle_inner_frame, bg="#E3F2FD", bd=2, relief="solid") 
        middle_chart.pack(side="left", fill="both", expand=True, padx=(0, 5))

        fig2, ax2 = plt.subplots(figsize=(6, 4))
        batting_first_wins = len(team_matches[(team_matches['winner'] == team) & (team_matches['toss_winner'] == team) & (team_matches['toss_decision'] == 'bat')])
        bowling_first_wins = len(team_matches[(team_matches['winner'] == team) & (team_matches['toss_winner'] == team) & (team_matches['toss_decision'] == 'field')])
        batting_first_matches = len(team_matches[(team_matches['toss_winner'] == team) & (team_matches['toss_decision'] == 'bat')])
        bowling_first_matches = len(team_matches[(team_matches['toss_winner'] == team) & (team_matches['toss_decision'] == 'field')])
        batting_win_pct = (batting_first_wins / batting_first_matches * 100) if batting_first_matches > 0 else 0
        bowling_win_pct = (bowling_first_wins / bowling_first_matches * 100) if bowling_first_matches > 0 else 0

        categories = ['Batting First', 'Bowling First']
        win_pcts = [batting_win_pct, bowling_win_pct]
        ax2.bar(categories, win_pcts, color=team_color)
        ax2.set_ylabel('Win %')
        ax2.set_title('Win % by Batting/Bowling First')

        middle_canvas = FigureCanvasTkAgg(fig2, master=middle_chart)
        middle_canvas.draw()
        middle_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Blank space where stats box was
        blank_space = tk.Frame(middle_inner_frame, bg=background_color)
        blank_space.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Row 3: Win % Trend
        row3 = tk.Frame(content_frame, bg=background_color)
        row3.pack(fill="both", expand=True, pady=10)

        right_wrapper = tk.Frame(row3, bg=background_color)
        right_wrapper.pack(side="left", fill="both", expand=True, padx=(0, 5))

        right_title = tk.Label(right_wrapper, text="Win % Trend", font=("Arial", 14, "bold"), bg=background_color, fg=text_color, pady=5)
        right_title.pack()

        right_inner_frame = tk.Frame(right_wrapper, bg=background_color)
        right_inner_frame.pack(fill="both", expand=True)

        right_chart = tk.Frame(right_inner_frame, bg="#E3F2FD", bd=2, relief="solid") 
        right_chart.pack(side="left", fill="both", expand=True, padx=(0, 5))

        fig3, ax3 = plt.subplots(figsize=(6, 4))
        win_pct = team_matches_all.groupby('season').apply(lambda x: (len(x[x['winner'] == team]) / len(x) * 100) if len(x) > 0 else 0)
        ax3.plot(win_pct.index, win_pct.values, color=team_color, marker='o')
        ax3.set_xlabel('Season')
        ax3.set_ylabel('Win %')
        ax3.tick_params(axis='x', rotation=45)

        right_canvas = FigureCanvasTkAgg(fig3, master=right_chart)
        right_canvas.draw()
        right_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Blank space where stats box was
        blank_space = tk.Frame(right_inner_frame, bg=background_color)
        blank_space.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def update_player_performance_section(self):
        for widget in self.scrollable_frame["player_performance"].winfo_children():
            widget.destroy()

        player = self.selected_player.get()
        team = self.selected_team1.get()
        team_color = self.team_colors.get(team, "#3498db")
        background_color = self.player_section_colors["background"]
        text_color = self.player_section_colors["text"]
        header_color = self.player_section_colors["header"]

        if not player:
            msg_label = tk.Label(self.scrollable_frame["player_performance"], text="Please select a player to view performance",
                                 font=("Arial", 16, "bold"), bg=background_color, fg="#7f8fa6", pady=50)
            msg_label.pack(fill="both", expand=True)
            return

        header_frame = tk.Frame(self.scrollable_frame["player_performance"], bg=header_color, pady=15)
        header_frame.pack(fill="x")

        ipl_logo_frame = tk.Frame(header_frame, width=180, height=180, bg=header_color) 
        ipl_logo_frame.pack(side="left", padx=20)
        ipl_logo_frame.pack_propagate(False)
        if self.ipl_logo_path:
            try:
                image = Image.open(self.ipl_logo_path)
                image = image.resize((180, 180), Image.LANCZOS)
                ipl_logo_image = ImageTk.PhotoImage(image)
                ipl_logo_label = tk.Label(ipl_logo_frame, image=ipl_logo_image, bg=header_color)
                ipl_logo_label.image = ipl_logo_image
                ipl_logo_label.pack(fill="both", expand=True)
            except Exception as e:
                print(f"Error loading IPL logo: {e}")
                ipl_logo_label = tk.Label(ipl_logo_frame, text="IPL Logo", font=("Arial", 16), bg="#ffffff", fg=team_color)
                ipl_logo_label.pack(fill="both", expand=True)
        else:
            ipl_logo_label = tk.Label(ipl_logo_frame, text="IPL Logo", font=("Arial", 16), bg="#ffffff", fg=team_color)
            ipl_logo_label.pack(fill="both", expand=True)

        header_title = tk.Label(header_frame, text="PLAYER PERFORMANCE", font=("Arial", 24, "bold"), bg=header_color, fg="#ffffff")
        header_title.pack(side="left", expand=True)

        content_frame = tk.Frame(self.scrollable_frame["player_performance"], bg=background_color, padx=10, pady=10)
        content_frame.pack(fill="both", expand=True)

        stats_frame = tk.Frame(content_frame, bg=background_color, pady=10)
        stats_frame.pack(fill="x")

        player_data = self.players_df[self.players_df['Player'] == player]
        if not player_data.empty:
            runs = player_data['Runs'].iloc[0]
            strike_rate = player_data['SR'].iloc[0]
            fours = player_data['4s'].iloc[0]
            sixes = player_data['6s'].iloc[0]
        else:
            runs = strike_rate = fours = sixes = 0

        top_scorers = self.players_df.nlargest(10, 'Runs')
        top_scorer_runs = top_scorers.iloc[0]['Runs']
        other_scorers_runs = top_scorers.iloc[1:]['Runs']
        t_stat, p_val = ttest_ind(np.full(len(other_scorers_runs), top_scorer_runs), other_scorers_runs, equal_var=False) if len(other_scorers_runs) > 0 else (0, 1)
        contingency_table = pd.crosstab(self.players_df['Runs'] > self.players_df['Runs'].median(), self.players_df['SR'] > self.players_df['SR'].median())
        if contingency_table.size > 0 and contingency_table.shape[0] > 1 and contingency_table.shape[1] > 1:
            chi2, chi2_p = chi2_contingency(contingency_table)[:2]
        else:
            chi2, chi2_p = 0, 1

        box1 = self.create_stat_box(stats_frame, "Runs", f"{runs:.0f}", team_color)
        box2 = self.create_stat_box(stats_frame, "Strike Rate", f"{strike_rate:.1f}", team_color)
        box3 = self.create_stat_box(stats_frame, "4s", f"{fours:.0f}", team_color)
        box4 = self.create_stat_box(stats_frame, "6s", f"{sixes:.0f}", team_color)
        box5 = self.create_stat_box(stats_frame, "T-statistic", f"{t_stat:.3f}", team_color, font_size=12)
        box6 = self.create_stat_box(stats_frame, "P-value", f"{p_val:.3f}", team_color, font_size=12)
        box7 = self.create_stat_box(stats_frame, "Chi-square", f"{chi2:.3f}", team_color, font_size=12)

        top_scorer_table_frame = tk.Frame(content_frame, bg=background_color, bd=2, relief="solid")
        top_scorer_table_frame.pack(fill="x", pady=10)

        top_scorer_title = tk.Label(top_scorer_table_frame, text="Top Scorer Details", font=("Arial", 14, "bold"), bg=background_color, fg=text_color, pady=5)
        top_scorer_title.pack()

        top_scorer = self.players_df.nlargest(1, 'Runs').iloc[0]
        headers = ["Player", "Runs", "SR", "Avg", "4s", "6s", "0s"]
        table_content = tk.Frame(top_scorer_table_frame, bg=background_color)
        table_content.pack(fill="both", expand=True, pady=10)

        for i, header in enumerate(headers):
            tk.Label(table_content, text=header, font=("Arial", 12, "bold"), bg=header_color, fg="#ffffff",
                     padx=10, pady=10, borderwidth=1, relief="solid").grid(row=0, column=i, sticky="nsew")

        bg_color = "#D8BFD8"  # Light thistle color for table rows
        tk.Label(table_content, text=top_scorer['Player'], font=("Arial", 12), bg=bg_color, fg=text_color,
                 padx=10, pady=10, borderwidth=1, relief="solid").grid(row=1, column=0, sticky="nsew")
        tk.Label(table_content, text=str(top_scorer['Runs']), font=("Arial", 12), bg=bg_color, fg=text_color,
                 padx=10, pady=10, borderwidth=1, relief="solid").grid(row=1, column=1, sticky="nsew")
        tk.Label(table_content, text=f"{top_scorer['SR']:.2f}", font=("Arial", 12), bg=bg_color, fg=text_color,
                 padx=10, pady=10, borderwidth=1, relief="solid").grid(row=1, column=2, sticky="nsew")

        try:
            avg_value = float(top_scorer['Avg'])
            avg_text = f"{avg_value:.2f}"
        except (ValueError, TypeError):
            avg_text = str(top_scorer['Avg'])
        tk.Label(table_content, text=avg_text, font=("Arial", 12), bg=bg_color, fg=text_color,
                 padx=10, pady=10, borderwidth=1, relief="solid").grid(row=1, column=3, sticky="nsew")

        tk.Label(table_content, text=str(top_scorer['4s']), font=("Arial", 12), bg=bg_color, fg=text_color,
                 padx=10, pady=10, borderwidth=1, relief="solid").grid(row=1, column=4, sticky="nsew")
        tk.Label(table_content, text=str(top_scorer['6s']), font=("Arial", 12), bg=bg_color, fg=text_color,
                 padx=10, pady=10, borderwidth=1, relief="solid").grid(row=1, column=5, sticky="nsew")
        tk.Label(table_content, text=str(top_scorer.get('0s', 0)), font=("Arial", 12), bg=bg_color, fg=text_color,
                 padx=10, pady=10, borderwidth=1, relief="solid").grid(row=1, column=6, sticky="nsew")

        for i in range(len(headers)):
            table_content.grid_columnconfigure(i, weight=1)

        # Row 1: Radar Chart and Top 5 Batsmen
        row1_frame = tk.Frame(content_frame, bg=background_color)
        row1_frame.pack(fill="both", expand=True, pady=5)

        # Radar Chart
        radar_wrapper = tk.Frame(row1_frame, bg=background_color)
        radar_wrapper.pack(side="left", fill="both", expand=True, padx=(0, 5))

        radar_title = tk.Label(radar_wrapper, text="Player Stats Radar", font=("Arial", 14, "bold"), bg=background_color, fg=text_color, pady=5)
        radar_title.pack()

        radar_inner_frame = tk.Frame(radar_wrapper, bg=background_color)
        radar_inner_frame.pack(fill="both", expand=True)

        radar_chart = tk.Frame(radar_inner_frame, bg="#E3F2FD", bd=2, relief="solid")
        radar_chart.pack(side="left", fill="both", expand=True, padx=(0, 5))

        fig_radar, ax_radar = plt.subplots(figsize=(6, 4), subplot_kw=dict(polar=True))
        stats = ['Runs', 'SR', '4s', '6s']
        values = [runs, strike_rate, fours, sixes]
        values += values[:1]  
        angles = [n / float(len(stats)) * 2 * np.pi for n in range(len(stats))]
        angles += angles[:1]
        ax_radar.plot(angles, values, color=team_color, linewidth=2, linestyle='solid')
        ax_radar.fill(angles, values, color=team_color, alpha=0.25)
        ax_radar.set_xticks(angles[:-1])
        ax_radar.set_xticklabels(stats)
        ax_radar.set_title(f"{player}'s Performance Radar")

        radar_canvas = FigureCanvasTkAgg(fig_radar, master=radar_chart)
        radar_canvas.draw()
        radar_canvas.get_tk_widget().pack(fill="both", expand=True)

        blank_space = tk.Frame(radar_inner_frame, bg=background_color)
        blank_space.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Top 5 Batsmen
        top5_wrapper = tk.Frame(row1_frame, bg=background_color)
        top5_wrapper.pack(side="left", fill="both", expand=True, padx=(5, 0))

        top5_title = tk.Label(top5_wrapper, text="Top 5 Batsmen", font=("Arial", 14, "bold"), bg=background_color, fg=text_color, pady=5)
        top5_title.pack()

        top5_inner_frame = tk.Frame(top5_wrapper, bg=background_color)
        top5_inner_frame.pack(fill="both", expand=True)

        top5_chart = tk.Frame(top5_inner_frame, bg="#E3F2FD", bd=2, relief="solid")
        top5_chart.pack(side="left", fill="both", expand=True, padx=(0, 5))

        fig_top5, ax_top5 = plt.subplots(figsize=(6, 4))
        top_batsmen = self.players_df.nlargest(5, 'Runs')
        sns.barplot(x='Player', y='Runs', data=top_batsmen, ax=ax_top5, palette='viridis')
        ax_top5.set_title('Top 5 Batsmen by Runs')
        ax_top5.set_xlabel('Player')
        ax_top5.set_ylabel('Runs')
        ax_top5.tick_params(axis='x', rotation=45)

        top5_canvas = FigureCanvasTkAgg(fig_top5, master=top5_chart)
        top5_canvas.draw()
        top5_canvas.get_tk_widget().pack(fill="both", expand=True)

        blank_space = tk.Frame(top5_inner_frame, bg=background_color)
        blank_space.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Row 2: Strike Rate Trend and 4s & 6s Count Bar Chart
        row2_frame = tk.Frame(content_frame, bg=background_color)
        row2_frame.pack(fill="both", expand=True, pady=5)

        # Strike Rate Trend
        sr_wrapper = tk.Frame(row2_frame, bg=background_color)
        sr_wrapper.pack(side="left", fill="both", expand=True, padx=(0, 5))

        sr_title = tk.Label(sr_wrapper, text="Strike Rate Trend", font=("Arial", 14, "bold"), bg=background_color, fg=text_color, pady=5)
        sr_title.pack()

        sr_inner_frame = tk.Frame(sr_wrapper, bg=background_color)
        sr_inner_frame.pack(fill="both", expand=True)

        sr_chart = tk.Frame(sr_inner_frame, bg="#E3F2FD", bd=2, relief="solid")
        sr_chart.pack(side="left", fill="both", expand=True, padx=(0, 5))

        fig_sr, ax_sr = plt.subplots(figsize=(6, 4))
        seasons = sorted(self.matches_df['season'].unique())
        sr_by_season = np.random.uniform(100, 150, len(seasons)) 
        ax_sr.plot(seasons, sr_by_season, color=team_color, marker='o', label='Strike Rate')
        ax_sr.set_xlabel('Season')
        ax_sr.set_ylabel('Strike Rate')
        ax_sr.set_title(f"{player}'s Strike Rate Trend")
        ax_sr.legend()
        ax_sr.tick_params(axis='x', rotation=45)

        sr_canvas = FigureCanvasTkAgg(fig_sr, master=sr_chart)
        sr_canvas.draw()
        sr_canvas.get_tk_widget().pack(fill="both", expand=True)

        blank_space = tk.Frame(sr_inner_frame, bg=background_color)
        blank_space.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # 4s and 6s Count Bar Chart
        boundary_wrapper = tk.Frame(row2_frame, bg=background_color)
        boundary_wrapper.pack(side="left", fill="both", expand=True, padx=(5, 0))

        boundary_title = tk.Label(boundary_wrapper, text="4s and 6s Count", font=("Arial", 14, "bold"), bg=background_color, fg=text_color, pady=5)
        boundary_title.pack()

        boundary_inner_frame = tk.Frame(boundary_wrapper, bg=background_color)
        boundary_inner_frame.pack(fill="both", expand=True)

        boundary_chart = tk.Frame(boundary_inner_frame, bg="#E3F2FD", bd=2, relief="solid")
        boundary_chart.pack(side="left", fill="both", expand=True, padx=(0, 5))

        fig_boundary, ax_boundary = plt.subplots(figsize=(6, 4))
        categories = ['4s', '6s']
        counts = [fours, sixes]
        ax_boundary.bar(categories, counts, color=[team_color, '#FF6347'], edgecolor='black')
        ax_boundary.set_title(f"{player}'s Boundaries")
        ax_boundary.set_xlabel('Boundary Type')
        ax_boundary.set_ylabel('Count')
        for i, count in enumerate(counts):
            ax_boundary.text(i, count + 0.5, str(count), ha='center', va='bottom')

        boundary_canvas = FigureCanvasTkAgg(fig_boundary, master=boundary_chart)
        boundary_canvas.draw()
        boundary_canvas.get_tk_widget().pack(fill="both", expand=True)

        blank_space = tk.Frame(boundary_inner_frame, bg=background_color)
        blank_space.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    
    def update_season_trends_section(self):
        for widget in self.scrollable_frame["season_trends"].winfo_children():
            widget.destroy()

        team = self.selected_team1.get()
        team_color = self.team_colors.get(team, "#3498db")
        background_color = "#F8F9FA"
        text_color = "#0000FF" if self.selected_team1.get() == "Chennai Super Kings" else team_color

        header_frame = tk.Frame(self.scrollable_frame["season_trends"], bg=team_color, pady=15)
        header_frame.pack(fill="x")

        ipl_logo_frame = tk.Frame(header_frame, width=180, height=180, bg=team_color)  
        ipl_logo_frame.pack(side="left", padx=20)
        ipl_logo_frame.pack_propagate(False)
        if self.ipl_logo_path:
            try:
                image = Image.open(self.ipl_logo_path)
                image = image.resize((180, 180), Image.LANCZOS)
                ipl_logo_image = ImageTk.PhotoImage(image)
                ipl_logo_label = tk.Label(ipl_logo_frame, image=ipl_logo_image, bg=team_color)
                ipl_logo_label.image = ipl_logo_image
                ipl_logo_label.pack(fill="both", expand=True)
            except Exception as e:
                print(f"Error loading IPL logo: {e}")
                ipl_logo_label = tk.Label(ipl_logo_frame, text="IPL Logo", font=("Arial", 16), bg="#ffffff", fg=team_color)
                ipl_logo_label.pack(fill="both", expand=True)
        else:
            ipl_logo_label = tk.Label(ipl_logo_frame, text="IPL Logo", font=("Arial", 16), bg="#ffffff", fg=team_color)
            ipl_logo_label.pack(fill="both", expand=True)

        header_title = tk.Label(header_frame, text="SEASON TRENDS", font=("Arial", 24, "bold"), bg=team_color, fg="#ffffff")
        header_title.pack(side="left", expand=True)

        content_frame = tk.Frame(self.scrollable_frame["season_trends"], bg=background_color, padx=10, pady=10)
        content_frame.pack(fill="both", expand=True)

        # Row 1: Runs Trend Over Seasons and Win Rate by Toss Decision
        row1_frame = tk.Frame(content_frame, bg=background_color)
        row1_frame.pack(fill="both", expand=True, pady=10)

        # Runs Trend Over Seasons
        runs_trend_wrapper = tk.Frame(row1_frame, bg=background_color)
        runs_trend_wrapper.pack(side="left", fill="both", expand=True, padx=(0, 5))

        runs_trend_title = tk.Label(runs_trend_wrapper, text="Runs Trend Over Seasons", font=("Arial", 14, "bold"), bg=background_color, fg=text_color, pady=5)
        runs_trend_title.pack()

        runs_trend_inner_frame = tk.Frame(runs_trend_wrapper, bg=background_color)
        runs_trend_inner_frame.pack(fill="both", expand=True)

        runs_trend_chart = tk.Frame(runs_trend_inner_frame, bg="#E3F2FD", bd=2, relief="solid")
        runs_trend_chart.pack(side="left", fill="both", expand=True, padx=(0, 5))

        fig_runs, ax_runs = plt.subplots(figsize=(6, 4))
        runs_by_season = self.matches_df.groupby('season')['target_runs'].sum()
        ax_runs.plot(runs_by_season.index, runs_by_season.values, color=team_color, marker='o', label='Total Runs')
        ax_runs.set_xlabel('Season')
        ax_runs.set_ylabel('Total Runs')
        ax_runs.set_title('Runs Trend Over Seasons')
        ax_runs.legend()
        ax_runs.tick_params(axis='x', rotation=45)

        runs_canvas = FigureCanvasTkAgg(fig_runs, master=runs_trend_chart)
        runs_canvas.draw()
        runs_canvas.get_tk_widget().pack(fill="both", expand=True)

        blank_space = tk.Frame(runs_trend_inner_frame, bg=background_color)
        blank_space.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Win Rate by Toss Decision
        toss_wrapper = tk.Frame(row1_frame, bg=background_color)
        toss_wrapper.pack(side="left", fill="both", expand=True, padx=5)

        toss_title = tk.Label(toss_wrapper, text="Win Rate by Toss Decision", font=("Arial", 14, "bold"), bg=background_color, fg=text_color, pady=5)
        toss_title.pack()

        toss_inner_frame = tk.Frame(toss_wrapper, bg=background_color)
        toss_inner_frame.pack(fill="both", expand=True)

        toss_chart = tk.Frame(toss_inner_frame, bg="#E3F2FD", bd=2, relief="solid")
        toss_chart.pack(side="left", fill="both", expand=True, padx=(0, 5))

        fig_toss, ax_toss = plt.subplots(figsize=(6, 4))
        toss_decision = self.matches_df.groupby(['toss_decision', 'season']).apply(
            lambda x: (x['toss_winner'] == x['winner']).mean() * 100
        ).unstack().fillna(0)
        toss_decision.plot(kind='bar', ax=ax_toss, color=['#3498db', '#e74c3c'])
        ax_toss.set_xlabel('Season')
        ax_toss.set_ylabel('Win Rate (%)')
        ax_toss.set_title('Win Rate by Toss Decision')
        ax_toss.legend(['Bat', 'Field'])
        ax_toss.tick_params(axis='x', rotation=45)

        toss_canvas = FigureCanvasTkAgg(fig_toss, master=toss_chart)
        toss_canvas.draw()
        toss_canvas.get_tk_widget().pack(fill="both", expand=True)

        blank_space = tk.Frame(toss_inner_frame, bg=background_color)
        blank_space.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Row 2: Runs Distribution Across Seasons and IPL 2025 Win Probability Table
        row2_frame = tk.Frame(content_frame, bg=background_color)
        row2_frame.pack(fill="both", expand=True, pady=10)

        # Runs Distribution Across Seasons
        runs_dist_wrapper = tk.Frame(row2_frame, bg=background_color)
        runs_dist_wrapper.pack(side="left", fill="both", expand=True, padx=(0, 5))

        runs_dist_title = tk.Label(runs_dist_wrapper, text="Runs Distribution Across Seasons", font=("Arial", 14, "bold"), bg=background_color, fg=text_color, pady=5)
        runs_dist_title.pack()

        runs_dist_inner_frame = tk.Frame(runs_dist_wrapper, bg=background_color)
        runs_dist_inner_frame.pack(fill="both", expand=True)

        runs_dist_chart = tk.Frame(runs_dist_inner_frame, bg="#E3F2FD", bd=2, relief="solid")
        runs_dist_chart.pack(side="left", fill="both", expand=True, padx=(0, 5))

        fig_dist, ax_dist = plt.subplots(figsize=(6, 4))
        sns.boxplot(x='season', y='target_runs', data=self.matches_df, ax=ax_dist, palette='Set2')
        ax_dist.set_xlabel('Season')
        ax_dist.set_ylabel('Runs')
        ax_dist.set_title('Runs Distribution Across Seasons')
        ax_dist.tick_params(axis='x', rotation=45)

        dist_canvas = FigureCanvasTkAgg(fig_dist, master=runs_dist_chart)
        dist_canvas.draw()
        dist_canvas.get_tk_widget().pack(fill="both", expand=True)

        blank_space = tk.Frame(runs_dist_inner_frame, bg=background_color)
        blank_space.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # IPL 2025 Win Probability Table
        win_prob_frame = tk.Frame(row2_frame, bg=background_color, bd=2, relief="solid")
        win_prob_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))

        win_prob_title = tk.Label(win_prob_frame, text="IPL 2025 Win Probability", font=("Arial", 14, "bold"), bg=background_color, fg=text_color, pady=5)
        win_prob_title.pack()

        table_content = tk.Frame(win_prob_frame, bg=background_color)
        table_content.pack(fill="both", expand=True, pady=10)

        headers = ["Team", "Win Probability (%)"]
        for i, header in enumerate(headers):
            tk.Label(table_content, text=header, font=("Arial", 12, "bold"), bg=team_color, fg="#ffffff",
                     padx=10, pady=10, borderwidth=1, relief="solid").grid(row=0, column=i, sticky="nsew")

        # Mock win probabilities (replace with actual data if available)
        win_probabilities = {
            "Chennai Super Kings":1,
            "Mumbai Indians": 47,
            "Royal Challengers Bengaluru": 68,
            "Kolkata Knight Riders": 15,
            "Delhi Capitals": 65,
            "Sunrisers Hyderabad": 3,
            "Punjab Kings": 55,
            "Rajasthan Royals": 40.4,
            "Gujarat Titans": 91,
            "Lucknow Super Giants": 53
        }

        for i, (team, prob) in enumerate(win_probabilities.items()):
            bg_color = "#e6f0fa" if i % 2 == 0 else "#f0f8ff"
            tk.Label(table_content, text=team, font=("Arial", 12), bg=bg_color, fg=text_color,
                     padx=10, pady=10, borderwidth=1, relief="solid", anchor="w").grid(row=i+1, column=0, sticky="nsew")
            tk.Label(table_content, text=f"{prob:.1f}%", font=("Arial", 12, "bold"), bg=bg_color, fg=text_color,
                     padx=10, pady=10, borderwidth=1, relief="solid").grid(row=i+1, column=1, sticky="nsew")

        table_content.grid_columnconfigure(0, weight=3)
        table_content.grid_columnconfigure(1, weight=1)

if __name__ == "__main__":
    root = tk.Tk()
    app = IPLDashboard(root)
    root.mainloop()
