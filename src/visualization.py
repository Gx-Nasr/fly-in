import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backend_bases import KeyEvent
from .data_classes import GraphData


class DroneVisualizer:
    def __init__(self, graph: GraphData) -> None:
        self.graph = graph
        self.bg_image_path = "./images/background.png"
        self.current_turn = 0
        self.max_turns = graph.turns

        self.COLORS = {
            "red": "#FF3B30", "darkred": "#8B0000", "crimson": "#DC143C",
            "maroon": "#800000", "orange": "#FF9500", "gold": "#FFD60A",
            "yellow": "#FFFF00", "green": "#34C759", "lime": "#32CD32",
            "blue": "#0A84FF", "cyan": "#64D2FF", "purple": "#AF52DE",
            "violet": "#BF5AF2", "magenta": "#FF2D55", "brown": "#A2845E",
            "black": "#1C1C1E", "gray": "#8E8E93", "white": "#FFFFFF",
            "pink": "#FF69B4", "silver": "#C0C0C0", "default": "#FFFFFF"
        }

        plt.rcParams['toolbar'] = 'None'
        self.fig = plt.figure()

        window_manager = plt.get_current_fig_manager()
        tk_root = window_manager.window

        screen_width = tk_root.winfo_screenwidth()
        screen_height = tk_root.winfo_screenheight()
        tk_root.geometry(f"{screen_width}x{screen_height}")
        tk_root.title("Fly-in")

        self.bg_image = mpimg.imread(self.bg_image_path)

        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

    def draw_current_state(self) -> None:
        self.fig.clear()

        ax = self.fig.add_axes([0, 0, 1, 1])
        ax.axis("off")

        SCALE_X = 6
        SCALE_Y = 12

        all_x = [zone.x * SCALE_X for zone in self.graph.zones_dict.values()]
        all_y = [zone.y * SCALE_Y for zone in self.graph.zones_dict.values()]

        padding_x = 8
        padding_y = 8

        xmin = min(all_x) - padding_x
        xmax = max(all_x) + padding_x

        ymin = min(all_y) - padding_y
        ymax = max(all_y) + padding_y

        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

        ax.imshow(
            self.bg_image,
            extent=[xmin, xmax, ymin, ymax],
            aspect="auto",
            zorder=0
        )

        # Connections
        for conn in self.graph.connections:
            x1 = conn.from_zone.x * SCALE_X
            y1 = conn.from_zone.y * SCALE_Y

            x2 = conn.to_zone.x * SCALE_X
            y2 = conn.to_zone.y * SCALE_Y

            ax.plot(
                [x1, x2],
                [y1, y2],
                color="#505860",
                linewidth=2,
                alpha=0.6,
                zorder=1
            )

        for zone in self.graph.zones_dict.values():

            draw_x = zone.x * SCALE_X
            draw_y = zone.y * SCALE_Y

            color_hex = self.COLORS.get(
                zone.color,
                self.COLORS["default"]
            )

            ax.scatter(
                draw_x,
                draw_y,
                color=color_hex,
                s=300,
                zorder=2,
                edgecolors="white",
                linewidths=1.5
            )

            ax.text(
                draw_x,
                draw_y - 2,
                zone.name,
                color="white",
                fontsize=7,
                ha="center"
            )

        for drone in self.graph.all_drones:

            if self.current_turn < len(drone.path):
                active_zone, _ = drone.path[self.current_turn]
            else:
                active_zone, _ = drone.path[-1]

            drone_x = active_zone.x * SCALE_X
            drone_y = active_zone.y * SCALE_Y

            ax.scatter(
                drone_x,
                drone_y,
                s=90,
                color="#00FF66",
                edgecolors="black",
                zorder=4
            )

            ax.text(
                drone_x,
                drone_y + 2,
                f"D{drone.id_drone + 1}",
                color="#00FF66",
                fontsize=8,
                ha="center",
                weight="bold",
                zorder=5
            )

        title_x = (xmin + xmax) / 2

        ax.text(
            title_x,
            ymax - 2,
            "DRONE ROUTING TRAFFIC CONTROL — "
            f"{len(self.graph.all_drones)} DRONES",
            color="white",
            fontsize=16,
            ha="center",
            weight="bold",
            fontname="monospace"
        )

        ax.text(
            title_x,
            ymax - 5,
            f"CURRENT TURN: {self.current_turn}/{self.max_turns - 1}",
            color=self.COLORS["gold"],
            fontsize=11,
            ha="center",
            weight="bold",
            fontname="monospace"
        )

        self.fig.canvas.draw()

    def on_key(self, event: KeyEvent) -> None:
        if event.key == 'right':
            if self.current_turn < self.max_turns - 1:
                self.current_turn += 1
                self.draw_current_state()
        elif event.key == 'left':
            if self.current_turn > 0:
                self.current_turn -= 1
                self.draw_current_state()

    def show(self) -> None:
        self.draw_current_state()
        plt.show()
